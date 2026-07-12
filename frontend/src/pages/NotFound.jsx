import { Link } from "react-router-dom"
import PublicLayout from "../components/PublicLayout"
import { MapPin, ArrowRight } from "lucide-react"

export default function NotFound() {
  return (
    <PublicLayout>
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4 py-24">
        <div className="w-16 h-16 rounded-2xl bg-[#00C853]/15 text-[#00E676] flex items-center justify-center mb-6">
          <MapPin size={28} />
        </div>
        <h1 className="font-display font-bold text-4xl text-white mb-3">Looks like you took a wrong turn</h1>
        <p className="text-gray-400 max-w-md mb-8">We couldn't find that page. Let's get you back on route.</p>
        <Link to="/">
          <button className="group bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold px-8 py-3.5 rounded-2xl inline-flex items-center gap-2 hover:scale-[1.02] transition-all">
            Back to home
            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
          </button>
        </Link>
      </div>
    </PublicLayout>
  )
}
