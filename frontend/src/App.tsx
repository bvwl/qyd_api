import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Login from './views/Login/index'
import Layout from './components/Layout/index'
import UserList from './views/User/UserList'
import MailList from './views/Mail/MailList'
import ProtectedRoute from './components/ProtectedRoute/index'
import 'dayjs/locale/zh-cn'

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/user/list" replace />} />
            <Route path="user/list" element={<UserList />} />
            <Route path="mail/list" element={<MailList />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
