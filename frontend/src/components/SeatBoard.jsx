/**
 * Signature element: a transit-departure-board style seat indicator.
 * Renders capacity as a row of segmented blocks (filled = taken, lit = available),
 * echoing campus shuttle signage rather than a generic progress bar.
 */
export default function SeatBoard({ capacity, available }) {
  const taken = capacity - available
  const blocks = Array.from({ length: capacity }, (_, i) => i < taken)

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        {blocks.map((isTaken, i) => (
          <span
            key={i}
            className={`w-2.5 h-5 rounded-[2px] ${
              isTaken ? "bg-ink-600" : "bg-signal shadow-[0_0_8px_rgba(214,242,60,0.6)]"
            }`}
          />
        ))}
      </div>
      <span className="font-mono-num text-sm text-signal tabular-nums">
        {available} LEFT
      </span>
    </div>
  )
}
