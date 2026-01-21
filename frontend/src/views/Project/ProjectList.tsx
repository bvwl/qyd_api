import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, message, Space, Popconfirm, Tag, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { Project } from '@/types'
import { ProjectStatus } from '@/types'
import { getProjectList, createProject, updateProject, deleteProject } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const ProjectList = () => {
  const [data, setData] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingProject, setEditingProject] = useState<Project | null>(null)
  const [searchName, setSearchName] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

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

  useEffect(() => {
    fetchData()
  }, [page, pageSize])

  const handleSearch = () => {
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchName('')
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
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

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
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
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
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
      render: (_: any, record: Project) => (
        <Space>
          {(isAdmin || isGM) && (
            <>
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
          {(isAdmin || isGM) && (
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增项目
            </Button>
          )}
        </div>
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
    </div>
  )
}

export default ProjectList
