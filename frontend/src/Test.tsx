export default function Test() {
  return (
    <div style={{ 
      padding: 50, 
      textAlign: 'center',
      fontSize: 20,
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{ color: '#1890ff', marginBottom: 20 }}>✅ React 正常工作</h1>
      <p>如果你能看到这个页面，说明前端基础环境正常</p>
      <p style={{ marginTop: 20, color: '#666' }}>
        现在可以访问：<a href="/login" style={{ color: '#1890ff' }}>/login</a>
      </p>
    </div>
  )
}
