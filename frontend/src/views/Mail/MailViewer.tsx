import { useState, useMemo } from 'react'
import { Button, Table, Modal, Input, Space, Tag, message, Spin, Empty, Tooltip } from 'antd'
import { ReloadOutlined, SearchOutlined, EyeOutlined, MailOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getInboxMessages, getMessageDetail } from '@/api/mail'
import { formatDateTime } from '@/utils/format'
import DOMPurify from 'dompurify'

interface EmailMessage {
  id: string
  subject: string
  from: string
  from_name: string
  received_time: string
  body_preview: string
  has_attachments: boolean
  is_read: boolean
}

interface EmailDetail {
  id: string
  subject: string
  from: string
  from_name: string
  to: string[]
  cc: string[]
  received_time: string
  body_type: string
  body_content: string
  has_attachments: boolean
  is_read: boolean
}

interface CacheData {
  messages: EmailMessage[]
  timestamp: number
  email: string
}

const CACHE_KEY = 'email_inbox_cache'
const CACHE_DURATION = 10 * 60 * 1000 // 10分钟

export default function MailViewer() {
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<EmailMessage[]>([])
  const [currentEmail, setCurrentEmail] = useState<string>('')
  const [searchText, setSearchText] = useState('')
  const [searchType, setSearchType] = useState<'text' | 'regex'>('text')
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [currentDetail, setCurrentDetail] = useState<EmailDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
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
      const res = await getInboxMessages({ email, top: 50 })
      if (res.code === 1) {
        setMessages(res.data)
        setCurrentEmail(email)
        saveToCache(email, res.data)
        message.success(`成功获取 ${res.count} 封邮件`)
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
  const handleViewDetail = async (messageId: string) => {
    if (!currentEmail) return

    setDetailModalVisible(true)
    setDetailLoading(true)
    setCurrentDetail(null)

    try {
      const res = await getMessageDetail(messageId, currentEmail)
      if (res.code === 1) {
        setCurrentDetail(res.data)
      } else {
        message.error(res.message || '获取邮件详情失败')
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取邮件详情失败')
    } finally {
      setDetailLoading(false)
    }
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
            regex.test(msg.subject) ||
            regex.test(msg.from) ||
            regex.test(msg.from_name) ||
            regex.test(msg.body_preview)
        )
      } else {
        // 文本搜索
        const lowerSearch = searchText.toLowerCase()
        return messages.filter(
          (msg) =>
            msg.subject.toLowerCase().includes(lowerSearch) ||
            msg.from.toLowerCase().includes(lowerSearch) ||
            msg.from_name.toLowerCase().includes(lowerSearch) ||
            msg.body_preview.toLowerCase().includes(lowerSearch)
        )
      }
    } catch (error) {
      message.error('正则表达式格式错误')
      return messages
    }
  }, [messages, searchText, searchType])

  const columns: ColumnsType<EmailMessage> = [
    {
      title: '状态',
      dataIndex: 'is_read',
      key: 'is_read',
      width: 80,
      render: (isRead: boolean) => (
        <Tag color={isRead ? 'default' : 'blue'}>{isRead ? '已读' : '未读'}</Tag>
      ),
    },
    {
      title: '主题',
      dataIndex: 'subject',
      key: 'subject',
      ellipsis: true,
      render: (text: string) => text || '(无主题)',
    },
    {
      title: '发件人',
      dataIndex: 'from_name',
      key: 'from_name',
      width: 200,
      render: (name: string, record: EmailMessage) => (
        <Tooltip title={record.from}>
          <span>{name || record.from}</span>
        </Tooltip>
      ),
    },
    {
      title: '预览',
      dataIndex: 'body_preview',
      key: 'body_preview',
      ellipsis: true,
      render: (text: string) => (
        <span style={{ color: '#999' }}>{text || '(无内容)'}</span>
      ),
    },
    {
      title: '附件',
      dataIndex: 'has_attachments',
      key: 'has_attachments',
      width: 80,
      render: (hasAttachments: boolean) =>
        hasAttachments ? <Tag color="orange">有</Tag> : <Tag>无</Tag>,
    },
    {
      title: '接收时间',
      dataIndex: 'received_time',
      key: 'received_time',
      width: 180,
      render: (time: string) => formatDateTime(time),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_: any, record: EmailMessage) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetail(record.id)}
        >
          查看
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
        rowKey="id"
        loading={loading}
        scroll={{ x: 1200 }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
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
        width={900}
        style={{ top: 20 }}
      >
        {detailLoading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
          </div>
        ) : currentDetail ? (
          <div>
            <div style={{ marginBottom: 16 }}>
              <p>
                <strong>主题：</strong>
                {currentDetail.subject || '(无主题)'}
              </p>
              <p>
                <strong>发件人：</strong>
                {currentDetail.from_name} &lt;{currentDetail.from}&gt;
              </p>
              <p>
                <strong>收件人：</strong>
                {currentDetail.to.join(', ')}
              </p>
              {currentDetail.cc.length > 0 && (
                <p>
                  <strong>抄送：</strong>
                  {currentDetail.cc.join(', ')}
                </p>
              )}
              <p>
                <strong>时间：</strong>
                {formatDateTime(currentDetail.received_time)}
              </p>
              <p>
                <strong>附件：</strong>
                {currentDetail.has_attachments ? (
                  <Tag color="orange">有附件</Tag>
                ) : (
                  <Tag>无附件</Tag>
                )}
              </p>
            </div>
            <div
              style={{
                border: '1px solid #d9d9d9',
                borderRadius: 4,
                padding: 16,
                maxHeight: 500,
                overflow: 'auto',
                backgroundColor: '#fafafa',
              }}
            >
              {currentDetail.body_type === 'HTML' ? (
                <div
                  dangerouslySetInnerHTML={{
                    __html: DOMPurify.sanitize(currentDetail.body_content),
                  }}
                />
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                  {currentDetail.body_content}
                </pre>
              )}
            </div>
          </div>
        ) : (
          <Empty description="加载失败" />
        )}
      </Modal>
    </div>
  )
}
