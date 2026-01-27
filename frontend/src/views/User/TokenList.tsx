import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, DatePicker, Alert } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, CopyOutlined, SearchOutlined } from '@ant-design/icons'
import type { UserToken, User } from '@/types'
import { getTokenList, createToken, updateToken, deleteToken, getUserList } from '@/api/user'
import { useUserStore } from '@/store/useUserStore'
import { copyToClipboard } from '@/utils/format'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const TokenList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<UserToken[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingToken, setEditingToken] = useState<UserToken | null>(null)
  const [userList, setUserList] = useState<User[]>([])
  const [searchUserId, setSearchUserId] = useState<string>()
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getTokenList({
        page,
        limit: pageSize,
        res_count: true,
        user_id: searchUserId,
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
    const loadData = async () => {
      // 先加载用户列表，成功后再加载Token数据
      const userSuccess = await fetchUserList()
      if (userSuccess) {
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
    setSearchUserId(undefined)
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingToken(null)
    form.resetFields()
    form.setFieldsValue({
      status: 1,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: UserToken) => {
    setEditingToken(record)
    form.setFieldsValue({
      status: record.status,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteToken(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingToken) {
        await updateToken(editingToken.id, values)
        message.success('更新成功')
      } else {
        await createToken(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleCopy = async (token: string) => {
    const success = await copyToClipboard(token)
    if (success) {
      message.success('Token已复制到剪贴板')
    } else {
      message.error('复制失败')
    }
  }

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的Token')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个Token吗？`,
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          let successCount = 0
          let failCount = 0

          for (const id of selectedRowKeys) {
            try {
              await deleteToken(id)
              successCount++
            } catch (error) {
              failCount++
            }
          }

          if (successCount > 0) {
            message.success(`成功删除 ${successCount} 个Token${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
            setSelectedRowKeys([])
            fetchData()
          } else {
            message.error('批量删除失败')
          }
        } catch (error) {
          message.error('批量删除失败')
        }
      },
    })
  }

  // 批量更新状态
  const handleBatchUpdateStatus = async (status: number) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要更新的Token')
      return
    }

    const statusText = status === 1 ? '正常' : '异常'
    Modal.confirm({
      title: '批量更新状态确认',
      content: `确定要将选中的 ${selectedRowKeys.length} 个Token状态设置为"${statusText}"吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          let successCount = 0
          let failCount = 0

          for (const id of selectedRowKeys) {
            try {
              await updateToken(id, { status })
              successCount++
            } catch (error) {
              failCount++
            }
          }

          if (successCount > 0) {
            message.success(`成功更新 ${successCount} 个Token${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
            setSelectedRowKeys([])
            fetchData()
          } else {
            message.error('批量更新失败')
          }
        } catch (error) {
          message.error('批量更新失败')
        }
      },
    })
  }

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys: React.Key[]) => {
      setSelectedRowKeys(selectedKeys as string[])
    },
    getCheckboxProps: (record: UserToken) => ({
      disabled: !isAdmin, // 非管理员禁用选择
    }),
  }

  const columns = [
    {
      title: 'Token',
      dataIndex: 'token',
      key: 'token',
      ellipsis: true,
      render: (token: string) => (
        <Space>
          <span style={{ fontFamily: 'monospace' }}>{token.substring(0, 20)}...</span>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(token)}
          />
        </Space>
      ),
    },
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      render: (user: any) => user?.nickname || user?.email || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => (
        <Tag color={status === 1 ? 'green' : 'red'}>
          {status === 1 ? '正常' : '异常'}
        </Tag>
      ),
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
      render: (_: any, record: UserToken) => (
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
                title="确定删除该Token吗？"
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
            <Select
              placeholder="选择用户"
              value={searchUserId}
              onChange={setSearchUserId}
              style={{ width: 200 }}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={userList.map(user => ({
                label: `${user.nickname} (${user.email})`,
                value: user.id,
              }))}
            />
            <Select
              placeholder="状态"
              value={searchStatus}
              onChange={setSearchStatus}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value={1}>正常</Select.Option>
              <Select.Option value={2}>异常</Select.Option>
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
          {isAdmin && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增Token
            </Button>
          )}
        </div>
      </div>

      {/* 批量操作提示和按钮 */}
      {isAdmin && selectedRowKeys.length > 0 && (
        <Alert
          message={
            <Space>
              <span>已选择 {selectedRowKeys.length} 项</span>
              <Button
                type="link"
                size="small"
                onClick={() => setSelectedRowKeys([])}
              >
                取消选择
              </Button>
            </Space>
          }
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <Space>
              <Button
                size="small"
                onClick={() => handleBatchUpdateStatus(1)}
              >
                批量设为正常
              </Button>
              <Button
                size="small"
                onClick={() => handleBatchUpdateStatus(2)}
              >
                批量设为异常
              </Button>
              <Button
                size="small"
                danger
                onClick={handleBatchDelete}
              >
                批量删除
              </Button>
            </Space>
          }
        />
      )}

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowSelection={isAdmin ? rowSelection : undefined}
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
        title={editingToken ? '编辑Token' : '新增Token'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          {!editingToken && (
            <>
              <Form.Item
                label="用户"
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
              <Form.Item
                label="Token"
                name="token"
                rules={[{ required: true, message: '请输入Token' }]}
              >
                <Input.TextArea placeholder="请输入Token" rows={3} />
              </Form.Item>
            </>
          )}
          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select>
              <Select.Option value={1}>正常</Select.Option>
              <Select.Option value={2}>异常</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default TokenList
