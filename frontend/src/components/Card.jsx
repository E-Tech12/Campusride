export default function Card({ children, className = "" }) {
  return (
    <div className={`bg-ink-800 border border-ink-600 rounded-card p-6 ${className}`}>
      {children}
    </div>
  )
}
