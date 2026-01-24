import { useState, useMemo } from 'react'
import { Button, Table, Modal, Input, Space, Tag, Empty, App, InputNumber } from 'antd'
import { ReloadOutlined, SearchOutlined, EyeOutlined, MailOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getInboxMessages } from '@/api/mail'
import DOMPurify from 'dompurify'

interface EmailMessage {
  from_email: string
  title: string
  content: string
  _key?: string  // 添加内部使用的唯一键
}

interface EmailDetail {
  subject: string
  from: string
  content: string
}

interface CacheData {
  messages: EmailMessage[]
  timestamp: number
  email: string
}

const CACHE_KEY = 'email_inbox_cache'
const CACHE_DURATION = 10 * 60 * 1000 // 10分钟

export default function MailViewer() {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<EmailMessage[]>([])
  const [currentEmail, setCurrentEmail] = useState<string>('')
  const [topCount, setTopCount] = useState<number>(10)  // 添加查询数量状态
  const [searchText, setSearchText] = useState('')
  const [searchType, setSearchType] = useState<'text' | 'regex'>('text')
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [currentDetail, setCurrentDetail] = useState<EmailDetail | null>(null)
  const [cacheInfo, setCacheInfo] = useState<string>('')

  // 从localStorage加载缓存
  const loadFromCache = (email: string): EmailMessage[] | null => {
    try {
      const cached = localStorage.getItem(CACHE_KEY)
      if (!cached) return null

      const cacheData: CacheData = JSON.parse(cached)
      const now = Date.now()

      // 检查缓存是否过期或邮箱不匹配
      if (
        cacheData.email !== email ||
        now - cacheData.timestamp > CACHE_DURATION
      ) {
        localStorage.removeItem(CACHE_KEY)
        return null
      }

      // 计算剩余时间
      const remainingTime = Math.ceil((CACHE_DURATION - (now - cacheData.timestamp)) / 1000 / 60)
      setCacheInfo(`使用缓存数据（剩余 ${remainingTime} 分钟）`)

      return cacheData.messages
    } catch (error) {
      console.error('加载缓存失败:', error)
      return null
    }
  }

  // 保存到localStorage
  const saveToCache = (email: string, messages: EmailMessage[]) => {
    try {
      const cacheData: CacheData = {
        messages,
        timestamp: Date.now(),
        email,
      }
      localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
      setCacheInfo('数据已缓存（10分钟有效）')
    } catch (error) {
      console.error('保存缓存失败:', error)
    }
  }

  // 清除缓存
  const clearCache = () => {
    localStorage.removeItem(CACHE_KEY)
    setCacheInfo('')
  }

  // 获取邮件列表
  const fetchMessages = async (email: string, useCache: boolean = true) => {
    if (!email) {
      message.warning('请输入邮箱地址')
      return
    }

    // 尝试从缓存加载
    if (useCache) {
      const cached = loadFromCache(email)
      if (cached) {
        setMessages(cached)
        setCurrentEmail(email)
        return
      }
    }

    setLoading(true)
    setCacheInfo('')
    try {
      const res = await getInboxMessages({ email, top: topCount })  // 使用 topCount 状态
      if (res.code === 1 && res.data && Array.isArray(res.data)) {
        // 为每条邮件添加唯一的 key
        const messagesWithKey = res.data.map((msg, index) => ({
          ...msg,
          _key: `${msg.from_email}-${msg.title}-${index}-${Date.now()}`
        }))
        setMessages(messagesWithKey)
        setCurrentEmail(email)
        saveToCache(email, messagesWithKey)
        message.success(`成功获取 ${res.data.length} 封邮件`)
      } else {
        message.error(res.message || '获取邮件失败')
        setMessages([])
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取邮件失败')
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  // 刷新邮件列表（强制从服务器获取）
  const handleRefresh = () => {
    if (!currentEmail) {
      message.warning('请先输入邮箱地址')
      return
    }
    clearCache()
    fetchMessages(currentEmail, false)
  }

  // 查看邮件详情
  const handleViewDetail = (message: EmailMessage) => {
    setDetailModalVisible(true)
    setCurrentDetail({
      subject: message.title || '(无主题)',
      from: message.from_email || '',
      content: message.content || '',
    })
  }

  // 搜索过滤
  const filteredMessages = useMemo(() => {
    if (!searchText) return messages

    try {
      if (searchType === 'regex') {
        // 正则表达式搜索
        const regex = new RegExp(searchText, 'i')
        return messages.filter(
          (msg) =>
            regex.test(msg.title || '') ||
            regex.test(msg.from_email || '') ||
            regex.test(msg.content || '')
        )
      } else {
        // 文本搜索
        const lowerSearch = searchText.toLowerCase()
        return messages.filter(
          (msg) =>
            (msg.title || '').toLowerCase().includes(lowerSearch) ||
            (msg.from_email || '').toLowerCase().includes(lowerSearch) ||
            (msg.content || '').toLowerCase().includes(lowerSearch)
        )
      }
    } catch (error) {
      message.error('正则表达式格式错误')
      return messages
    }
  }, [messages, searchText, searchType])

  const columns: ColumnsType<EmailMessage> = [
    {
      title: '主题',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      ellipsis: true,
      render: (text: string) => text || '(无主题)',
    },
    {
      title: '发件人',
      dataIndex: 'from_email',
      key: 'from_email',
      width: 250,
      ellipsis: true,
    },
    {
      title: '内容预览',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (text: string) => {
        // 移除 HTML 标签，只显示纯文本预览
        const plainText = text?.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim() || ''
        const preview = plainText.substring(0, 80)
        const displayText = preview || '(无内容)'
        const suffix = plainText.length > 80 ? '...' : ''
        return (
          <span style={{ color: '#999' }}>
            {displayText}{suffix}
          </span>
        )
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_: any, record: EmailMessage) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record)}
        >
          查看详情
        </Button>
      ),
    },
  ]

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 16 }}>
        <Space wrap style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space wrap>
            <Input
              placeholder="输入邮箱地址"
              prefix={<MailOutlined />}
              value={currentEmail}
              onChange={(e) => setCurrentEmail(e.target.value)}
              onPressEnter={() => fetchMessages(currentEmail)}
              style={{ width: 300 }}
            />
            <Space.Compact>
              <Button disabled style={{ cursor: 'default' }}>查询</Button>
              <InputNumber
                min={1}
                max={100}
                value={topCount}
                onChange={(value) => setTopCount(value || 10)}
                style={{ width: 60 }}
              />
              <Button disabled style={{ cursor: 'default' }}>条</Button>
            </Space.Compact>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={() => fetchMessages(currentEmail)}
              loading={loading}
            >
              查看邮件
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              disabled={!currentEmail}
            >
              刷新
            </Button>
            {cacheInfo && (
              <Tag color="green" style={{ marginLeft: 8 }}>
                {cacheInfo}
              </Tag>
            )}
          </Space>
          <Space>
            <Input
              placeholder={searchType === 'regex' ? '输入正则表达式' : '搜索邮件内容'}
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
            />
            <Button
              type={searchType === 'text' ? 'default' : 'primary'}
              onClick={() => setSearchType(searchType === 'text' ? 'regex' : 'text')}
            >
              {searchType === 'text' ? '文本搜索' : '正则搜索'}
            </Button>
          </Space>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={filteredMessages}
        rowKey="_key"
        loading={loading}
        scroll={{ x: 1000 }}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50'],
          showTotal: (total) => `共 ${total} 封邮件`,
        }}
        locale={{
          emptyText: currentEmail ? (
            <Empty description="暂无邮件" />
          ) : (
            <Empty description="请输入邮箱地址并点击查看邮件" />
          ),
        }}
      />

      {/* 邮件详情弹窗 */}
      <Modal
        title="邮件详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={1000}
        style={{ top: 20 }}
      >
        {currentDetail ? (
          <div>
            <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
              <p style={{ marginBottom: 8 }}>
                <strong>主题：</strong>
                <span style={{ marginLeft: 8 }}>{currentDetail.subject}</span>
              </p>
              <p style={{ marginBottom: 0 }}>
                <strong>发件人：</strong>
                <span style={{ marginLeft: 8 }}>{currentDetail.from}</span>
              </p>
            </div>
            <div
              style={{
                border: '1px solid #d9d9d9',
                borderRadius: 4,
                padding: 20,
                maxHeight: 600,
                overflow: 'auto',
                backgroundColor: '#fff',
              }}
            >
              <div
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(currentDetail.content, {
                    ADD_TAGS: ['style'],
                    ADD_ATTR: ['target', 'style'],
                  }),
                }}
                style={{
                  wordBreak: 'break-word',
                  lineHeight: '1.6',
                }}
              />
            </div>
          </div>
        ) : (
          <Empty description="无数据" />
        )}
      </Modal>
    </div>
  )
}
