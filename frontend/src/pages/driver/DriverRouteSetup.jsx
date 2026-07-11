import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../services/api"
import Card from "../../components/Card"
import Button from "../../components/Button"
import Input from "../../components/Input"
import { GripVertical, X, Plus } from "lucide-react"

export default function DriverRouteSetup() {
  const navigate = useNavigate()
  const [zones, setZones] = useState([])
  const [existingRoutes, setExistingRoutes] = useState([])
  const [name, setName] = useState("")
  const [selectedStops, setSelectedStops] = useState([]) // ordered array of zone objects
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get("/rides/zones").then((res) => setZones(res.data))
    api.get("/driver/routes").then((res) => setExistingRoutes(res.data))
  }, [])

  const addStop = (zone) => {
    if (selectedStops.find((s) => s.id === zone.id)) return
    setSelectedStops([...selectedStops, zone])
  }

  const removeStop = (zoneId) => {
    setSelectedStops(selectedStops.filter((s) => s.id !== zoneId))
  }

  const moveStop = (index, direction) => {
    const newStops = [...selectedStops]
    const target = index + direction
    if (target < 0 || target >= newStops.length) return
    ;[newStops[index], newStops[target]] = [newStops[target], newStops[index]]
    setSelectedStops(newStops)
  }

  const handleSubmit = async () => {
    setError("")
    if (!name || selectedStops.length === 0) {
      setError("Name your route and add at least one stop")
      return
    }
    setLoading(true)
    try {
      await api.post("/driver/route", {
        name,
        zone_ids: selectedStops.map((s) => s.id),
      })
      navigate("/driver")
    } catch (err) {
      setError(err.response?.data?.error || "Could not create route")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6">
      <h1 className="font-display font-bold text-2xl mb-2">Set up your route</h1>
      <p className="text-mist text-sm mb-6">Pick the stops along your path, in order. Students will book a seat to one of these stops at its fixed price.</p>

      {existingRoutes.length > 0 && (
        <Card className="mb-6">
          <div className="font-mono-num text-xs uppercase tracking-wide text-mist mb-3">Your routes</div>
          <div className="space-y-2">
            {existingRoutes.map((r) => (
              <div key={r.id} className="text-sm flex justify-between items-center py-2 border-b border-ink-700 last:border-0">
                <span>{r.name}</span>
                <span className="text-mist text-xs">{r.stops.length} stops</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="mb-6">
        <Input label="Route name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Main Gate to Off-Campus" />
      </Card>

      <div className="grid sm:grid-cols-2 gap-6">
        <Card>
          <div className="font-mono-num text-xs uppercase tracking-wide text-mist mb-3">Available zones</div>
          <div className="space-y-2">
            {zones.map((z) => (
              <button
                key={z.id}
                onClick={() => addStop(z)}
                disabled={selectedStops.some((s) => s.id === z.id)}
                className="w-full flex justify-between items-center px-3 py-2.5 rounded-lg border border-ink-600 hover:border-signal/40 disabled:opacity-30 disabled:cursor-not-allowed text-left text-sm transition-colors"
              >
                <span>{z.name}</span>
                <span className="flex items-center gap-2 font-mono-num text-signal text-xs">
                  ₦{z.price} <Plus size={14} />
                </span>
              </button>
            ))}
          </div>
        </Card>

        <Card>
          <div className="font-mono-num text-xs uppercase tracking-wide text-mist mb-3">Your route, in order</div>
          {selectedStops.length === 0 && <p className="text-sm text-mist">Add stops from the left.</p>}
          <div className="space-y-2">
            {selectedStops.map((s, i) => (
              <div key={s.id} className="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-ink-600 bg-ink-900">
                <span className="font-mono-num text-xs text-mist w-5">{i + 1}</span>
                <span className="flex-1 text-sm">{s.name}</span>
                <span className="font-mono-num text-signal text-xs">₦{s.price}</span>
                <div className="flex flex-col">
                  <button onClick={() => moveStop(i, -1)} disabled={i === 0} className="text-mist hover:text-white disabled:opacity-20 text-xs leading-none">▲</button>
                  <button onClick={() => moveStop(i, 1)} disabled={i === selectedStops.length - 1} className="text-mist hover:text-white disabled:opacity-20 text-xs leading-none">▼</button>
                </div>
                <button onClick={() => removeStop(s.id)} className="text-mist hover:text-coral"><X size={14} /></button>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {error && <p className="text-sm text-coral mt-4">{error}</p>}
      <Button onClick={handleSubmit} loading={loading} className="w-full mt-6">Save route</Button>
    </div>
  )
}
