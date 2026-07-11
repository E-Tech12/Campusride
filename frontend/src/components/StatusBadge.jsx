const STYLES = {
  pending: "bg-amber-400/15 text-amber-300 border-amber-400/30",
  approved: "bg-signal/15 text-signal border-signal/30",
  rejected: "bg-coral/15 text-coral border-coral/30",
  suspended: "bg-mist/15 text-mist border-mist/30",
  accepted: "bg-signal/15 text-signal border-signal/30",
  ongoing: "bg-sky-400/15 text-sky-300 border-sky-400/30",
  completed: "bg-mist/15 text-mist border-mist/30",
  cancelled: "bg-coral/15 text-coral border-coral/30",
}

export default function StatusBadge({ status }) {
  const style = STYLES[status] || "bg-mist/15 text-mist border-mist/30"
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-mono-num uppercase tracking-wide border ${style}`}>
      {status}
    </span>
  )
}
