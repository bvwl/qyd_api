import { useState, useEffect } from 'react'
import { Table, Button, Space, Tag, Input, Select, message, Modal, Form } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import { getRoleList } from '@/api/user'
import type { User, Role } from '@/types'
import { UserStatus } from '@/types'
import { USER_STATUS_MAP } from '@/utils/constants'
import { formatDateTime } from '@/utils/format'

export default function UserList() {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchEmail, setSearchEmail] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [form] = Form.useForm()

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await getUserList({
        page,
        limit: pageSize,
        res_count: true,
        email: searchEmail || undefined,
        status: searchStatus,
      })
      setDataSource(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      // 404 表示无数据
      setDataSource([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoles = async () => {
    try {
      const res = await getRoleList({ limit: 100 })
      setRoles(res.items || [])
    } catch (error) {
      setRoles([])
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize, searchEmail, searchStatus])

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleAdd = () => {
    setEditingUser(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: User) => {
    setEditingUser(record)
    form.setFieldsValue({
      ...record,
      role_ids: record.roles?.map(r => r.id) || [],
    })
    setModalVisible(true)
  }

  const handleDelete = (record: User) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除用户 ${record.nickname} 吗？`,
      onOk: async () => {
        try {
          await deleteUser(record.id)
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
      if (editingUser) {
        await updateUser(editingUser.id, values)
        message.success('更新成功')
      } else {
        await createUser(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      key: 'nickname',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: UserStatus) => {
        const config = USER_STATUS_MAP[status]
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
    {
      title: '角色',
      dataIndex: 'roles',
      key: 'roles',
      render: (roles: Role[]) => (
        <>
          {roles?.map(role => (
            <Tag key={role.id} color="blue">{role.name}</Tag>
          ))}
        </>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      render: (text: string) => formatDateTime(text),
    },
    {
      title: '操作',
      key: 'action',
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
      <Space style={{ marginBottom: 16 }}>
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
          {Object.entries(USER_STATUS_MAP).map(([key, value]) => (
            <Select.Option key={key} value={Number(key)}>
              {value.text}
            </Select.Option>
          ))}
        </Select>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          新增用户
        </Button>
      </Space>

      <Table
        loading={loading}
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
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
        title={editingUser ? '编辑用户' : '新增用户'}
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
            name="nickname"
            label="昵称"
            rules={[{ required: true, message: '请输入昵称' }]}
          >
            <Input placeholder="请输入昵称" />
          </Form.Item>
          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}
          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              {Object.entries(USER_STATUS_MAP).map(([key, value]) => (
                <Select.Option key={key} value={Number(key)}>
                  {value.text}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item name="role_ids" label="角色">
            <Select mode="multiple" placeholder="请选择角色">
              {roles.map(role => (
                <Select.Option key={role.id} value={role.id}>
                  {role.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
