import { useEffect } from 'react'
import { useAuth } from '../context/authContext'
import { useNavigate } from 'react-router-dom'

const HomePage = () => {
  const navigate = useNavigate()
  const { isLoggedIn } = useAuth()
  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/signin")
    }
  })
  return (
    <div>HomePage</div>
  )
}

export default HomePage