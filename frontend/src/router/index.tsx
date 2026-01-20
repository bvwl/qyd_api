import { createBrowserRouter, Navigate } from 'react-router-dom'
import Login from '@/views/Login/index'
import Layout from '@/components/Layout/index'
import UserList from '@/views/User/UserList'
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
        element: <Navigate to="/user/list" replace />,
      },
      {
        path: 'user/list',
        element: <UserList />,
      },
      {
        path: 'mail/list',
        element: <MailList />,
      },
    ],
  },
])

export default router
