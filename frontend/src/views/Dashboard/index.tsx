import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Spin, Alert } from 'antd'
import { UserOutlined, ProjectOutlined, TeamOutlined, DatabaseOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getUserList } from '@/api/user'
import { getProjectList } from '@/api/project'
import { getProjectAccountList } from '@/api/project'
import { useUserStore } from '@/store/useUserStore'

interface DashboardStats {
  user_count?: number
  project_count: number
  account_count: number
  role: string
  user_email: string
  user_nickname: string
}

interface ProjectWithAccounts {
  id: string
  name: string
  account_count: number
  status: number
}

const PROJECT_STATUS_MAP: Record<number, { text: string; color: string }> = {
  1: { text: '正常', color: 'success' },
  2: { text: '未编写', color: 'default' },
  3: { text: '编写中', color: 'processing' },
  4: { text: '项目结束', color: 'default' },
  5: { text: '项目跑路', color: 'error' },
  6: { text: '项目维护', color: 'warning' },
  7: { text: '未分配', color: 'default' },
  8: { text: '账号不支持', color: 'error' },
  9: { text: 'IP不支持', color: 'error' },
}

const ROLE_NAME_MAP: Record<string, string> = {
  ADMIN: '管理员',
  GM: '项目管理员',
  IT: '技术人员',
  MANUAL: '手动操作员',
}

export default function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [projects, setProjects] = useState<ProjectWithAccounts[]>([])
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
      let projectList: any[] = []

      try {
        if (primary_role === 'ADMIN') {
          // 管理员：获取所有数据
          const [usersRes, projectsRes, accountsRes] = await Promise.all([
            getUserList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectList({ page: 1, limit: 100, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
          ])
          user_count = usersRes.count || 0
          project_count = projectsRes.count || 0
          account_count = accountsRes.count || 0
          projectList = projectsRes.items || []
        } else if (primary_role === 'GM') {
          // GM：获取所有项目和账户
          const [projectsRes, accountsRes] = await Promise.all([
            getProjectList({ page: 1, limit: 100, res_count: true }).catch(() => ({ count: 0, items: [] })),
            getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] })),
          ])
          project_count = projectsRes.count || 0
          account_count = accountsRes.count || 0
          projectList = projectsRes.items || []
        } else {
          // IT/MANUAL：只显示自己关联的项目
          const projectsRes = await getProjectList({ page: 1, limit: 100, res_count: true }).catch(() => ({ count: 0, items: [] }))
          projectList = projectsRes.items || []
          project_count = projectList.length
          
          // 统计这些项目的账户数
          if (projectList.length > 0) {
            const accountsRes = await getProjectAccountList({ page: 1, limit: 1, res_count: true }).catch(() => ({ count: 0, items: [] }))
            account_count = accountsRes.count || 0
          }
        }

        // 为每个项目获取账户数量
        const projectsWithAccounts: ProjectWithAccounts[] = await Promise.all(
          projectList.slice(0, 20).map(async (project) => {
            try {
              const accountsRes = await getProjectAccountList({
                project_id: project.id,
                page: 1,
                limit: 1,
                res_count: true,
              })
              return {
                id: project.id,
                name: project.name,
                account_count: accountsRes.count || 0,
                status: project.status,
              }
            } catch {
              return {
                id: project.id,
                name: project.name,
                account_count: 0,
                status: project.status,
              }
            }
          })
        )

        setStats({
          user_count,
          project_count,
          account_count,
          role: primary_role,
          user_email: userInfo.email,
          user_nickname: userInfo.nickname,
        })
        setProjects(projectsWithAccounts)
      } catch (error) {
        // 设置默认值，避免页面崩溃
        setStats({
          user_count: undefined,
          project_count: 0,
          account_count: 0,
          role: primary_role,
          user_email: userInfo.email,
          user_nickname: userInfo.nickname,
        })
        setProjects([])
      }
    } catch (error) {
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [userInfo])

  const columns: ColumnsType<ProjectWithAccounts> = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '账户数量',
      dataIndex: 'account_count',
      key: 'account_count',
      render: (count: number) => (
        <span style={{ fontWeight: 'bold', color: '#1890ff' }}>{count}</span>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: number) => {
        const config = PROJECT_STATUS_MAP[status] || { text: '未知', color: 'default' }
        return <Tag color={config.color}>{config.text}</Tag>
      },
    },
  ]

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
          当前角色：<Tag color="blue">{ROLE_NAME_MAP[stats.role] || stats.role}</Tag>
          邮箱：{stats.user_email}
        </p>
      </Card>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {stats.user_count !== null && stats.user_count !== undefined && (
          <Col xs={24} sm={12} lg={6}>
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
        
        <Col xs={24} sm={12} lg={stats.user_count !== null ? 6 : 8}>
          <Card>
            <Statistic
              title={stats.role === 'ADMIN' || stats.role === 'GM' ? '项目总数' : '我的项目'}
              value={stats.project_count}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={stats.user_count !== null ? 6 : 8}>
          <Card>
            <Statistic
              title={stats.role === 'ADMIN' || stats.role === 'GM' ? '账户总数' : '我的账户'}
              value={stats.account_count}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        
        {stats.user_count !== null && (
          <Col xs={24} sm={12} lg={6}>
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

      {/* 项目列表 */}
      <Card
        title={
          <span>
            <ProjectOutlined style={{ marginRight: 8 }} />
            {stats.role === 'ADMIN' || stats.role === 'GM' ? '所有项目' : '我的项目'}
          </span>
        }
      >
        <Table
          dataSource={projects}
          columns={columns}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个项目`,
          }}
          locale={{
            emptyText: '暂无项目数据',
          }}
        />
      </Card>

      {/* 角色说明 */}
      {(stats.role === 'IT' || stats.role === 'MANUAL') && (
        <Card
          title="提示"
          style={{ marginTop: 24 }}
          type="inner"
        >
          <p style={{ margin: 0, color: '#666' }}>
            <strong>注意：</strong>
            {stats.role === 'IT' && ' 作为技术人员，您只能查看和管理分配给您的项目。'}
            {stats.role === 'MANUAL' && ' 作为手动操作员，您只能查看和操作分配给您的项目。'}
          </p>
        </Card>
      )}
    </div>
  )
}
