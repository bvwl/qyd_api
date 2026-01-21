import ApiTester from '@/components/ApiTester'

export default function MailApi() {
  return (
    <ApiTester
      title="邮箱列表 API"
      description="获取邮箱列表，支持分页、搜索和状态过滤"
      defaultMethod="GET"
      defaultUrl="/v1/mail/info"
      defaultParams={[
        { key: 'page', value: '1', enabled: true },
        { key: 'limit', value: '10', enabled: true },
        { key: 'res_count', value: 'true', enabled: true },
        { key: 'email', value: '', enabled: false },
        { key: 'status', value: '', enabled: false },
      ]}
      examples={[
        {
          name: '获取所有邮箱',
          method: 'GET',
          url: '/v1/mail/info',
          params: [
            { key: 'page', value: '1', enabled: true },
            { key: 'limit', value: '10', enabled: true },
          ]
        },
        {
          name: '搜索邮箱',
          method: 'GET',
          url: '/v1/mail/info',
          params: [
            { key: 'email', value: 'test', enabled: true },
            { key: 'limit', value: '10', enabled: true },
          ]
        }
      ]}
    />
  )
}
