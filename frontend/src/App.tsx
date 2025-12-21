import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import SigninPage from './pages/SigninPage'
import SignupPage from './pages/SignupPage'
import NotFound from './pages/NotFound'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import { AuthProvider } from './context/authContext'
import Layout from './layout'
import LogoutPage from './pages/LogoutPage'

function App() {

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path='/signin' element={<SigninPage />} />
          <Route path='/signup' element={<SignupPage />} />
          <Route element={<Layout />} >
            <Route path='/' element={<HomePage />} />
            <Route path='/dashboard' element={<DashboardPage />} />
            <Route path='/logout' element={<LogoutPage />} />
          </Route>
          <Route path='*' element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
