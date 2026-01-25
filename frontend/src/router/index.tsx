import { createBrowserRouter, Navigate } from 'react-router-dom'
import Login from '@/views/Login/index'
import Layout from '@/components/Layout/index'
import Dashboard from '@/views/Dashboard/index'
import UserList from '@/views/User/UserList'
import RoleList from '@/views/User/RoleList'
import RouteList from '@/views/User/RouteList'
import TokenList from '@/views/User/TokenList'
import LogList from '@/views/User/LogList'
import MailList from '@/views/Mail/MailList'
import MailViewer from '@/views/Mail/MailViewer'
import MailSend from '@/views/Mail/MailSend'
import ProjectList from '@/views/Project/ProjectList'
import ProjectAccount from '@/views/Project/ProjectAccount'
import ProjectWallet from '@/views/Project/ProjectWallet'
import WalletBatchCreate from '@/views/Project/WalletBatchCreate'
import ServerList from '@/views/Server/ServerList'
import CountryList from '@/views/Server/CountryList'
import GroupList from '@/views/Server/GroupList'
import ServerAccount from '@/views/Server/ServerAccount'
import XuiServerList from '@/views/Xui/XuiServerList'
import XuiInboundList from '@/views/Xui/XuiInboundList'
import XuiAccountManage from '@/views/Xui/XuiAccountManage'
import XuiAccountList from '@/views/Xui/XuiAccountList'
import XuiOperationLog from '@/views/Xui/XuiOperationLog'
import ProtectedRoute from '@/components/ProtectedRoute/index'
import PermissionManageWorking from '@/views/User/PermissionManageWorking'

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: <ProtectedRoute><Layout /></ProtectedRoute>,
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <Dashboard />,
      },
      {
        path: 'user/list',
        element: <UserList />,
      },
      {
        path: 'user/role',
        element: <RoleList />,
      },
      {
        path: 'user/route',
        element: <RouteList />,
      },
      {
        path: 'user/permission',
        element: <PermissionManageWorking />,
      },
      {
        path: 'user/token',
        element: <TokenList />,
      },
      {
        path: 'user/log',
        element: <LogList />,
      },
      {
        path: 'project/list',
        element: <ProjectList />,
      },
      {
        path: 'project/account',
        element: <ProjectAccount />,
      },
      {
        path: 'project/wallet/batch-create',
        element: <WalletBatchCreate />,
      },
      {
        path: 'project/wallet',
        element: <ProjectWallet />,
      },
      {
        path: 'server/list',
        element: <ServerList />,
      },
      {
        path: 'server/country',
        element: <CountryList />,
      },
      {
        path: 'server/group',
        element: <GroupList />,
      },
      {
        path: 'server/account',
        element: <ServerAccount />,
      },
      {
        path: 'mail/list',
        element: <MailList />,
      },
      {
        path: 'mail/send',
        element: <MailSend />,
      },
      {
        path: 'mail/viewer',
        element: <MailViewer />,
      },
      {
        path: 'xui/server',
        element: <XuiServerList />,
      },
      {
        path: 'xui/inbound',
        element: <XuiInboundList />,
      },
      {
        path: 'xui/account',
        element: <XuiAccountList />,
      },
      {
        path: 'xui/log',
        element: <XuiOperationLog />,
      },
    ],
  },
])

export default router
