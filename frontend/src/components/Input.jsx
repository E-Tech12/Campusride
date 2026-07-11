export default function Input({ label, error, className = "", ...props }) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-mist mb-1.5">{label}</label>
      )}
      <input
        className={`w-full bg-ink-800 border border-ink-600 rounded-xl px-4 py-2.5 text-white placeholder:text-mist/50 focus:border-signal focus:ring-1 focus:ring-signal outline-none transition-colors ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-coral">{error}</p>}
    </div>
  )
}
