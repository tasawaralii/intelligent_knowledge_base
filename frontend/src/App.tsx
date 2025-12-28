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
import NotesPage from './pages/NotesPage'
import PersonsPage from './pages/PersonsPage'
import PlacesPage from './pages/PlacesPage'
import EventsPage from './pages/EventsPage'
import RelationsPage from './pages/RelationsPage'
import ArchivePage from './pages/ArchivePage'
import BinPage from './pages/BinPage'
import FactsPage from './pages/FactsPage'

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
            <Route path='/notes' element={<NotesPage />} />
            <Route path='/places' element={<PlacesPage />} />
            <Route path='/persons' element={<PersonsPage />} />
            <Route path='/events' element={<EventsPage />} />
            <Route path='/relations' element={<RelationsPage />} />
            <Route path='/facts' element={<FactsPage />} />
            <Route path='/archive' element={<ArchivePage />} />
            <Route path='/bin' element={<BinPage />} />
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
