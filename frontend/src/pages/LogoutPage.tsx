import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'

const LogoutPage = () => {
    useEffect(() => {
        localStorage.removeItem("access_token")
    },[])
  return (
    <Navigate to={"/signin"} />
  )
}

export default LogoutPage