import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Spin, Alert, Button, App, Modal, Input, Space, Typography, Tag } from 'antd'
import { UserOutlined, ProjectOutlined, TeamOutlined, DatabaseOutlined, CopyOutlined, ReloadOutlined, EyeOutlined, EyeInvisibleOutlined, CloudServerOutlined, RiseOutlined } from '@ant-design/icons'
import { getUserList } from '@/api/user'
import { getProjectList } from '@/api/project'
import { getProjectAccountList } from '@/api/project'
import { getTokenList, generateToken } from '@/api/user'
import { getServerAccountList, generateServerAccount, getServerAccountPassword } from '@/api/server'
import { getProjectStatsForDashboard } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'
import type { UserToken, ServerAccount } from '@/types'
import ProjectStatsChart from './ProjectStatsChart'

const { Text } = Typography

interface DashboardStats {
  user_count?: number
  project_count: number
  account_count: number
  today_update_count: number
  role: string
  user_email: string
  user_nickname: string
}

const ROLE_NAME_MAP: Record<string, string> = {
  ADMIN: '管理员',
  GM: '项目管理员',
  IT: '技术人员',
  MANUAL: '手动操作员',
}

export default function Dashboard() {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [tokenLoading, setTokenLoading] = useState(false)
  const [serverAccountLoading, setServerAccountLoading] = useState(false)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [userToken, setUserToken] = useState<UserToken | null>(null)
  const [serverAccount, setServerAccount] = useState<ServerAccount | null>(null)
  const [tokenVisible, setTokenVisible] = useState(false)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [decryptedPassword, setDecryptedPassword] = useState<string>('')
  const userInfo = useUserStore((state) => state.userInfo)

  const fetchData = async () => {
    try {
      setLoading(true)
      
      if (!userInfo) {
        return
      }

      // 确定用户的主要角色
      const role_priority: Record<string, number> = { ADMIN: 4, GM: 3, IT: 2, MANUAL: 1 }
      const user_roles = userInfo.roles?.map(r => r.code) || []
      const primary_role = user_roles.length > 0
        ? user_roles.reduce((a, b) => (role_priority[a] || 0) > (role_priority[b] || 0) ? a : b)
        : 'MANUAL'

      // 根据角色获取数据
      let user_count: number | undefined
      let project_count = 0
      let account_count = 0
      let today_update_count = 0

      try {
        if (primary_role === 'ADMIN') {
          // 管理员：获取统计数据
          const [usersRes, projectsRes, accountsRes, todayStatsRes] = await Promise.all([
            getUserList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectStatsForDashboard({ days: 1 }).catch(() => ({ code: 0, data: [] })),
          ])
          user_count = usersRes.count || 0
          project_count = projectsRes.count || 0
          account_count = accountsRes.count || 0
          // 获取今天的更新数量（总和）
          if (todayStatsRes.code === 1 && todayStatsRes.data && todayStatsRes.data.length > 0) {
            today_update_count = todayStatsRes.data[0].counts[0] || 0
          }
        } else if (primary_role === 'GM') {
          // GM：获取项目和账户统计
          const [projectsRes, accountsRes, todayStatsRes] = await Promise.all([
            getProjectList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectStatsForDashboard({ days: 1 }).catch(() => ({ code: 0, data: [] })),
          ])
          project_count = projectsRes.count || 0
          account_count = accountsRes.count || 0
          // 获取今天的更新数量（总和）
          if (todayStatsRes.code === 1 && todayStatsRes.data && todayStatsRes.data.length > 0) {
            today_update_count = todayStatsRes.data[0].counts[0] || 0
          }
        } else {
          // IT/MANUAL：获取自己的项目和账户统计
          const [projectsRes, accountsRes, todayStatsRes] = await Promise.all([
            getProjectList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectStatsForDashboard({ days: 1 }).catch(() => ({ code: 0, data: [] })),
          ])
          project_count = projectsRes.count || 0
          account_count = accountsRes.count || 0
          // 获取今天的更新数量（总和）
          if (todayStatsRes.code === 1 && todayStatsRes.data && todayStatsRes.data.length > 0) {
            today_update_count = todayStatsRes.data[0].counts[0] || 0
          }
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }

      setStats({
        user_count,
        project_count,
        account_count,
        today_update_count,
        role: primary_role,
        user_email: userInfo.email,
        user_nickname: userInfo.nickname,
      })
    } catch (error) {
      console.error('加载仪表盘数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    if (userInfo?.id) {
      fetchUserToken()
      fetchServerAccount()
    }
  }, [userInfo])

  const fetchUserToken = async () => {
    if (!userInfo?.id) return
    
    try {
      const res = await getTokenList({
        user_id: userInfo.id,
        status: 1,  // 只获取正常状态的token
        page: 1,
        limit: 1,
      })
      if (res.items && res.items.length > 0) {
        setUserToken(res.items[0])
      } else {
        setUserToken(null)
      }
    } catch (error) {
      setUserToken(null)
    }
  }

  const fetchServerAccount = async () => {
    if (!userInfo?.id) return
    
    try {
      const res = await getServerAccountList({
        page: 1,
        limit: 1,
      })
      if (res.items && res.items.length > 0) {
        setServerAccount(res.items[0])
        // 如果是管理员，password 字段已经是解密后的密码
        const userRoles = userInfo.roles?.map(r => r.code) || []
        const isAdmin = userRoles.includes('ADMIN')
        if (isAdmin) {
          setDecryptedPassword(res.items[0].password)
        }
      } else {
        setServerAccount(null)
      }
    } catch (error) {
      setServerAccount(null)
    }
  }

  const handleGenerateToken = () => {
    Modal.confirm({
      title: '确认生成新Token',
      content: '生成新Token后，旧Token将立即失效。确定要继续吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          setTokenLoading(true)
          const newToken = await generateToken()
          setUserToken(newToken)
          message.success('Token生成成功')
        } catch (error) {
          message.error('Token生成失败')
        } finally {
          setTokenLoading(false)
        }
      },
    })
  }

  const handleCopyToken = () => {
    if (!userToken?.token) return
    
    navigator.clipboard.writeText(userToken.token).then(() => {
      message.success('Token已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败，请手动复制')
    })
  }

  const handleGenerateServerAccount = () => {
    Modal.confirm({
      title: '确认生成服务器账号',
      content: serverAccount 
        ? '您已有服务器账号，此操作将返回现有账号信息。'
        : '将为您生成一个服务器账号，用户名和密码将自动生成。确定要继续吗？',
      okText: '确定',
      cancelText: '取消',
      onOk: async () => {
        try {
          setServerAccountLoading(true)
          const account = await generateServerAccount()
          
          // 保存账号信息
          const oldPassword = serverAccount?.password
          setServerAccount(account)
          
          // 如果是新生成的账号（密码不同），显示提示弹窗
          if (!oldPassword || oldPassword !== account.password) {
            Modal.success({
              title: '服务器账号生成成功',
              content: (
                <div>
                  <p>用户名：{account.username}</p>
                  <p>密码：{account.password}</p>
                  <p style={{ color: 'red', marginTop: 16 }}>
                    请立即保存密码，此密码仅显示一次！
                  </p>
                </div>
              ),
              width: 500,
            })
            // 设置解密密码用于后续显示
            setDecryptedPassword(account.password)
          } else {
            // 已存在账号
            message.success('服务器账号已存在')
            // 如果是管理员，password 已经是解密后的
            const userRoles = userInfo?.roles?.map(r => r.code) || []
            const isAdmin = userRoles.includes('ADMIN')
            if (isAdmin) {
              setDecryptedPassword(account.password)
            }
          }
        } catch (error) {
          message.error('服务器账号生成失败')
        } finally {
          setServerAccountLoading(false)
        }
      },
    })
  }

  const handleCopyUsername = () => {
    if (!serverAccount?.username) return
    
    navigator.clipboard.writeText(serverAccount.username).then(() => {
      message.success('用户名已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败，请手动复制')
    })
  }

  const handleViewPassword = async () => {
    if (!serverAccount?.id) return
    
    try {
      setServerAccountLoading(true)
      const account = await getServerAccountPassword(serverAccount.id)
      // password 字段已经是解密后的密码
      setDecryptedPassword(account.password)
      setPasswordVisible(true)
      message.success('密码已解密')
    } catch (error) {
      message.error('获取密码失败')
    } finally {
      setServerAccountLoading(false)
    }
  }

  const handleCopyPassword = () => {
    if (!decryptedPassword) return
    
    navigator.clipboard.writeText(decryptedPassword).then(() => {
      message.success('密码已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败，请手动复制')
    })
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" tip="加载中...">
          <div style={{ minHeight: 100 }} />
        </Spin>
      </div>
    )
  }

  if (!stats) {
    return (
      <Alert
        message="无法加载仪表盘数据"
        description="请刷新页面重试"
        type="error"
        showIcon
      />
    )
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 欢迎信息 */}
      <Card style={{ marginBottom: 24 }}>
        <h2 style={{ margin: 0 }}>
          欢迎回来，{stats.user_nickname}！
        </h2>
        <p style={{ margin: '8px 0 0', color: '#666' }}>
          当前角色：
          {userInfo?.roles && userInfo.roles.length > 0 ? (
            userInfo.roles.map((role) => (
              <Tag key={role.code} color="blue" style={{ marginLeft: 4 }}>
                {ROLE_NAME_MAP[role.code] || role.name}
              </Tag>
            ))
          ) : (
            <Tag color="blue">{ROLE_NAME_MAP[stats.role] || stats.role}</Tag>
          )}
          <span style={{ marginLeft: 16 }}>邮箱：{stats.user_email}</span>
        </p>
      </Card>

      {/* API Token 和服务器账号 - 左右对称布局 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* API Token 卡片 - 左侧 */}
        <Col xs={24} lg={12}>
          <Card 
            title="API Token" 
            style={{ height: '100%' }}
            extra={
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={handleGenerateToken}
                loading={tokenLoading}
              >
                重新生成
              </Button>
            }
          >
            {userToken ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">Token:</Text>
                  <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Input
                      value={userToken.token}
                      readOnly
                      type={tokenVisible ? 'text' : 'password'}
                      style={{ flex: 1, fontFamily: 'monospace' }}
                      suffix={
                        <Space.Compact>
                          <Button
                            type="text"
                            size="small"
                            icon={tokenVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                            onClick={() => setTokenVisible(!tokenVisible)}
                          />
                          <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={handleCopyToken}
                          />
                        </Space.Compact>
                      }
                    />
                  </div>
                </div>
                <div>
                  <Text type="secondary">创建时间: </Text>
                  <Text>{userToken.create_time}</Text>
                </div>
                <Alert
                  message="提示"
                  description="请妥善保管您的Token，不要泄露给他人。重新生成Token后，旧Token将立即失效。"
                  type="info"
                  showIcon
                />
              </Space>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Text type="secondary">您还没有Token</Text>
                <div style={{ marginTop: 16 }}>
                  <Button
                    type="primary"
                    icon={<ReloadOutlined />}
                    onClick={handleGenerateToken}
                    loading={tokenLoading}
                  >
                    生成Token
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </Col>

        {/* 服务器账号卡片 - 右侧 */}
        <Col xs={24} lg={12}>
          <Card 
            title={
              <span>
                <CloudServerOutlined style={{ marginRight: 8 }} />
                服务器账号
              </span>
            }
            style={{ height: '100%' }}
            extra={
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={handleGenerateServerAccount}
                loading={serverAccountLoading}
              >
                {serverAccount ? '查看账号' : '生成账号'}
              </Button>
            }
          >
            {serverAccount ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">用户名:</Text>
                  <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Input
                      value={serverAccount.username}
                      readOnly
                      style={{ flex: 1, fontFamily: 'monospace' }}
                      suffix={
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={handleCopyUsername}
                        />
                      }
                    />
                  </div>
                </div>
                <div>
                  <Text type="secondary">密码:</Text>
                  <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Input
                      value={passwordVisible && decryptedPassword ? decryptedPassword : '••••••••••••••••'}
                      readOnly
                      type={passwordVisible ? 'text' : 'password'}
                      style={{ flex: 1, fontFamily: 'monospace' }}
                      suffix={
                        <Space.Compact>
                          <Button
                            type="text"
                            size="small"
                            icon={passwordVisible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                            onClick={() => {
                              if (!passwordVisible && !decryptedPassword) {
                                handleViewPassword()
                              } else {
                                setPasswordVisible(!passwordVisible)
                              }
                            }}
                            loading={serverAccountLoading}
                          />
                          {decryptedPassword && (
                            <Button
                              type="text"
                              size="small"
                              icon={<CopyOutlined />}
                              onClick={handleCopyPassword}
                            />
                          )}
                        </Space.Compact>
                      }
                    />
                  </div>
                </div>
                <div>
                  <Text type="secondary">创建时间: </Text>
                  <Text>{serverAccount.create_time}</Text>
                </div>
                <Alert
                  message="提示"
                  description="服务器账号用于访问SOCKS5代理服务器。点击眼睛图标可查看密码。每个用户只能拥有一个服务器账号。"
                  type="info"
                  showIcon
                />
              </Space>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <Text type="secondary">您还没有服务器账号</Text>
                <div style={{ marginTop: 16 }}>
                  <Button
                    type="primary"
                    icon={<CloudServerOutlined />}
                    onClick={handleGenerateServerAccount}
                    loading={serverAccountLoading}
                  >
                    生成服务器账号
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {stats.user_count !== undefined && (
          <Col xs={24} sm={12} lg={5}>
            <Card>
              <Statistic
                title="用户总数"
                value={stats.user_count}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
        )}
        
        <Col xs={24} sm={12} lg={stats.user_count !== undefined ? 5 : 6}>
          <Card>
            <Statistic
              title={stats.role === 'ADMIN' || stats.role === 'GM' ? '项目总数' : '我的项目'}
              value={stats.project_count}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={stats.user_count !== undefined ? 5 : 6}>
          <Card>
            <Statistic
              title={stats.role === 'ADMIN' || stats.role === 'GM' ? '账户总数' : '我的账户'}
              value={stats.account_count}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={stats.user_count !== undefined ? 5 : 6}>
          <Card>
            <Statistic
              title="今日更新"
              value={stats.today_update_count}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        
        {stats.user_count !== undefined && (
          <Col xs={24} sm={12} lg={4}>
            <Card>
              <Statistic
                title="在线用户"
                value={1}
                prefix={<TeamOutlined />}
                valueStyle={{ color: '#722ed1' }}
                suffix="/ 1"
              />
            </Card>
          </Col>
        )}
      </Row>

      {/* 项目统计图表 */}
      <ProjectStatsChart />
    </div>
  )
}
