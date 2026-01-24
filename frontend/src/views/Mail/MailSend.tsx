import { useState } from 'react'
import { Form, Input, Button, Select, Card, App, Space } from 'antd'
import { SendOutlined, MailOutlined } from '@ant-design/icons'
import { sendOutlookEmail } from '@/api/mail'

const { TextArea } = Input
const { Option } = Select

export default function MailSend() {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [contentType, setContentType] = useState<'Text' | 'HTML'>('Text')

  const handleSend = async (values: any) => {
    setLoading(true)
    try {
      const res = await sendOutlookEmail({
        email: values.email,
        to_email: values.to_email,
        subject: values.subject,
        content: values.content,
        content_type: contentType,
      })
      
      if (res.code === 1) {
        message.success('邮件发送成功')
        form.resetFields()
      } else {
        message.error(res.message || '邮件发送失败')
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '邮件发送失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card 
        title={
          <Space>
            <MailOutlined />
            <span>发送邮件</span>
          </Space>
        }
        style={{ maxWidth: 1200, margin: '0 auto' }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSend}
          autoComplete="off"
        >
          <Form.Item
            label="发件人邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入发件人邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              placeholder="请输入发件人邮箱地址"
              prefix={<MailOutlined />}
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="收件人邮箱"
            name="to_email"
            rules={[
              { required: true, message: '请输入收件人邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              placeholder="请输入收件人邮箱地址"
              prefix={<MailOutlined />}
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="邮件主题"
            name="subject"
            rules={[{ required: true, message: '请输入邮件主题' }]}
          >
            <Input
              placeholder="请输入邮件主题"
              size="large"
            />
          </Form.Item>

          <Form.Item
            label="内容格式"
            required
          >
            <Select
              value={contentType}
              onChange={setContentType}
              size="large"
              style={{ width: 200 }}
            >
              <Option value="Text">纯文本 (Text)</Option>
              <Option value="HTML">HTML格式</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label={
              <Space>
                <span>邮件内容</span>
                {contentType === 'HTML' && (
                  <span style={{ color: '#999', fontSize: '12px' }}>
                    (支持HTML标签)
                  </span>
                )}
              </Space>
            }
            name="content"
            rules={[{ required: true, message: '请输入邮件内容' }]}
          >
            <TextArea
              placeholder={
                contentType === 'Text'
                  ? '请输入邮件内容'
                  : '请输入HTML格式的邮件内容，例如：<h1>标题</h1><p>段落内容</p>'
              }
              rows={12}
              showCount
              maxLength={50000}
            />
          </Form.Item>

          {contentType === 'HTML' && (
            <div style={{ 
              marginBottom: 24, 
              padding: 12, 
              background: '#f5f5f5', 
              borderRadius: 4,
              fontSize: '12px',
              color: '#666'
            }}>
              <div style={{ marginBottom: 8, fontWeight: 'bold' }}>HTML 格式示例：</div>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
{`<html>
  <body>
    <h1>欢迎</h1>
    <p>这是一封HTML格式的邮件。</p>
    <ul>
      <li>支持列表</li>
      <li>支持样式</li>
    </ul>
  </body>
</html>`}
              </pre>
            </div>
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                loading={loading}
                size="large"
              >
                发送邮件
              </Button>
              <Button
                onClick={() => form.resetFields()}
                size="large"
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
