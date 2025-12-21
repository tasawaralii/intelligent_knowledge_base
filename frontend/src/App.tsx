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
import ComingSoonPage from './pages/ComingSoonPage'

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
            <Route path='/notes' element={<ComingSoonPage />} />
            <Route path='/places' element={<ComingSoonPage />} />
            <Route path='/persons' element={<ComingSoonPage />} />
            <Route path='/events' element={<ComingSoonPage />} />
            <Route path='/archive' element={<ComingSoonPage />} />
            <Route path='/bin' element={<ComingSoonPage />} />
            <Route path='/settings' element={<ComingSoonPage />} />
            <Route path='/logout' element={<LogoutPage />} />
          </Route>
          <Route path='*' element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
