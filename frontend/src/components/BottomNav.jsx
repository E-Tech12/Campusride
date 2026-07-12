import { Link, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { MapPin, LayoutDashboard, Car, ShieldCheck, Wallet, BarChart3, PieChart } from "lucide-react"

// Persistent bottom tab bar for small screens, in the style of Uber/Bolt/
// modern fintech apps. Desktop keeps the top NavBar's horizontal links;
// this only renders below the md breakpoint and only once a role is known.
export default function BottomNav() {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) return null

  let tabs = []
  if (user.role === "student") {
    tabs = [
      { to: "/student", label: "Ride", icon: MapPin },
      { to: "/student/history", label: "Trips", icon: LayoutDashboard },
      { to: "/student/wallet", label: "Wallet", icon: Wallet },
      { to: "/driver/apply", label: "Drive", icon: Car },
    ]
  } else if (user.role === "driver") {
    tabs = [
      { to: "/driver", label: "Console", icon: Car },
      { to: "/driver/earnings", label: "Earnings", icon: BarChart3 },
    ]
  } else if (user.role === "admin") {
    tabs = [
      { to: "/admin", label: "Ops", icon: ShieldCheck },
      { to: "/admin/finance", label: "Finance", icon: PieChart },
    ]
  }

  if (!tabs.length) return null

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-ink-950/95 backdrop-blur border-t border-ink-700 pb-[env(safe-area-inset-bottom)]"
      aria-label="Primary"
    >
      <div className={`grid`} style={{ gridTemplateColumns: `repeat(${tabs.length}, minmax(0, 1fr))` }}>
        {tabs.map((t) => {
          const Icon = t.icon
          const active = location.pathname === t.to
          return (
            <Link
              key={t.to}
              to={t.to}
              className="relative flex flex-col items-center justify-center gap-1 py-2.5 min-h-[56px] active:scale-95 transition-transform"
            >
              {active && (
                <span className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full bg-signal" />
              )}
              <Icon size={20} strokeWidth={active ? 2.4 : 2} className={active ? "text-signal" : "text-mist"} />
              <span className={`text-[10px] font-medium leading-none ${active ? "text-signal" : "text-mist"}`}>
                {t.label}
              </span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
