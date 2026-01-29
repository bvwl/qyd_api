import { useState, useEffect } from 'react'
import { Table, Button, Space, Tag, Input, Select, Modal, Form, DatePicker, Tooltip, App } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, CopyOutlined } from '@ant-design/icons'
import type { ColumnsType, TableProps } from 'antd/es/table'
import { getUserList, createUser, updateUser, deleteUser } from '@/api/user'
import { getRoleList } from '@/api/user'
import type { User, Role } from '@/types'
import { UserStatus } from '@/types'
import { USER_STATUS_MAP } from '@/utils/constants'
import { formatDateTime, copyToClipboard } from '@/utils/format'
import { useUserStore } from '@/store/useUserStore'
import { Dayjs } from 'dayjs'
import { filterEmptyStrings } from '@/utils/form'

const { RangePicker } = DatePicker

type SortOrder = 'ascend' | 'descend' | null

export default function UserList() {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<User[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchEmail, setSearchEmail] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [orderBy, setOrderBy] = useState<string>('-create_time')
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [roles, setRoles] = useState<Role[]>([])
  const [form] = Form.useForm()
  
  const hasPermission = useUserStore((state) => state.hasPermission)
  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    try {
      setLoading(true)
      const res = await getUserList({
        page,
        limit: pageSize,
        res_count: true,
        email: searchEmail || undefined,
        status: searchStatus,
        order_by: orderBy,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
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
  }, [page, pageSize, searchEmail, searchStatus, orderBy])

  useEffect(() => {
    fetchRoles()
  }, [])

  const handleAdd = () => {
    setEditingUser(null)
    form.resetFields()
    // 确保角色列表已加载
    if (roles.length === 0) {
      fetchRoles()
    }
    setModalVisible(true)
  }

  const handleEdit = async (record: User) => {
    setEditingUser(record)
    
    // 确保角色列表已加载
    if (roles.length === 0) {
      await fetchRoles()
    }
    
    // 等待一下确保 roles 状态已更新
    setTimeout(() => {
      // 设置表单值
      const roleIds = record.roles?.map(r => r.id) || []
      
      form.setFieldsValue({
        email: record.email,
        nickname: record.nickname,
        status: record.status,
        role_ids: roleIds,
      })
      
      setModalVisible(true)
    }, 100)
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

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的用户')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个用户吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await Promise.all(selectedRowKeys.map(id => deleteUser(id)))
          message.success(`成功删除 ${selectedRowKeys.length} 个用户`)
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
      if (editingUser) {
        await updateUser(editingUser.id, filteredValues)
        message.success('更新成功')
      } else {
        await createUser(filteredValues)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 获取角色标签颜色
  const getRoleColor = (code: string) => {
    const colorMap: Record<string, string> = {
      ADMIN: 'red',
      GM: 'orange',
      IT: 'blue',
      MANUAL: 'default'
    }
    return colorMap[code] || 'default'
  }

  const handleTableChange: TableProps<User>['onChange'] = (_pagination, _filters, sorter: any) => {
    if (sorter.field) {
      const order = sorter.order === 'ascend' ? '' : '-'
      setOrderBy(`${order}${sorter.field}`)
      setPage(1)
      setTimeout(() => {
        fetchData()
      }, 0)
    }
  }

  const getSortOrder = (field: string): SortOrder => {
    if (orderBy === field) return 'ascend'
    if (orderBy === `-${field}`) return 'descend'
    return null
  }

  const handleCopyId = async (id: string) => {
    const success = await copyToClipboard(id)
    if (success) {
      message.success('用户ID已复制到剪贴板')
    } else {
      message.error('复制失败')
    }
  }

  const columns: ColumnsType<User> = [
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      sorter: true,
      sortOrder: getSortOrder('email'),
    },
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (id: string) => (
        <Tooltip title={id}>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyId(id)}
          >
            复制
          </Button>
        </Tooltip>
      ),
    },
    {
      title: '昵称',
      dataIndex: 'nickname',
      key: 'nickname',
      sorter: true,
      sortOrder: getSortOrder('nickname'),
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
            <Tag key={role.id} color={getRoleColor(role.code)}>{role.name}</Tag>
          ))}
          {(!roles || roles.length === 0) && <Tag>无角色</Tag>}
        </>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      sorter: true,
      sortOrder: getSortOrder('create_time'),
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
            {Object.entries(USER_STATUS_MAP).map(([key, value]) => (
              <Select.Option key={key} value={Number(key)}>
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
          <Button onClick={() => { setSearchEmail(''); setSearchStatus(undefined); setCreateTimeRange(null); setUpdateTimeRange(null); setOrderBy('-create_time'); setSelectedRowKeys([]); setPage(1); setTimeout(fetchData, 0); }}>
            重置
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
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
            新增用户
          </Button>
        </Space>
      </div>

      <Table
        loading={loading}
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
        onChange={handleTableChange}
        rowSelection={{
          selectedRowKeys,
          onChange: (selectedKeys) => setSelectedRowKeys(selectedKeys as string[]),
          preserveSelectedRowKeys: true,
        }}
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
            <Select 
              mode="multiple" 
              placeholder="请选择角色"
              optionFilterProp="children"
              showSearch
              filterOption={(input, option) => {
                if (!option || !option.children) return false
                const children = option.children
                return String(children).toLowerCase().includes(input.toLowerCase())
              }}
            >
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
