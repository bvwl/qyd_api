import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, DatePicker, Transfer, Tooltip } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, TeamOutlined, CopyOutlined } from '@ant-design/icons'
import type { Project, User } from '@/types'
import { ProjectStatus } from '@/types'
import { getProjectList, createProject, updateProject, deleteProject } from '@/api/project'
import { getUserList } from '@/api/user'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'
import type { TableProps } from 'antd'

const { RangePicker } = DatePicker

type SortOrder = 'ascend' | 'descend' | null

interface TransferItem {
  key: string
  title: string
  description: string
}

const ProjectList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [searchName, setSearchName] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [searchUserId, setSearchUserId] = useState<string>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [orderBy, setOrderBy] = useState<string>('-create_time')
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  // 人员管理相关状态
  const [userModalVisible, setUserModalVisible] = useState(false)
  const [managingProject, setManagingProject] = useState<Project | null>(null)
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [selectedUserKeys, setSelectedUserKeys] = useState<string[]>([])
  const [userLoading, setUserLoading] = useState(false)
  
  // 用户筛选列表
  const [filterUsers, setFilterUsers] = useState<User[]>([])

  const isAdmin = hasPermission('ADMIN')
  const isGM = hasPermission('GM')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getProjectList({
        page,
        limit: pageSize,
        res_count: true,
        name: searchName || undefined,
        status: searchStatus,
        user_id: searchUserId,
        order_by: orderBy,
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

  // 加载用户列表（用于筛选）
  const fetchFilterUsers = async () => {
    if (!isAdmin && !isGM) return // 只有管理员和GM可以按用户筛选
    
    try {
      const res = await getUserList({ page: 1, limit: 1000 })
      setFilterUsers(res.items || [])
    } catch (error) {
      setFilterUsers([])
    }
  }

  useEffect(() => {
    fetchData()
  }, [page, pageSize])
  
  useEffect(() => {
    fetchFilterUsers()
  }, [])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchName('')
    setSearchStatus(undefined)
    setSearchUserId(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setOrderBy('-create_time')
    setSelectedRowKeys([])
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingProject(null)
    form.resetFields()
    form.setFieldsValue({
      status: ProjectStatus.NORMAL,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: Project) => {
    setEditingProject(record)
    form.setFieldsValue({
      name: record.name,
      status: record.status,
      content: record.content,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProject(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的项目')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个项目吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await Promise.all(selectedRowKeys.map(id => deleteProject(id)))
          message.success(`成功删除 ${selectedRowKeys.length} 个项目`)
          setSelectedRowKeys([])
          fetchData()
        } catch (error) {
          message.error('批量删除失败')
        }
      }
    })
  }

  const handleTableChange: TableProps<Project>['onChange'] = (_pagination, _filters, sorter: any) => {
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

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingProject) {
        await updateProject(editingProject.id, values)
        message.success('更新成功')
      } else {
        await createProject(values)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  // 打开人员管理弹窗
  const handleManageUsers = async (record: Project) => {
    setManagingProject(record)
    setUserLoading(true)
    setUserModalVisible(true)
    
    try {
      // 获取所有用户
      const usersRes = await getUserList({ page: 1, limit: 1000 })
      setAllUsers(usersRes.items || [])
      
      // 设置当前项目已关联的用户，过滤掉无效值
      const currentUserIds = (record.users?.map(u => u.id) || []).filter(id => id != null && id !== '')
      setSelectedUserKeys(currentUserIds)
    } catch (error) {
      message.error('获取用户列表失败')
      setAllUsers([])
      setSelectedUserKeys([])
    } finally {
      setUserLoading(false)
    }
  }

  // 保存人员关联
  const handleSaveUsers = async () => {
    if (!managingProject) return
    
    try {
      setUserLoading(true)
      // 过滤掉null、undefined等无效值
      const validUserIds = selectedUserKeys.filter(id => id != null && id !== '')
      await updateProject(managingProject.id, {
        user_ids: validUserIds,
      })
      message.success('人员关联更新成功')
      setUserModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('更新失败')
    } finally {
      setUserLoading(false)
    }
  }

  const getStatusText = (status: ProjectStatus) => {
    const statusMap: Record<ProjectStatus, { text: string; color: string }> = {
      [ProjectStatus.NORMAL]: { text: '正常', color: 'green' },
      [ProjectStatus.NOT_WRITTEN]: { text: '未编写', color: 'default' },
      [ProjectStatus.WRITING]: { text: '编写中', color: 'blue' },
      [ProjectStatus.FINISHED]: { text: '项目结束', color: 'orange' },
      [ProjectStatus.RUNAWAY]: { text: '项目跑路', color: 'red' },
      [ProjectStatus.MAINTENANCE]: { text: '项目维护', color: 'purple' },
      [ProjectStatus.UNASSIGNED]: { text: '未分配', color: 'default' },
      [ProjectStatus.ACCOUNT_UNSUPPORTED]: { text: '账号不支持', color: 'red' },
      [ProjectStatus.IP_UNSUPPORTED]: { text: 'IP不支持', color: 'red' },
    }
    return statusMap[status] || { text: '未知', color: 'default' }
  }

  const handleCopyId = (id: string) => {
    navigator.clipboard.writeText(id).then(() => {
      message.success('项目ID已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败')
    })
  }

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      sorter: true,
      sortOrder: getSortOrder('name'),
    },
    {
      title: '项目ID',
      dataIndex: 'id',
      key: 'id',
      width: 280,
      ellipsis: true,
      render: (id: string) => (
        <Space>
          <Tooltip title={id}>
            <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
              {id.substring(0, 8)}...{id.substring(id.length - 8)}
            </span>
          </Tooltip>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyId(id)}
          />
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: ProjectStatus) => {
        const { text, color } = getStatusText(status)
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '关联人员',
      dataIndex: 'users',
      key: 'users',
      render: (users: any[]) => (
        <Space size={[0, 4]} wrap>
          {users && users.length > 0 ? (
            users.map(user => (
              <Tag key={user.id} color="blue">
                {user.nickname || user.email}
              </Tag>
            ))
          ) : (
            <span style={{ color: '#999' }}>未分配</span>
          )}
        </Space>
      ),
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      sorter: true,
      sortOrder: getSortOrder('create_time'),
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      sorter: true,
      sortOrder: getSortOrder('update_time'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Project) => (
        <Space>
          {(isAdmin || isGM) && (
            <>
              <Button
                type="link"
                icon={<TeamOutlined />}
                onClick={() => handleManageUsers(record)}
              >
                管理人员
              </Button>
              <Button
                type="link"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定删除该项目吗？"
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
          <Space style={{ marginBottom: '16px' }} wrap>
            <Input
              placeholder="项目名称"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Select
              placeholder="状态"
              value={searchStatus}
              onChange={setSearchStatus}
              style={{ width: 150 }}
              allowClear
            >
              <Select.Option value={ProjectStatus.NORMAL}>正常</Select.Option>
              <Select.Option value={ProjectStatus.NOT_WRITTEN}>未编写</Select.Option>
              <Select.Option value={ProjectStatus.WRITING}>编写中</Select.Option>
              <Select.Option value={ProjectStatus.FINISHED}>项目结束</Select.Option>
              <Select.Option value={ProjectStatus.RUNAWAY}>项目跑路</Select.Option>
              <Select.Option value={ProjectStatus.MAINTENANCE}>项目维护</Select.Option>
              <Select.Option value={ProjectStatus.UNASSIGNED}>未分配</Select.Option>
              <Select.Option value={ProjectStatus.ACCOUNT_UNSUPPORTED}>账号不支持</Select.Option>
              <Select.Option value={ProjectStatus.IP_UNSUPPORTED}>IP不支持</Select.Option>
            </Select>
            {(isAdmin || isGM) && (
              <Select
                placeholder="关联用户"
                value={searchUserId}
                onChange={setSearchUserId}
                style={{ width: 200 }}
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                options={filterUsers.map(user => ({
                  label: user.nickname || user.email,
                  value: user.id,
                }))}
              />
            )}
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
            {selectedRowKeys.length > 0 && (isAdmin || isGM) && (
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                onClick={handleBatchDelete}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            )}
            {(isAdmin || isGM) && (
              <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                新增项目
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
        onChange={handleTableChange}
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
        title={editingProject ? '编辑项目' : '新增项目'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="项目名称"
            name="name"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>
          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              <Select.Option value={ProjectStatus.NORMAL}>正常</Select.Option>
              <Select.Option value={ProjectStatus.NOT_WRITTEN}>未编写</Select.Option>
              <Select.Option value={ProjectStatus.WRITING}>编写中</Select.Option>
              <Select.Option value={ProjectStatus.FINISHED}>项目结束</Select.Option>
              <Select.Option value={ProjectStatus.RUNAWAY}>项目跑路</Select.Option>
              <Select.Option value={ProjectStatus.MAINTENANCE}>项目维护</Select.Option>
              <Select.Option value={ProjectStatus.UNASSIGNED}>未分配</Select.Option>
              <Select.Option value={ProjectStatus.ACCOUNT_UNSUPPORTED}>账号不支持</Select.Option>
              <Select.Option value={ProjectStatus.IP_UNSUPPORTED}>IP不支持</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item label="内容" name="content">
            <Input.TextArea placeholder="请输入项目内容" rows={4} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 人员管理弹窗 */}
      <Modal
        title={`管理项目人员 - ${managingProject?.name || ''}`}
        open={userModalVisible}
        onOk={handleSaveUsers}
        onCancel={() => setUserModalVisible(false)}
        okText="保存"
        cancelText="取消"
        width={700}
        confirmLoading={userLoading}
      >
        <div style={{ marginBottom: 16 }}>
          <p style={{ color: '#666', marginBottom: 8 }}>
            选择要关联到此项目的人员。关联后，这些人员可以查看和管理该项目的数据。
          </p>
        </div>
        <Transfer
          dataSource={allUsers.map(user => ({
            key: user.id,
            title: user.nickname || user.email,
            description: user.email,
          }))}
          titles={['可选人员', '已关联人员']}
          targetKeys={selectedUserKeys}
          onChange={setSelectedUserKeys}
          render={item => (
            <div>
              <div style={{ fontWeight: 500 }}>{item.title}</div>
              <div style={{ fontSize: 12, color: '#999' }}>{item.description}</div>
            </div>
          )}
          listStyle={{
            width: 300,
            height: 400,
          }}
          showSearch
          filterOption={(inputValue, item) =>
            item.title.toLowerCase().includes(inputValue.toLowerCase()) ||
            item.description.toLowerCase().includes(inputValue.toLowerCase())
          }
          locale={{
            itemUnit: '人',
            itemsUnit: '人',
            searchPlaceholder: '搜索人员',
            notFoundContent: '无数据',
          }}
        />
      </Modal>
    </div>
  )
}

export default ProjectList
