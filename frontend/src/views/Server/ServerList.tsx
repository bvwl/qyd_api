import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, Tag, Select, InputNumber, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ServerInfo, ServerGroup } from '@/types'
import { Status } from '@/types'
import { getServerList, createServer, updateServer, deleteServer, getGroupList } from '@/api/server'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ServerList = () => {
  const [data, setData] = useState<ServerInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingServer, setEditingServer] = useState<ServerInfo | null>(null)
  const [groupList, setGroupList] = useState<ServerGroup[]>([])
  const [searchHost, setSearchHost] = useState('')
  const [searchGroupId, setSearchGroupId] = useState<string>()
  const [searchStatus, setSearchStatus] = useState<number>()
  const [searchIsSale, setSearchIsSale] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getServerList({
        page,
        limit: pageSize,
        res_count: true,
        host: searchHost || undefined,
        group_id: searchGroupId,
        status: searchStatus,
        is_sale: searchIsSale,
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

  const fetchGroupList = async () => {
    try {
      const res = await getGroupList({
        page: 1,
        limit: 1000,
      })
      setGroupList(res.items || [])
      return true  // 返回成功状态
    } catch (error) {
      setGroupList([])
      return false  // 返回失败状态
    }
  }

  useEffect(() => {
    const loadData = async () => {
      // 先加载分组列表，成功后再加载服务器数据
      const groupSuccess = await fetchGroupList()
      if (groupSuccess) {
        fetchData()
      }
    }
    loadData()
  }, [page, pageSize])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchHost('')
    setSearchGroupId(undefined)
    setSearchStatus(undefined)
    setSearchIsSale(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setSelectedRowKeys([])
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingServer(null)
    form.resetFields()
    form.setFieldsValue({
      status: Status.NORMAL,
      is_sale: 0,
      ssh_port: 22,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: ServerInfo) => {
    setEditingServer(record)
    form.setFieldsValue({
      host: record.host,
      ssh_port: record.ssh_port,
      password: record.password,
      status: record.status,
      domain: record.domain,
      is_sale: record.is_sale,
      port: record.port,
      group_id: record.group_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteServer(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的服务器')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个服务器吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await Promise.all(selectedRowKeys.map(id => deleteServer(id)))
          message.success(`成功删除 ${selectedRowKeys.length} 个服务器`)
          setSelectedRowKeys([])
          fetchData()
        } catch (error) {
          message.error('批量删除失败')
        }
      }
    })
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingServer) {
        await updateServer(editingServer.id, values)
        message.success('更新成功')
      } else {
        await createServer(values)
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
      title: '主机地址',
      dataIndex: 'host',
      key: 'host',
    },
    {
      title: 'SSH端口',
      dataIndex: 'ssh_port',
      key: 'ssh_port',
    },
    {
      title: '域名',
      dataIndex: 'domain',
      key: 'domain',
      ellipsis: true,
    },
    {
      title: '分组',
      dataIndex: 'group',
      key: 'group',
      render: (group: ServerGroup) => group?.name || '-',
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
      title: '是否出售',
      dataIndex: 'is_sale',
      key: 'is_sale',
      render: (is_sale: number) => (
        <Tag color={is_sale === 1 ? 'orange' : 'default'}>
          {is_sale === 1 ? '已出售' : '未出售'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: ServerInfo) => (
        <Space>
          {isAdmin && (
            <>
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定删除该服务器吗？"
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
              placeholder="主机地址"
              value={searchHost}
              onChange={(e) => setSearchHost(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Select
              placeholder="分组"
              value={searchGroupId}
              onChange={setSearchGroupId}
              style={{ width: 200 }}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={groupList.map(group => ({
                label: `${group.name} (${group.country?.name || '未知'})`,
                value: group.id,
              }))}
            />
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
            <Select
              placeholder="是否出售"
              value={searchIsSale}
              onChange={setSearchIsSale}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value={0}>未出售</Select.Option>
              <Select.Option value={1}>已出售</Select.Option>
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
          <Space>
            {selectedRowKeys.length > 0 && isAdmin && (
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                onClick={handleBatchDelete}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            )}
            {isAdmin && (
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                新增服务器
              </Button>
            )}
          </Space>
        </div>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys as string[]),
          preserveSelectedRowKeys: true,
        }}
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
        title={editingServer ? '编辑服务器' : '新增服务器'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="主机地址"
            name="host"
            rules={[{ required: true, message: '请输入主机地址' }]}
          >
            <Input placeholder="请输入主机地址（IP或域名）" />
          </Form.Item>
          <Form.Item
            label="SSH端口"
            name="ssh_port"
          >
            <InputNumber placeholder="请输入SSH端口" style={{ width: '100%' }} min={1} max={65535} />
          </Form.Item>
          <Form.Item label="密码" name="password">
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Form.Item label="域名" name="domain">
            <Input placeholder="请输入域名" />
          </Form.Item>
          <Form.Item label="端口" name="port">
            <InputNumber placeholder="请输入端口" style={{ width: '100%' }} min={1} max={65535} />
          </Form.Item>
          <Form.Item label="分组" name="group_id">
            <Select
              placeholder="请选择分组"
              showSearch
              allowClear
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={groupList.map(group => ({
                label: `${group.name} (${group.country?.name || '未知'})`,
                value: group.id,
              }))}
            />
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
            label="是否出售"
            name="is_sale"
            rules={[{ required: true, message: '请选择是否出售' }]}
          >
            <Select placeholder="请选择是否出售">
              <Select.Option value={0}>未出售</Select.Option>
              <Select.Option value={1}>已出售</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ServerList
