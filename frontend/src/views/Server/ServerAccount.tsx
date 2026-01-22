import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ServerAccount, User } from '@/types'
import { getServerAccountList, createServerAccount, updateServerAccount, deleteServerAccount } from '@/api/server'
import { getUserList } from '@/api/user'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ServerAccountList = () => {
  const [data, setData] = useState<ServerAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingAccount, setEditingAccount] = useState<ServerAccount | null>(null)
  const [userList, setUserList] = useState<User[]>([])
  const [searchUserId, setSearchUserId] = useState<string>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getServerAccountList({
        page,
        limit: pageSize,
        res_count: true,
        user_id: searchUserId,
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

  const fetchUserList = async () => {
    try {
      const res = await getUserList({
        page: 1,
        limit: 1000,
      })
      setUserList(res.items || [])
      return true  // 返回成功状态
    } catch (error) {
      setUserList([])
      return false  // 返回失败状态
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize, searchUserId])

  useEffect(() => {
    const loadData = async () => {
      // 先加载用户列表
      await fetchUserList()
    }
    loadData()
  }, [])

  const handleAdd = () => {
    setEditingAccount(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (record: ServerAccount) => {
    setEditingAccount(record)
    form.setFieldsValue({
      username: record.username,
      password: record.password,
      user_id: record.user_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteServerAccount(id)
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
        await updateServerAccount(editingAccount.id, values)
        message.success('更新成功')
      } else {
        await createServerAccount(values)
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
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: '关联用户',
      dataIndex: 'user',
      key: 'user',
      render: (user: User) => user?.nickname || user?.email || '-',
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
      render: (_: any, record: ServerAccount) => (
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="选择用户"
            value={searchUserId}
            onChange={setSearchUserId}
            allowClear
            showSearch
            style={{ width: 250 }}
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
            options={userList.map(user => ({
              label: `${user.nickname} (${user.email})`,
              value: user.id,
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
          <Button onClick={() => { setSearchUserId(undefined); setCreateTimeRange(null); setUpdateTimeRange(null); setPage(1); setTimeout(fetchData, 0); }}>
            重置
          </Button>
        </Space>
        {isAdmin && (
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增账号
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
        title={editingAccount ? '编辑账号' : '新增账号'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input placeholder="请输入用户名" />
          </Form.Item>
          <Form.Item
            label="密码"
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Form.Item
            label="关联用户"
            name="user_id"
            rules={[{ required: true, message: '请选择用户' }]}
          >
            <Select
              placeholder="请选择用户"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={userList.map(user => ({
                label: `${user.nickname} (${user.email})`,
                value: user.id,
              }))}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default ServerAccountList
