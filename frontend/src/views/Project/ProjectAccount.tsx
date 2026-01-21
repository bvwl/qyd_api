import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, Tag, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ProjectAccount, Project } from '@/types'
import { AccountType, Status } from '@/types'
import { getProjectAccountList, createProjectAccount, updateProjectAccount, deleteProjectAccount, getProjectList } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ProjectAccountList = () => {
  const [data, setData] = useState<ProjectAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingAccount, setEditingAccount] = useState<ProjectAccount | null>(null)
  const [projectList, setProjectList] = useState<Project[]>([])
  const [searchAccount, setSearchAccount] = useState('')
  const [searchAccountType, setSearchAccountType] = useState<number>()
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')
  const isGM = hasPermission('GM')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getProjectAccountList({
        page,
        limit: pageSize,
        res_count: true,
        account: searchAccount || undefined,
        account_type: searchAccountType,
        status: searchStatus,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
      })
      setData(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      // 404 表示无数据，静默处理
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const fetchProjectList = async () => {
    try {
      const res = await getProjectList({
        page: 1,
        limit: 1000,
      })
      setProjectList(res.items || [])
    } catch (error) {
      setProjectList([])
    }
  }

  useEffect(() => {
    fetchData()
    fetchProjectList()
  }, [page, pageSize])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchAccount('')
    setSearchAccountType(undefined)
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingAccount(null)
    form.resetFields()
    form.setFieldsValue({
      status: Status.NORMAL,
      account_type: AccountType.EMAIL,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: ProjectAccount) => {
    setEditingAccount(record)
    form.setFieldsValue({
      account: record.account,
      password: record.password,
      status: record.status,
      account_type: record.account_type,
      project_id: record.project_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProjectAccount(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingAccount) {
        await updateProjectAccount(editingAccount.id, values)
        message.success('更新成功')
      } else {
        await createProjectAccount(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const getAccountTypeText = (type: AccountType) => {
    const typeMap: Record<AccountType, string> = {
      [AccountType.EMAIL]: '邮箱',
      [AccountType.WALLET]: '钱包',
      [AccountType.X]: 'X',
      [AccountType.OTHER1]: '其他1',
      [AccountType.OTHER2]: '其他2',
    }
    return typeMap[type] || '未知'
  }

  const columns = [
    {
      title: '账号',
      dataIndex: 'account',
      key: 'account',
    },
    {
      title: '账号类型',
      dataIndex: 'account_type',
      key: 'account_type',
      render: (type: AccountType) => getAccountTypeText(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: Status) => (
        <Tag color={status === Status.NORMAL ? 'green' : 'red'}>
          {status === Status.NORMAL ? '正常' : '异常'}
        </Tag>
      ),
    },
    {
      title: '项目',
      dataIndex: 'project',
      key: 'project',
      render: (project: any) => project?.name || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ProjectAccount) => (
        <Space>
          {(isAdmin || isGM) && (
            <>
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定删除该账号吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Space wrap>
            <Input
              placeholder="账号"
              value={searchAccount}
              onChange={(e) => setSearchAccount(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Select
              placeholder="账号类型"
              value={searchAccountType}
              onChange={setSearchAccountType}
              style={{ width: 150 }}
              allowClear
            >
              <Select.Option value={AccountType.EMAIL}>邮箱</Select.Option>
              <Select.Option value={AccountType.WALLET}>钱包</Select.Option>
              <Select.Option value={AccountType.X}>X</Select.Option>
              <Select.Option value={AccountType.OTHER1}>其他1</Select.Option>
              <Select.Option value={AccountType.OTHER2}>其他2</Select.Option>
            </Select>
            <Select
              placeholder="状态"
              value={searchStatus}
              onChange={setSearchStatus}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value={Status.NORMAL}>正常</Select.Option>
              <Select.Option value={Status.ABNORMAL}>异常</Select.Option>
            </Select>
            <RangePicker
              placeholder={['创建开始日期', '创建结束日期']}
              value={createTimeRange}
              onChange={(dates) => setCreateTimeRange(dates as [Dayjs, Dayjs] | null)}
              format="YYYY-MM-DD"
              style={{ width: 260 }}
            />
            <RangePicker
              placeholder={['更新开始日期', '更新结束日期']}
              value={updateTimeRange}
              onChange={(dates) => setUpdateTimeRange(dates as [Dayjs, Dayjs] | null)}
              format="YYYY-MM-DD"
              style={{ width: 260 }}
            />
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
              搜索
            </Button>
            <Button onClick={handleReset}>重置</Button>
          </Space>
          {(isAdmin || isGM) && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增账号
            </Button>
          )}
        </div>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />

      <Modal
        title={editingAccount ? '编辑账号' : '新增账号'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="账号"
            name="account"
            rules={[{ required: true, message: '请输入账号' }]}
          >
            <Input placeholder="请输入账号" />
          </Form.Item>
          <Form.Item label="密码" name="password">
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Form.Item
            label="账号类型"
            name="account_type"
            rules={[{ required: true, message: '请选择账号类型' }]}
          >
            <Select placeholder="请选择账号类型">
              <Select.Option value={AccountType.EMAIL}>邮箱</Select.Option>
              <Select.Option value={AccountType.WALLET}>钱包</Select.Option>
              <Select.Option value={AccountType.X}>X</Select.Option>
              <Select.Option value={AccountType.OTHER1}>其他1</Select.Option>
              <Select.Option value={AccountType.OTHER2}>其他2</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              <Select.Option value={Status.NORMAL}>正常</Select.Option>
              <Select.Option value={Status.ABNORMAL}>异常</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            label="项目"
            name="project_id"
            rules={[{ required: true, message: '请选择项目' }]}
          >
            <Select
              placeholder="请选择项目"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={projectList.map(project => ({
                label: project.name,
                value: project.id,
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProjectAccountList
