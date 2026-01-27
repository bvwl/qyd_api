import { useState, useEffect } from 'react'
import { Table, Button, Modal, Form, Input, App, Space, Popconfirm, Tag, Select, DatePicker } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined } from '@ant-design/icons'
import type { ServerCountry } from '@/types'
import { Status } from '@/types'
import { getCountryList, createCountry, updateCountry, deleteCountry } from '@/api/server'
import { useUserStore } from '@/store/useUserStore'
import dayjs, { Dayjs } from 'dayjs'

const { RangePicker } = DatePicker

const CountryList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<ServerCountry[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCountry, setEditingCountry] = useState<ServerCountry | null>(null)
  const [searchName, setSearchName] = useState('')
  const [searchShortName, setSearchShortName] = useState('')
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await getCountryList({
        page,
        limit: pageSize,
        res_count: true,
        name: searchName || undefined,
        short_name: searchShortName || undefined,
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
    setSearchShortName('')
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const handleAdd = () => {
    setEditingCountry(null)
    form.resetFields()
    form.setFieldsValue({
      status: Status.NORMAL,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: ServerCountry) => {
    setEditingCountry(record)
    form.setFieldsValue({
      short_name: record.short_name,
      name: record.name,
      status: record.status,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteCountry(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的国家')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个国家吗？`,
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        let successCount = 0
        let failCount = 0
        const errors: string[] = []

        for (const id of selectedRowKeys) {
          try {
            await deleteCountry(id as string)
            successCount++
          } catch (error: any) {
            failCount++
            const country = data.find(item => item.id === id)
            errors.push(`${country?.name} - ${error.response?.data?.detail || '删除失败'}`)
          }
        }

        if (failCount === 0) {
          message.success(`成功删除 ${successCount} 个国家`)
        } else {
          Modal.warning({
            title: '批量删除完成',
            content: (
              <div>
                <p>成功: {successCount} 个</p>
                <p>失败: {failCount} 个</p>
                {errors.length > 0 && (
                  <>
                    <p style={{ marginTop: 8, fontWeight: 'bold' }}>失败详情:</p>
                    {errors.slice(0, 5).map((error, index) => (
                      <p key={index} style={{ fontSize: '12px', color: '#ff4d4f' }}>• {error}</p>
                    ))}
                    {errors.length > 5 && (
                      <p style={{ fontSize: '12px', color: '#ff4d4f' }}>... 还有 {errors.length - 5} 个错误</p>
                    )}
                  </>
                )}
              </div>
            ),
            width: 500,
          })
        }

        setSelectedRowKeys([])
        fetchData()
      },
    })
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editingCountry) {
        await updateCountry(editingCountry.id, values)
        message.success('更新成功')
      } else {
        await createCountry(values)
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
      title: '简称',
      dataIndex: 'short_name',
      key: 'short_name',
    },
    {
      title: '国家名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: Status) => (
        <Tag color={status === Status.NORMAL ? 'green' : 'red'}>
          {status === Status.NORMAL ? '正常' : '异常'}
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
      render: (_: any, record: ServerCountry) => (
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
                title="确定删除该国家吗？"
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
              placeholder="国家名称"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Input
              placeholder="简称"
              value={searchShortName}
              onChange={(e) => setSearchShortName(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 150 }}
            />
            <Select
              placeholder="状态"
              value={searchStatus}
              onChange={setSearchStatus}
              style={{ width: 120 }}
              allowClear
            >
              <Select.Option value={Status.NORMAL}>正常</Select.Option>
              <Select.Option value={Status.ABNORMAL}>异常</Select.Option>
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
              新增国家
            </Button>
          )}
        </div>
      </div>

      {isAdmin && selectedRowKeys.length > 0 && (
        <div style={{ marginBottom: 16, padding: '12px', background: '#f0f2f5', borderRadius: '4px' }}>
          <Space>
            <span>已选择 {selectedRowKeys.length} 项</span>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleBatchDelete}
            >
              批量删除
            </Button>
            <Button onClick={() => setSelectedRowKeys([])}>
              取消选择
            </Button>
          </Space>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        rowSelection={isAdmin ? {
          selectedRowKeys,
          onChange: (selectedRowKeys) => setSelectedRowKeys(selectedRowKeys),
        } : undefined}
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
        title={editingCountry ? '编辑国家' : '新增国家'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => setModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="简称"
            name="short_name"
            rules={[{ required: true, message: '请输入国家简称' }]}
          >
            <Input placeholder="请输入国家简称（如：US、CN）" />
          </Form.Item>
          <Form.Item
            label="国家名称"
            name="name"
            rules={[{ required: true, message: '请输入国家名称' }]}
          >
            <Input placeholder="请输入国家名称" />
          </Form.Item>
          <Form.Item
            label="状态"
            name="status"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              <Select.Option value={Status.NORMAL}>正常</Select.Option>
              <Select.Option value={Status.ABNORMAL}>异常</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CountryList
