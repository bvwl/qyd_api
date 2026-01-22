import { useState, useEffect } from 'react'
import { Card, Row, Col, List, Tree, Button, message, Spin, Empty } from 'antd'
import { TeamOutlined, SaveOutlined } from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'

interface Role {
  id: string
  name: string
  code: string
  description: string
}

interface Route {
  id: string
  name: string
  path: string
  title: string
  icon?: string
  children?: Route[]
}

export default function PermissionManageWorking() {
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [routeTree, setRouteTree] = useState<DataNode[]>([])
  const [checkedKeys, setCheckedKeys] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        message.error('请先登录')
        return
      }

      // 获取角色列表
      const rolesResponse = await fetch('http://127.0.0.1:6080/v1/user/role?page=1&limit=100', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const rolesData = await rolesResponse.json()
      
      // 获取路由树
      const routesResponse = await fetch('http://127.0.0.1:6080/v1/user/route/tree?status=1', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const routesData = await routesResponse.json()

      if (rolesResponse.ok && routesResponse.ok) {
        setRoles(rolesData.items || [])
        setRouteTree(buildTree(routesData || []))
        // 数据加载成功，不显示提示
      } else {
        message.error('加载数据失败')
      }
    } catch (error: any) {
      console.error('加载数据失败:', error)
      message.error(`加载失败: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const buildTree = (routes: Route[]): DataNode[] => {
    return routes.map(route => ({
      title: route.title,
      key: route.id,
      children: route.children ? buildTree(route.children) : undefined
    }))
  }

  const handleSelectRole = async (role: Role) => {
    setSelectedRole(role)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://127.0.0.1:6080/v1/user/role/${role.id}/routes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const routes = await response.json()
      
      if (response.ok) {
        const ids = extractIds(routes)
        setCheckedKeys(ids)
      } else {
        message.error('加载权限失败')
      }
    } catch (error) {
      console.error('加载权限失败:', error)
      message.error('加载权限失败')
    }
  }

  const extractIds = (routes: any[]): string[] => {
    const ids: string[] = []
    const extract = (list: any[]) => {
      list.forEach((r: any) => {
        ids.push(r.id)
        if (r.children) extract(r.children)
      })
    }
    extract(routes)
    return ids
  }

  const handleSave = async () => {
    if (!selectedRole) return
    
    setSaving(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`http://127.0.0.1:6080/v1/user/role/${selectedRole.id}/routes`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(checkedKeys)
      })
      
      if (response.ok) {
        message.success('保存成功')
      } else {
        const data = await response.json()
        message.error(`保存失败: ${data.detail || '未知错误'}`)
      }
    } catch (error: any) {
      console.error('保存失败:', error)
      message.error(`保存失败: ${error.message}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card title="权限管理">
      <Spin spinning={loading}>
        <Row gutter={16}>
          <Col span={8}>
            <Card title="角色列表" size="small">
              <List
                dataSource={roles}
                renderItem={(role) => (
                  <List.Item
                    onClick={() => handleSelectRole(role)}
                    style={{
                      cursor: 'pointer',
                      background: selectedRole?.id === role.id ? '#e6f7ff' : 'transparent',
                      padding: '12px'
                    }}
                  >
                    <List.Item.Meta
                      avatar={<TeamOutlined />}
                      title={role.name}
                      description={role.code}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          
          <Col span={16}>
            <Card
              title={selectedRole ? `配置权限：${selectedRole.name}` : '请选择角色'}
              size="small"
              extra={
                selectedRole && (
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    loading={saving}
                    onClick={handleSave}
                  >
                    保存
                  </Button>
                )
              }
            >
              {!selectedRole ? (
                <Empty description="请选择角色" />
              ) : (
                <Tree
                  checkable
                  defaultExpandAll
                  checkedKeys={checkedKeys}
                  onCheck={(checked: any) => setCheckedKeys(checked)}
                  treeData={routeTree}
                />
              )}
            </Card>
          </Col>
        </Row>
      </Spin>
    </Card>
  )
}
