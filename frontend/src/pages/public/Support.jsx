import { Link } from "react-router-dom"
import PublicLayout from "../../components/PublicLayout"
import { PageHero, ClosingCTA } from "../../components/PublicPageKit"
import { LifeBuoy, Wallet, Car, HelpCircle, Mail, ArrowRight } from "lucide-react"

const TOPICS = [
  {
    icon: Car,
    color: "#00E676",
    title: "Ride support",
    desc: "Issues with a ride request, a driver not arriving, or a trip that ended unexpectedly.",
    items: ["My driver hasn't arrived", "I was charged for a cancelled ride", "I want to report a driver"],
  },
  {
    icon: Wallet,
    color: "#7B61FF",
    title: "Wallet support",
    desc: "Top-ups, payouts, and anything related to your CampusRide wallet balance.",
    items: ["My top-up didn't reflect", "How do driver payouts work", "I was double-charged"],
  },
  {
    icon: HelpCircle,
    color: "#00C853",
    title: "Account & general",
    desc: "Login issues, verification codes, and general questions about the platform.",
    items: ["I didn't receive my verification code", "How do I reset my password", "How do I become a driver"],
  },
]

export default function Support() {
  return (
    <PublicLayout>
      <PageHero
        eyebrow="Support"
        title="We're here to help"
        subtitle="Browse common topics below, check the FAQ, or reach our team directly — we respond to every report."
      />

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid sm:grid-cols-3 gap-6">
        {TOPICS.map((t) => (
          <div key={t.title} className="rounded-2xl border border-white/10 bg-white/5 p-6 flex flex-col">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${t.color}22`, color: t.color }}>
              <t.icon size={20} />
            </div>
            <h3 className="font-display font-semibold text-lg text-white mb-1.5">{t.title}</h3>
            <p className="text-gray-400 text-sm mb-4">{t.desc}</p>
            <ul className="space-y-2 mt-auto">
              {t.items.map((i) => (
                <li key={i} className="text-xs text-gray-500 flex items-start gap-2">
                  <span className="mt-1 w-1 h-1 rounded-full bg-gray-600 shrink-0" /> {i}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-4">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 sm:p-10 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-[#00C853]/15 text-[#00E676] flex items-center justify-center shrink-0">
              <LifeBuoy size={22} />
            </div>
            <div>
              <h3 className="font-display font-semibold text-lg text-white">Full help center &amp; FAQ</h3>
              <p className="text-gray-400 text-sm">Answers to the most common questions from riders and drivers.</p>
            </div>
          </div>
          <Link to="/faq" className="shrink-0">
            <button className="bg-white/10 hover:bg-white/15 border border-white/10 text-white font-semibold px-5 py-2.5 rounded-xl flex items-center gap-2 transition-colors text-sm">
              Visit FAQ <ArrowRight size={15} />
            </button>
          </Link>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 sm:p-10 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/15 text-blue-400 flex items-center justify-center shrink-0">
              <Mail size={22} />
            </div>
            <div>
              <h3 className="font-display font-semibold text-lg text-white">Still stuck? Reach us directly</h3>
              <p className="text-gray-400 text-sm">Our contact page gets you straight to the support team.</p>
            </div>
          </div>
          <Link to="/contact" className="shrink-0">
            <button className="bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-5 py-2.5 rounded-xl flex items-center gap-2 transition-all text-sm hover:scale-[1.02]">
              Contact us <ArrowRight size={15} />
            </button>
          </Link>
        </div>
      </section>

      <ClosingCTA />
    </PublicLayout>
  )
}
