import { useState, useEffect, useCallback } from 'react'
import { Table, Button, Modal, Form, Input, InputNumber, App, Space, Popconfirm, Tag, Select, DatePicker, Tooltip, Descriptions, Card, Statistic, Row, Col } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined, SearchOutlined, HistoryOutlined, CopyOutlined, BarChartOutlined, DownloadOutlined } from '@ant-design/icons'
import type { ProjectAccount, Project } from '@/types'
import { AccountType, Status } from '@/types'
import { getProjectAccountList, createProjectAccount, updateProjectAccount, deleteProjectAccount, getProjectList, getProjectAccountStats, exportAllProjectStats, exportTodayProjectStats } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import { copyToClipboard } from '@/utils/format'
import { Dayjs } from 'dayjs'
import type { TableProps } from 'antd'

const { RangePicker } = DatePicker

type SortOrder = 'ascend' | 'descend' | null

const ProjectAccountList = () => {
  const { message } = App.useApp()
  const [data, setData] = useState<ProjectAccount[]>([])
  const [loading, setLoading] = useState(false)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [modalVisible, setModalVisible] = useState(false)
  const [historyModalVisible, setHistoryModalVisible] = useState(false)
  const [statsModalVisible, setStatsModalVisible] = useState(false)
  const [currentHistoryAccount, setCurrentHistoryAccount] = useState<ProjectAccount | null>(null)
  const [editingAccount, setEditingAccount] = useState<ProjectAccount | null>(null)
  const [projectList, setProjectList] = useState<Project[]>([])
  const [searchProjectId, setSearchProjectId] = useState<string>()
  const [searchAccount, setSearchAccount] = useState('')
  const [searchAccountType, setSearchAccountType] = useState<number>()
  const [searchStatus, setSearchStatus] = useState<number>()
  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [orderBy, setOrderBy] = useState<string>('-update_time')
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [form] = Form.useForm()
  const { hasPermission } = useUserStore()

  const isAdmin = hasPermission('ADMIN')
  const isGM = hasPermission('GM')

  // 使用 useEffect 直接监听 page 和 pageSize 的变化
  useEffect(() => {
    // 如果没有选择项目，不查询账号列表
    if (!searchProjectId) {
      setData([])
      setTotal(0)
      return
    }

    console.log('useEffect triggered with page:', page, 'pageSize:', pageSize)
    
    const loadData = async () => {
      setLoading(true)
      try {
        const res = await getProjectAccountList({
          page,
          limit: pageSize,
          res_count: true,
          project_id: searchProjectId,
          account: searchAccount || undefined,
          account_type: searchAccountType,
          status: searchStatus,
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

    loadData()
  }, [page, pageSize, searchProjectId, orderBy])

  // fetchData 函数用于手动触发（如搜索按钮）
  const fetchData = async () => {
    if (!searchProjectId) {
      setData([])
      setTotal(0)
      return
    }

    setLoading(true)
    try {
      const res = await getProjectAccountList({
        page,
        limit: pageSize,
        res_count: true,
        project_id: searchProjectId,
        account: searchAccount || undefined,
        account_type: searchAccountType,
        status: searchStatus,
        order_by: orderBy,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
      })
      setData(res.items || [])
      setTotal(res.count || 0)
    } catch (error) {
      setData([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const fetchProjectList = async () => {
    try {
      const res = await getProjectList({
        page: 1,
        limit: 100,
      })
      setProjectList(res.items || [])
      return true  // 返回成功状态
    } catch (error) {
      setProjectList([])
      message.error('加载项目列表失败')
      return false  // 返回失败状态
    }
  }

  useEffect(() => {
    const loadData = async () => {
      await fetchProjectList()
    }
    loadData()
  }, [])

  const handleSearch = () => {
    // 验证是否选择了项目
    if (!searchProjectId) {
      message.warning('请先选择项目')
      return
    }
    setPage(1)
    fetchData()
  }

  const handleReset = () => {
    setSearchProjectId(undefined)
    setSearchAccount('')
    setSearchAccountType(undefined)
    setSearchStatus(undefined)
    setCreateTimeRange(null)
    setUpdateTimeRange(null)
    setOrderBy('-update_time')
    setPage(1)
    setSelectedRowKeys([])
    // 重置后清空数据
    setData([])
    setTotal(0)
  }

  const handleShowHistory = (record: ProjectAccount) => {
    setCurrentHistoryAccount(record)
    setHistoryModalVisible(true)
  }

  const handleAdd = () => {
    setEditingAccount(null)
    form.resetFields()
    form.setFieldsValue({
      status: Status.NORMAL,
      account_type: AccountType.EMAIL,
    })
    setModalVisible(true)
  }

  const handleEdit = (record: ProjectAccount) => {
    setEditingAccount(record)
    form.setFieldsValue({
      account: record.account,
      password: record.password,
      status: record.status,
      account_type: record.account_type,
      balance: record.balance,
      project_id: record.project_id,
    })
    setModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await deleteProjectAccount(id)
      message.success('删除成功')
      fetchData()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的账号')
      return
    }

    Modal.confirm({
      title: '批量删除确认',
      content: `确定要删除选中的 ${selectedRowKeys.length} 个账号吗？`,
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          await Promise.all(selectedRowKeys.map(id => deleteProjectAccount(id)))
          message.success(`成功删除 ${selectedRowKeys.length} 个账号`)
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
      
      // 过滤掉空字符串，将其转换为 undefined
      // 这样后端的 exclude_unset=True 才能正确工作
      const filteredValues = Object.entries(values).reduce((acc, [key, value]) => {
        // 如果值是空字符串，不包含该字段（相当于 undefined）
        if (value === '') {
          return acc
        }
        // 其他值正常包含
        acc[key] = value
        return acc
      }, {} as any)
      
      if (editingAccount) {
        await updateProjectAccount(editingAccount.id, filteredValues)
        message.success('更新成功')
      } else {
        await createProjectAccount(filteredValues)
        message.success('创建成功')
      }
      setModalVisible(false)
      fetchData()
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleTableChange: TableProps<ProjectAccount>['onChange'] = (_pagination, _filters, sorter: any) => {
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

  const getAccountTypeText = (type: AccountType) => {
    const typeMap: Record<AccountType, string> = {
      [AccountType.EMAIL]: '邮箱',
      [AccountType.WALLET]: '钱包',
      [AccountType.X]: 'X',
      [AccountType.OTHER1]: '其他1',
      [AccountType.OTHER2]: '其他2',
    }
    return typeMap[type] || '未知'
  }

  const handleCopyId = async (id: string) => {
    const success = await copyToClipboard(id)
    if (success) {
      message.success('ID已复制到剪贴板')
    } else {
      message.error('复制失败')
    }
  }

  // 获取统计数据（用于弹窗显示）
  const [statsData, setStatsData] = useState<any>(null)
  
  // 计算统计数据 - 调用后端API
  const handleShowStats = async () => {
    if (!searchProjectId) {
      message.warning('请先选择项目')
      return
    }
    
    try {
      setLoading(true)
      const res = await getProjectAccountStats({
        project_id: searchProjectId,
        account: searchAccount || undefined,
        status: searchStatus,
        account_type: searchAccountType,
        create_time_start: createTimeRange?.[0]?.format('YYYY-MM-DD'),
        create_time_end: createTimeRange?.[1]?.format('YYYY-MM-DD'),
        update_time_start: updateTimeRange?.[0]?.format('YYYY-MM-DD'),
        update_time_end: updateTimeRange?.[1]?.format('YYYY-MM-DD'),
      })
      
      if (res.code === 1 && res.data) {
        if (res.data.total_count === 0) {
          message.warning('当前筛选条件下没有数据')
          return
        }
        // 保存统计数据并打开弹窗
        setStatsData(res.data)
        setStatsModalVisible(true)
      } else {
        message.error(res.message || '获取统计数据失败')
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取统计数据失败')
    } finally {
      setLoading(false)
    }
  }

  // 导出所有项目统计数据
  const handleExportAllStats = async () => {
    try {
      setLoading(true)
      const blob = await exportAllProjectStats()
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // 生成中文文件名
      const now = new Date()
      const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
      const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
      link.download = `项目统计汇总_${dateStr}_${timeStr}.xlsx`
      
      // 触发下载
      document.body.appendChild(link)
      link.click()
      
      // 清理
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('导出成功')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导出失败')
    } finally {
      setLoading(false)
    }
  }

  // 导出当天所有项目统计数据
  const handleExportTodayStats = async () => {
    try {
      setLoading(true)
      const blob = await exportTodayProjectStats()
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // 生成中文文件名
      const now = new Date()
      const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
      const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
      link.download = `当天项目统计_${dateStr}_${timeStr}.xlsx`
      
      // 触发下载
      document.body.appendChild(link)
      link.click()
      
      // 清理
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      message.success('导出成功')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '导出失败')
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '账号',
      dataIndex: 'account',
      key: 'account',
      width: 200,
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
      title: '账号类型',
      dataIndex: 'account_type',
      key: 'account_type',
      width: 100,
      render: (type: AccountType) => getAccountTypeText(type),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: Status) => (
        <Tag color={status === Status.NORMAL ? 'green' : 'red'}>
          {status === Status.NORMAL ? '正常' : '异常'}
        </Tag>
      ),
    },
    {
      title: '余额',
      dataIndex: 'balance',
      key: 'balance',
      width: 120,
      sorter: true,
      sortOrder: getSortOrder('balance'),
      render: (balance: number | string) => Number(balance).toFixed(2),
    },
    {
      title: '变动',
      dataIndex: 'variable',
      key: 'variable',
      width: 120,
      sorter: true,
      sortOrder: getSortOrder('variable'),
      render: (variable: number | string) => {
        const num = Number(variable)
        const color = num > 0 ? 'green' : num < 0 ? 'red' : 'default'
        return <span style={{ color }}>{num > 0 ? '+' : ''}{num.toFixed(2)}</span>
      },
    },
    {
      title: '项目',
      dataIndex: 'project',
      key: 'project',
      width: 150,
      render: (project: any) => project?.name || '-',
    },
    {
      title: '更新时间',
      dataIndex: 'update_time',
      key: 'update_time',
      width: 180,
      sorter: true,
      sortOrder: getSortOrder('update_time'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right' as const,
      render: (_: any, record: ProjectAccount) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<HistoryOutlined />}
            onClick={() => handleShowHistory(record)}
          >
            历史
          </Button>
          <Button
            type="link"
            size="small"
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
            <Button type="link" danger size="small" icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
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
              placeholder="选择项目（必选）"
              value={searchProjectId}
              onChange={setSearchProjectId}
              style={{ width: 200 }}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={projectList.map(project => ({
                label: project.name,
                value: project.id,
              }))}
            />
            <Input
              placeholder="账号（可选）"
              value={searchAccount}
              onChange={(e) => setSearchAccount(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 200 }}
            />
            <Select
              placeholder="账号类型"
              value={searchAccountType}
              onChange={setSearchAccountType}
              style={{ width: 150 }}
              allowClear
            >
              <Select.Option value={AccountType.EMAIL}>邮箱</Select.Option>
              <Select.Option value={AccountType.WALLET}>钱包</Select.Option>
              <Select.Option value={AccountType.X}>X</Select.Option>
              <Select.Option value={AccountType.OTHER1}>其他1</Select.Option>
              <Select.Option value={AccountType.OTHER2}>其他2</Select.Option>
            </Select>
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
            <Button 
              icon={<BarChartOutlined />} 
              onClick={handleShowStats}
              disabled={!searchProjectId}
            >
              统计分析
            </Button>
            {(isAdmin || isGM) && (
              <>
                <Button 
                  type="default"
                  icon={<DownloadOutlined />} 
                  onClick={handleExportAllStats}
                >
                  导出所有项目统计
                </Button>
                <Button 
                  type="default"
                  icon={<DownloadOutlined />} 
                  onClick={handleExportTodayStats}
                >
                  导出当天项目统计
                </Button>
              </>
            )}
          </Space>
          <Space>
            {selectedRowKeys.length > 0 && (
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                onClick={handleBatchDelete}
              >
                批量删除 ({selectedRowKeys.length})
              </Button>
            )}
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增账号
            </Button>
          </Space>
        </div>
      </div>

      {!searchProjectId && data.length === 0 && (
        <div style={{ 
          textAlign: 'center', 
          padding: '40px', 
          background: '#fafafa', 
          border: '1px dashed #d9d9d9',
          borderRadius: '4px',
          marginBottom: '16px'
        }}>
          <p style={{ fontSize: '16px', color: '#999', margin: 0 }}>
            请先选择项目，然后点击"搜索"按钮查看账号列表
          </p>
        </div>
      )}

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        onChange={handleTableChange}
        scroll={{ x: 1200 }}
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
          onChange: (newPage, newPageSize) => {
            console.log('Pagination onChange:', newPage, newPageSize)
            setPage(newPage)
            setPageSize(newPageSize)
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
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="账号"
            name="account"
            rules={[{ required: true, message: '请输入账号' }]}
          >
            <Input placeholder="请输入账号" />
          </Form.Item>
          <Form.Item label="密码" name="password">
            <Input.Password placeholder="请输入密码" />
          </Form.Item>
          <Form.Item
            label="账号类型"
            name="account_type"
            rules={[{ required: true, message: '请选择账号类型' }]}
          >
            <Select placeholder="请选择账号类型">
              <Select.Option value={AccountType.EMAIL}>邮箱</Select.Option>
              <Select.Option value={AccountType.WALLET}>钱包</Select.Option>
              <Select.Option value={AccountType.X}>X</Select.Option>
              <Select.Option value={AccountType.OTHER1}>其他1</Select.Option>
              <Select.Option value={AccountType.OTHER2}>其他2</Select.Option>
            </Select>
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
          <Form.Item
            label="项目"
            name="project_id"
            rules={[{ required: true, message: '请选择项目' }]}
          >
            <Select
              placeholder="请选择项目"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={projectList.map(project => ({
                label: project.name,
                value: project.id,
              }))}
            />
          </Form.Item>
          <Form.Item
            label={
              <span>
                余额
                <Tooltip title="可选，不填默认为0。更新余额时会自动计算变动和记录历史">
                  <span style={{ marginLeft: 4, color: '#999' }}>(?)</span>
                </Tooltip>
              </span>
            }
            name="balance"
          >
            <InputNumber
              placeholder="请输入余额（可选）"
              style={{ width: '100%' }}
              min={0}
              precision={2}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 统计分析弹窗 */}
      <Modal
        title={`统计分析 - ${projectList.find(p => p.id === searchProjectId)?.name || '未知项目'}`}
        open={statsModalVisible}
        onCancel={() => setStatsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setStatsModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {statsData ? (
          <div>
            <Card style={{ marginBottom: 16 }}>
              <Statistic 
                title="统计账号数量" 
                value={statsData.total_count} 
                suffix="个"
              />
            </Card>

            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={24}>
                <Card title="当前余额统计" bordered>
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="最高分"
                        value={statsData.balance.max.toFixed(2)}
                        valueStyle={{ color: '#3f8600' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="最低分"
                        value={statsData.balance.min.toFixed(2)}
                        valueStyle={{ color: '#cf1322' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="平均分"
                        value={statsData.balance.avg.toFixed(2)}
                        valueStyle={{ color: '#1890ff' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="总分"
                        value={statsData.balance.sum.toFixed(2)}
                        valueStyle={{ color: '#722ed1' }}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={24}>
                <Card title="变动统计" bordered>
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="变动最高分"
                        value={statsData.variable.max.toFixed(2)}
                        valueStyle={{ color: '#3f8600' }}
                        prefix={statsData.variable.max > 0 ? '+' : ''}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="变动最低分"
                        value={statsData.variable.min.toFixed(2)}
                        valueStyle={{ color: '#cf1322' }}
                        prefix={statsData.variable.min > 0 ? '+' : ''}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="变动平均分"
                        value={statsData.variable.avg.toFixed(2)}
                        valueStyle={{ color: '#1890ff' }}
                        prefix={statsData.variable.avg > 0 ? '+' : ''}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="变动总分"
                        value={statsData.variable.sum.toFixed(2)}
                        valueStyle={{ 
                          color: statsData.variable.sum > 0 ? '#3f8600' : 
                                 statsData.variable.sum < 0 ? '#cf1322' : '#666'
                        }}
                        prefix={statsData.variable.sum > 0 ? '+' : ''}
                      />
                    </Col>
                  </Row>
                </Card>
              </Col>
            </Row>

            <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
              <p style={{ margin: 0, color: '#666', fontSize: 12 }}>
                <strong>说明：</strong>
                <br />
                • 当前余额：账号的当前余额分数
                <br />
                • 变动：相比前一天的余额变化（正数表示增加，负数表示减少）
                <br />
                • 总分：所有账号的余额/变动总和
                <br />
                • 统计基于当前筛选条件下的所有账号数据（不受分页限制）
              </p>
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>加载中...</p>
          </div>
        )}
      </Modal>

      <Modal
        title="历史余额"
        open={historyModalVisible}
        onCancel={() => setHistoryModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setHistoryModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={600}
      >
        {currentHistoryAccount && (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="账号">{currentHistoryAccount.account}</Descriptions.Item>
              <Descriptions.Item label="项目">{currentHistoryAccount.project?.name || '-'}</Descriptions.Item>
              <Descriptions.Item label="当前余额">
                {Number(currentHistoryAccount.balance).toFixed(2)}
              </Descriptions.Item>
              <Descriptions.Item label="变动余额">
                <span style={{ 
                  color: Number(currentHistoryAccount.variable) > 0 ? 'green' : 
                         Number(currentHistoryAccount.variable) < 0 ? 'red' : 'default' 
                }}>
                  {Number(currentHistoryAccount.variable) > 0 ? '+' : ''}
                  {Number(currentHistoryAccount.variable).toFixed(2)}
                </span>
              </Descriptions.Item>
            </Descriptions>
            
            <div style={{ marginTop: 16 }}>
              <h4>历史记录（最近7天）</h4>
              {currentHistoryAccount.balance_history && 
               Object.keys(currentHistoryAccount.balance_history).length > 0 ? (
                <Table
                  dataSource={Object.entries(currentHistoryAccount.balance_history)
                    .sort(([dateA], [dateB]) => dateB.localeCompare(dateA))
                    .map(([date, balance], index) => ({
                      key: index,
                      date,
                      balance: Number(balance).toFixed(2),
                    }))}
                  columns={[
                    {
                      title: '日期',
                      dataIndex: 'date',
                      key: 'date',
                    },
                    {
                      title: '余额',
                      dataIndex: 'balance',
                      key: 'balance',
                      align: 'right' as const,
                    },
                  ]}
                  pagination={false}
                  size="small"
                />
              ) : (
                <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                  暂无历史记录
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ProjectAccountList
