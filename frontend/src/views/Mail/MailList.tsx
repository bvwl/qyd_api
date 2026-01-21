import { useState, useEffect } from 'react'
import { Table, Button, Space, Tag, Input, Select, message, Modal, Form, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, SyncOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getEmailList, createEmail, updateEmail, deleteEmail, batchUpdateEmailStatus } from '@/api/mail'
import { getServerList } from '@/api/server'
import type { EmailInfo, ServerInfo } from '@/types'
import { Status, EmailType } from '@/types'
import { STATUS_MAP, EMAIL_TYPE_MAP } from '@/utils/constants'
import { formatDateTime, maskPassword } from '@/utils/format'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

export default function MailList() {
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
  const [modalVisible, setModalVisible] = useState(false)
  const [batchModalVisible, setBatchModalVisible] = useState(false)
  const [editingEmail, setEditingEmail] = useState<EmailInfo | null>(null)
  const [servers, setServers] = useState<ServerInfo[]>([])
  const [form] = Form.useForm()
  const [batchForm] = Form.useForm()

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
    } catch (error) {
      setServers([])
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize, searchEmail, searchStatus, searchEmailType])

  useEffect(() => {
    fetchServers()
  }, [])

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

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingEmail) {
        await updateEmail(editingEmail.id, values)
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
      width: 200,
    },
    {
      title: '密码',
      dataIndex: 'password',
      key: 'password',
      render: (text: string) => maskPassword(text),
    },
    {
      title: '辅助邮箱',
      dataIndex: 'auxiliary_email',
      key: 'auxiliary_email',
      width: 180,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: Status) => {
        const config = STATUS_MAP[status]
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '代理服务器',
      dataIndex: 'server_info',
      key: 'server_info',
      render: (server: ServerInfo) => server?.host || '-',
    },
    {
      title: '代理端口',
      dataIndex: 'server_info',
      key: 'port',
      render: (server: ServerInfo) => server?.port || '-',
    },
    {
      title: 'Token状态',
      dataIndex: 'access_token',
      key: 'token_status',
      render: (token: string) => (
        <Tag color={token ? 'success' : 'default'}>
          {token ? '已授权' : '未授权'}
        </Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      render: (text: string) => formatDateTime(text),
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 150,
      render: (_, record) => (
        <Space>
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
          <Button type="primary" icon={<SearchOutlined />} onClick={() => { setPage(1); fetchData(); }}>
            搜索
          </Button>
          <Button onClick={() => { setSearchEmail(''); setSearchStatus(undefined); setSearchEmailType(undefined); setCreateTimeRange(null); setUpdateTimeRange(null); setPage(1); setTimeout(fetchData, 0); }}>
            重置
          </Button>
          <Button icon={<SyncOutlined />} onClick={handleBatchUpdate}>
            批量更新状态
          </Button>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增邮箱
        </Button>
      </div>

      <Table
        loading={loading}
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
        scroll={{ x: 1200 }}
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
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
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
            rules={[{ required: true, message: '请输入辅助邮箱密码' }]}
          >
            <Input.Password placeholder="请输入辅助邮箱密码" />
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
