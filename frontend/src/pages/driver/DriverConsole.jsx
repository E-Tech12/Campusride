import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import api from "../../services/api"
import { getSocket } from "../../services/socket"
import { useGeolocation } from "../../hooks/useGeolocation"
import Card from "../../components/Card"
import Button from "../../components/Button"
import SeatBoard from "../../components/SeatBoard"
import StatusBadge from "../../components/StatusBadge"
import { Power, MapPin, Route as RouteIcon } from "lucide-react"

export default function DriverConsole() {
  const navigate = useNavigate()
  const { position } = useGeolocation(true)
  const [driver, setDriver] = useState(null)
  const [routes, setRoutes] = useState([])
  const [requests, setRequests] = useState([])
  const [toggling, setToggling] = useState(false)
  const [error, setError] = useState("")

  const refresh = useCallback(async () => {
    const [driverRes, routesRes, requestsRes] = await Promise.all([
      api.get("/driver/me"),
      api.get("/driver/routes"),
      api.get("/driver/requests"),
    ])
    setDriver(driverRes.data)
    setRoutes(routesRes.data)
    setRequests(requestsRes.data)
  }, [])

  useEffect(() => { refresh() }, [refresh])

  useEffect(() => {
    const socket = getSocket()
    const onNewRequest = (req) => setRequests((prev) => [req, ...prev])
    const onRequestUpdate = (req) =>
      setRequests((prev) => prev.map((r) => (r.id === req.id ? req : r)))
    socket.on("new_ride_request", onNewRequest)
    socket.on("ride_request_update", onRequestUpdate)
    return () => {
      socket.off("new_ride_request", onNewRequest)
      socket.off("ride_request_update", onRequestUpdate)
    }
  }, [])

  // push live location while online
  useEffect(() => {
    if (!driver?.is_online || !position) return
    api.post("/driver/location", position).catch(() => {})
    const socket = getSocket()
    socket.emit("driver_location_ping", { driver_id: driver.id, ...position })
  }, [driver?.is_online, position?.lat, position?.lng])

  const handleToggle = async () => {
    if (!driver) return
    setToggling(true)
    setError("")
    try {
      if (driver.is_online) {
        await api.post("/driver/go-offline")
      } else {
        if (!routes.length) {
          setError("Set up a route before going online")
          setToggling(false)
          return
        }
        await api.post("/driver/go-online", {
          route_id: driver.active_route_id || routes[0].id,
          lat: position?.lat,
          lng: position?.lng,
        })
      }
      await refresh()
    } catch (err) {
      setError(err.response?.data?.error || "Could not update status")
    } finally {
      setToggling(false)
    }
  }

  const handleRespond = async (requestId, decision) => {
    await api.post(`/driver/requests/${requestId}/respond`, { decision })
    refresh()
  }

  const handlePickup = async (requestId) => {
    await api.post(`/driver/requests/${requestId}/pickup`)
    refresh()
  }

  const handleComplete = async (requestId) => {
    await api.post(`/driver/requests/${requestId}/complete`)
    refresh()
  }

  if (!driver) return null

  const pending = requests.filter((r) => r.status === "pending")
  const active = requests.filter((r) => ["accepted", "ongoing"].includes(r.status))
  const history = requests.filter((r) => ["completed", "rejected", "cancelled"].includes(r.status))

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="font-display font-bold text-2xl">Driver console</h1>
          <p className="text-mist text-sm">{driver.vehicle_color} {driver.vehicle_make} {driver.vehicle_model} · {driver.plate_number}</p>
        </div>
        <Button
          variant={driver.is_online ? "danger" : "primary"}
          onClick={handleToggle}
          loading={toggling}
          className="gap-2"
        >
          <Power size={16} /> {driver.is_online ? "Go offline" : "Go online"}
        </Button>
      </div>

      {error && <p className="text-sm text-coral mb-4">{error}</p>}

      <Card className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <SeatBoard capacity={driver.seat_capacity} available={driver.seats_available} />
        <button
          onClick={() => navigate("/driver/route-setup")}
          className="flex items-center gap-2 text-sm text-signal hover:underline"
        >
          <RouteIcon size={15} /> {routes.length ? "Manage routes" : "Set up a route"}
        </button>
      </Card>

      {pending.length > 0 && (
        <Section title="Incoming requests">
          {pending.map((r) => (
            <Card key={r.id} className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="font-medium text-sm">{r.student_name}</div>
                <div className="text-xs text-mist flex items-center gap-1"><MapPin size={12} /> Destination: {r.zone?.name}</div>
                {(r.distance_km != null || r.eta_minutes != null) && (
                  <div className="text-xs text-mist mt-0.5">
                    {r.distance_km != null && <>{r.distance_km} km away</>}
                    {r.distance_km != null && r.eta_minutes != null && <> · </>}
                    {r.eta_minutes != null && <>~{r.eta_minutes} min to pickup</>}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-3">
                <span className="font-mono-num text-sm text-signal">₦{r.price}</span>
                <Button variant="outline" className="px-3 py-1.5 text-xs" onClick={() => handleRespond(r.id, "reject")}>Decline</Button>
                <Button className="px-3 py-1.5 text-xs" onClick={() => handleRespond(r.id, "accept")}>Accept</Button>
              </div>
            </Card>
          ))}
        </Section>
      )}

      {active.length > 0 && (
        <Section title="Active passengers">
          {active.map((r) => (
            <Card key={r.id} className="flex items-center justify-between flex-wrap gap-3">
              <div>
                <div className="font-medium text-sm">{r.student_name}</div>
                <div className="text-xs text-mist flex items-center gap-1"><MapPin size={12} /> {r.zone?.name}</div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={r.status} />
                {r.status === "accepted" && (
                  <Button className="px-3 py-1.5 text-xs" onClick={() => handlePickup(r.id)}>Picked up</Button>
                )}
                {r.status === "ongoing" && (
                  <Button className="px-3 py-1.5 text-xs" onClick={() => handleComplete(r.id)}>Drop off</Button>
                )}
              </div>
            </Card>
          ))}
        </Section>
      )}

      {history.length > 0 && (
        <Section title="History">
          {history.slice(0, 10).map((r) => (
            <Card key={r.id} className="flex items-center justify-between">
              <div>
                <div className="font-medium text-sm">{r.student_name}</div>
                <div className="text-xs text-mist">{r.zone?.name}</div>
              </div>
              <StatusBadge status={r.status} />
            </Card>
          ))}
        </Section>
      )}

      {!pending.length && !active.length && !history.length && (
        <Card className="text-center text-mist py-10">No requests yet. Go online to start receiving them.</Card>
      )}
    </div>
  )
}

function Section({ title, children }) {
  return (
    <div className="mb-6">
      <div className="font-mono-num text-xs uppercase tracking-wide text-mist mb-2">{title}</div>
      <div className="space-y-2">{children}</div>
    </div>
  )
}
