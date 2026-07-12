import PublicLayout from "../../components/PublicLayout"
import { PageHero, InfoCard, ClosingCTA, Section } from "../../components/PublicPageKit"
import { ShieldCheck, Radar, FileText, AlertTriangle, Phone, Eye } from "lucide-react"

export default function Safety() {
  return (
    <PublicLayout>
      <PageHero
        eyebrow="Safety"
        title="Safety is the whole reason CampusRide exists"
        subtitle="Every driver, every ride, and every payment on CampusRide is designed around one question: is this the safest way for a student to get across campus?"
      />

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid sm:grid-cols-2 gap-6">
        <InfoCard icon={ShieldCheck} title="Driver verification" color="#00E676">
          Every driver submits a valid license, vehicle documents, and plate number before
          applying. Campus admins manually review and approve each application — no driver
          goes live until they're verified. Admins can suspend a driver's account instantly
          if a concern is raised.
        </InfoCard>
        <InfoCard icon={Radar} title="Ride tracking" color="#7B61FF">
          From the moment a ride is accepted to drop-off, the driver's live location is
          visible to the rider and to campus admins on the operations dashboard. Trip status,
          pickup, and drop-off events are all logged.
        </InfoCard>
      </section>

      <Section title="Safety policies" icon={FileText} color="#00C853">
        <ul className="space-y-3 text-gray-400 text-sm leading-relaxed">
          <li className="flex gap-3"><Bullet />Drivers must operate the exact vehicle and plate on file — mismatches can be reported.</li>
          <li className="flex gap-3"><Bullet />Seat capacity is enforced per vehicle; drivers cannot accept more riders than seats available.</li>
          <li className="flex gap-3"><Bullet />All in-app payments go through the CampusRide wallet — riders are never asked to pay a driver in cash off-platform.</li>
          <li className="flex gap-3"><Bullet />Ride history is retained for both riders and drivers, so any incident can be traced to a specific trip.</li>
          <li className="flex gap-3"><Bullet />Repeated cancellations, low ratings, or policy violations can trigger admin review or suspension.</li>
        </ul>
      </Section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-red-500/15 text-red-400 flex items-center justify-center">
            <AlertTriangle size={20} />
          </div>
          <h2 className="font-display font-bold text-2xl text-white">Emergency procedures</h2>
        </div>
        <div className="grid sm:grid-cols-3 gap-4">
          <EmergencyStep icon={Phone} step="1" text="If you feel unsafe during a ride, contact campus security or local emergency services immediately." />
          <EmergencyStep icon={Eye} step="2" text="Report the incident through the Support page as soon as you're safe — include the driver name and approximate time." />
          <EmergencyStep icon={ShieldCheck} step="3" text="Admins investigate every report and can suspend a driver's access to the platform while reviewing." />
        </div>
      </section>

      <ClosingCTA
        heading="Have a safety concern?"
        sub="Our support team reviews every report personally."
        primaryTo="/contact"
        primaryLabel="Contact support"
      />
    </PublicLayout>
  )
}

function Bullet() {
  return <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#00E676] shrink-0" />
}

function EmergencyStep({ icon: Icon, step, text }) {
  return (
    <div className="p-5 rounded-2xl border border-white/10 bg-white/5 relative">
      <span className="absolute -top-3 -left-3 w-7 h-7 rounded-full bg-[#0a0a0f] border border-red-500/30 text-red-400 text-xs font-bold flex items-center justify-center">
        {step}
      </span>
      <Icon size={18} className="text-red-400 mb-3" />
      <p className="text-gray-300 text-sm leading-relaxed">{text}</p>
    </div>
  )
}
