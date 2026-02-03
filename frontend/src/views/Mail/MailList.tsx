import { useState, useEffect } from 'react'
import { Table, Button, Space, Tag, Input, Select, Modal, Form, DatePicker, App } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, SyncOutlined, CopyOutlined } from '@ant-design/icons'
import type { ColumnsType, TableProps } from 'antd/es/table'
import { getEmailList, createEmail, updateEmail, deleteEmail, batchUpdateEmailStatus } from '@/api/mail'
import { getServerList } from '@/api/server'
import type { EmailInfo, ServerInfo } from '@/types'
import { Status, EmailType } from '@/types'
import { STATUS_MAP, EMAIL_TYPE_MAP } from '@/utils/constants'
import { formatDateTime, copyToClipboard } from '@/utils/format'
import { Dayjs } from 'dayjs'
import { useUserStore } from '@/store/useUserStore'

const { RangePicker } = DatePicker

type SortOrder = 'ascend' | 'descend' | null

export default function MailList() {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<EmailInfo[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchEmail, setSearchEmail] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [searchEmailType, setSearchEmailType] = useState<EmailType>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [orderBy, setOrderBy] = useState<string>('-update_time')
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [modalVisible, setModalVisible] = useState(false)
  const [batchModalVisible, setBatchModalVisible] = useState(false)
  const [editingEmail, setEditingEmail] = useState<EmailInfo | null>(null)
  const [servers, setServers] = useState<ServerInfo[]>([])
  const [form] = Form.useForm()
  const [batchForm] = Form.useForm()
  
  // 获取用户信息，判断是否为管理员
  const { userInfo } = useUserStore()
  const isAdmin = userInfo?.roles?.some(role => role.code === 'ADMIN') || false

  // 复制邮箱地址
  const handleCopyEmail = async (email: string) => {
    const success = await copyToClipboard(email)
    if (success) {
      message.success('邮箱地址已复制')
    } else {
      message.error('复制失败')
    }
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await getEmailList({
        page,
        limit: pageSize,
        res_count: true,
        email: searchEmail || undefined,
        status: searchStatus,
        email_type: searchEmailType,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
        order_by: orderBy,
      })
      setDataSource(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      setDataSource([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const fetchServers = async () => {
    try {
      const res = await getServerList({ limit: 1000 })
      setServers(res.items || [])
      return true  // 返回成功状态
    } catch (error) {
      setServers([])
      return false  // 返回失败状态
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize, orderBy])

  useEffect(() => {
    const loadData = async () => {
      await fetchServers()
    }
    loadData()
  }, [])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchEmail('')
    setSearchStatus(undefined)
    setSearchEmailType(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setOrderBy('-update_time')
    setSelectedRowKeys([])
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleTableChange: TableProps<EmailInfo>['onChange'] = (_pagination, _filters, sorter: any) => {
    if (sorter.field) {
      const order = sorter.order === 'ascend' ? '' : '-'
      setOrderBy(`${order}${sorter.field}`)
      setPage(1)
    }
  }

  const getSortOrder = (field: string): SortOrder => {
    if (orderBy === field) return 'ascend'
    if (orderBy === `-${field}`) return 'descend'
    return null
  }

  const handleAdd = () => {
    setEditingEmail(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: EmailInfo) => {
    setEditingEmail(record)
    form.setFieldsValue(record)
    setModalVisible(true)
  }

  const handleDelete = (record: EmailInfo) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除邮箱 ${record.email} 吗？`,
      onOk: async () => {
        try {
          await deleteEmail(record.id)
          message.success('删除成功')
          fetchData()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的邮箱')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个邮箱吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await Promise.all(selectedRowKeys.map(id => deleteEmail(id)))
          message.success(`成功删除 ${selectedRowKeys.length} 个邮箱`)
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
      
      // 如果是编辑模式，移除空的密码字段（不修改密码）
      if (editingEmail) {
        const updateData: any = { ...values }
        if (!updateData.password) {
          delete updateData.password
        }
        if (!updateData.auxiliary_email_password) {
          delete updateData.auxiliary_email_password
        }
        await updateEmail(editingEmail.id, updateData)
        message.success('更新成功')
      } else {
        await createEmail(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleBatchUpdate = () => {
    batchForm.resetFields()
    setBatchModalVisible(true)
  }

  const handleBatchSubmit = async () => {
    try {
      const values = await batchForm.validateFields()
      const res = await batchUpdateEmailStatus(values)
      message.success(`批量更新成功，共更新 ${res.count} 条记录`)
      setBatchModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('批量更新失败')
    }
  }

  const columns: ColumnsType<EmailInfo> = [
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 300,
      sorter: true,
      sortOrder: getSortOrder('email'),
      render: (text: string) => (
        <Space size={4}>
          <span>{text}</span>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyEmail(text)}
            style={{ padding: '0 4px', minWidth: 'auto' }}
            title="复制邮箱"
          />
        </Space>
      ),
    },
    {
      title: '辅助邮箱',
      dataIndex: 'auxiliary_email',
      key: 'auxiliary_email',
      width: 280,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      sorter: true,
      sortOrder: getSortOrder('status'),
      render: (status: Status) => {
        const config = STATUS_MAP[status]
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: 'Token状态',
      dataIndex: 'access_token',
      key: 'token_status',
      width: 100,
      render: (token: string) => (
        <Tag color={token ? 'success' : 'default'}>
          {token ? '已授权' : '未授权'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 160,
      sorter: true,
      sortOrder: getSortOrder('create_time'),
      render: (text: string) => formatDateTime(text),
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      width: 160,
      sorter: true,
      sortOrder: getSortOrder('update_time'),
      render: (text: string) => formatDateTime(text),
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space>
          {isAdmin && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Button
                type="link"
                size="small"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(record)}
              >
                删除
              </Button>
            </>
          )}
          {!isAdmin && <span style={{ color: '#999' }}>-</span>}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="搜索邮箱"
            prefix={<SearchOutlined />}
            value={searchEmail}
            onChange={(e) => setSearchEmail(e.target.value)}
            style={{ width: 200 }}
          />
          <Select
            placeholder="选择状态"
            value={searchStatus}
            onChange={setSearchStatus}
            allowClear
            style={{ width: 120 }}
          >
            {Object.entries(STATUS_MAP).map(([key, value]) => (
              <Select.Option key={key} value={Number(key)}>
                {value.text}
              </Select.Option>
            ))}
          </Select>
          <Select
            placeholder="选择邮箱类型"
            value={searchEmailType}
            onChange={setSearchEmailType}
            allowClear
            style={{ width: 180 }}
          >
            {Object.entries(EMAIL_TYPE_MAP).map(([key, value]) => (
              <Select.Option key={key} value={key}>
                {value.text}
              </Select.Option>
            ))}
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
          <Button onClick={handleReset}>
            重置
          </Button>
          <Button icon={<SyncOutlined />} onClick={handleBatchUpdate}>
            批量更新状态
          </Button>
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
              新增邮箱
            </Button>
          )}
        </Space>
      </div>

      <Table
        loading={loading}
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
        scroll={{ x: 1200 }}
        onChange={handleTableChange}
        rowSelection={isAdmin ? {
          selectedRowKeys,
          onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys as string[]),
          preserveSelectedRowKeys: true,
        } : undefined}
        pagination={{
          current: page,
          pageSize,
          total,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            setPage(page)
            setPageSize(pageSize)
          },
        }}
      />

      <Modal
        title={editingEmail ? '编辑邮箱' : '新增邮箱'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item
            name="password"
            label="密码"
            rules={[{ required: !editingEmail, message: '请输入密码' }]}
          >
            <Input.Password placeholder={editingEmail ? '留空则不修改密码' : '请输入密码'} />
          </Form.Item>
          <Form.Item
            name="auxiliary_email"
            label="辅助邮箱"
            rules={[{ required: true, message: '请输入辅助邮箱' }]}
          >
            <Input placeholder="请输入辅助邮箱" />
          </Form.Item>
          <Form.Item
            name="auxiliary_email_password"
            label="辅助邮箱密码"
            rules={[{ required: !editingEmail, message: '请输入辅助邮箱密码' }]}
          >
            <Input.Password placeholder={editingEmail ? '留空则不修改密码' : '请输入辅助邮箱密码'} />
          </Form.Item>
          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              {Object.entries(STATUS_MAP).map(([key, value]) => (
                <Select.Option key={key} value={Number(key)}>
                  {value.text}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="server_id" label="代理服务器">
            <Select placeholder="请选择代理服务器" allowClear>
              {servers.map(server => (
                <Select.Option key={server.id} value={server.id}>
                  {server.host} ({server.domain})
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="client_id" label="Client ID">
            <Input placeholder="请输入Client ID" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="批量更新邮箱状态"
        open={batchModalVisible}
        onOk={handleBatchSubmit}
        onCancel={() => setBatchModalVisible(false)}
      >
        <Form form={batchForm} layout="vertical">
          <Form.Item
            name="from_status"
            label="源状态"
            rules={[{ required: true, message: '请选择源状态' }]}
          >
            <Select placeholder="请选择源状态">
              {Object.entries(STATUS_MAP).map(([key, value]) => (
                <Select.Option key={key} value={Number(key)}>
                  {value.text}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="to_status"
            label="目标状态"
            rules={[{ required: true, message: '请选择目标状态' }]}
          >
            <Select placeholder="请选择目标状态">
              {Object.entries(STATUS_MAP).map(([key, value]) => (
                <Select.Option key={key} value={Number(key)}>
                  {value.text}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
