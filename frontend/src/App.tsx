import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, App as AntApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Login from './views/Login/index'
import Layout from './components/Layout/index'
import UserList from './views/User/UserList'
import RoleList from './views/User/RoleList'
import RouteList from './views/User/RouteList'
import TokenList from './views/User/TokenList'
import LogList from './views/User/LogList'
import ProjectList from './views/Project/ProjectList'
import ProjectAccount from './views/Project/ProjectAccount'
import ProjectWallet from './views/Project/ProjectWallet'
import CountryList from './views/Server/CountryList'
import GroupList from './views/Server/GroupList'
import ServerList from './views/Server/ServerList'
import ServerAccount from './views/Server/ServerAccount'
import MailList from './views/Mail/MailList'
import MailViewer from './views/Mail/MailViewer'
import Dashboard from './views/Dashboard/index'
import Diagnostic from './views/Diagnostic'
import UserApi from './views/ApiDocs/UserApi'
import UserCreate from './views/ApiDocs/UserCreate'
import RoleApi from './views/ApiDocs/RoleApi'
import ProjectApi from './views/ApiDocs/ProjectApi'
import ProjectAccountApi from './views/ApiDocs/ProjectAccountApi'
import ServerApi from './views/ApiDocs/ServerApi'
import MailApi from './views/ApiDocs/MailApi'
import PermissionManageWorking from './views/User/PermissionManageWorking'
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
      <AntApp>
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
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="user/list" element={<UserList />} />
              <Route path="user/role" element={<RoleList />} />
              <Route path="user/route" element={<RouteList />} />
              <Route path="user/permission" element={<PermissionManageWorking />} />
              <Route path="user/token" element={<TokenList />} />
              <Route path="user/log" element={<LogList />} />
              <Route path="project/list" element={<ProjectList />} />
              <Route path="project/account" element={<ProjectAccount />} />
              <Route path="project/wallet" element={<ProjectWallet />} />
              <Route path="server/country" element={<CountryList />} />
              <Route path="server/group" element={<GroupList />} />
              <Route path="server/list" element={<ServerList />} />
              <Route path="server/account" element={<ServerAccount />} />
              <Route path="mail/list" element={<MailList />} />
              <Route path="mail/viewer" element={<MailViewer />} />
              <Route path="api-docs/user" element={<UserApi />} />
              <Route path="api-docs/user-create" element={<UserCreate />} />
              <Route path="api-docs/role" element={<RoleApi />} />
              <Route path="api-docs/project" element={<ProjectApi />} />
              <Route path="api-docs/project-account" element={<ProjectAccountApi />} />
              <Route path="api-docs/server" element={<ServerApi />} />
              <Route path="api-docs/mail" element={<MailApi />} />
              <Route path="diagnostic" element={<Diagnostic />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  )
}

export default App
