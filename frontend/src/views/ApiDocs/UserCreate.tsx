import ApiTester from '@/components/ApiTester'

export default function UserCreate() {
  return (
    <ApiTester
      title="创建用户 API"
      description="创建新用户，需要提供邮箱、昵称、密码等信息"
      defaultMethod="POST"
      defaultUrl="/v1/user/user"
      defaultBody={`{
  "email": "test@example.com",
  "nickname": "测试用户",
  "password": "123456",
  "status": 1,
  "role_ids": []
}`}
      examples={[
        {
          name: '创建普通用户',
          method: 'POST',
          url: '/v1/user/user',
          body: `{
  "email": "user@example.com",
  "nickname": "普通用户",
  "password": "123456",
  "status": 1,
  "role_ids": []
}`
        },
        {
          name: '创建管理员',
          method: 'POST',
          url: '/v1/user/user',
          body: `{
  "email": "admin@example.com",
  "nickname": "管理员",
  "password": "admin123",
  "status": 1,
  "role_ids": []
}`
        }
      ]}
    />
  )
}
