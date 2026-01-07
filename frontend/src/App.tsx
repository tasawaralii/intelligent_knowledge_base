import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import SigninPage from './pages/SigninPage'
import SignupPage from './pages/SignupPage'
import NotFound from './pages/NotFound'
import HomePage from './pages/HomePage'
import PersonDetailPage from './pages/PersonDetailPage'
import DashboardPage from './pages/DashboardPage'
import { AuthProvider } from './context/authContext'
import { AlertProvider } from './context/alertContext'
import { AlertContainer } from './components/Alert'
import Layout from './layout'
import LogoutPage from './pages/LogoutPage'
import ComingSoonPage from './pages/ComingSoonPage'
import NotesPage from './pages/NotesPage'
import NotePage from './pages/NotePage'
import PersonsPage from './pages/PersonsPage'
import PlacesPage from './pages/PlacesPage'
import EventsPage from './pages/EventsPage'
import RelationsPage from './pages/RelationsPage'
import ArchivePage from './pages/ArchivePage'
import BinPage from './pages/BinPage'
import FactsPage from './pages/FactsPage'
import { FamilyTreePage } from './pages/FamilyTreePage'

function App() {

  return (
    <AuthProvider>
      <AlertProvider>
        <AlertContainer />
        <Router>
          <Routes>
            <Route path='/signin' element={<SigninPage />} />
            <Route path='/signup' element={<SignupPage />} />
            <Route element={<Layout />} >
              <Route path='/' element={<HomePage />} />
              <Route path='/dashboard' element={<DashboardPage />} />
              <Route path='/notes' element={<NotesPage />} />
              <Route path='/notes/:note_id' element={<NotePage />} />
              <Route path='/places/:place_slug?' element={<PlacesPage />} />
              <Route path='/persons' element={<PersonsPage />} />
              <Route path='/persons/:person_slug' element={<PersonDetailPage />} />
              <Route path='/events/:event_slug?' element={<EventsPage />} />
              <Route path='/relations' element={<RelationsPage />} />
              <Route path='/facts' element={<FactsPage />} />
              <Route path='/family-tree/:person_id' element={<FamilyTreePage />} />
              <Route path='/archive' element={<ArchivePage />} />
              <Route path='/bin' element={<BinPage />} />
              <Route path='/settings' element={<ComingSoonPage />} />
              <Route path='/logout' element={<LogoutPage />} />
            </Route>
            <Route path='*' element={<NotFound />} />
          </Routes>
        </Router>
      </AlertProvider>
    </AuthProvider>
  )
}

export default App
