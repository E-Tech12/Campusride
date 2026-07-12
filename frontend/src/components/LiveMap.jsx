import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline } from "react-leaflet"
import L from "leaflet"
import { useEffect, useRef, useMemo } from "react"
import SeatBoard from "./SeatBoard"

function buildDriverIcon(heading) {
  return L.divIcon({
    className: "",
    html: `<div style="
      width:34px;height:34px;border-radius:10px;
      background:#D6F23C;display:flex;align-items:center;justify-content:center;
      box-shadow:0 0 0 3px #0B0F14, 0 4px 12px rgba(0,0,0,0.5);
      font-size:16px;transform:rotate(${heading}deg);transition:transform 400ms ease;">🚐</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  })
}

const meIcon = L.divIcon({
  className: "",
  html: `<div style="
    width:16px;height:16px;border-radius:50%;
    background:#3B82F6;box-shadow:0 0 0 4px rgba(59,130,246,0.25), 0 0 0 2px #0B0F14;"></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8],
})

function Recenter({ lat, lng }) {
  const map = useMap()
  useEffect(() => {
    if (lat && lng) map.setView([lat, lng], map.getZoom(), { animate: true })
  }, [lat, lng])
  return null
}

// Compass bearing in degrees (0 = north) from point A to point B, used to
// rotate the vehicle marker so it visually faces its direction of travel.
function bearing(lat1, lng1, lat2, lng2) {
  const toRad = (d) => (d * Math.PI) / 180
  const toDeg = (r) => (r * 180) / Math.PI
  const y = Math.sin(toRad(lng2 - lng1)) * Math.cos(toRad(lat2))
  const x =
    Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
    Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(toRad(lng2 - lng1))
  return (toDeg(Math.atan2(y, x)) + 360) % 360
}

const ANIMATION_MS = 800

// Wraps a Leaflet marker and glides it to new positions instead of
// teleporting, so drivers appear to move smoothly across the map as
// location pings come in.
function AnimatedMarker({ position, icon, eventHandlers, children }) {
  const markerRef = useRef(null)
  const animRef = useRef(null)
  const currentPos = useRef(position)

  useEffect(() => {
    const marker = markerRef.current
    if (!marker) return
    const from = currentPos.current
    const to = position
    if (!from || (from[0] === to[0] && from[1] === to[1])) return

    if (animRef.current) cancelAnimationFrame(animRef.current)
    const start = performance.now()

    const step = (now) => {
      const t = Math.min(1, (now - start) / ANIMATION_MS)
      const lat = from[0] + (to[0] - from[0]) * t
      const lng = from[1] + (to[1] - from[1]) * t
      marker.setLatLng([lat, lng])
      if (t < 1) {
        animRef.current = requestAnimationFrame(step)
      } else {
        currentPos.current = to
      }
    }
    animRef.current = requestAnimationFrame(step)
    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [position?.[0], position?.[1]])

  return (
    <Marker ref={markerRef} position={position} icon={icon} eventHandlers={eventHandlers}>
      {children}
    </Marker>
  )
}

export default function LiveMap({ myPosition, drivers, onSelectDriver, selectedDriverId }) {
  const center = myPosition || { lat: 6.5244, lng: 3.3792 } // fallback default
  const prevPosRef = useRef({})
  const headingRef = useRef({})

  // Recomputes per-driver heading whenever a new ping moves them.
  const driverIcons = useMemo(() => {
    const icons = {}
    drivers.forEach((d) => {
      if (d.current_lat == null || d.current_lng == null) return
      const prev = prevPosRef.current[d.id]
      if (prev && (prev.lat !== d.current_lat || prev.lng !== d.current_lng)) {
        headingRef.current[d.id] = bearing(prev.lat, prev.lng, d.current_lat, d.current_lng)
      }
      prevPosRef.current[d.id] = { lat: d.current_lat, lng: d.current_lng }
      icons[d.id] = buildDriverIcon(headingRef.current[d.id] || 0)
    })
    return icons
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drivers])

  const selectedDriver = drivers.find((d) => d.id === selectedDriverId)

  // Straight-line path from you to the selected driver, and on to their
  // first route stop if it has coordinates. This is a direct-line visual
  // guide, not a turn-by-turn road route (no routing engine is wired up).
  const routePath = useMemo(() => {
    if (!selectedDriver || !myPosition) return null
    const points = [[myPosition.lat, myPosition.lng], [selectedDriver.current_lat, selectedDriver.current_lng]]
    const firstStop = selectedDriver.active_route?.stops?.find((s) => s.zone?.lat && s.zone?.lng)
    if (firstStop) points.push([firstStop.zone.lat, firstStop.zone.lng])
    return points
  }, [selectedDriver, myPosition])

  return (
    <div className="rounded-card overflow-hidden border border-ink-600 h-full relative">
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={15}
        scrollWheelZoom={true}
        style={{ height: "100%", width: "100%", minHeight: "420px" }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap &copy; CARTO'
        />
        {myPosition && (
          <>
            <Marker position={[myPosition.lat, myPosition.lng]} icon={meIcon}>
              <Popup>You are here</Popup>
            </Marker>
            <Recenter lat={myPosition.lat} lng={myPosition.lng} />
          </>
        )}
        {routePath && (
          <Polyline
            positions={routePath}
            pathOptions={{ color: "#D6F23C", weight: 3, opacity: 0.8, dashArray: "6 8" }}
          />
        )}
        {drivers
          .filter((d) => d.current_lat && d.current_lng)
          .map((d) => (
            <AnimatedMarker
              key={d.id}
              position={[d.current_lat, d.current_lng]}
              icon={driverIcons[d.id] || buildDriverIcon(0)}
              eventHandlers={{ click: () => onSelectDriver(d) }}
            >
              <Popup>
                <div className="font-display font-semibold text-ink-950 mb-1">
                  {d.vehicle_color} {d.vehicle_make} {d.vehicle_model}
                </div>
                <div className="text-xs text-ink-700 mb-2">{d.plate_number}</div>
                <SeatBoard capacity={d.seat_capacity} available={d.seats_available} />
              </Popup>
            </AnimatedMarker>
          ))}
      </MapContainer>

      {/* Nearest-driver ETA card, floated above the map like Uber/Bolt */}
      {!selectedDriver && drivers.length > 0 && drivers[0].eta_minutes != null && (
        <div className="absolute top-3 left-3 right-3 sm:right-auto sm:max-w-xs bg-ink-900/95 backdrop-blur border border-ink-700 rounded-xl px-4 py-3 shadow-glass z-[400]">
          <div className="text-[10px] uppercase tracking-wide text-mist font-mono-num mb-1">Nearest driver</div>
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <div className="text-sm font-medium text-white truncate">
                {drivers[0].vehicle_color} {drivers[0].vehicle_make} {drivers[0].vehicle_model}
              </div>
              <div className="text-xs text-mist truncate">{drivers[0].plate_number} · {drivers[0].distance_km} km</div>
            </div>
            <div className="text-right shrink-0">
              <div className="font-mono-num text-lg font-bold text-signal leading-none">{drivers[0].eta_minutes}</div>
              <div className="text-[10px] text-mist">min ETA</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
