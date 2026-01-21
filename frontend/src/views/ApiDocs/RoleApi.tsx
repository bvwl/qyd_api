import ApiTester from '@/components/ApiTester'

export default function RoleApi() {
  return (
    <ApiTester
      title="角色列表 API"
      description="获取角色列表，支持分页查询"
      defaultMethod="GET"
      defaultUrl="/v1/user/role"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '100', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
      ]}
      examples={[
        {
          name: '获取所有角色',
          method: 'GET',
          url: '/v1/user/role',
          params: [
            { key: 'limit', value: '100', enabled: true },
          ]
        }
      ]}
    />
  )
}
