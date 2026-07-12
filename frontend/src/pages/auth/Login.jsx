import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../../services/api"
import { useAuth } from "../../context/AuthContext"
import Input from "../../components/Input"
import PublicLayout from "../../components/PublicLayout"

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({ identifier: "", password: "" })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const res = await api.post("/auth/login", {
        email: form.identifier, // backend checks email or username
        password: form.password,
      })
      login(res.data.access_token, res.data.user)
      
      const role = res.data.user.role
      if (role === "student") navigate("/student")
      else if (role === "driver") navigate("/driver")
      else if (role === "admin") navigate("/admin")
      else navigate("/")
    } catch (err) {
      if (err.response?.data?.needs_verification) {
        navigate("/verify-email", { state: { email: form.identifier } })
      } else {
        setError(err.response?.data?.error || "Login failed")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <PublicLayout>
      <div className="flex min-h-[calc(100vh-128px)] items-center justify-center px-4 py-12 relative overflow-hidden">
        {/* Decorative background glows */}
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-brand/10 blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-signal/10 blur-[120px] pointer-events-none" />

        <div className="relative z-10 w-full max-w-[400px] rounded-card border border-ink-800 bg-ink-900 p-6 sm:p-8 shadow-glass">
          <div className="mb-8 text-center">
            <h1 className="font-display text-3xl font-bold text-white">Welcome back</h1>
            <p className="mt-2 text-mist">Log in to your CampusRide account.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email or Username"
              value={form.identifier}
              onChange={(e) => setForm({ ...form, identifier: e.target.value })}
              required
            />
            <div>
              <div className="flex justify-between items-center mb-1">
                 <label className="block text-sm font-medium text-mist">Password</label>
                 <Link to="/forgot-password" className="text-xs font-medium text-signal hover:underline">Forgot password?</Link>
              </div>
              <input
                 type="password"
                 className="w-full rounded-xl border border-ink-700 bg-ink-950 p-3 text-white placeholder-ink-600 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal"
                 value={form.password}
                 onChange={(e) => setForm({ ...form, password: e.target.value })}
                 required
              />
            </div>

            {error && <p className="text-sm font-medium text-coral">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-signal py-3.5 font-bold text-ink-950 shadow-glow transition-all hover:bg-signal-dim disabled:opacity-50 mt-6"
            >
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-mist">
            Don't have an account?{" "}
            <Link to="/register" className="font-medium text-signal hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </PublicLayout>
  )
}
