import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import api from "../../services/api"
import Input from "../../components/Input"
import PublicLayout from "../../components/PublicLayout"
import { GraduationCap, Car, Check } from "lucide-react"

export default function Register() {
  const navigate = useNavigate()
  const [role, setRole] = useState("student")
  const [form, setForm] = useState({
    full_name: "", email: "", username: "", student_id: "", phone: "", password: "",
    license_number: "", vehicle_make: "", vehicle_model: "", plate_number: "", vehicle_color: "", seat_capacity: "4"
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await api.post("/auth/register", { ...form, role })
      navigate("/verify-email", { state: { email: form.email } })
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <PublicLayout>
    <div className="flex min-h-[calc(100vh-128px)] items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Decorative background glows */}
      <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-signal/10 blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] rounded-full bg-brand/10 blur-[120px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-lg rounded-card border border-ink-800 bg-ink-900 p-5 sm:p-8 shadow-glass">
        <div className="mb-8 text-center">
          <h1 className="font-display text-3xl font-bold text-white">Create your account</h1>
          <p className="mt-2 text-mist">Join CampusRide and start your journey.</p>
        </div>

        <div className="relative mb-8 grid grid-cols-2 rounded-2xl border border-ink-800 bg-ink-950 p-1.5">
          <div
            className="absolute inset-y-1.5 left-1.5 w-[calc(50%-6px)] rounded-xl bg-gradient-to-r from-signal to-signal-dim shadow-glow transition-transform duration-300 ease-out"
            style={{ transform: role === "driver" ? "translateX(100%)" : "translateX(0)" }}
          />
          <button
            type="button"
            onClick={() => setRole("student")}
            className={`relative z-10 flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-colors duration-200 ${
              role === "student" ? "text-ink-950" : "text-mist hover:text-white"
            }`}
          >
            <GraduationCap size={16} />
            Student
            {role === "student" && <Check size={14} className="opacity-80" />}
          </button>
          <button
            type="button"
            onClick={() => setRole("driver")}
            className={`relative z-10 flex items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-colors duration-200 ${
              role === "driver" ? "text-ink-950" : "text-mist hover:text-white"
            }`}
          >
            <Car size={16} />
            Driver
            {role === "driver" && <Check size={14} className="opacity-80" />}
          </button>
        </div>
        <p className="-mt-5 mb-6 text-center text-xs text-mist">
          {role === "student"
            ? "Book rides across campus with your student account."
            : "Apply to drive students on your route and start earning."}
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input label="Full Name" value={form.full_name} onChange={handleChange("full_name")} required />
          <Input label="Email Address" type="email" value={form.email} onChange={handleChange("email")} required />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Username" value={form.username} onChange={handleChange("username")} required />
            <Input label="Phone Number" value={form.phone} onChange={handleChange("phone")} />
          </div>

          {role === "student" && (
            <Input label="Student ID" value={form.student_id} onChange={handleChange("student_id")} required />
          )}

          {role === "driver" && (
            <div className="space-y-5 border-t border-ink-800 pt-5 mt-2">
              <h3 className="font-display text-sm uppercase tracking-wider text-mist">Vehicle Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input label="License Number" value={form.license_number} onChange={handleChange("license_number")} required />
                <Input label="Plate Number" value={form.plate_number} onChange={handleChange("plate_number")} required />
                <Input label="Vehicle Make" value={form.vehicle_make} onChange={handleChange("vehicle_make")} placeholder="e.g. Toyota" required />
                <Input label="Vehicle Model" value={form.vehicle_model} onChange={handleChange("vehicle_model")} placeholder="e.g. Camry" required />
                <Input label="Vehicle Color" value={form.vehicle_color} onChange={handleChange("vehicle_color")} required />
                <Input label="Seat Capacity" type="number" value={form.seat_capacity} onChange={handleChange("seat_capacity")} required min="1" max="10" />
              </div>
            </div>
          )}

          <div className="pt-2">
             <Input label="Password" type="password" value={form.password} onChange={handleChange("password")} required minLength={6} />
          </div>
          
          {error && <p className="text-sm font-medium text-coral">{error}</p>}
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full rounded-xl bg-signal py-3.5 font-bold text-ink-950 shadow-glow transition-all hover:bg-signal-dim disabled:opacity-50 mt-6"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-mist">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-signal hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
    </PublicLayout>
  )
}
