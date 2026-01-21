import ApiTester from '@/components/ApiTester'

export default function UserApi() {
  return (
    <ApiTester
      title="用户列表 API"
      description="获取用户列表，支持分页、搜索和时间范围过滤"
      defaultMethod="GET"
      defaultUrl="/v1/user/user"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '10', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
        { key: 'email', value: '', enabled: false },
        { key: 'status', value: '', enabled: false },
        { key: 'create_time_start', value: '', enabled: false },
        { key: 'create_time_end', value: '', enabled: false },
      ]}
      examples={[
        {
          name: '获取第一页',
          method: 'GET',
          url: '/v1/user/user',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
            { key: 'res_count', value: 'true', enabled: true },
          ]
        },
        {
          name: '搜索用户',
          method: 'GET',
          url: '/v1/user/user',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
            { key: 'email', value: 'zhiyu', enabled: true },
          ]
        }
      ]}
    />
  )
}
