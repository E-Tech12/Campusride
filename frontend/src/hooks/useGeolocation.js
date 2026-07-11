import { useState, useEffect, useRef } from "react"

export function useGeolocation(watch = false) {
  const [position, setPosition] = useState(null)
  const [error, setError] = useState(null)
  const watchId = useRef(null)

  useEffect(() => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by this browser")
      return
    }

    const onSuccess = (pos) => {
      setPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude })
      setError(null)
    }
    const onError = (err) => setError(err.message)

    if (watch) {
      watchId.current = navigator.geolocation.watchPosition(onSuccess, onError, {
        enableHighAccuracy: true,
        maximumAge: 5000,
        timeout: 10000,
      })
    } else {
      navigator.geolocation.getCurrentPosition(onSuccess, onError, {
        enableHighAccuracy: true,
        timeout: 10000,
      })
    }

    return () => {
      if (watchId.current !== null) {
        navigator.geolocation.clearWatch(watchId.current)
      }
    }
  }, [watch])

  return { position, error }
}
