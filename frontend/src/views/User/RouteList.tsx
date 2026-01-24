import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Switch, InputNumber, Tag, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { Route } from '@/types'
import { getRouteList, createRoute, updateRoute, deleteRoute } from '@/api/user'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const RouteList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<Route[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRoute, setEditingRoute] = useState<Route | null>(null)
  const [searchName, setSearchName] = useState('')
  const [searchPath, setSearchPath] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getRouteList({
        page,
        limit: pageSize,
        res_count: true,
        name: searchName || undefined,
        path: searchPath || undefined,
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
    setSearchPath('')
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingRoute(null)
    form.resetFields()
    form.setFieldsValue({
      sort: 0,
      is_hidden: false,
      is_cache: true,
      is_affix: false,
      status: 1,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: Route) => {
    setEditingRoute(record)
    form.setFieldsValue({
      name: record.name,
      path: record.path,
      component: record.component,
      title: record.title,
      icon: record.icon,
      sort: record.sort,
      redirect: record.redirect,
      is_hidden: record.is_hidden,
      is_cache: record.is_cache,
      is_affix: record.is_affix,
      status: record.status,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteRoute(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingRoute) {
        await updateRoute(editingRoute.id, values)
        message.success('更新成功')
      } else {
        await createRoute(values)
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
      title: '路由名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '路由路径',
      dataIndex: 'path',
      key: 'path',
    },
    {
      title: '菜单标题',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: '图标',
      dataIndex: 'icon',
      key: 'icon',
    },
    {
      title: '排序',
      dataIndex: 'sort',
      key: 'sort',
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
      title: '操作',
      key: 'action',
      render: (_: any, record: Route) => (
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
                title="确定删除该路由吗？"
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
              placeholder="路由名称"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Input
              placeholder="路由路径"
              value={searchPath}
              onChange={(e) => setSearchPath(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
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
              新增路由
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
        title={editingRoute ? '编辑路由' : '新增路由'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="路由名称"
            name="name"
            rules={[{ required: true, message: '请输入路由名称' }]}
          >
            <Input placeholder="请输入路由名称（唯一标识）" />
          </Form.Item>
          <Form.Item
            label="路由路径"
            name="path"
            rules={[{ required: true, message: '请输入路由路径' }]}
          >
            <Input placeholder="请输入路由路径（如：/user/list）" />
          </Form.Item>
          <Form.Item
            label="菜单标题"
            name="title"
            rules={[{ required: true, message: '请输入菜单标题' }]}
          >
            <Input placeholder="请输入菜单标题" />
          </Form.Item>
          <Form.Item label="组件路径" name="component">
            <Input placeholder="请输入前端组件路径" />
          </Form.Item>
          <Form.Item label="菜单图标" name="icon">
            <Input placeholder="请输入菜单图标" />
          </Form.Item>
          <Form.Item label="排序" name="sort">
            <InputNumber placeholder="数字越小越靠前" style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item label="重定向路径" name="redirect">
            <Input placeholder="请输入重定向路径" />
          </Form.Item>
          <Form.Item label="是否隐藏菜单" name="is_hidden" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="是否缓存页面" name="is_cache" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="是否固定标签页" name="is_affix" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default RouteList
