import { Link } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"
import PublicLayout from "../../components/PublicLayout"
import { PageHero, Section } from "../../components/PublicPageKit"
import { CheckCircle2, FileCheck, Wallet, TrendingUp, ArrowRight, ClipboardList } from "lucide-react"

const REQUIREMENTS = [
  "A valid driver's license",
  "A registered vehicle with a valid plate number",
  "An active CampusRide student or driver account",
  "Willingness to run a fixed campus route with defined stops",
]

const STEPS = [
  { title: "Create an account", desc: "Sign up or log in with your existing CampusRide account." },
  { title: "Submit your application", desc: "Fill in your license, vehicle make, model, plate number, color, and seat capacity." },
  { title: "Admin review", desc: "Campus admins verify your details — most applications are reviewed within a short turnaround." },
  { title: "Go live", desc: "Once approved, set your route and stops, go online, and start accepting ride requests." },
]

export default function BecomeDriver() {
  const { user } = useAuth()
  const applyHref = !user ? "/register" : user.role === "student" ? "/driver/apply" : user.role === "driver" ? "/driver" : "/admin"
  const applyLabel = !user ? "Create an account to apply" : user.role === "student" ? "Start your application" : user.role === "driver" ? "Go to driver console" : "Go to admin dashboard"

  return (
    <PublicLayout>
      <PageHero
        eyebrow="Become a Driver"
        title="Turn your route into an income"
        subtitle="Drive students between the stops you already pass through, get paid straight to your CampusRide wallet, and grow your earnings with every trip."
      />

      <Section title="Driver requirements" icon={FileCheck} color="#00E676">
        <ul className="grid sm:grid-cols-2 gap-3">
          {REQUIREMENTS.map((r) => (
            <li key={r} className="flex items-start gap-3 text-sm text-gray-300">
              <CheckCircle2 size={18} className="text-[#00E676] shrink-0 mt-0.5" />
              {r}
            </li>
          ))}
        </ul>
      </Section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-400 flex items-center justify-center">
            <ClipboardList size={20} />
          </div>
          <h2 className="font-display font-bold text-2xl text-white">Application process</h2>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {STEPS.map((s, i) => (
            <div key={s.title} className="relative p-5 rounded-2xl border border-white/10 bg-white/5">
              <span className="absolute -top-3 -left-3 w-7 h-7 rounded-full bg-[#0a0a0f] border border-[#00C853]/40 text-[#00E676] text-xs font-bold flex items-center justify-center">
                {i + 1}
              </span>
              <h3 className="font-display font-semibold text-white text-sm mb-1.5 mt-1">{s.title}</h3>
              <p className="text-gray-400 text-xs leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 grid sm:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 sm:p-8">
          <div className="w-11 h-11 rounded-xl bg-[#00C853]/15 text-[#00E676] flex items-center justify-center mb-4">
            <TrendingUp size={20} />
          </div>
          <h3 className="font-display font-semibold text-xl text-white mb-2">Earnings potential</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            Each ride you complete is paid at a flat, transparent zone price set by campus
            admin — riders see it before booking, so there's no haggling. CampusRide takes a
            platform commission per ride, and the rest is credited straight to your driver
            wallet. Your driver dashboard shows today's, this week's, and this month's
            earnings, plus your acceptance rate and rating.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 sm:p-8">
          <div className="w-11 h-11 rounded-xl bg-blue-500/15 text-blue-400 flex items-center justify-center mb-4">
            <Wallet size={20} />
          </div>
          <h3 className="font-display font-semibold text-xl text-white mb-2">Driver benefits</h3>
          <ul className="space-y-2 text-gray-400 text-sm">
            <li>• Set your own route and drive when you're free</li>
            <li>• Fill up to 4 seats per trip on shared routes</li>
            <li>• Real-time ride requests with pickup guidance</li>
            <li>• Wallet payouts, no manual invoicing</li>
          </ul>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 pt-12">
        <div className="rounded-3xl border border-white/10 bg-gradient-to-r from-[#00C853]/10 via-purple-500/10 to-[#00E676]/10 p-10 sm:p-14 text-center">
          <h2 className="font-display font-bold text-2xl sm:text-3xl text-white mb-3">Ready to start driving?</h2>
          <p className="text-gray-400 mb-8 max-w-xl mx-auto">Applications are reviewed by campus admin before you go live.</p>
          <Link to={applyHref}>
            <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-8 py-3.5 rounded-2xl inline-flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.25)] transition-all duration-300 hover:scale-[1.02]">
              {applyLabel}
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </Link>
        </div>
      </section>
    </PublicLayout>
  )
}
