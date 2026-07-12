import PublicLayout from "../../components/PublicLayout"
import { PageHero } from "../../components/PublicPageKit"

const SECTIONS = [
  {
    title: "1. Information we collect",
    body: "When you register, we collect your name, email, username, phone number, and — for students — student ID. Drivers additionally provide license, vehicle, and plate details. While using the app, we collect ride history, wallet transactions, and, during an active ride, live location data needed to match and track that ride.",
  },
  {
    title: "2. How we use your information",
    body: "We use this information to operate the platform: matching riders with drivers, calculating fares, processing wallet payments, verifying driver eligibility, showing live ETAs, and investigating safety reports. We do not sell your personal information to third parties.",
  },
  {
    title: "3. Location data",
    body: "Driver location is shared in real time with riders during an active or pending ride so they can track their pickup, and with campus admins for safety monitoring. Location sharing is tied to ride and online/offline driver status — it is not collected when a driver is offline.",
  },
  {
    title: "4. Payments",
    body: "Wallet top-ups are processed through our third-party payment provider. We store transaction references and amounts for your ride and wallet history; we do not store your full card details on our servers.",
  },
  {
    title: "5. Who can see your information",
    body: "Riders can see a driver's name, vehicle, and live location during a ride. Drivers can see a rider's name and pickup/drop-off stop for accepted requests. Campus administrators can see account, ride, and wallet data to operate and moderate the platform.",
  },
  {
    title: "6. Data retention",
    body: "We retain ride history, wallet transactions, and account information for as long as your account is active, and as needed to resolve disputes, meet legal obligations, or maintain platform safety records.",
  },
  {
    title: "7. Your choices",
    body: "You can update your profile information from your account, and you can request account deletion by contacting support. Some information, such as completed ride and transaction records, may be retained where required for accounting or safety purposes.",
  },
  {
    title: "8. Security",
    body: "We use industry-standard practices — including encrypted password storage and token-based authentication — to protect your account. No system is perfectly secure, and we encourage you to use a strong, unique password.",
  },
  {
    title: "9. Changes to this policy",
    body: "We may update this policy as CampusRide evolves. We'll post the updated version here with a new effective date.",
  },
]

export default function Privacy() {
  return (
    <PublicLayout>
      <PageHero eyebrow="Legal" title="Privacy Policy" subtitle="Last updated July 2026. This explains what data CampusRide collects and how it's used." />
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-10">
        {SECTIONS.map((s) => (
          <div key={s.title}>
            <h2 className="font-display font-semibold text-xl text-white mb-2">{s.title}</h2>
            <p className="text-gray-400 text-sm leading-relaxed">{s.body}</p>
          </div>
        ))}
        <p className="text-gray-500 text-xs pt-6 border-t border-white/5">
          Questions about your data? Reach out through our <a href="/contact" className="text-[#00E676] hover:underline">contact page</a>.
        </p>
      </section>
    </PublicLayout>
  )
}
