import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"

// Small shared building blocks used across the public/marketing pages
// (About, Safety, Support, Become a Driver, Contact, Terms, Privacy, FAQ)
// so they share one consistent visual language instead of each page
// re-inventing its own hero/card/CTA styling.

export function PageHero({ eyebrow, title, subtitle }) {
  return (
    <section className="relative overflow-hidden border-b border-white/5">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[300px] bg-green-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <span className="text-[#00E676] text-sm font-semibold uppercase tracking-wider">{eyebrow}</span>
        <h1 className="font-display font-bold text-4xl sm:text-5xl text-white mt-3 mb-5 leading-tight">{title}</h1>
        {subtitle && <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">{subtitle}</p>}
      </div>
    </section>
  )
}

export function InfoCard({ icon: Icon, title, color = "#00E676", children }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 sm:p-8">
      <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${color}22`, color }}>
        <Icon size={20} />
      </div>
      <h3 className="font-display font-semibold text-xl text-white mb-2">{title}</h3>
      <div className="text-gray-400 text-sm leading-relaxed">{children}</div>
    </div>
  )
}

export function ClosingCTA({
  heading = "Ready to get moving?",
  sub = "Join CampusRide today — as a rider or a driver.",
  primaryTo = "/register",
  primaryLabel = "Create an account",
}) {
  return (
    <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
      <div className="rounded-3xl border border-white/10 bg-gradient-to-r from-[#00C853]/10 via-purple-500/10 to-[#00E676]/10 p-10 sm:p-14 text-center">
        <h2 className="font-display font-bold text-2xl sm:text-3xl text-white mb-3">{heading}</h2>
        <p className="text-gray-400 mb-8 max-w-xl mx-auto">{sub}</p>
        <Link to={primaryTo}>
          <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-8 py-3.5 rounded-2xl inline-flex items-center gap-2 hover:shadow-[0_0_40px_rgba(0,200,83,0.25)] transition-all duration-300 hover:scale-[1.02]">
            {primaryLabel}
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </Link>
      </div>
    </section>
  )
}

export function Section({ title, icon: Icon, color = "#00E676", children }) {
  return (
    <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-8 sm:p-10">
        {title && (
          <div className="flex items-center gap-3 mb-4">
            {Icon && (
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}22`, color }}>
                <Icon size={20} />
              </div>
            )}
            <h2 className="font-display font-bold text-2xl text-white">{title}</h2>
          </div>
        )}
        {children}
      </div>
    </section>
  )
}
