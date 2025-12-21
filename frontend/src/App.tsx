import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import SigninPage from './pages/SigninPage'
import SignupPage from './pages/SignupPage'
import NotFound from './pages/NotFound'
import HomePage from './pages/HomePage'
import { AuthProvider } from './context/authContext'
import Layout from './layout'

function App() {

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path='/signin' element={<SigninPage />} />
          <Route path='/signup' element={<SignupPage />} />
          <Route element={<Layout />} >
            <Route path='/' element={<HomePage />} />
          </Route>
          <Route path='*' element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
