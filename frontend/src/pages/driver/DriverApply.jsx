import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../services/api"
import Input from "../../components/Input"
import Button from "../../components/Button"
import Card from "../../components/Card"
import StatusBadge from "../../components/StatusBadge"

export default function DriverApply() {
  const navigate = useNavigate()
  const [existing, setExisting] = useState(null)
  const [checking, setChecking] = useState(true)
  const [form, setForm] = useState({
    vehicle_make: "", vehicle_model: "", vehicle_color: "",
    plate_number: "", license_number: "", seat_capacity: 4,
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get("/driver/me")
      .then((res) => setExisting(res.data))
      .catch(() => setExisting(null))
      .finally(() => setChecking(false))
  }, [])

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const res = await api.post("/driver/apply", form)
      setExisting(res.data.driver)
    } catch (err) {
      setError(err.response?.data?.error || "Application failed")
    } finally {
      setLoading(false)
    }
  }

  if (checking) return null

  if (existing) {
    return (
      <div className="max-w-md mx-auto px-4 pt-16">
        <h1 className="font-display font-bold text-3xl mb-2">Driver application</h1>
        <Card className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-mist">Status</span>
            <StatusBadge status={existing.status} />
          </div>
          <div className="space-y-2 text-sm">
            <Row label="Vehicle" value={`${existing.vehicle_color} ${existing.vehicle_make} ${existing.vehicle_model}`} />
            <Row label="Plate" value={existing.plate_number} />
            <Row label="Seats" value={existing.seat_capacity} />
          </div>
          {existing.status === "pending" && (
            <p className="text-xs text-mist mt-4">Your application is awaiting admin review. You'll be able to go online once approved.</p>
          )}
          {existing.status === "rejected" && (
            <p className="text-xs text-coral mt-4">Rejected: {existing.rejection_reason}</p>
          )}
          {existing.status === "approved" && (
            <Button className="w-full mt-4" onClick={() => navigate("/driver")}>Go to driver console</Button>
          )}
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto px-4 pt-16 pb-16">
      <h1 className="font-display font-bold text-3xl mb-2">Become a driver</h1>
      <p className="text-mist mb-8">Submit your vehicle details for admin approval.</p>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input label="Make" value={form.vehicle_make} onChange={handleChange("vehicle_make")} required placeholder="Toyota" />
            <Input label="Model" value={form.vehicle_model} onChange={handleChange("vehicle_model")} required placeholder="Sienna" />
          </div>
          <Input label="Color" value={form.vehicle_color} onChange={handleChange("vehicle_color")} required placeholder="Blue" />
          <Input label="Plate number" value={form.plate_number} onChange={handleChange("plate_number")} required placeholder="KJA-204-XY" />
          <Input label="License number" value={form.license_number} onChange={handleChange("license_number")} required />
          <Input
            label="Seat capacity"
            type="number"
            min={1}
            max={8}
            value={form.seat_capacity}
            onChange={handleChange("seat_capacity")}
            required
          />
          {error && <p className="text-sm text-coral">{error}</p>}
          <Button type="submit" loading={loading} className="w-full">Submit application</Button>
        </form>
      </Card>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between">
      <span className="text-mist">{label}</span>
      <span>{value}</span>
    </div>
  )
}
