const VARIANTS = {
  primary: "bg-signal text-ink-950 hover:bg-signal-dim active:scale-[0.98]",
  secondary: "bg-ink-700 text-white hover:bg-ink-600 border border-ink-600",
  ghost: "bg-transparent text-mist hover:text-white hover:bg-ink-800",
  danger: "bg-coral text-white hover:bg-coral/80",
  outline: "bg-transparent border border-signal text-signal hover:bg-signal/10",
}

export default function Button({
  children,
  variant = "primary",
  className = "",
  disabled = false,
  loading = false,
  ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {loading && <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
      {children}
    </button>
  )
}
