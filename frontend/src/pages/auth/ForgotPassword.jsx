import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../services/api"
import Input from "../../components/Input"
import Button from "../../components/Button"
import Card from "../../components/Card"

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState("")

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.post("/auth/forgot-password", { email })
      setInfo("If that email exists, a reset code has been sent.")
      setTimeout(() => navigate("/reset-password", { state: { email } }), 1200)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 pt-16">
      <h1 className="font-display font-bold text-3xl mb-2">Forgot password</h1>
      <p className="text-mist mb-8">We'll email you a reset code.</p>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          {info && <p className="text-sm text-signal">{info}</p>}
          <Button type="submit" loading={loading} className="w-full">Send reset code</Button>
        </form>
      </Card>
    </div>
  )
}
