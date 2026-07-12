import { useEffect, useRef, useState } from "react"

// Tiny scroll-reveal hook: attach the returned ref to any element and it
// gets `true` once it scrolls into view, so callers can fade/slide it in.
// No animation library needed -- plain IntersectionObserver + CSS transition.
export function useReveal(options = {}) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { threshold: 0.15, ...options }
    )
    observer.observe(node)
    return () => observer.disconnect()
  }, [])

  return [ref, visible]
}
