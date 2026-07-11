import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet"
import L from "leaflet"
import { useEffect, useRef } from "react"
import SeatBoard from "./SeatBoard"

const driverIcon = L.divIcon({
  className: "",
  html: `<div style="
    width:34px;height:34px;border-radius:10px;
    background:#D6F23C;display:flex;align-items:center;justify-content:center;
    box-shadow:0 0 0 3px #0B0F14, 0 4px 12px rgba(0,0,0,0.5);
    font-size:16px;">🚐</div>`,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
})

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

  return (
    <div className="rounded-card overflow-hidden border border-ink-600 h-full">
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
        {drivers
          .filter((d) => d.current_lat && d.current_lng)
          .map((d) => (
            <AnimatedMarker
              key={d.id}
              position={[d.current_lat, d.current_lng]}
              icon={driverIcon}
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
    </div>
  )
}
