import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, DatePicker, Select } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, EyeInvisibleOutlined, SearchOutlined } from '@ant-design/icons'
import type { ProjectWallet, Project } from '@/types'
import { getProjectWalletList, createProjectWallet, updateProjectWallet, deleteProjectWallet, getProjectList } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ProjectWalletList = () => {
  const [data, setData] = useState<ProjectWallet[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingWallet, setEditingWallet] = useState<ProjectWallet | null>(null)
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({})
  const [projectList, setProjectList] = useState<Project[]>([])
  const [searchChain, setSearchChain] = useState('')
  const [searchProjectId, setSearchProjectId] = useState<string>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')
  const isGM = hasPermission('GM')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getProjectWalletList({
        page,
        limit: pageSize,
        res_count: true,
        chain: searchChain || undefined,
        project_id: searchProjectId,
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
    setSearchChain('')
    setSearchProjectId(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingWallet(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: ProjectWallet) => {
    setEditingWallet(record)
    form.setFieldsValue({
      private_key: record.private_key,
      public_key: record.public_key,
      mnemonic: record.mnemonic,
      chain: record.chain,
      remark: record.remark,
      project_id: record.project_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProjectWallet(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingWallet) {
        await updateProjectWallet(editingWallet.id, values)
        message.success('更新成功')
      } else {
        await createProjectWallet(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const toggleVisible = (id: string, field: string) => {
    const key = `${id}-${field}`
    setVisibleKeys(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const renderSensitiveField = (value: string, id: string, field: string) => {
    const key = `${id}-${field}`
    const isVisible = visibleKeys[key]
    return (
      <Space>
        <span style={{ fontFamily: 'monospace' }}>
          {isVisible ? value : '••••••••••••'}
        </span>
        <Button
          type="link"
          size="small"
          icon={isVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
          onClick={() => toggleVisible(id, field)}
        />
      </Space>
    )
  }

  const columns = [
    {
      title: '公钥',
      dataIndex: 'public_key',
      key: 'public_key',
      ellipsis: true,
      render: (text: string, record: ProjectWallet) => renderSensitiveField(text, record.id, 'public'),
    },
    {
      title: '链',
      dataIndex: 'chain',
      key: 'chain',
    },
    {
      title: '项目',
      dataIndex: 'project',
      key: 'project',
      render: (project: any) => project?.name || '-',
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ProjectWallet) => (
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
                title="确定删除该钱包吗？"
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
          <Input
            placeholder="搜索链"
            prefix={<SearchOutlined />}
            value={searchChain}
            onChange={(e) => setSearchChain(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            placeholder="选择项目"
            value={searchProjectId}
            onChange={setSearchProjectId}
            style={{ width: 200 }}
            allowClear
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={projectList.map(project => ({
              label: project.name,
              value: project.id,
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
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>
            重置
          </Button>
        </Space>
        {(isAdmin || isGM) && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增钱包
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
        title={editingWallet ? '编辑钱包' : '新增钱包'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
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
          <Form.Item
            label="私钥"
            name="private_key"
            rules={[{ required: true, message: '请输入私钥' }]}
          >
            <Input.TextArea placeholder="请输入私钥" rows={3} />
          </Form.Item>
          <Form.Item
            label="公钥"
            name="public_key"
            rules={[{ required: true, message: '请输入公钥' }]}
          >
            <Input.TextArea placeholder="请输入公钥" rows={3} />
          </Form.Item>
          <Form.Item
            label="助记词"
            name="mnemonic"
            rules={[{ required: true, message: '请输入助记词' }]}
          >
            <Input.TextArea placeholder="请输入助记词" rows={3} />
          </Form.Item>
          <Form.Item
            label="链"
            name="chain"
            rules={[{ required: true, message: '请输入链名称' }]}
          >
            <Input placeholder="请输入链名称（如：ETH、BSC）" />
          </Form.Item>
          <Form.Item label="备注" name="remark">
            <Input.TextArea placeholder="请输入备注" rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ProjectWalletList
