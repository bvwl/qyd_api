import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, DatePicker, Transfer, Tooltip, Upload, List } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, TeamOutlined, CopyOutlined, UploadOutlined, DownloadOutlined, FileOutlined } from '@ant-design/icons'
import type { Project, User } from '@/types'
import { ProjectStatus } from '@/types'
import { getProjectList, createProject, updateProject, deleteProject, uploadProjectFile, getProjectFiles, downloadProjectFile, deleteProjectFile } from '@/api/project'
import { getUserList } from '@/api/user'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'
import type { TableProps } from 'antd'
import { filterEmptyStrings } from '@/utils/form'
import { copyToClipboard } from '@/utils/format'
import type { UploadFile } from 'antd/es/upload/interface'

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
  const { hasPermission, userInfo } = useUserStore()

  // 人员管理相关状态
  const [userModalVisible, setUserModalVisible] = useState(false)
  const [managingProject, setManagingProject] = useState<Project | null>(null)
  const [allUsers, setAllUsers] = useState<User[]>([])
  const [selectedUserKeys, setSelectedUserKeys] = useState<string[]>([])
  const [userLoading, setUserLoading] = useState(false)
  
  // 用户筛选列表
  const [filterUsers, setFilterUsers] = useState<User[]>([])

  // 文件管理相关状态
  const [fileModalVisible, setFileModalVisible] = useState(false)
  const [managingFileProject, setManagingFileProject] = useState<Project | null>(null)
  const [projectFiles, setProjectFiles] = useState<Array<{ name: string; size: number; modified_time: number }>>([])
  const [fileLoading, setFileLoading] = useState(false)
  const [uploadingFile, setUploadingFile] = useState(false)

  // 权限判断 - 使用数组方式更可靠
  const canManageProject = hasPermission(['ADMIN', 'GM'])
  
  // 监控权限变化
  useEffect(() => {
    console.log('ProjectList 权限更新:', {
      userInfo,
      roles: userInfo?.roles?.map(r => r.code),
      canManageProject,
    })
  }, [userInfo, canManageProject])

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
    if (!canManageProject) return // 只有管理员和GM可以按用户筛选
    
    try {
      const res = await getUserList({ page: 1, limit: 1000 })
      setFilterUsers(res.items || [])
    } catch (error) {
      setFilterUsers([])
    }
  }

  // 当分页、排序变化时重新加载数据
  useEffect(() => {
    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, orderBy])
  
  useEffect(() => {
    fetchFilterUsers()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  const handleTableChange: TableProps<Project>['onChange'] = (pagination, _filters, sorter: any) => {
    console.log('Table onChange 触发:', { pagination, sorter })
    
    // 处理分页变化
    if (pagination.current !== page) {
      console.log('页码变化:', page, '->', pagination.current)
      setPage(pagination.current || 1)
    }
    if (pagination.pageSize !== pageSize) {
      console.log('每页数量变化:', pageSize, '->', pagination.pageSize)
      setPageSize(pagination.pageSize || 10)
    }
    
    // 处理排序变化
    if (sorter.field) {
      const order = sorter.order === 'ascend' ? '' : '-'
      const newOrderBy = `${order}${sorter.field}`
      console.log('排序变化:', orderBy, '->', newOrderBy)
      setOrderBy(newOrderBy)
      setPage(1)
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
      const filteredValues = filterEmptyStrings(values)
      if (editingProject) {
        await updateProject(editingProject.id, filteredValues)
        message.success('更新成功')
      } else {
        await createProject(filteredValues)
        message.success('创建成功')
      }
      setModalVisible(false)
      // 确保数据刷新
      await fetchData()
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
      // 确保数据刷新
      await fetchData()
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

  const handleCopyId = async (id: string) => {
    const success = await copyToClipboard(id)
    if (success) {
      message.success('项目ID已复制到剪贴板')
    } else {
      message.error('复制失败')
    }
  }

  // 打开文件管理弹窗
  const handleManageFiles = async (record: Project) => {
    setManagingFileProject(record)
    setFileModalVisible(true)
    await loadProjectFiles(record.id)
  }

  // 加载项目文件列表
  const loadProjectFiles = async (projectId: string) => {
    setFileLoading(true)
    try {
      const res = await getProjectFiles(projectId)
      setProjectFiles(res.files || [])
    } catch (error) {
      message.error('获取文件列表失败')
      setProjectFiles([])
    } finally {
      setFileLoading(false)
    }
  }

  // 上传文件
  const handleUpload = async (file: File) => {
    if (!managingFileProject) return false

    // 检查文件类型
    const allowedTypes = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase()
    if (!allowedTypes.includes(fileExt)) {
      message.error(`不支持的文件格式。允许的格式：${allowedTypes.join(', ')}`)
      return false
    }

    // 检查文件大小（50MB）
    if (file.size > 50 * 1024 * 1024) {
      message.error('文件大小不能超过 50MB')
      return false
    }

    setUploadingFile(true)
    try {
      await uploadProjectFile(managingFileProject.id, file)
      message.success('文件上传成功')
      // 重新加载文件列表，不更新项目内容
      await loadProjectFiles(managingFileProject.id)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '文件上传失败')
    } finally {
      setUploadingFile(false)
    }

    return false // 阻止默认上传行为
  }

  // 下载文件
  const handleDownload = async (filename: string) => {
    if (!managingFileProject) return

    try {
      const blob = await downloadProjectFile(managingFileProject.id, filename)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      message.success('文件下载成功')
    } catch (error) {
      message.error('文件下载失败')
    }
  }

  // 删除文件
  const handleDeleteFile = async (filename: string) => {
    if (!managingFileProject) return

    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件 "${filename}" 吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteProjectFile(managingFileProject.id, filename)
          message.success('文件删除成功')
          await loadProjectFiles(managingFileProject.id)
        } catch (error) {
          message.error('文件删除失败')
        }
      }
    })
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  // 格式化时间
  const formatTime = (timestamp: number) => {
    return dayjs(timestamp * 1000).format('YYYY-MM-DD HH:mm:ss')
  }

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      sorter: true,
      sortOrder: getSortOrder('name'),
      ellipsis: {
        showTitle: false,
      },
      render: (name: string) => (
        <Tooltip placement="topLeft" title={name}>
          {name}
        </Tooltip>
      ),
    },
    {
      title: '项目ID',
      dataIndex: 'id',
      key: 'id',
      width: 200,
      ellipsis: true,
      render: (id: string) => (
        <Space>
          <Tooltip title={id}>
            <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
              {id.substring(0, 8)}...
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
      width: 100,
      render: (status: ProjectStatus) => {
        const { text, color } = getStatusText(status)
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '关联人员',
      dataIndex: 'users',
      key: 'users',
      width: 200,
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
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (content: string) => (
        <Tooltip placement="topLeft" title={content}>
          {content || '-'}
        </Tooltip>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 110,
      sorter: true,
      sortOrder: getSortOrder('create_time'),
      render: (text: string) => text ? text.split(' ')[0] : '-',
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      width: 110,
      sorter: true,
      sortOrder: getSortOrder('update_time'),
      render: (text: string) => text ? text.split(' ')[0] : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 320,
      render: (_: any, record: Project) => (
        <Space size="small" wrap>
          <Button
            type="link"
            icon={<FileOutlined />}
            onClick={() => handleManageFiles(record)}
          >
            文件
          </Button>
          {canManageProject && (
            <>
              <Button
                type="link"
                icon={<TeamOutlined />}
                onClick={() => handleManageUsers(record)}
              >
                管理
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
            {canManageProject && (
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
            {selectedRowKeys.length > 0 && canManageProject && (
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                onClick={handleBatchDelete}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            )}
            {canManageProject && (
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

      {/* 文件管理弹窗 */}
      <Modal
        title={`文件管理 - ${managingFileProject?.name || ''}`}
        open={fileModalVisible}
        onCancel={() => setFileModalVisible(false)}
        footer={null}
        width={700}
      >
        <div style={{ marginBottom: 16 }}>
          {canManageProject && (
            <Upload
              beforeUpload={handleUpload}
              showUploadList={false}
              disabled={uploadingFile}
            >
              <Button icon={<UploadOutlined />} loading={uploadingFile}>
                上传文件
              </Button>
            </Upload>
          )}
          <p style={{ color: '#666', marginTop: 8, fontSize: 12 }}>
            支持格式：PDF, Word, Excel, PowerPoint, TXT（最大 50MB）
          </p>
        </div>

        <List
          loading={fileLoading}
          dataSource={projectFiles}
          locale={{ emptyText: '暂无文件' }}
          renderItem={(file) => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownload(file.name)}
                >
                  下载
                </Button>,
                canManageProject && (
                  <Popconfirm
                    title="确定删除该文件吗？"
                    onConfirm={() => handleDeleteFile(file.name)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button type="link" danger icon={<DeleteOutlined />}>
                      删除
                    </Button>
                  </Popconfirm>
                ),
              ].filter(Boolean)}
            >
              <List.Item.Meta
                avatar={<FileOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                title={file.name}
                description={
                  <Space split="|">
                    <span>{formatFileSize(file.size)}</span>
                    <span>{formatTime(file.modified_time)}</span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  )
}

export default ProjectList
