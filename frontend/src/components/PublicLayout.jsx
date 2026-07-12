import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { Car, Menu, X, User, LogOut, HelpCircle, ChevronDown } from "lucide-react"
import { useState } from "react"

// Shared header + footer for every public-facing page (landing, about, safety,
// support, become a driver, contact, terms, privacy, faq, and all auth pages).
// This is what makes those pages feel like one connected product instead of
// disconnected screens: same logo, same nav, same footer, same way home.
const PUBLIC_LINKS = [
  { to: "/about", label: "About" },
  { to: "/safety", label: "Safety" },
  { to: "/become-a-driver", label: "Drivers" },
  { to: "/support", label: "Support" },
]

export default function PublicLayout({ children, transparentTop = false }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const initial = user?.full_name?.charAt(0) || "U"
  const firstName = user?.full_name?.split(" ")[0] || "User"
  const dashboardPath = user?.role === "driver" ? "/driver" : user?.role === "admin" ? "/admin" : "/student"

  const handleLogout = () => {
    logout()
    navigate("/")
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col">
      {/* ============================ NAVBAR ============================ */}
      <nav className={`sticky top-0 z-50 bg-[#0a0a0f]/80 backdrop-blur-xl border-b border-white/5 ${transparentTop ? "" : ""}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2.5 group shrink-0">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center shadow-lg shadow-[#00C853]/20 group-hover:shadow-[#00C853]/40 transition-shadow duration-300">
                <Car size={18} className="text-[#0a0a0f]" strokeWidth={2.5} />
              </div>
              <span className="text-white font-bold text-xl tracking-tight">
                Campus<span className="text-[#00E676]">Ride</span>
              </span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              {PUBLIC_LINKS.map((l) => (
                <Link key={l.to} to={l.to} className="text-gray-400 hover:text-white text-sm font-medium transition-colors">
                  {l.label}
                </Link>
              ))}
            </div>

            <div className="hidden md:flex items-center gap-3">
              {user ? (
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen((v) => !v)}
                    className="flex items-center gap-2 bg-white/5 hover:bg-white/10 px-4 py-2 rounded-xl transition-all duration-200 border border-white/5 hover:border-white/10"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center text-[#0a0a0f] font-bold text-sm">
                      {initial}
                    </div>
                    <span className="text-white text-sm font-medium">{firstName}</span>
                    <ChevronDown size={16} className={`text-gray-400 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} />
                  </button>

                  {dropdownOpen && (
                    <>
                      <div className="fixed inset-0 z-40" onClick={() => setDropdownOpen(false)} />
                      <div className="absolute right-0 mt-2 w-56 bg-[#14141f]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl py-2 z-50">
                        <div className="px-4 py-3 border-b border-white/5">
                          <p className="text-white text-sm font-medium">{user.full_name}</p>
                          <p className="text-gray-400 text-xs">{user.email}</p>
                        </div>
                        <Link
                          to={dashboardPath}
                          onClick={() => setDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors text-sm"
                        >
                          <User size={16} /> Dashboard
                        </Link>
                        <Link
                          to="/support"
                          onClick={() => setDropdownOpen(false)}
                          className="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors text-sm"
                        >
                          <HelpCircle size={16} /> Help
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-colors text-sm border-t border-white/5 mt-1"
                        >
                          <LogOut size={16} /> Logout
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <>
                  <Link to="/login">
                    <button className="text-gray-300 hover:text-white px-5 py-2 rounded-xl text-sm font-medium transition-colors">Log in</button>
                  </Link>
                  <Link to="/register">
                    <button className="bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-6 py-2.5 rounded-xl text-sm hover:shadow-[0_0_30px_rgba(0,200,83,0.2)] transition-all duration-300 hover:scale-[1.02]">
                      Get started
                    </button>
                  </Link>
                </>
              )}
            </div>

            <button
              onClick={() => setMobileMenuOpen((v) => !v)}
              className="md:hidden text-white p-2 hover:bg-white/5 rounded-xl transition-colors"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-white/5">
              <div className="flex flex-col gap-1">
                {PUBLIC_LINKS.map((l) => (
                  <Link
                    key={l.to}
                    to={l.to}
                    onClick={() => setMobileMenuOpen(false)}
                    className="text-gray-400 hover:text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-white/5"
                  >
                    {l.label}
                  </Link>
                ))}
                <div className="h-px bg-white/5 my-2" />
                {user ? (
                  <>
                    <Link
                      to={dashboardPath}
                      onClick={() => setMobileMenuOpen(false)}
                      className="text-white px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-white/5"
                    >
                      Go to dashboard
                    </Link>
                    <button
                      onClick={() => {
                        setMobileMenuOpen(false)
                        handleLogout()
                      }}
                      className="text-left text-red-400 px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-red-500/5"
                    >
                      Log out
                    </button>
                  </>
                ) : (
                  <div className="flex flex-col gap-2 px-4 pt-2">
                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                      <button className="w-full text-gray-300 border border-white/10 px-5 py-2.5 rounded-xl text-sm font-medium">Log in</button>
                    </Link>
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                      <button className="w-full bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-6 py-2.5 rounded-xl text-sm">
                        Get started
                      </button>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      <div className="flex-1">{children}</div>

      {/* ============================ FOOTER ============================ */}
      <footer className="border-t border-white/5 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8">
            <div className="col-span-2 md:col-span-1">
              <Link to="/" className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center">
                  <Car size={16} className="text-[#0a0a0f]" />
                </div>
                <span className="font-bold text-white text-lg">CampusRide</span>
              </Link>
              <p className="text-sm text-gray-400">Safe, reliable, student-run transportation for campus life.</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3 text-sm">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link to="/safety" className="hover:text-white transition-colors">Safety</Link></li>
                <li><Link to="/become-a-driver" className="hover:text-white transition-colors">Become a Driver</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3 text-sm">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/support" className="hover:text-white transition-colors">Help center</Link></li>
                <li><Link to="/faq" className="hover:text-white transition-colors">FAQ</Link></li>
                <li><Link to="/contact" className="hover:text-white transition-colors">Contact support</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3 text-sm">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/5 mt-8 pt-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-gray-500">
            <p>&copy; {new Date().getFullYear()} CampusRide. All rights reserved.</p>
            <div className="flex gap-4">
              <Link to="/terms" className="hover:text-gray-300 transition-colors">Terms</Link>
              <Link to="/privacy" className="hover:text-gray-300 transition-colors">Privacy</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
