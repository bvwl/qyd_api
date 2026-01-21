import ApiTester from '@/components/ApiTester'

export default function ServerApi() {
  return (
    <ApiTester
      title="服务器列表 API"
      description="获取服务器列表，支持分页和状态过滤"
      defaultMethod="GET"
      defaultUrl="/v1/server/info"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '10', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
        { key: 'host', value: '', enabled: false },
        { key: 'status', value: '', enabled: false },
      ]}
      examples={[
        {
          name: '获取所有服务器',
          method: 'GET',
          url: '/v1/server/info',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
          ]
        }
      ]}
    />
  )
}
