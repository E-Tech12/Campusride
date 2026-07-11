import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import RouteBackground from "../components/RouteBackground"
import {
  MapPin,
  Users,
  ShieldCheck,
  ArrowRight,
  Car,
  Clock,
  Star,
  ChevronRight,
  Sparkles,
  Menu,
  X,
  User,
  LogOut,
  Settings,
  HelpCircle,
  ChevronDown,
} from "lucide-react"
import { useState } from "react"

export default function Landing() {
  const { user, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const initial = user?.full_name?.charAt(0) || "U"
  const firstName = user?.full_name?.split(" ")[0] || "User"
  const dashboardPath = user?.role === "driver" ? "/driver" : user?.role === "admin" ? "/admin" : "/student"

  return (
    <div className="min-h-screen bg-[#0a0a0f] relative">
      {/* ============================================================
          ANIMATED BACKGROUND (SVG route lines + pulsing driver dots)
          ============================================================ */}
      <div className="fixed inset-0 w-full h-full z-0 overflow-hidden">
        <RouteBackground />
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/40 via-[#0a0a0f]/60 to-[#0a0a0f]/95" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0f]/70 to-transparent" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-green-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      {/* ============================================================
          NAVBAR
          ============================================================ */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0a0f]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center shadow-lg shadow-[#00C853]/20 group-hover:shadow-[#00C853]/40 transition-shadow duration-300">
                <Car size={18} className="text-[#0a0a0f]" strokeWidth={2.5} />
              </div>
              <span className="text-white font-bold text-xl tracking-tight">
                Campus<span className="text-[#00E676]">Ride</span>
              </span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <Link to="/about" className="text-gray-400 hover:text-white text-sm font-medium transition-colors">About</Link>
              <Link to="/safety" className="text-gray-400 hover:text-white text-sm font-medium transition-colors">Safety</Link>
              <Link to="/driver/apply" className="text-gray-400 hover:text-white text-sm font-medium transition-colors">Drivers</Link>
              <Link to="/support" className="text-gray-400 hover:text-white text-sm font-medium transition-colors">Support</Link>
            </div>

            <div className="hidden md:flex items-center gap-3">
              {user ? (
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex items-center gap-2 bg-white/5 hover:bg-white/10 px-4 py-2 rounded-xl transition-all duration-200 border border-white/5 hover:border-white/10"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center text-[#0a0a0f] font-bold text-sm">
                      {initial}
                    </div>
                    <span className="text-white text-sm font-medium">{firstName}</span>
                    <ChevronDown size={16} className={`text-gray-400 transition-transform duration-200 ${dropdownOpen ? "rotate-180" : ""}`} />
                  </button>

                  {dropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-[#14141f]/95 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl py-2 animate-slideDown">
                      <div className="px-4 py-3 border-b border-white/5">
                        <p className="text-white text-sm font-medium">{user.full_name}</p>
                        <p className="text-gray-400 text-xs">{user.email}</p>
                      </div>
                      <Link to={dashboardPath} className="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors text-sm">
                        <User size={16} /> Dashboard
                      </Link>
                      <Link to="/settings" className="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors text-sm">
                        <Settings size={16} /> Settings
                      </Link>
                      <Link to="/help" className="flex items-center gap-3 px-4 py-2.5 text-gray-300 hover:text-white hover:bg-white/5 transition-colors text-sm">
                        <HelpCircle size={16} /> Help
                      </Link>
                      <button
                        onClick={logout}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/5 transition-colors text-sm border-t border-white/5 mt-1"
                      >
                        <LogOut size={16} /> Logout
                      </button>
                    </div>
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
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden text-white p-2 hover:bg-white/5 rounded-xl transition-colors"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {mobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-white/5 animate-slideDown">
              <div className="flex flex-col gap-1">
                <Link to="/about" className="text-gray-400 hover:text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-white/5">About</Link>
                <Link to="/safety" className="text-gray-400 hover:text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-white/5">Safety</Link>
                <Link to="/driver/apply" className="text-gray-400 hover:text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-white/5">Drivers</Link>
                <Link to="/support" className="text-gray-400 hover:text-white px-4 py-2.5 rounded-xl text-sm font-medium transition-colors hover:bg-white/5">Support</Link>
                {user ? (
                  <>
                    <Link to={dashboardPath} className="text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-white/5 transition-colors">Dashboard</Link>
                    <button onClick={logout} className="text-red-400 px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-red-500/5 transition-colors text-left">Logout</button>
                  </>
                ) : (
                  <div className="flex flex-col gap-2 mt-2 px-4">
                    <Link to="/login">
                      <button className="w-full text-gray-300 hover:text-white py-2.5 rounded-xl text-sm font-medium transition-colors">Log in</button>
                    </Link>
                    <Link to="/register">
                      <button className="w-full bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold py-2.5 rounded-xl text-sm hover:shadow-[0_0_30px_rgba(0,200,83,0.15)] transition-all">
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

      <div className="h-16 relative z-10" />

      {/* ============================================================
          HERO
          ============================================================ */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <section className="pt-16 pb-20 lg:pt-24 lg:pb-28 grid lg:grid-cols-2 gap-16 items-center min-h-[calc(100vh-4rem)]">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 bg-[#00C853]/10 text-[#00E676] px-4 py-2 rounded-full text-sm font-medium border border-[#00C853]/20 animate-fadeIn">
              <Sparkles size={16} />
              <span>Now available on campus</span>
            </div>

            <div className="animate-fadeIn animation-delay-200">
              <h1 className="font-display font-bold text-5xl sm:text-6xl lg:text-7xl leading-[1.05] tracking-tight">
                <span className="text-white">Share a seat,</span>
                <br />
                <span className="bg-gradient-to-r from-[#00E676] via-[#00C853] to-[#009624] bg-clip-text text-transparent">
                  not a fare.
                </span>
              </h1>
            </div>

            <p className="text-gray-300 text-lg lg:text-xl leading-relaxed max-w-lg animate-fadeIn animation-delay-300">
              See vetted campus drivers live on the map, check seats left on their route,
              and book your stop for a flat zone price — up to 4 students, one car, one route.
            </p>

            <div className="flex flex-wrap gap-4 pt-2 animate-fadeIn animation-delay-400">
              {user ? (
                <Link to={dashboardPath}>
                  <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-8 py-4 rounded-2xl flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.3)] transition-all duration-300 hover:scale-[1.02]">
                    Go to dashboard
                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                  </button>
                </Link>
              ) : (
                <>
                  <Link to="/register">
                    <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-8 py-4 rounded-2xl flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.3)] transition-all duration-300 hover:scale-[1.02]">
                      Get started
                      <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                  </Link>
                  <Link to="/login">
                    <button className="border border-white/10 text-white px-8 py-4 rounded-2xl font-medium hover:bg-white/5 transition-colors backdrop-blur-sm">
                      Log in
                    </button>
                  </Link>
                </>
              )}
            </div>

            <div className="flex items-center gap-8 pt-4 border-t border-white/5 animate-fadeIn animation-delay-500">
              <div className="flex -space-x-2">
                {["A", "B", "C", "D"].map((letter, i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full border-2 border-[#0a0a0f] bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center text-xs font-bold text-white shadow-lg"
                  >
                    {letter}
                  </div>
                ))}
              </div>
              <div>
                <div className="flex items-center gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} size={16} className="fill-[#00E676] text-[#00E676]" />
                  ))}
                </div>
                <p className="text-sm text-gray-400">
                  Trusted by <span className="text-white font-semibold">500+</span> students
                </p>
              </div>
            </div>
          </div>

          {/* Right - live driver preview card */}
          <div className="relative animate-fadeIn animation-delay-300">
            <div className="absolute -top-4 -left-4 bg-[#14141f]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/30 z-10 animate-float">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-500/20 rounded-xl flex items-center justify-center">
                  <Car size={20} className="text-green-400" />
                </div>
                <div>
                  <p className="text-xs text-gray-400">Active drivers</p>
                  <p className="text-xl font-bold text-white">24 <span className="text-sm font-normal text-gray-400">nearby</span></p>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-4 -right-4 bg-[#14141f]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/30 z-10 animate-float-delayed">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-[#00C853]/20 rounded-xl flex items-center justify-center">
                  <Clock size={20} className="text-[#00E676]" />
                </div>
                <div>
                  <p className="text-xs text-gray-400">Avg. pickup</p>
                  <p className="text-xl font-bold text-white">3 <span className="text-sm font-normal text-gray-400">min</span></p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-[#14141f]/95 to-[#1a1a2e]/95 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl shadow-black/50 hover:shadow-[#00C853]/5 transition-shadow duration-500">
              <div className="flex items-center justify-between mb-6">
                <div className="text-xs text-gray-400 uppercase tracking-widest flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  Live near you
                </div>
                <Link to="/student" className="text-[#00E676] text-sm font-medium hover:text-[#00C853] flex items-center gap-1 transition-colors">
                  View all <ChevronRight size={14} />
                </Link>
              </div>

              <div className="space-y-3">
                {[
                  { name: "Toyota Sienna", color: "Blue", plate: "KJA-204-XY", left: 2, total: 5, eta: "2 min" },
                  { name: "Honda Odyssey", color: "Black", plate: "ABJ-771-LK", left: 4, total: 4, eta: "5 min" },
                  { name: "Tesla Model 3", color: "White", plate: "CAM-003-TS", left: 3, total: 4, eta: "1 min" },
                ].map((d, i) => (
                  <div
                    key={i}
                    className="group flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all duration-300 cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center">
                        <Car size={20} className="text-gray-400" />
                      </div>
                      <div>
                        <div className="font-medium text-white group-hover:text-[#00E676] transition-colors text-sm">
                          {d.name} <span className="text-sm font-normal text-gray-400">· {d.color}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <span className="font-mono">{d.plate}</span>
                          <span className="w-1 h-1 bg-gray-600 rounded-full" />
                          <span className="flex items-center gap-1"><Clock size={12} /> {d.eta}</span>
                        </div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="flex gap-1 justify-end mb-1">
                        {Array.from({ length: d.total }).map((_, j) => (
                          <span
                            key={j}
                            className={`w-2 h-6 rounded-[2px] transition-all duration-300 ${
                              j < d.total - d.left ? "bg-gray-700" : "bg-gradient-to-t from-[#00C853] to-[#00E676]"
                            }`}
                          />
                        ))}
                      </div>
                      <div className="text-xs text-gray-400">
                        <span className="text-[#00E676] font-semibold">{d.left}</span> seats left
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ============================================================
            FEATURES
            ============================================================ */}
        <section className="py-20 relative">
          <div className="text-center mb-16">
            <span className="text-[#00E676] text-sm font-semibold uppercase tracking-wider">Why CampusRide?</span>
            <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mt-3 mb-4">
              Everything you need for{" "}
              <span className="bg-gradient-to-r from-[#00E676] to-[#00C853] bg-clip-text text-transparent">campus travel</span>
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Safe, affordable, and convenient — built specifically for students.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            <Feature
              icon={MapPin}
              title="Live Map"
              desc="See drivers' real-time location and pick the nearest one before you commit."
              iconBg="bg-[#00C853]/20"
              iconColor="text-[#00E676]"
              borderColor="border-[#00C853]/20"
            />
            <Feature
              icon={Users}
              title="Shared Seats"
              desc="Each driver runs a fixed route — up to 4 students can ride together, each to their own stop."
              iconBg="bg-purple-500/20"
              iconColor="text-purple-400"
              borderColor="border-purple-500/20"
            />
            <Feature
              icon={ShieldCheck}
              title="Vetted Drivers"
              desc="Every driver is approved by campus admin, with verified vehicle and license info on file."
              iconBg="bg-blue-500/20"
              iconColor="text-blue-400"
              borderColor="border-blue-500/20"
            />
          </div>
        </section>

        {/* ============================================================
            STATS
            ============================================================ */}
        <section className="py-16 border-t border-white/5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-4xl font-bold text-white">500+</p>
              <p className="text-sm text-gray-400 mt-1">Active riders</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-white">50+</p>
              <p className="text-sm text-gray-400 mt-1">Student drivers</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-white">4.9</p>
              <p className="text-sm text-gray-400 mt-1">Average rating</p>
            </div>
            <div>
              <p className="text-4xl font-bold text-white">24/7</p>
              <p className="text-sm text-gray-400 mt-1">Always available</p>
            </div>
          </div>
        </section>

        {/* ============================================================
            CTA
            ============================================================ */}
        <section className="py-20">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#00C853]/10 via-purple-500/10 to-[#00E676]/10 border border-white/10 p-12 text-center">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#00C853]/5 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl" />

            <div className="relative z-10">
              <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mb-4">
                Ready to{" "}
                <span className="bg-gradient-to-r from-[#00E676] to-[#00C853] bg-clip-text text-transparent">ride smarter</span>?
              </h2>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
                Join hundreds of students already using CampusRide to get around campus.
              </p>
              <Link to="/register">
                <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-10 py-4 rounded-2xl flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.2)] transition-all duration-300 hover:scale-[1.02] mx-auto">
                  Get started now
                  <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>
            </div>
          </div>
        </section>

        {/* ============================================================
            FOOTER
            ============================================================ */}
        <footer className="py-12 border-t border-white/5">
          <div className="grid sm:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00C853] to-[#00E676] flex items-center justify-center">
                  <Car size={16} className="text-[#0a0a0f]" />
                </div>
                <span className="font-bold text-white text-lg">CampusRide</span>
              </div>
              <p className="text-sm text-gray-400">Safe & reliable campus transportation for students.</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">How it works</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Safety</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-3">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/5 mt-8 pt-8 text-center text-sm text-gray-500">
            <p>&copy; 2026 CampusRide. All rights reserved.</p>
          </div>
        </footer>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-12px); }
        }
        .animate-float { animation: float 4s ease-in-out infinite; }
        .animate-float-delayed { animation: float 4s ease-in-out infinite 1.5s; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn { animation: fadeIn 0.6s ease-out forwards; }
        .animation-delay-200 { animation-delay: 0.2s; }
        .animation-delay-300 { animation-delay: 0.3s; }
        .animation-delay-400 { animation-delay: 0.4s; }
        .animation-delay-500 { animation-delay: 0.5s; }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slideDown { animation: slideDown 0.3s ease-out forwards; }
        @media (prefers-reduced-motion: reduce) {
          .animate-float, .animate-float-delayed, .animate-fadeIn, .animate-slideDown { animation: none; }
        }
      `}</style>
    </div>
  )
}

function Feature({ icon: Icon, title, desc, iconBg, iconColor, borderColor }) {
  return (
    <div className={`group p-8 rounded-2xl border ${borderColor} bg-white/5 hover:bg-white/10 transition-all duration-300 hover:scale-[1.02] hover:shadow-[0_0_40px_rgba(0,200,83,0.05)]`}>
      <div className={`w-14 h-14 rounded-2xl ${iconBg} flex items-center justify-center ${iconColor} mb-5 group-hover:scale-110 transition-transform duration-300`}>
        <Icon size={24} />
      </div>
      <h3 className="font-display font-semibold text-white text-lg mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
    </div>
  )
}
