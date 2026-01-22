import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  List,
  Tree,
  Button,
  message,
  Spin,
  Typography,
  Space,
  Tag,
  Input,
  Empty,
} from 'antd'
import {
  TeamOutlined,
  SaveOutlined,
  ReloadOutlined,
  SearchOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import type { DataNode } from 'antd/es/tree'
import { getRoleList, getRoleRoutes, setRoleRoutes, getRouteTree } from '@/api/user'
import type { Role, Route } from '@/types'

const { Title, Text } = Typography

export default function PermissionManage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [routeTree, setRouteTree] = useState<DataNode[]>([])
  const [checkedKeys, setCheckedKeys] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [treeLoading, setTreeLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [error, setError] = useState<string>('')

  // 加载角色列表
  const loadRoles = async () => {
    try {
      setLoading(true)
      setError('')
      console.log('开始加载角色列表...')
      const res = await getRoleList({ page: 1, limit: 100 })
      console.log('角色列表响应:', res)
      
      if (res && res.items) {
        setRoles(res.items)
        console.log(`成功加载 ${res.items.length} 个角色`)
      } else {
        console.warn('角色列表响应格式异常:', res)
        setError('角色列表数据格式异常')
      }
    } catch (error: any) {
      console.error('加载角色列表失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      setError(`加载角色列表失败: ${errorMsg}`)
      message.error(`加载角色列表失败: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  // 加载路由树
  const loadRouteTree = async () => {
    try {
      setTreeLoading(true)
      setError('')
      console.log('开始加载路由树...')
      const routes = await getRouteTree({ status: 1 })
      console.log('路由树响应:', routes)
      
      if (Array.isArray(routes)) {
        const treeData = convertToTreeData(routes)
        setRouteTree(treeData)
        console.log(`成功加载 ${routes.length} 个路由`)
      } else {
        console.warn('路由树响应格式异常:', routes)
        setError('路由树数据格式异常')
      }
    } catch (error: any) {
      console.error('加载路由树失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      setError(`加载路由树失败: ${errorMsg}`)
      message.error(`加载路由树失败: ${errorMsg}`)
    } finally {
      setTreeLoading(false)
    }
  }

  // 加载角色的路由权限
  const loadRoleRoutes = async (roleId: string) => {
    try {
      setTreeLoading(true)
      setError('')
      console.log('开始加载角色路由，角色ID:', roleId)
      const routes = await getRoleRoutes(roleId)
      console.log('角色路由响应:', routes)
      
      if (Array.isArray(routes)) {
        const routeIds = extractRouteIds(routes)
        setCheckedKeys(routeIds)
        console.log(`成功加载 ${routeIds.length} 个权限`)
      } else {
        console.warn('角色路由响应格式异常:', routes)
        setError('角色路由数据格式异常')
      }
    } catch (error: any) {
      console.error('加载角色权限失败:', error)
      const errorMsg = error.response?.data?.detail || error.message || '未知错误'
      setError(`加载角色权限失败: ${errorMsg}`)
      message.error(`加载角色权限失败: ${errorMsg}`)
    } finally {
      setTreeLoading(false)
    }
  }

  // 将路由数据转换为树形结构
  const convertToTreeData = (routes: Route[]): DataNode[] => {
    return routes.map((route) => ({
      title: (
        <Space>
          <span>{route.title}</span>
          {route.route_type === 2 && <Tag color="blue">按钮</Tag>}
          {route.route_type === 3 && <Tag color="green">接口</Tag>}
          {route.permission && (
            <Tag color="orange" style={{ fontSize: 11 }}>
              {route.permission}
            </Tag>
          )}
        </Space>
      ),
      key: route.id,
      children: route.children && route.children.length > 0 
        ? convertToTreeData(route.children) 
        : undefined,
    }))
  }

  // 提取所有路由ID
  const extractRouteIds = (routes: Route[]): string[] => {
    const ids: string[] = []
    const extract = (routeList: Route[]) => {
      routeList.forEach((route) => {
        ids.push(route.id)
        if (route.children && route.children.length > 0) {
          extract(route.children)
        }
      })
    }
    extract(routes)
    return ids
  }

  // 保存权限配置
  const handleSave = async () => {
    if (!selectedRole) {
      message.warning('请先选择角色')
      return
    }

    try {
      setSaving(true)
      await setRoleRoutes(selectedRole.id, checkedKeys)
      message.success('权限保存成功')
    } catch (error) {
      message.error('权限保存失败')
    } finally {
      setSaving(false)
    }
  }

  // 选择角色
  const handleSelectRole = (role: Role) => {
    setSelectedRole(role)
    loadRoleRoutes(role.id)
  }

  // 刷新
  const handleRefresh = () => {
    loadRoles()
    loadRouteTree()
    if (selectedRole) {
      loadRoleRoutes(selectedRole.id)
    }
  }

  // 全选/取消全选
  const handleCheckAll = (checked: boolean) => {
    if (checked) {
      const allKeys = getAllKeys(routeTree)
      setCheckedKeys(allKeys)
    } else {
      setCheckedKeys([])
    }
  }

  // 获取所有节点的key
  const getAllKeys = (nodes: DataNode[]): string[] => {
    const keys: string[] = []
    const extract = (nodeList: DataNode[]) => {
      nodeList.forEach((node) => {
        keys.push(node.key as string)
        if (node.children) {
          extract(node.children)
        }
      })
    }
    extract(nodes)
    return keys
  }

  useEffect(() => {
    loadRoles()
    loadRouteTree()
  }, [])

  // 过滤角色列表
  const filteredRoles = roles.filter((role) =>
    role.name.toLowerCase().includes(searchText.toLowerCase()) ||
    role.code.toLowerCase().includes(searchText.toLowerCase())
  )

  return (
    <div>
      <Card
        title={
          <Space>
            <TeamOutlined />
            <span>权限管理</span>
          </Space>
        }
        extra={
          <Space>
            <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
              刷新
            </Button>
          </Space>
        }
      >
        {error && (
          <div style={{ marginBottom: 16, padding: 12, background: '#fff2e8', border: '1px solid #ffbb96', borderRadius: 4 }}>
            <Text type="danger">{error}</Text>
          </div>
        )}
        
        <Row gutter={16}>
          {/* 左侧：角色列表 */}
          <Col span={6}>
            <Card
              title="角色列表"
              size="small"
              style={{ height: 'calc(100vh - 250px)', overflow: 'auto' }}
            >
              <Input
                placeholder="搜索角色"
                prefix={<SearchOutlined />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                style={{ marginBottom: 16 }}
              />
              <Spin spinning={loading}>
                {filteredRoles.length === 0 ? (
                  <Empty description="暂无角色" />
                ) : (
                  <List
                    dataSource={filteredRoles}
                    renderItem={(role) => (
                      <List.Item
                        style={{
                          cursor: 'pointer',
                          background:
                            selectedRole?.id === role.id ? '#e6f7ff' : 'transparent',
                          padding: '12px',
                          borderRadius: '4px',
                          marginBottom: '8px',
                        }}
                        onClick={() => handleSelectRole(role)}
                      >
                        <List.Item.Meta
                          avatar={
                            selectedRole?.id === role.id ? (
                              <CheckCircleOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                            ) : (
                              <TeamOutlined style={{ fontSize: 20 }} />
                            )
                          }
                          title={
                            <Space>
                              <Text strong>{role.name}</Text>
                              {selectedRole?.id === role.id && (
                                <Tag color="blue">已选择</Tag>
                              )}
                            </Space>
                          }
                          description={
                            <Space direction="vertical" size={0}>
                              <Text type="secondary" style={{ fontSize: 12 }}>
                                标识: {role.code}
                              </Text>
                              {role.description && (
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                  {role.description}
                                </Text>
                              )}
                            </Space>
                          }
                        />
                      </List.Item>
                    )}
                  />
                )}
              </Spin>
            </Card>
          </Col>

          {/* 右侧：权限树 */}
          <Col span={18}>
            <Card
              title={
                selectedRole ? (
                  <Space>
                    <span>配置权限：</span>
                    <Tag color="blue">{selectedRole.name}</Tag>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      ({selectedRole.code})
                    </Text>
                  </Space>
                ) : (
                  '请选择角色'
                )
              }
              size="small"
              extra={
                selectedRole && (
                  <Space>
                    <Button
                      size="small"
                      onClick={() => handleCheckAll(true)}
                    >
                      全选
                    </Button>
                    <Button
                      size="small"
                      onClick={() => handleCheckAll(false)}
                    >
                      取消全选
                    </Button>
                    <Button
                      type="primary"
                      icon={<SaveOutlined />}
                      loading={saving}
                      onClick={handleSave}
                    >
                      保存权限
                    </Button>
                  </Space>
                )
              }
              style={{ height: 'calc(100vh - 250px)', overflow: 'auto' }}
            >
              {!selectedRole ? (
                <Empty
                  description="请从左侧选择一个角色来配置权限"
                  style={{ marginTop: 100 }}
                />
              ) : (
                <Spin spinning={treeLoading}>
                  {routeTree.length === 0 ? (
                    <Empty description="暂无路由数据" />
                  ) : (
                    <>
                      <div style={{ marginBottom: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
                        <Space direction="vertical" size={4}>
                          <Text strong>权限说明：</Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            • 勾选菜单项后，用户可以看到该菜单
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            • <Tag color="blue" style={{ fontSize: 11 }}>按钮</Tag> 标记的是页面内的操作按钮权限
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            • <Tag color="green" style={{ fontSize: 11 }}>接口</Tag> 标记的是API接口权限
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            • <Tag color="orange" style={{ fontSize: 11 }}>权限标识</Tag> 用于前端权限控制
                          </Text>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            • 已选择 <Tag color="blue">{checkedKeys.length}</Tag> 个权限
                          </Text>
                        </Space>
                      </div>
                      <Tree
                        checkable
                        defaultExpandAll
                        checkedKeys={checkedKeys}
                        onCheck={(checked) => {
                          setCheckedKeys(checked as string[])
                        }}
                        treeData={routeTree}
                        style={{ fontSize: 14 }}
                      />
                    </>
                  )}
                </Spin>
              )}
            </Card>
          </Col>
        </Row>
      </Card>
    </div>
  )
}
