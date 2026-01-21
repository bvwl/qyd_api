import ApiTester from '@/components/ApiTester'

export default function ProjectAccountApi() {
  return (
    <ApiTester
      title="项目账号 API"
      description="获取项目账号列表，支持分页和过滤"
      defaultMethod="GET"
      defaultUrl="/v1/project/account"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '10', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
        { key: 'account', value: '', enabled: false },
        { key: 'project_id', value: '', enabled: false },
        { key: 'status', value: '', enabled: false },
      ]}
      examples={[
        {
          name: '获取所有账号',
          method: 'GET',
          url: '/v1/project/account',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
          ]
        }
      ]}
    />
  )
}
