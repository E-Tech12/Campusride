import { useState } from "react"
import PublicLayout from "../../components/PublicLayout"
import { PageHero } from "../../components/PublicPageKit"
import { Mail, ShieldAlert, Car, Send } from "lucide-react"

const SUPPORT_EMAIL = "support@campusride.app"

const CHANNELS = [
  { icon: Mail, title: "General support", desc: "Account, wallet, or ride questions", color: "#00E676" },
  { icon: ShieldAlert, title: "Safety report", desc: "Report a driver or a safety concern", color: "#FF4D4D" },
  { icon: Car, title: "Driver applications", desc: "Questions about becoming a driver", color: "#7B61FF" },
]

export default function Contact() {
  const [form, setForm] = useState({ name: "", email: "", topic: "General support", message: "" })

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = (e) => {
    e.preventDefault()
    const subject = encodeURIComponent(`[${form.topic}] Message from ${form.name || "a CampusRide user"}`)
    const body = encodeURIComponent(
      `${form.message}\n\n---\nFrom: ${form.name}\nEmail: ${form.email}\nTopic: ${form.topic}`
    )
    window.location.href = `mailto:${SUPPORT_EMAIL}?subject=${subject}&body=${body}`
  }

  return (
    <PublicLayout>
      <PageHero
        eyebrow="Contact"
        title="Talk to the CampusRide team"
        subtitle="Pick a topic below or send us a message directly — we read and respond to every one."
      />

      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          {CHANNELS.map((c) => (
            <button
              key={c.title}
              type="button"
              onClick={() => setForm((f) => ({ ...f, topic: c.title }))}
              className={`w-full text-left p-5 rounded-2xl border transition-colors ${
                form.topic === c.title ? "border-[#00C853]/40 bg-[#00C853]/5" : "border-white/10 bg-white/5 hover:bg-white/10"
              }`}
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-3" style={{ backgroundColor: `${c.color}22`, color: c.color }}>
                <c.icon size={18} />
              </div>
              <p className="text-white font-semibold text-sm mb-0.5">{c.title}</p>
              <p className="text-gray-400 text-xs">{c.desc}</p>
            </button>
          ))}
          <div className="p-5 rounded-2xl border border-white/10 bg-white/5">
            <p className="text-gray-400 text-xs mb-1">Or email us directly</p>
            <a href={`mailto:${SUPPORT_EMAIL}`} className="text-[#00E676] text-sm font-medium hover:underline break-all">{SUPPORT_EMAIL}</a>
          </div>
        </div>

        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="rounded-3xl border border-white/10 bg-white/5 p-6 sm:p-8 space-y-5">
            <div className="grid sm:grid-cols-2 gap-5">
              <Field label="Your name">
                <input
                  value={form.name}
                  onChange={handleChange("name")}
                  required
                  className="w-full rounded-xl border border-white/10 bg-black/30 p-3 text-white placeholder-gray-600 focus:border-[#00E676] focus:outline-none focus:ring-1 focus:ring-[#00E676]"
                  placeholder="Jane Doe"
                />
              </Field>
              <Field label="Your email">
                <input
                  type="email"
                  value={form.email}
                  onChange={handleChange("email")}
                  required
                  className="w-full rounded-xl border border-white/10 bg-black/30 p-3 text-white placeholder-gray-600 focus:border-[#00E676] focus:outline-none focus:ring-1 focus:ring-[#00E676]"
                  placeholder="jane@school.edu"
                />
              </Field>
            </div>
            <Field label="Topic">
              <select
                value={form.topic}
                onChange={handleChange("topic")}
                className="w-full rounded-xl border border-white/10 bg-black/30 p-3 text-white focus:border-[#00E676] focus:outline-none focus:ring-1 focus:ring-[#00E676]"
              >
                {CHANNELS.map((c) => (
                  <option key={c.title} value={c.title}>{c.title}</option>
                ))}
              </select>
            </Field>
            <Field label="Message">
              <textarea
                value={form.message}
                onChange={handleChange("message")}
                required
                rows={5}
                className="w-full rounded-xl border border-white/10 bg-black/30 p-3 text-white placeholder-gray-600 focus:border-[#00E676] focus:outline-none focus:ring-1 focus:ring-[#00E676] resize-none"
                placeholder="Tell us what's going on..."
              />
            </Field>
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-[#00C853] to-[#00E676] text-[#0a0a0f] font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:scale-[1.01] transition-transform"
            >
              <Send size={16} /> Send message
            </button>
            <p className="text-gray-500 text-xs text-center">This opens your email app with the message pre-filled to {SUPPORT_EMAIL}.</p>
          </form>
        </div>
      </section>
    </PublicLayout>
  )
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-gray-400 mb-1.5">{label}</span>
      {children}
    </label>
  )
}
