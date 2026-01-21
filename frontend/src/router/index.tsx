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
import ProtectedRoute from '@/components/ProtectedRoute/index'

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
        path: 'user/token',
        element: <TokenList />,
      },
      {
        path: 'user/log',
        element: <LogList />,
      },
      {
        path: 'mail/list',
        element: <MailList />,
      },
    ],
  },
])

export default router
