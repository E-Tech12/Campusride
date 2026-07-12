import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import api from "../../services/api"
import { useAuth } from "../../context/AuthContext"
import Input from "../../components/Input"
import Button from "../../components/Button"
import Card from "../../components/Card"
import PublicLayout from "../../components/PublicLayout"

export default function VerifyEmail() {
  const location = useLocation()
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState(location.state?.email || "")
  const [otp, setOtp] = useState("")
  const [error, setError] = useState("")
  const [info, setInfo] = useState("")
  const [loading, setLoading] = useState(false)
  const [resending, setResending] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const res = await api.post("/auth/verify-email", { email, otp_code: otp })
      login(res.data.access_token, res.data.user)
      const role = res.data.user.role
      if (role === "driver") navigate("/driver")
      else if (role === "admin") navigate("/admin")
      else navigate("/student")
    } catch (err) {
      setError(err.response?.data?.error || "Verification failed")
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResending(true)
    setError("")
    setInfo("")
    try {
      await api.post("/auth/resend-otp", { email, purpose: "email_verification" })
      setInfo("A new code has been sent.")
    } catch (err) {
      setError(err.response?.data?.error || "Could not resend code")
    } finally {
      setResending(false)
    }
  }

  return (
    <PublicLayout>
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="font-display font-bold text-3xl mb-2 text-white">Verify your email</h1>
      <p className="text-mist mb-8">Enter the 6-digit code we sent to your email.</p>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input
            label="Verification code"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength={6}
            placeholder="000000"
            className="font-mono-num text-center text-lg tracking-widest"
            required
          />
          {error && <p className="text-sm text-coral">{error}</p>}
          {info && <p className="text-sm text-signal">{info}</p>}
          <Button type="submit" loading={loading} className="w-full">Verify</Button>
        </form>
        <button
          onClick={handleResend}
          disabled={resending}
          className="mt-4 text-sm text-mist hover:text-signal disabled:opacity-50"
        >
          {resending ? "Sending..." : "Resend code"}
        </button>
      </Card>
    </div>
    </PublicLayout>
  )
}
