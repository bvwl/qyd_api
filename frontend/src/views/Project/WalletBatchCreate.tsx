import { useState, useEffect, useRef } from 'react'
import { 
  Card, 
  Form, 
  Input, 
  InputNumber, 
  Select, 
  Button, 
  Table, 
  Space, 
  App, 
  Typography,
  Alert,
  Statistic,
  Row,
  Col,
  Tooltip
} from 'antd'
import { 
  PlusOutlined, 
  DownloadOutlined, 
  EyeOutlined, 
  EyeInvisibleOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined
} from '@ant-design/icons'
import type { ProjectWallet } from '@/types'
import { batchCreateWallet } from '@/api/project'

const { Title, Text } = Typography
const { TextArea } = Input

interface WalletWithVisible extends ProjectWallet {
  visible?: boolean
}

const WalletBatchCreate = () => {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [wallets, setWallets] = useState<WalletWithVisible[]>([])
  const [countdown, setCountdown] = useState(0)
  const [visibleKeys, setVisibleKeys] = useState<Record<string, boolean>>({})
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // 倒计时效果
  useEffect(() => {
    if (countdown > 0) {
      timerRef.current = setTimeout(() => {
        setCountdown(countdown - 1)
      }, 1000)
    } else if (countdown === 0 && wallets.length > 0) {
      message.warning('临时数据已过期')
      setWallets([])
    }

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [countdown, wallets.length, message])

  // 清理定时器
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
      }
    }
  }, [])

  const handleCreate = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)

      const res = await batchCreateWallet({
        project_name: values.project_name,
        chain: values.chain,
        count: values.count,
        remark: values.remark
      })

      message.success(`成功创建 ${res.count} 个钱包`)
      
      // 设置钱包数据和10分钟倒计时
      setWallets(res.items.map(item => ({ ...item, visible: false })))
      setCountdown(600) // 10分钟 = 600秒

    } catch (error: any) {
      console.error('创建失败:', error)
      message.error(error.response?.data?.detail || '创建失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (wallets.length === 0) {
      message.warning('没有可下载的数据')
      return
    }

    try {
      // 动态导入xlsx
      const XLSX = await import('xlsx')
      
      // 准备导出数据
      const exportData = wallets.map((wallet, index) => ({
        '序号': index + 1,
        '链': wallet.chain,
        '公钥': wallet.public_key,
        '私钥': wallet.private_key,
        '助记词': wallet.mnemonic || '-',
        '备注': wallet.remark || '-',
        '创建时间': wallet.create_time
      }))

      // 创建工作簿
      const ws = XLSX.utils.json_to_sheet(exportData)
      const wb = XLSX.utils.book_new()
      XLSX.utils.book_append_sheet(wb, ws, '钱包列表')

      // 设置列宽
      ws['!cols'] = [
        { wch: 8 },  // 序号
        { wch: 10 }, // 链
        { wch: 50 }, // 公钥
        { wch: 70 }, // 私钥
        { wch: 80 }, // 助记词
        { wch: 20 }, // 备注
        { wch: 20 }  // 创建时间
      ]

      // 下载文件
      const fileName = `钱包_${form.getFieldValue('chain')}_${new Date().getTime()}.xlsx`
      XLSX.writeFile(wb, fileName)

      message.success('下载成功')
    } catch (error) {
      console.error('下载失败:', error)
      message.error('下载失败，请确保已安装xlsx依赖')
    }
  }

  const toggleVisible = (id: string, field: string) => {
    const key = `${id}-${field}`
    setVisibleKeys(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const renderSensitiveField = (value: string, id: string, field: string) => {
    if (!value) return '-'
    
    const key = `${id}-${field}`
    const isVisible = visibleKeys[key]
    
    return (
      <Space>
        <Text 
          copyable={{ text: value }}
          style={{ 
            fontFamily: 'monospace',
            maxWidth: field === 'mnemonic' ? 300 : 200,
            display: 'inline-block'
          }}
          ellipsis
        >
          {isVisible ? value : '••••••••••••'}
        </Text>
        <Button
          type="link"
          size="small"
          icon={isVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
          onClick={() => toggleVisible(id, field)}
        />
      </Space>
    )
  }

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  const columns = [
    {
      title: '序号',
      key: 'index',
      width: 80,
      render: (_: any, __: any, index: number) => index + 1
    },
    {
      title: '链',
      dataIndex: 'chain',
      key: 'chain',
      width: 100
    },
    {
      title: '公钥',
      dataIndex: 'public_key',
      key: 'public_key',
      ellipsis: true,
      render: (text: string, record: WalletWithVisible) => 
        renderSensitiveField(text, record.id, 'public')
    },
    {
      title: '私钥',
      dataIndex: 'private_key',
      key: 'private_key',
      ellipsis: true,
      render: (text: string, record: WalletWithVisible) => 
        renderSensitiveField(text, record.id, 'private')
    },
    {
      title: '助记词',
      dataIndex: 'mnemonic',
      key: 'mnemonic',
      ellipsis: true,
      render: (text: string, record: WalletWithVisible) => 
        text ? renderSensitiveField(text, record.id, 'mnemonic') : '-'
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 180
    }
  ]

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={4}>批量创建钱包</Title>
        <Alert
          message="功能说明"
          description={
            <div>
              <p>1. 支持批量创建 ETH 和 Solana 钱包</p>
              <p>2. 私钥和助记词使用 AES 加密存储到数据库</p>
              <p>3. 创建后的钱包会<strong>自动保存到数据库</strong>，同时在前端临时显示 10 分钟</p>
              <p>4. 可以下载为 Excel 文件（包含明文私钥和助记词），请妥善保管</p>
              <p>5. 10分钟后前端临时数据会清除，但数据库中的钱包仍然保留</p>
              <p>6. 所有登录用户均可使用此功能</p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form
          form={form}
          layout="vertical"
          initialValues={{
            chain: 'ETH',
            count: 10
          }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="项目名称"
                name="project_name"
                rules={[{ required: true, message: '请输入项目名称' }]}
                tooltip="用于加密私钥和助记词，请妥善保管"
              >
                <Input placeholder="请输入项目名称" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="链类型"
                name="chain"
                rules={[{ required: true, message: '请选择链类型' }]}
              >
                <Select>
                  <Select.Option value="ETH">ETH (以太坊)</Select.Option>
                  <Select.Option value="SOL">SOL (Solana)</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="创建数量"
                name="count"
                rules={[
                  { required: true, message: '请输入创建数量' },
                  { type: 'number', min: 1, max: 100, message: '数量范围：1-100' }
                ]}
              >
                <InputNumber 
                  min={1} 
                  max={100} 
                  style={{ width: '100%' }}
                  placeholder="1-100"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            label="备注"
            name="remark"
          >
            <TextArea 
              placeholder="请输入备注信息（可选）" 
              rows={2}
              maxLength={200}
              showCount
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleCreate}
              loading={loading}
              size="large"
            >
              批量创建钱包
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {wallets.length > 0 && (
        <Card style={{ marginTop: 24 }}>
          <div style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic 
                  title="创建数量" 
                  value={wallets.length} 
                  suffix="个"
                  prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="剩余时间" 
                  value={formatTime(countdown)}
                  prefix={<ClockCircleOutlined style={{ color: countdown < 60 ? '#ff4d4f' : '#1890ff' }} />}
                  valueStyle={{ color: countdown < 60 ? '#ff4d4f' : undefined }}
                />
              </Col>
              <Col span={12} style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                <Space>
                  <Tooltip title="下载为 Excel 文件（包含明文私钥和助记词）">
                    <Button
                      type="primary"
                      icon={<DownloadOutlined />}
                      onClick={handleDownload}
                      size="large"
                    >
                      下载钱包
                    </Button>
                  </Tooltip>
                </Space>
              </Col>
            </Row>
          </div>

          {countdown < 60 && (
            <Alert
              message="提示"
              description="前端临时数据即将过期，请尽快下载Excel文件！数据库中的钱包不受影响。"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
          )}

          <Table
            columns={columns}
            dataSource={wallets}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 个钱包`
            }}
            scroll={{ x: 1200 }}
          />
        </Card>
      )}
    </div>
  )
}

export default WalletBatchCreate
