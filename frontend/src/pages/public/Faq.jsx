import { useState } from "react"
import PublicLayout from "../../components/PublicLayout"
import { PageHero, ClosingCTA } from "../../components/PublicPageKit"
import { ChevronDown } from "lucide-react"

const GROUPS = [
  {
    title: "Getting started",
    items: [
      { q: "How do I sign up?", a: "Tap Sign up, choose whether you're registering as a student or a driver, and fill in your details. Students verify their email with a 6-digit code before their first login." },
      { q: "I didn't receive my verification code", a: "Check your spam folder first. If it's still missing, use the Resend code button on the Verify Email page — codes can be resent as many times as needed." },
      { q: "I forgot my password", a: "Go to the Login page and tap Forgot password. We'll email you a reset code you can use on the Reset Password page." },
    ],
  },
  {
    title: "Rides",
    items: [
      { q: "How is the ride price decided?", a: "Prices are flat and set per drop-off zone by campus admin. You'll see the exact price before you request a seat — no surge pricing." },
      { q: "How many people can share a ride?", a: "Each driver has a seat capacity (commonly 4). Multiple students can share the same route to different stops on the same trip." },
      { q: "Can I track my driver?", a: "Yes — once a driver accepts your request, you can see their live location and estimated arrival time on the map." },
      { q: "What if my driver cancels or doesn't show?", a: "Report it through Support. Any funds held for that ride are handled according to our cancellation policy, and repeated issues are reviewed by admins." },
    ],
  },
  {
    title: "Wallet & payments",
    items: [
      { q: "How do I top up my wallet?", a: "Open Wallet from your dashboard and choose a top-up amount — you'll be redirected to our payment provider to complete the payment securely." },
      { q: "How do drivers get paid?", a: "Ride fares are credited to the driver's wallet after platform commission is deducted. Drivers can request a withdrawal, which is reviewed and approved by admin." },
      { q: "Is my payment information stored?", a: "We don't store your full card details — payments are processed by our payment provider and we keep only the transaction reference and amount." },
    ],
  },
  {
    title: "Becoming a driver",
    items: [
      { q: "How do I apply to become a driver?", a: "From your student account, go to Become a Driver and submit your license, vehicle, and route details. Campus admin reviews every application." },
      { q: "How long does approval take?", a: "Review times vary by campus admin availability. You'll see your application status update once it's reviewed." },
      { q: "Can I drive and remain a student on the same account?", a: "Yes — once approved, your account gains driver access alongside your existing student features." },
    ],
  },
]

export default function Faq() {
  const [openKey, setOpenKey] = useState(null)

  return (
    <PublicLayout>
      <PageHero eyebrow="FAQ" title="Frequently asked questions" subtitle="Can't find what you're looking for? Our support team is one message away." />

      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-10">
        {GROUPS.map((g) => (
          <div key={g.title}>
            <h2 className="text-[#00E676] text-sm font-semibold uppercase tracking-wider mb-4">{g.title}</h2>
            <div className="space-y-3">
              {g.items.map((item) => {
                const key = `${g.title}-${item.q}`
                const open = openKey === key
                return (
                  <div key={key} className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">
                    <button
                      onClick={() => setOpenKey(open ? null : key)}
                      className="w-full flex items-center justify-between gap-4 p-5 text-left"
                    >
                      <span className="text-white font-medium text-sm sm:text-base">{item.q}</span>
                      <ChevronDown size={18} className={`text-gray-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`} />
                    </button>
                    {open && <p className="px-5 pb-5 text-gray-400 text-sm leading-relaxed">{item.a}</p>}
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </section>

      <ClosingCTA
        heading="Didn't find your answer?"
        sub="Send our support team a message and we'll get back to you."
        primaryTo="/contact"
        primaryLabel="Contact support"
      />
    </PublicLayout>
  )
}
