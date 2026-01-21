import ApiTester from '@/components/ApiTester'

export default function ProjectApi() {
  return (
    <ApiTester
      title="项目列表 API"
      description="获取项目列表，支持分页、搜索和状态过滤"
      defaultMethod="GET"
      defaultUrl="/v1/project/info"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '10', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
        { key: 'name', value: '', enabled: false },
        { key: 'status', value: '', enabled: false },
      ]}
      examples={[
        {
          name: '获取第一页',
          method: 'GET',
          url: '/v1/project/info',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
            { key: 'res_count', value: 'true', enabled: true },
          ]
        },
        {
          name: '搜索项目',
          method: 'GET',
          url: '/v1/project/info',
          params: [
            { key: 'name', value: '测试', enabled: true },
            { key: 'limit', value: '10', enabled: true },
          ]
        }
      ]}
    />
  )
}
