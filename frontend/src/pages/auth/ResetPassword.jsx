import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import api from "../../services/api"
import Input from "../../components/Input"
import Button from "../../components/Button"
import Card from "../../components/Card"
import PublicLayout from "../../components/PublicLayout"

export default function ResetPassword() {
  const location = useLocation()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: location.state?.email || "",
    otp_code: "",
    new_password: "",
  })
  const [confirm, setConfirm] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    if (form.new_password !== confirm) {
      setError("Passwords do not match")
      return
    }
    setLoading(true)
    try {
      await api.post("/auth/reset-password", form)
      navigate("/login")
    } catch (err) {
      setError(err.response?.data?.error || "Reset failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <PublicLayout>
    <div className="max-w-md mx-auto px-4 py-16">
      <h1 className="font-display font-bold text-3xl mb-2 text-white">Reset password</h1>
      <p className="text-mist mb-8">Enter the code from your email and a new password.</p>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={form.email} onChange={handleChange("email")} required />
          <Input
            label="Reset code"
            value={form.otp_code}
            onChange={handleChange("otp_code")}
            maxLength={6}
            className="font-mono-num text-center text-lg tracking-widest"
            required
          />
          <Input label="New password" type="password" value={form.new_password} onChange={handleChange("new_password")} minLength={6} required />
          <Input label="Confirm new password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} minLength={6} required />
          {error && <p className="text-sm text-coral">{error}</p>}
          <Button type="submit" loading={loading} className="w-full">Reset password</Button>
        </form>
      </Card>
    </div>
    </PublicLayout>
  )
}
