import PublicLayout from "../../components/PublicLayout"
import { PageHero } from "../../components/PublicPageKit"

const SECTIONS = [
  {
    title: "1. Acceptance of terms",
    body: "By creating a CampusRide account or using the platform as a rider, driver, or administrator, you agree to these Terms of Service and our Privacy Policy. If you don't agree, please don't use the platform.",
  },
  {
    title: "2. Who can use CampusRide",
    body: "CampusRide is intended for students, staff, and approved drivers affiliated with the participating campus. You must provide accurate registration information and keep your account credentials confidential.",
  },
  {
    title: "3. Rides and pricing",
    body: "Ride prices are set per zone by campus administrators and shown before you request a ride. Prices are flat and do not fluctuate with demand. Funds for a ride may be held at request time and are released, refunded, or captured depending on how the ride is completed or cancelled.",
  },
  {
    title: "4. Driver responsibilities",
    body: "Drivers must maintain accurate vehicle and license information, operate only the vehicle registered on their account, respect the seat capacity on file, and follow all applicable traffic and campus safety rules. Admins may suspend driver access for policy violations, safety reports, or extended inactivity review.",
  },
  {
    title: "5. Wallet & payments",
    body: "Your in-app wallet holds funds used to pay for rides and to receive driver earnings. Top-ups are processed through our payment provider. Platform commission is deducted from completed rides before driver payout. Withdrawal requests are reviewed by admins before funds are released.",
  },
  {
    title: "6. Cancellations & refunds",
    body: "Riders may cancel a pending ride request before it's accepted. Depending on timing and driver status, held funds may be refunded to your wallet. Repeated last-minute cancellations may affect your account standing.",
  },
  {
    title: "7. Conduct",
    body: "Riders and drivers agree to treat each other respectfully, refrain from harassment or unsafe behavior, and report safety concerns promptly. CampusRide may suspend or terminate accounts that violate this standard.",
  },
  {
    title: "8. Limitation of liability",
    body: "CampusRide facilitates connections between riders and independent drivers but is not itself a transportation carrier. While we vet drivers and monitor rides, we are not liable for the independent actions of platform users to the fullest extent permitted by law.",
  },
  {
    title: "9. Changes to these terms",
    body: "We may update these terms as the platform evolves. Continued use of CampusRide after changes take effect constitutes acceptance of the updated terms.",
  },
]

export default function Terms() {
  return (
    <PublicLayout>
      <PageHero eyebrow="Legal" title="Terms of Service" subtitle="Last updated July 2026. Please read these terms carefully before using CampusRide." />
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-10">
        {SECTIONS.map((s) => (
          <div key={s.title}>
            <h2 className="font-display font-semibold text-xl text-white mb-2">{s.title}</h2>
            <p className="text-gray-400 text-sm leading-relaxed">{s.body}</p>
          </div>
        ))}
        <p className="text-gray-500 text-xs pt-6 border-t border-white/5">
          Questions about these terms? Reach out through our <a href="/contact" className="text-[#00E676] hover:underline">contact page</a>.
        </p>
      </section>
    </PublicLayout>
  )
}
