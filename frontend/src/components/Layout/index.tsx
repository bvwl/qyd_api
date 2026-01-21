import { useState } from 'react'
import { Layout, Menu, Avatar, Dropdown, theme } from 'antd'
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
} from '@ant-design/icons'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import type { MenuProps } from 'antd'

const { Header, Sider, Content } = Layout

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { userInfo, logout } = useUserStore()
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  const menuItems: MenuProps['items'] = [
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
        { key: '/project/balance', label: '项目余额' },
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
      key: '/mail',
      icon: <MailOutlined />,
      label: '邮箱管理',
      children: [
        { key: '/mail/list', label: '邮箱列表' },
        { key: '/mail/outlook', label: 'Outlook授权' },
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

  const userMenuItems: MenuProps['items'] = [
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
    </Layout>
  )
}
