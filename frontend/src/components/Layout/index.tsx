import { useState, useEffect } from 'react'
import { Layout, Menu, Avatar, Dropdown, theme, Modal, Form, Input, message } from 'antd'
import {
  DashboardOutlined,
  UserOutlined,
  ProjectOutlined,
  CloudServerOutlined,
  MailOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  ApiOutlined,
  EditOutlined,
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import { updateUser, getUserRoutes } from '@/api/user'
import type { MenuProps } from 'antd'

const { Header, Sider, Content } = Layout

// 图标映射
const iconMap: Record<string, any> = {
  'DashboardOutlined': <DashboardOutlined />,
  'UserOutlined': <UserOutlined />,
  'ProjectOutlined': <ProjectOutlined />,
  'CloudServerOutlined': <CloudServerOutlined />,
  'MailOutlined': <MailOutlined />,
  'ApiOutlined': <ApiOutlined />,
}

// 默认菜单配置（用于管理员或路由加载失败时）
const DEFAULT_MENU_ITEMS: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '仪表盘',
  },
  {
    key: '/user',
    icon: <UserOutlined />,
    label: '用户管理',
    children: [
      { key: '/user/list', label: '用户列表' },
      { key: '/user/role', label: '角色管理' },
      { key: '/user/route', label: '路由管理' },
      { key: '/user/permission', label: '权限管理' },
      { key: '/user/token', label: 'Token管理' },
      { key: '/user/log', label: '操作日志' },
    ],
  },
  {
    key: '/project',
    icon: <ProjectOutlined />,
    label: '项目管理',
    children: [
      { key: '/project/list', label: '项目列表' },
      { key: '/project/account', label: '项目账号' },
      { key: '/project/wallet', label: '项目钱包' },
      { key: '/project/wallet/batch-create', label: '批量创建钱包' },
    ],
  },
  {
    key: '/server',
    icon: <CloudServerOutlined />,
    label: '服务器管理',
    children: [
      { key: '/server/country', label: '国家管理' },
      { key: '/server/group', label: '分组管理' },
      { key: '/server/list', label: '服务器列表' },
      { key: '/server/account', label: '服务器账号' },
    ],
  },
  {
    key: '/xui',
    icon: <CloudServerOutlined />,
    label: 'XUI管理',
    children: [
      { key: '/xui/server', label: '服务器列表' },
      { key: '/xui/inbound', label: '入站列表' },
      { key: '/xui/account', label: '账号管理' },
      { key: '/xui/log', label: '操作日志' },
    ],
  },
  {
    key: '/mail',
    icon: <MailOutlined />,
    label: '邮箱管理',
    children: [
      { key: '/mail/list', label: '邮箱列表' },
      { key: '/mail/viewer', label: '邮件查看' },
      { key: '/mail/send', label: '发送邮件' },
    ],
  },
  {
    key: '/api-docs',
    icon: <ApiOutlined />,
    label: 'API文档',
    children: [
      { key: '/api-docs/user', label: '用户列表' },
      { key: '/api-docs/user-create', label: '创建用户' },
      { key: '/api-docs/role', label: '角色列表' },
      { key: '/api-docs/project', label: '项目列表' },
      { key: '/api-docs/project-account', label: '项目账号' },
      { key: '/api-docs/server', label: '服务器列表' },
      { key: '/api-docs/mail', label: '邮箱列表' },
    ],
  },
]

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const [profileModalVisible, setProfileModalVisible] = useState(false)
  const [menuItems, setMenuItems] = useState<MenuProps['items']>([])
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const location = useLocation()
  const { userInfo, logout, setUserInfo } = useUserStore()
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  // 加载用户路由权限
  useEffect(() => {
    if (userInfo) {
      loadUserRoutes()
    }
  }, [userInfo])

  const loadUserRoutes = async () => {
    try {
      // 检查用户是否是管理员
      const isAdmin = userInfo?.roles?.some((role: any) => role.code === 'ADMIN')
      
      // 如果用户是管理员，直接使用默认菜单（包含所有功能）
      if (isAdmin) {
        console.log('管理员用户，使用默认完整菜单')
        setMenuItems(DEFAULT_MENU_ITEMS)
        return
      }
      
      // 非管理员从后端获取路由权限
      const routes = await getUserRoutes()
      const items = buildMenuItems(routes)
      setMenuItems(items)
    } catch (error) {
      console.error('加载菜单失败:', error)
      
      // 如果加载失败且用户是管理员，使用默认菜单
      const isAdmin = userInfo?.roles?.some((role: any) => role.code === 'ADMIN')
      if (isAdmin) {
        console.log('管理员用户加载失败，使用默认菜单')
        setMenuItems(DEFAULT_MENU_ITEMS)
      } else {
        // 非管理员加载失败，只显示仪表盘
        setMenuItems([
          {
            key: '/dashboard',
            icon: <DashboardOutlined />,
            label: '仪表盘',
          }
        ])
      }
    }
  }

  const buildMenuItems = (routes: any[]): MenuProps['items'] => {
    return routes
      .filter(route => !route.is_hidden && route.route_type === 1) // 只显示菜单类型且未隐藏的
      .map(route => {
        const item: any = {
          key: route.path,
          label: route.title,
          icon: route.icon ? iconMap[route.icon] : null,
        }
        
        if (route.children && route.children.length > 0) {
          item.children = buildMenuItems(route.children)
        }
        
        return item
      })
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <EditOutlined />,
      label: '修改信息',
      onClick: () => {
        setProfileModalVisible(true)
        form.setFieldsValue({
          nickname: userInfo?.nickname,
          email: userInfo?.email,
        })
      },
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout()
        navigate('/login')
      },
    },
  ]

  const handleUpdateProfile = async () => {
    try {
      const values = await form.validateFields()
      if (!userInfo?.id) return

      // 只传递修改过的字段
      const updateData: any = {}
      
      // 检查昵称是否修改
      if (values.nickname && values.nickname !== userInfo.nickname) {
        updateData.nickname = values.nickname
      }
      
      // 检查邮箱是否修改
      if (values.email && values.email !== userInfo.email) {
        updateData.email = values.email
      }
      
      // 如果提供了新密码，则更新密码
      if (values.password) {
        updateData.password = values.password
      }

      // 如果没有任何修改，提示用户
      if (Object.keys(updateData).length === 0) {
        message.info('没有修改任何信息')
        return
      }

      await updateUser(userInfo.id, updateData)
      
      // 更新本地用户信息
      const updatedUserInfo = { ...userInfo }
      if (updateData.nickname) updatedUserInfo.nickname = values.nickname
      if (updateData.email) updatedUserInfo.email = values.email
      setUserInfo(updatedUserInfo)

      message.success('信息更新成功')
      setProfileModalVisible(false)
      form.resetFields()
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return
      }
      message.error('信息更新失败')
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontSize: 20,
            fontWeight: 'bold',
          }}
        >
          {collapsed ? 'QYD' : 'QYD 管理系统'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div
            style={{ fontSize: 20, cursor: 'pointer' }}
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          </div>
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar icon={<UserOutlined />} src={userInfo?.avatar} />
              <span>{userInfo?.nickname || userInfo?.email}</span>
            </div>
          </Dropdown>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Outlet />
        </Content>
      </Layout>

      {/* 修改信息弹窗 */}
      <Modal
        title="修改个人信息"
        open={profileModalVisible}
        onOk={handleUpdateProfile}
        onCancel={() => {
          setProfileModalVisible(false)
          form.resetFields()
        }}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          autoComplete="off"
        >
          <Form.Item
            label="昵称"
            name="nickname"
          >
            <Input placeholder="请输入昵称" />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input placeholder="请输入邮箱" />
          </Form.Item>

          <Form.Item
            label="新密码"
            name="password"
            rules={[
              { min: 6, message: '密码至少6个字符' },
            ]}
          >
            <Input.Password placeholder="不修改请留空" />
          </Form.Item>

          <Form.Item
            label="确认密码"
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve()
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'))
                },
              }),
            ]}
          >
            <Input.Password placeholder="请再次输入新密码" />
          </Form.Item>
        </Form>
      </Modal>
    </Layout>
  )
}
