import { useState, useEffect } from 'react'
import { Table, message, Tag, Input, Button, Space, DatePicker, Select } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import type { UserLog } from '@/types'
import { getLogList } from '@/api/user'

const { RangePicker } = DatePicker

const LogList = () => {
  const [data, setData] = useState<UserLog[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchUserId, setSearchUserId] = useState('')
  const [searchAction, setSearchAction] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const params: any = {
        page,
        limit: pageSize,
        res_count: true,
      }
      
      if (searchUserId) {
        params.user_id = searchUserId
      }
      
      if (searchAction) {
        params.action = searchAction
      }
      
      // 添加时间范围
      if (createTimeRange && createTimeRange[0] && createTimeRange[1]) {
        params.create_time_start = createTimeRange[0].format('YYYY-MM-DD')
        params.create_time_end = createTimeRange[1].format('YYYY-MM-DD')
      }
      
      const res = await getLogList(params)
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
    setSearchUserId('')
    setSearchAction(undefined)
    setCreateTimeRange(null)
    setPage(1)
    setTimeout(() => {
      fetchData()
    }, 0)
  }

  const getActionText = (action: number) => {
    const actionMap: Record<number, { text: string; color: string }> = {
      1: { text: '登录', color: 'blue' },
      2: { text: '登出', color: 'default' },
      3: { text: '创建', color: 'green' },
      4: { text: '更新', color: 'orange' },
      5: { text: '删除', color: 'red' },
      6: { text: '查询', color: 'cyan' },
    }
    return actionMap[action] || { text: '未知', color: 'default' }
  }

  const columns = [
    {
      title: '用户',
      dataIndex: 'user',
      key: 'user',
      render: (user: any) => user?.nickname || user?.email || '-',
    },
    {
      title: '操作类型',
      dataIndex: 'action',
      key: 'action',
      render: (action: number) => {
        const { text, color } = getActionText(action)
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '操作描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
    },
    {
      title: 'User-Agent',
      dataIndex: 'user_agent',
      key: 'user_agent',
      ellipsis: true,
      width: 200,
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 180,
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '16px' }}>
        <Space style={{ marginBottom: '16px' }} wrap>
          <Input
            placeholder="请输入用户ID"
            value={searchUserId}
            onChange={(e) => setSearchUserId(e.target.value)}
            style={{ width: 200 }}
            onPressEnter={handleSearch}
          />
          <Select
            placeholder="操作类型"
            value={searchAction}
            onChange={setSearchAction}
            style={{ width: 150 }}
            allowClear
          >
            <Select.Option value={1}>登录</Select.Option>
            <Select.Option value={2}>登出</Select.Option>
            <Select.Option value={3}>创建</Select.Option>
            <Select.Option value={4}>更新</Select.Option>
            <Select.Option value={5}>删除</Select.Option>
            <Select.Option value={6}>查询</Select.Option>
          </Select>
          <RangePicker
            placeholder={['创建开始日期', '创建结束日期']}
            value={createTimeRange}
            onChange={setCreateTimeRange}
            format="YYYY-MM-DD"
            style={{ width: 260 }}
          />
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>
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
    </div>
  )
}

export default LogList
