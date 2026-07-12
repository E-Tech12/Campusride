import { Link, useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { MapPin, LayoutDashboard, Car, ShieldCheck, LogOut, Menu, X, Wallet, BarChart3, PieChart } from "lucide-react"
import { useState } from "react"

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const links = []
  if (user?.role === "student") {
    links.push({ to: "/student", label: "Find a ride", icon: MapPin })
    links.push({ to: "/student/history", label: "My trips", icon: LayoutDashboard })
    links.push({ to: "/student/wallet", label: "Wallet", icon: Wallet })
    links.push({ to: "/driver/apply", label: "Become a driver", icon: Car })
  }
  if (user?.role === "driver") {
    links.push({ to: "/driver", label: "Driver console", icon: Car })
    links.push({ to: "/driver/earnings", label: "Earnings", icon: BarChart3 })
  }
  if (user?.role === "admin") {
    links.push({ to: "/admin", label: "Admin", icon: ShieldCheck })
    links.push({ to: "/admin/finance", label: "Finance", icon: PieChart })
  }

  return (
    <header className="sticky top-0 z-50 bg-ink-950/90 backdrop-blur border-b border-ink-700">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-display font-bold text-lg text-white">
          <span className="w-8 h-8 rounded-lg bg-signal flex items-center justify-center text-ink-950">
            <MapPin size={18} strokeWidth={2.5} />
          </span>
          CampusRide
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {links.map((l) => {
            const Icon = l.icon
            const active = location.pathname === l.to
            return (
              <Link
                key={l.to}
                to={l.to}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-colors ${
                  active ? "bg-signal/10 text-signal" : "text-mist hover:text-white hover:bg-ink-800"
                }`}
              >
                <Icon size={16} />
                {l.label}
              </Link>
            )
          })}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          {user ? (
            <>
              <span className="text-sm text-mist">{user.full_name}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-sm text-mist hover:text-coral transition-colors"
              >
                <LogOut size={15} /> Log out
              </button>
            </>
          ) : (
            <div className="flex gap-2">
              <Link to="/login" className="text-sm font-medium text-mist hover:text-white">Log in</Link>
              <Link to="/register" className="text-sm font-semibold bg-signal text-ink-950 px-4 py-2 rounded-lg">Sign up</Link>
            </div>
          )}
        </div>

        <button className="md:hidden text-white" onClick={() => setOpen(!open)}>
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-ink-700 px-4 py-3 space-y-1 bg-ink-950">
          {/* Primary section links live in the bottom tab bar on mobile; this
              drawer only surfaces account-level actions to avoid duplicating
              the same nav in two places. */}
          {user ? (
            <>
              <div className="px-3 py-2 text-sm text-mist">Signed in as <span className="text-white font-medium">{user.full_name}</span></div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium text-coral hover:bg-ink-800"
              >
                <LogOut size={16} /> Log out
              </button>
            </>
          ) : (
            <div className="flex gap-2 pt-2">
              <Link to="/login" onClick={() => setOpen(false)} className="flex-1 text-center py-2.5 rounded-lg border border-ink-600 text-sm">Log in</Link>
              <Link to="/register" onClick={() => setOpen(false)} className="flex-1 text-center py-2.5 rounded-lg bg-signal text-ink-950 text-sm font-semibold">Sign up</Link>
            </div>
          )}
        </div>
      )}
    </header>
  )
}
