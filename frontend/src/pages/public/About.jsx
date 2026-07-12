import PublicLayout from "../../components/PublicLayout"
import { PageHero, InfoCard, ClosingCTA, Section } from "../../components/PublicPageKit"
import { Target, Eye, Layers, Heart } from "lucide-react"

export default function About() {
  return (
    <PublicLayout>
      <PageHero
        eyebrow="About CampusRide"
        title="Built by students, for student mobility"
        subtitle="CampusRide connects students with vetted campus drivers running fixed routes — so getting around campus is safer, cheaper, and predictable."
      />

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid sm:grid-cols-2 gap-6">
        <InfoCard icon={Target} title="Our mission" color="#00E676">
          Make campus transportation safe, affordable, and available to every student — no
          matter the time of day or distance across campus.
        </InfoCard>
        <InfoCard icon={Eye} title="Our vision" color="#7B61FF">
          A campus where no student worries about how they'll get to class, a hostel, or an
          event, and where driving for fellow students is a reliable way to earn.
        </InfoCard>
      </section>

      <Section title="Platform overview" icon={Layers}>
        <p className="text-gray-400 leading-relaxed mb-6">
          CampusRide pairs students needing a ride with campus-approved drivers already
          running a fixed route. Riders see live driver locations, real-time seat
          availability, and an estimated arrival time before requesting. Drivers accept ride
          requests, get pickup guidance, and get paid straight into their in-app wallet.
          Approvals, ride matching, payments, and safety monitoring are managed by campus
          administrators from a live operations dashboard.
        </p>
        <div className="grid sm:grid-cols-3 gap-4 text-sm">
          <MiniStat label="For students" value="Request, track, and pay for rides in one app" />
          <MiniStat label="For drivers" value="Turn spare time into earnings on routes you already run" />
          <MiniStat label="For admins" value="Approve drivers, monitor trips, and manage payouts live" />
        </div>
      </Section>

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-blue-500/15 text-blue-400 flex items-center justify-center">
            <Heart size={20} />
          </div>
          <h2 className="font-display font-bold text-2xl text-white">Why students and drivers choose us</h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            "Flat, predictable zone pricing — no surge, no haggling.",
            "Every driver is verified and approved by campus admin before going live.",
            "Live GPS tracking from acceptance to drop-off.",
            "In-app wallet for fast, cashless top-ups and payouts.",
            "Shared routes mean lower fares for riders and steady income for drivers.",
            "A support team you can reach when something goes wrong.",
          ].map((b) => (
            <div key={b} className="flex items-start gap-3 p-4 rounded-xl bg-white/5 border border-white/5">
              <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#00E676] shrink-0" />
              <p className="text-gray-300 text-sm leading-relaxed">{b}</p>
            </div>
          ))}
        </div>
      </section>

      <ClosingCTA />
    </PublicLayout>
  )
}

function MiniStat({ label, value }) {
  return (
    <div className="p-4 rounded-xl bg-black/20 border border-white/5">
      <p className="text-[#00E676] font-semibold text-xs uppercase tracking-wide mb-1">{label}</p>
      <p className="text-gray-300">{value}</p>
    </div>
  )
}
