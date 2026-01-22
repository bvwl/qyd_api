import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import './index.less'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const login = useUserStore((state) => state.login)

  const onFinish = async (values: { email: string; password: string }) => {
    try {
      setLoading(true)
      await login(values.email, values.password)
      message.success('登录成功')
      navigate('/')
    } catch (error: any) {
      // 根据错误状态码显示不同的错误信息
      if (error.response) {
        const { status, data } = error.response
        switch (status) {
          case 400:
            message.error(data?.detail || '邮箱或密码错误')
            break
          case 401:
            message.error('登录失败，请检查邮箱和密码')
            break
          case 403:
            message.error('账户已被禁用，请联系管理员')
            break
          case 500:
            message.error('服务器错误，请稍后重试')
            break
          default:
            message.error(data?.detail || '登录失败，请稍后重试')
            break
        }
      } else if (error.request) {
        message.error('网络连接失败，请检查网络')
      } else {
        message.error('登录失败，请稍后重试')
      }
    } finally {
      setLoading(false)
    }
  }

  // 自定义邮箱验证规则，允许zhiyu账户通过
  const validateEmail = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入邮箱'))
    }
    // 允许zhiyu账户通过验证
    if (value === 'zhiyu') {
      return Promise.resolve()
    }
    // 其他账户需要符合邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return Promise.reject(new Error('请输入有效的邮箱地址'))
    }
    return Promise.resolve()
  }

  return (
    <div className="login-container">
      <Card className="login-card" title="QYD 项目管理系统">
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { validator: validateEmail },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
