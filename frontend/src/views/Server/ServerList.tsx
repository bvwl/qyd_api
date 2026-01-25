import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, InputNumber, DatePicker, Spin } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, CopyOutlined, ApiOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import type { ServerInfo, ServerGroup } from '@/types'
import { Status } from '@/types'
import { getServerList, createServer, updateServer, deleteServer, getGroupList } from '@/api/server'
import { checkProxyDirect } from '@/api/system'
import { useUserStore } from '@/store/useUserStore'
import { Dayjs } from 'dayjs'
import { filterEmptyStrings } from '@/utils/form'

const { RangePicker } = DatePicker

const ServerList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<ServerInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingServer, setEditingServer] = useState<ServerInfo | null>(null)
  const [groupList, setGroupList] = useState<ServerGroup[]>([])
  const [searchHost, setSearchHost] = useState('')
  const [searchDomain, setSearchDomain] = useState('')
  const [searchPort, setSearchPort] = useState<number>()
  const [searchProxyType, setSearchProxyType] = useState<string>()
  const [searchGroupId, setSearchGroupId] = useState<string>()
  const [searchStatus, setSearchStatus] = useState<number>()
  const [searchIsSale, setSearchIsSale] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [testingProxy, setTestingProxy] = useState<string | null>(null)
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
        domain: searchDomain || undefined,
        port: searchPort,
        group_id: searchGroupId,
        status: searchStatus,
        is_sale: searchIsSale,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
      })
      
      let items = res.items || []
      
      // 客户端筛选：根据代理类型过滤
      if (searchProxyType) {
        items = items.filter(item => item.proxy_type === searchProxyType)
      }
      
      setData(items)
      // 如果有代理类型筛选，总数需要重新计算
      setTotal(searchProxyType ? items.length : (res.count || 0))
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
    setSearchDomain('')
    setSearchPort(undefined)
    setSearchProxyType(undefined)
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
      is_sale: 1,  // 默认为可以出售
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
      const filteredValues = filterEmptyStrings(values)
      if (editingServer) {
        await updateServer(editingServer.id, filteredValues)
        message.success('更新成功')
      } else {
        await createServer(filteredValues)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleCopyProxyUrl = (proxyUrl?: string, proxyType?: string) => {
    if (!proxyUrl) {
      message.warning('代理信息不可用')
      return
    }
    
    const typeText = proxyType === 'http' ? 'HTTP' : proxyType === 'socks5' ? 'SOCKS5' : ''
    
    navigator.clipboard.writeText(proxyUrl).then(() => {
      message.success(`${typeText} 代理信息已复制到剪贴板`)
    }).catch(() => {
      message.error('复制失败，请手动复制')
    })
  }

  const handleTestProxy = async (proxyUrl?: string, serverId?: string) => {
    if (!proxyUrl) {
      message.warning('代理信息不可用')
      return
    }

    setTestingProxy(serverId || null)
    
    try {
      const result = await checkProxyDirect(proxyUrl)
      
      if (result.status === 'success') {
        Modal.success({
          title: '代理检测成功',
          content: (
            <div>
              <p><strong>代理地址：</strong>{proxyUrl}</p>
              <p><strong>检测IP：</strong>{result.ip}</p>
              <p><strong>检测来源：</strong>{result.source}</p>
              <p style={{ color: '#52c41a', marginTop: 8 }}>✅ 代理可用</p>
            </div>
          ),
        })
      } else {
        Modal.error({
          title: '代理检测失败',
          content: (
            <div>
              <p><strong>代理地址：</strong>{proxyUrl}</p>
              <p style={{ color: '#ff4d4f', marginTop: 8 }}>❌ 代理不可用</p>
              <p><strong>原因：</strong>{result.details?.error || result.message}</p>
            </div>
          ),
        })
      }
    } catch (error: any) {
      Modal.error({
        title: '代理检测失败',
        content: (
          <div>
            <p><strong>代理地址：</strong>{proxyUrl}</p>
            <p style={{ color: '#ff4d4f', marginTop: 8 }}>❌ 检测请求失败</p>
            <p><strong>错误：</strong>{error.message || '未知错误'}</p>
          </div>
        ),
      })
    } finally {
      setTestingProxy(null)
    }
  }

  const columns = [
    {
      title: '主机地址',
      dataIndex: 'host',
      key: 'host',
      width: 140,
    },
    {
      title: '域名',
      dataIndex: 'domain',
      key: 'domain',
      width: 150,
      ellipsis: true,
    },
    {
      title: '代理端口',
      dataIndex: 'port',
      key: 'port',
      width: 90,
    },
    {
      title: '代理类型',
      dataIndex: 'proxy_type',
      key: 'proxy_type',
      width: 90,
      render: (proxy_type: string) => {
        if (!proxy_type) return '-'
        return (
          <Tag color={proxy_type === 'http' ? 'blue' : 'green'}>
            {proxy_type.toUpperCase()}
          </Tag>
        )
      },
    },
    {
      title: '分组',
      dataIndex: 'group',
      key: 'group',
      width: 100,
      render: (group: ServerGroup) => group?.name || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 70,
      render: (status: Status) => (
        <Tag color={status === Status.NORMAL ? 'green' : 'red'}>
          {status === Status.NORMAL ? '正常' : '异常'}
        </Tag>
      ),
    },
    {
      title: '是否可以出售',
      dataIndex: 'is_sale',
      key: 'is_sale',
      width: 110,
      render: (is_sale: number) => (
        <Tag color={is_sale === 1 ? 'green' : 'default'}>
          {is_sale === 1 ? '可以出售' : '不可以出售'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
    },
    {
      title: '操作',
      key: 'action',
      width: 300,
      fixed: 'right' as const,
      render: (_: any, record: ServerInfo) => (
        <Space size="small">
          <Button
            type="link"
            icon={<CopyOutlined />}
            onClick={() => handleCopyProxyUrl(record.proxy_url, record.proxy_type)}
            title={`复制${record.proxy_type === 'http' ? 'HTTP' : 'SOCKS5'}代理信息`}
          >
            复制代理
          </Button>
          {record.proxy_type === 'http' && (
            <Button
              type="link"
              icon={testingProxy === record.id ? <Spin size="small" /> : <ApiOutlined />}
              onClick={() => handleTestProxy(record.proxy_url, record.id)}
              disabled={testingProxy === record.id}
              title="测试代理是否可用"
            >
              测试代理
            </Button>
          )}
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
              style={{ width: 150 }}
            />
            <Input
              placeholder="域名"
              value={searchDomain}
              onChange={(e) => setSearchDomain(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 150 }}
            />
            <InputNumber
              placeholder="代理端口"
              value={searchPort}
              onChange={(value) => setSearchPort(value || undefined)}
              onPressEnter={handleSearch}
              style={{ width: 120 }}
              min={1}
              max={65535}
            />
            <Select
              placeholder="代理类型"
              value={searchProxyType}
              onChange={setSearchProxyType}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value="http">HTTP</Select.Option>
              <Select.Option value="socks5">SOCKS5</Select.Option>
            </Select>
            <Select
              placeholder="分组"
              value={searchGroupId}
              onChange={setSearchGroupId}
              style={{ width: 180 }}
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
              style={{ width: 100 }}
              allowClear
            >
              <Select.Option value={Status.NORMAL}>正常</Select.Option>
              <Select.Option value={Status.ABNORMAL}>异常</Select.Option>
            </Select>
            <Select
              placeholder="是否可以出售"
              value={searchIsSale}
              onChange={setSearchIsSale}
              style={{ width: 130 }}
              allowClear
            >
              <Select.Option value={1}>可以出售</Select.Option>
              <Select.Option value={2}>不可以出售</Select.Option>
            </Select>
            <RangePicker
              placeholder={['创建开始', '创建结束']}
              value={createTimeRange}
              onChange={(dates) => setCreateTimeRange(dates as [Dayjs, Dayjs] | null)}
              format="YYYY-MM-DD"
              style={{ width: 240 }}
            />
            <RangePicker
              placeholder={['更新开始', '更新结束']}
              value={updateTimeRange}
              onChange={(dates) => setUpdateTimeRange(dates as [Dayjs, Dayjs] | null)}
              format="YYYY-MM-DD"
              style={{ width: 240 }}
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
        scroll={{ x: 1250 }}
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
            label="是否可以出售"
            name="is_sale"
            rules={[{ required: true, message: '请选择是否可以出售' }]}
          >
            <Select placeholder="请选择是否可以出售">
              <Select.Option value={1}>可以出售</Select.Option>
              <Select.Option value={2}>不可以出售</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ServerList
