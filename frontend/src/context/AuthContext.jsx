import { createContext, useContext, useState, useEffect, useCallback } from "react"
import api from "../services/api"
import { connectSocket, disconnectSocket } from "../services/socket"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("cr_user")
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  const refreshMe = useCallback(async () => {
    const token = localStorage.getItem("cr_token")
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const res = await api.get("/auth/me")
      setUser(res.data)
      localStorage.setItem("cr_user", JSON.stringify(res.data))
    } catch (e) {
      // interceptor handles 401 redirect
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshMe()
  }, [refreshMe])

  useEffect(() => {
    if (user) {
      connectSocket()
    }
    return () => disconnectSocket()
  }, [user?.id])

  const login = (userData, token) => {
    localStorage.setItem("cr_token", token)
    localStorage.setItem("cr_user", JSON.stringify(userData))
    setUser(userData)
  }
  
  const logout = () => {
    localStorage.removeItem("cr_token")
    localStorage.removeItem("cr_user")
    disconnectSocket()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, login, logout, refreshMe, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
