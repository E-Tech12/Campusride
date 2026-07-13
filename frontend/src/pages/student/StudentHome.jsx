import { useState, useEffect, useCallback } from "react"
import api from "../../services/api"
import { getSocket } from "../../services/socket"
import { useGeolocation } from "../../hooks/useGeolocation"
import LiveMap from "../../components/LiveMap"
import SeatBoard from "../../components/SeatBoard"
import Card from "../../components/Card"
import Button from "../../components/Button"
import StatusBadge from "../../components/StatusBadge"
import { Navigation, X, MapPin } from "lucide-react"

export default function StudentHome() {
  const { position, error: geoError } = useGeolocation(true)
  const [drivers, setDrivers] = useState([])
  const [selected, setSelected] = useState(null)
  const [bookingZone, setBookingZone] = useState(null)
  const [booking, setBooking] = useState(false)
  const [bookingError, setBookingError] = useState("")
  const [activeRequest, setActiveRequest] = useState(null)

  const fetchNearby = useCallback(async () => {
    if (!position) return
    try {
      const res = await api.get("/rides/nearby-drivers", {
        params: { lat: position.lat, lng: position.lng, radius_km: 5 },
      })
      setDrivers(res.data)
    } catch (e) {
      // ignore
    }
  }, [position])

  useEffect(() => {
    fetchNearby()
    const interval = setInterval(fetchNearby, 8000)
    return () => clearInterval(interval)
  }, [fetchNearby])

  useEffect(() => {
    // check for an existing active request on load
    api.get("/rides/my-requests").then((res) => {
      const active = res.data.find((r) => ["pending", "accepted", "ongoing"].includes(r.status))
      if (active) setActiveRequest(active)
    })
  }, [])

  useEffect(() => {
    const socket = getSocket()
    socket.emit("subscribe_location")
    
    const onLocationUpdate = (data) => {
      setDrivers((prev) =>
        prev.map((d) => (d.id === data.driver_id ? { ...d, current_lat: data.lat, current_lng: data.lng } : d))
      )
    }
    const onStatusUpdate = (driverData) => {
      setDrivers((prev) => {
        const exists = prev.some((d) => d.id === driverData.id)
        if (!driverData.is_online) return prev.filter((d) => d.id !== driverData.id)
        if (exists) return prev.map((d) => (d.id === driverData.id ? { ...d, ...driverData } : d))
        return prev
      })
    }
    const onRequestUpdate = (req) => {
      setActiveRequest((prev) => (prev && prev.id === req.id ? req : prev))
    }

    socket.on("driver_location_update", onLocationUpdate)
    socket.on("driver_status_update", onStatusUpdate)
    socket.on("ride_request_update", onRequestUpdate)
    return () => {
      socket.emit("unsubscribe_location")
      socket.off("driver_location_update", onLocationUpdate)
      socket.off("driver_status_update", onStatusUpdate)
      socket.off("ride_request_update", onRequestUpdate)
    }
  }, [])

  const handleRequestSeat = async () => {
    if (!selected || !bookingZone) return
    setBooking(true)
    setBookingError("")
    try {
      const res = await api.post("/rides/request", {
        driver_id: selected.id,
        zone_id: bookingZone.id,
        pickup_lat: position?.lat,
        pickup_lng: position?.lng,
      })
      setActiveRequest(res.data.ride_request)
      setSelected(null)
      setBookingZone(null)
    } catch (err) {
      setBookingError(err.response?.data?.error || "Could not request seat")
    } finally {
      setBooking(false)
    }
  }

  const handleCancel = async () => {
    if (!activeRequest) return
    await api.post(`/rides/requests/${activeRequest.id}/cancel`)
    setActiveRequest(null)
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
      <div className="flex items-center justify-between flex-wrap gap-2 mb-4">
        <h1 className="font-display font-bold text-2xl">Find a ride</h1>
        {geoError && <span className="text-xs text-coral">Enable location to see nearby drivers</span>}
      </div>

      {activeRequest && (
        <Card className="mb-4 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            <StatusBadge status={activeRequest.status} />
            <div>
              <div className="font-medium text-sm">Trip to {activeRequest.zone?.name}</div>
              <div className="text-xs text-mist font-mono-num">₦{activeRequest.price}</div>
            </div>
          </div>
          {["pending", "accepted"].includes(activeRequest.status) && (
            <Button variant="danger" onClick={handleCancel} className="text-xs px-3 py-1.5">
              Cancel request
            </Button>
          )}
        </Card>
      )}

      <div className="grid lg:grid-cols-[1fr_360px] gap-6">
        <div className="h-[65vh] min-h-[320px] max-h-[460px] lg:h-[600px] lg:max-h-none">
          <LiveMap myPosition={position} drivers={drivers} onSelectDriver={setSelected} />
        </div>

        <div className="space-y-3">
          <div className="font-mono-num text-xs uppercase tracking-wide text-mist mb-1">
            {drivers.length} driver{drivers.length !== 1 ? "s" : ""} nearby
          </div>
          {drivers.length === 0 && (
            <Card className="text-center text-mist text-sm py-10">
              <MapPin className="mx-auto mb-2 text-mist" size={24} />
              No drivers online nearby right now.
            </Card>
          )}
          {drivers.map((d) => (
            <Card
              key={d.id}
              className="cursor-pointer hover:border-signal/40 transition-colors"
              onClick={() => setSelected(d)}
            >
              <div className="flex justify-between items-start gap-2 mb-2 flex-wrap">
                <div className="min-w-0">
                  <div className="font-medium text-sm truncate">{d.vehicle_color} {d.vehicle_make} {d.vehicle_model}</div>
                  <div className="text-xs text-mist font-mono-num">{d.plate_number}</div>
                </div>
                {d.distance_km != null && (
                  <span className="flex items-center gap-1 text-xs text-signal font-mono-num shrink-0">
                    <Navigation size={12} /> {d.distance_km} km{d.eta_minutes != null ? ` · ~${d.eta_minutes} min` : ""}
                  </span>
                )}
              </div>
              <SeatBoard capacity={d.seat_capacity} available={d.seats_available} />
              {d.active_route && (
                <div className="mt-2 text-xs text-mist truncate">{d.active_route.name}</div>
              )}
            </Card>
          ))}
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4" onClick={() => setSelected(null)}>
          <div onClick={(e) => e.stopPropagation()} className="bg-ink-800 border border-ink-600 rounded-card p-4 sm:p-6 max-w-md w-full max-h-[85vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4 gap-3">
              <div className="min-w-0">
                <h2 className="font-display font-semibold text-lg truncate">{selected.vehicle_color} {selected.vehicle_make} {selected.vehicle_model}</h2>
                <p className="text-sm text-mist font-mono-num">{selected.plate_number}</p>
              </div>
              <button onClick={() => setSelected(null)} className="text-mist hover:text-white shrink-0 -mr-1 p-1"><X size={20} /></button>
            </div>

            <SeatBoard capacity={selected.seat_capacity} available={selected.seats_available} />

            <div className="mt-5">
              <div className="text-sm font-medium mb-2">Choose your stop</div>
              <div className="space-y-2">
                {selected.active_route?.stops?.map((stop) => (
                  <button
                    key={stop.id}
                    onClick={() => setBookingZone(stop.zone)}
                    className={`w-full flex justify-between items-center px-4 py-3 rounded-xl border text-left transition-colors ${
                      bookingZone?.id === stop.zone.id
                        ? "border-signal bg-signal/10"
                        : "border-ink-600 hover:border-ink-500"
                    }`}
                  >
                    <span className="text-sm">{stop.zone.name}</span>
                    <span className="font-mono-num text-sm text-signal">₦{stop.zone.price}</span>
                  </button>
                ))}
                {!selected.active_route?.stops?.length && (
                  <p className="text-sm text-mist">This driver has no route stops set.</p>
                )}
              </div>
            </div>

            {bookingError && <p className="text-sm text-coral mt-3">{bookingError}</p>}

            <Button
              onClick={handleRequestSeat}
              disabled={!bookingZone || selected.seats_available <= 0}
              loading={booking}
              className="w-full mt-5"
            >
              {selected.seats_available <= 0 ? "No seats available" : bookingZone ? `Request seat · ₦${bookingZone.price}` : "Select a stop"}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
