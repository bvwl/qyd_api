import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, InputNumber, message, Space, Popconfirm, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ProjectBalance, ProjectAccount } from '@/types'
import { getProjectBalanceList, createProjectBalance, updateProjectBalance, deleteProjectBalance, getProjectAccountList } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ProjectBalanceList = () => {
  const [data, setData] = useState<ProjectBalance[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingBalance, setEditingBalance] = useState<ProjectBalance | null>(null)
  const [accountList, setAccountList] = useState<ProjectAccount[]>([])
  const [searchAccountId, setSearchAccountId] = useState<string>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')
  const isGM = hasPermission('GM')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getProjectBalanceList({
        page,
        limit: pageSize,
        res_count: true,
        account_id: searchAccountId,
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

  const fetchAccountList = async () => {
    try {
      const res = await getProjectAccountList({
        page: 1,
        limit: 1000,
      })
      setAccountList(res.items || [])
    } catch (error) {
      setAccountList([])
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize, searchAccountId])

  useEffect(() => {
    fetchAccountList()
  }, [])

  const handleAdd = () => {
    setEditingBalance(null)
    form.resetFields()
    form.setFieldsValue({
      balance: 0,
      variable: 0,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: ProjectBalance) => {
    setEditingBalance(record)
    form.setFieldsValue({
      balance: record.balance,
      variable: record.variable,
      account_id: record.account_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProjectBalance(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingBalance) {
        await updateProjectBalance(editingBalance.id, values)
        message.success('更新成功')
      } else {
        await createProjectBalance(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const columns = [
    {
      title: '账号',
      dataIndex: 'account',
      key: 'account',
      render: (account: any) => account?.account || '-',
    },
    {
      title: '余额',
      dataIndex: 'balance',
      key: 'balance',
      render: (balance: number) => balance.toFixed(2),
    },
    {
      title: '变量',
      dataIndex: 'variable',
      key: 'variable',
      render: (variable: number) => {
        const color = variable > 0 ? 'green' : variable < 0 ? 'red' : 'default'
        return <span style={{ color }}>{variable > 0 ? '+' : ''}{variable.toFixed(2)}</span>
      },
    },
    {
      title: '项目',
      dataIndex: 'account',
      key: 'project',
      render: (account: any) => account?.project?.name || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ProjectBalance) => (
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
                title="确定删除该余额记录吗？"
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="选择账号"
            value={searchAccountId}
            onChange={setSearchAccountId}
            allowClear
            showSearch
            style={{ width: 250 }}
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={accountList.map(account => ({
              label: `${account.account} (${account.project?.name || '未知项目'})`,
              value: account.id,
            }))}
          />
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
          <Button type="primary" icon={<SearchOutlined />} onClick={() => { setPage(1); fetchData(); }}>
            搜索
          </Button>
          <Button onClick={() => { setSearchAccountId(undefined); setCreateTimeRange(null); setUpdateTimeRange(null); setPage(1); setTimeout(fetchData, 0); }}>
            重置
          </Button>
        </Space>
        {(isAdmin || isGM) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增余额记录
          </Button>
        )}
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
        title={editingBalance ? '编辑余额' : '新增余额记录'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="账号"
            name="account_id"
            rules={[{ required: true, message: '请选择账号' }]}
          >
            <Select
              placeholder="请选择账号"
              showSearch
              disabled={!!editingBalance}
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={accountList.map(account => ({
                label: `${account.account} (${account.project?.name || '未知项目'})`,
                value: account.id,
              }))}
            />
          </Form.Item>
          <Form.Item
            label="余额"
            name="balance"
            rules={[{ required: true, message: '请输入余额' }]}
          >
            <InputNumber
              placeholder="请输入余额"
              style={{ width: '100%' }}
              min={0}
              precision={2}
            />
          </Form.Item>
          <Form.Item
            label="变量"
            name="variable"
            rules={[{ required: true, message: '请输入变量' }]}
          >
            <InputNumber
              placeholder="请输入变量（正数为增加，负数为减少）"
              style={{ width: '100%' }}
              precision={2}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProjectBalanceList
