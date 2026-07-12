import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import RouteBackground from "../components/RouteBackground"
import PublicLayout from "../components/PublicLayout"
import {
  MapPin,
  Users,
  ShieldCheck,
  ArrowRight,
  Car,
  Clock,
  ChevronRight,
  Sparkles,
  UserPlus,
  Navigation,
  Flag,
  Star,
} from "lucide-react"
import { useState, useEffect } from "react"
import api from "../services/api"
import { useReveal } from "../hooks/useReveal"

const STEPS = [
  { icon: UserPlus, title: "Request a ride", desc: "Pick your pickup point and destination on campus, then send your request." },
  { icon: Car, title: "Driver accepts", desc: "A nearby vetted driver on that route accepts and heads your way." },
  { icon: Navigation, title: "Track live", desc: "Watch your driver move toward you in real time, with a live ETA." },
  { icon: Flag, title: "Reach destination", desc: "Hop in, ride with fellow students, and get dropped off at your stop." },
]

const TESTIMONIALS = [
  { name: "Amara O.", role: "300L Computer Science", quote: "I stopped worrying about getting to early morning classes. I can see the driver coming before I even leave my room." },
  { name: "Tunde A.", role: "CampusRide Driver", quote: "Driving between classes covers my transport costs and then some. The earnings dashboard makes it easy to track." },
  { name: "Chidera N.", role: "200L Law", quote: "Being able to see seats left before booking is the feature I didn't know I needed. No more guessing." },
]

export default function Landing() {
  const { user } = useAuth()
  const [platformStats, setPlatformStats] = useState(null)

  useEffect(() => {
    api.get("/admin/public-stats").then((res) => setPlatformStats(res.data)).catch(() => {})
  }, [])

  const [featuresRef, featuresVisible] = useReveal()
  const [statsRef, statsVisible] = useReveal()
  const [stepsRef, stepsVisible] = useReveal()
  const [testimonialsRef, testimonialsVisible] = useReveal()
  const [ctaRef, ctaVisible] = useReveal()
  const revealCls = (visible) =>
    `transition-all duration-700 ease-out ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}`

  const dashboardPath = user?.role === "driver" ? "/driver" : user?.role === "admin" ? "/admin" : "/student"

  return (
    <PublicLayout>
      <div className="min-h-screen bg-[#0a0a0f] relative">
        {/* ANIMATED BACKGROUND */}
        <div className="fixed inset-0 w-full h-full z-0 overflow-hidden pointer-events-none">
          <RouteBackground />
          <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/40 via-[#0a0a0f]/60 to-[#0a0a0f]/95" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0a0a0f]/70 to-transparent" />
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-green-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl animate-pulse delay-1000" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* ============================ HERO ============================ */}
          <section className="pt-12 pb-20 lg:pt-16 lg:pb-28 grid lg:grid-cols-2 gap-16 items-center min-h-[calc(100vh-8rem)]">
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
                  <p className="text-sm text-gray-400">
                    Trusted by <span className="text-white font-semibold">{platformStats ? `${platformStats.total_students}+` : "growing numbers of"}</span> students
                  </p>
                </div>
              </div>
            </div>

            {/* Right - live driver preview card (illustrative product preview) */}
            <div className="relative animate-fadeIn animation-delay-300">
              <div className="absolute -top-4 -left-4 bg-[#14141f]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/30 z-10 animate-float">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-500/20 rounded-xl flex items-center justify-center">
                    <Car size={20} className="text-green-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Active drivers</p>
                    <p className="text-xl font-bold text-white">
                      {platformStats ? platformStats.total_drivers : "—"} <span className="text-sm font-normal text-gray-400">on campus</span>
                    </p>
                  </div>
                </div>
              </div>

              <div className="absolute -bottom-4 -right-4 bg-[#14141f]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl shadow-black/30 z-10 animate-float-delayed">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-[#00C853]/20 rounded-xl flex items-center justify-center">
                    <Clock size={20} className="text-[#00E676]" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Rides completed</p>
                    <p className="text-xl font-bold text-white">{platformStats ? platformStats.completed_rides : "—"}</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#14141f]/95 to-[#1a1a2e]/95 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl shadow-black/50 hover:shadow-[#00C853]/5 transition-shadow duration-500">
                <div className="flex items-center justify-between mb-6">
                  <div className="text-xs text-gray-400 uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                    Live near you
                  </div>
                  <Link to={user ? "/student" : "/register"} className="text-[#00E676] text-sm font-medium hover:text-[#00C853] flex items-center gap-1 transition-colors">
                    View all <ChevronRight size={14} />
                  </Link>
                </div>

                <div className="space-y-3">
                  {[
                    { name: "Toyota Sienna", color: "Blue", left: 2, total: 5, eta: "2 min" },
                    { name: "Honda Odyssey", color: "Black", left: 4, total: 4, eta: "5 min" },
                    { name: "Tesla Model 3", color: "White", left: 3, total: 4, eta: "1 min" },
                  ].map((d, i) => (
                    <div
                      key={i}
                      className="group flex items-center justify-between p-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 transition-all duration-300"
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
                            <span className="flex items-center gap-1"><Clock size={12} /> ETA {d.eta}</span>
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
                <p className="text-[11px] text-gray-600 mt-4 text-center">Sample preview — sign in to see live drivers near you</p>
              </div>
            </div>
          </section>

          {/* ============================ HOW IT WORKS ============================ */}
          <section ref={stepsRef} className={`py-20 border-t border-white/5 ${revealCls(stepsVisible)}`}>
            <div className="text-center mb-16">
              <span className="text-[#00E676] text-sm font-semibold uppercase tracking-wider">How it works</span>
              <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mt-3 mb-4">
                From request to <span className="bg-gradient-to-r from-[#00E676] to-[#00C853] bg-clip-text text-transparent">drop-off</span>, in four steps
              </h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {STEPS.map((s, i) => (
                <div key={s.title} className="relative p-6 rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 transition-all duration-300">
                  <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-[#0a0a0f] border border-[#00C853]/40 text-[#00E676] text-xs font-bold flex items-center justify-center">
                    {i + 1}
                  </div>
                  <div className="w-12 h-12 rounded-xl bg-[#00C853]/15 text-[#00E676] flex items-center justify-center mb-4">
                    <s.icon size={22} />
                  </div>
                  <h3 className="font-display font-semibold text-white mb-1.5">{s.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{s.desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* ============================ FEATURES ============================ */}
          <section ref={featuresRef} className={`py-20 relative ${revealCls(featuresVisible)}`}>
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

          {/* ============================ STATS ============================ */}
          <section ref={statsRef} className={`py-16 border-t border-white/5 ${revealCls(statsVisible)}`}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
              <div>
                <p className="text-4xl font-bold text-white">{platformStats ? `${platformStats.total_students}+` : "—"}</p>
                <p className="text-sm text-gray-400 mt-1">Registered students</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-white">{platformStats ? platformStats.total_drivers : "—"}</p>
                <p className="text-sm text-gray-400 mt-1">Approved drivers</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-white">{platformStats ? platformStats.completed_rides : "—"}</p>
                <p className="text-sm text-gray-400 mt-1">Rides completed</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-white">24/7</p>
                <p className="text-sm text-gray-400 mt-1">Always available</p>
              </div>
            </div>
          </section>

          {/* ============================ TESTIMONIALS ============================ */}
          <section ref={testimonialsRef} className={`py-20 border-t border-white/5 ${revealCls(testimonialsVisible)}`}>
            <div className="text-center mb-16">
              <span className="text-[#00E676] text-sm font-semibold uppercase tracking-wider">Voices from campus</span>
              <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mt-3">What riders and drivers say</h2>
            </div>
            <div className="grid sm:grid-cols-3 gap-6">
              {TESTIMONIALS.map((t) => (
                <div key={t.name} className="p-6 rounded-2xl border border-white/10 bg-white/5">
                  <div className="flex gap-0.5 mb-4 text-[#00E676]">
                    {Array.from({ length: 5 }).map((_, i) => <Star key={i} size={14} fill="currentColor" />)}
                  </div>
                  <p className="text-gray-300 text-sm leading-relaxed mb-5">"{t.quote}"</p>
                  <div>
                    <p className="text-white text-sm font-semibold">{t.name}</p>
                    <p className="text-gray-500 text-xs">{t.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ============================ FAQ PREVIEW ============================ */}
          <section className="py-20 border-t border-white/5">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-8 sm:p-12 flex flex-col sm:flex-row items-center justify-between gap-6">
              <div>
                <h2 className="font-display font-bold text-2xl sm:text-3xl text-white mb-2">Still have questions?</h2>
                <p className="text-gray-400">Answers on pricing, safety, wallet top-ups, and becoming a driver.</p>
              </div>
              <Link to="/faq" className="shrink-0">
                <button className="bg-white/10 hover:bg-white/15 border border-white/10 text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 transition-colors">
                  Visit FAQ <ArrowRight size={16} />
                </button>
              </Link>
            </div>
          </section>

          {/* ============================ CTA ============================ */}
          <section ref={ctaRef} className={`py-20 ${revealCls(ctaVisible)}`}>
            <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#00C853]/10 via-purple-500/10 to-[#00E676]/10 border border-white/10 p-12 text-center">
              <div className="absolute top-0 right-0 w-64 h-64 bg-[#00C853]/5 rounded-full blur-3xl" />
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl" />

              <div className="relative z-10">
                <h2 className="font-display font-bold text-3xl sm:text-4xl text-white mb-4">
                  Ready to{" "}
                  <span className="bg-gradient-to-r from-[#00E676] to-[#00C853] bg-clip-text text-transparent">ride smarter</span>?
                </h2>
                <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
                  Join students already using CampusRide to get around campus.
                </p>
                {user ? (
                  <Link to={dashboardPath}>
                    <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-10 py-4 rounded-2xl flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.2)] transition-all duration-300 hover:scale-[1.02] mx-auto">
                      Go to dashboard
                      <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                  </Link>
                ) : (
                  <Link to="/register">
                    <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-10 py-4 rounded-2xl flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.2)] transition-all duration-300 hover:scale-[1.02] mx-auto">
                      Get started now
                      <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                    </button>
                  </Link>
                )}
              </div>
            </div>
          </section>
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
          @media (prefers-reduced-motion: reduce) {
            .animate-float, .animate-float-delayed, .animate-fadeIn { animation: none; }
          }
        `}</style>
      </div>
    </PublicLayout>
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
