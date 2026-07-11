/**
 * Animated abstract hero background: a faint road-grid with glowing route lines
 * that draw themselves, plus pulsing "live driver" dots. Pure SVG/CSS, no
 * external image or video assets, so there's nothing to source or license.
 */
export default function RouteBackground() {
  return (
    <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
      <svg
        viewBox="0 0 1200 800"
        preserveAspectRatio="xMidYMid slice"
        className="w-full h-full"
      >
        <defs>
          <linearGradient id="routeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00E676" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#00C853" stopOpacity="0.2" />
          </linearGradient>
          <radialGradient id="dotGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#00E676" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#00E676" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* faint static street grid */}
        <g stroke="#ffffff" strokeOpacity="0.04" strokeWidth="1">
          {Array.from({ length: 13 }).map((_, i) => (
            <line key={`v${i}`} x1={i * 100} y1="0" x2={i * 100} y2="800" />
          ))}
          {Array.from({ length: 9 }).map((_, i) => (
            <line key={`h${i}`} x1="0" y1={i * 100} x2="1200" y2={i * 100} />
          ))}
        </g>

        {/* animated route paths that draw themselves */}
        <path
          d="M -50 620 C 200 560, 300 680, 480 540 S 760 380, 1000 420 S 1260 300, 1300 260"
          fill="none"
          stroke="url(#routeGrad)"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray="6 10"
          className="route-path route-path-1"
        />
        <path
          d="M -50 240 C 180 280, 320 160, 520 220 S 780 340, 960 200 S 1180 120, 1300 160"
          fill="none"
          stroke="url(#routeGrad)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray="5 9"
          className="route-path route-path-2"
        />
        <path
          d="M -50 420 C 150 440, 380 380, 540 460 S 820 520, 1020 440 S 1180 480, 1300 460"
          fill="none"
          stroke="#7C3AED"
          strokeOpacity="0.35"
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray="4 8"
          className="route-path route-path-3"
        />

        {/* pulsing live-driver dots, riding along the routes */}
        <g className="pulse-dot pulse-dot-1">
          <circle cx="480" cy="540" r="16" fill="url(#dotGlow)" />
          <circle cx="480" cy="540" r="4" fill="#00E676" />
        </g>
        <g className="pulse-dot pulse-dot-2">
          <circle cx="960" cy="200" r="16" fill="url(#dotGlow)" />
          <circle cx="960" cy="200" r="4" fill="#00E676" />
        </g>
        <g className="pulse-dot pulse-dot-3">
          <circle cx="540" cy="460" r="14" fill="url(#dotGlow)" />
          <circle cx="540" cy="460" r="3.5" fill="#A78BFA" />
        </g>
        <g className="pulse-dot pulse-dot-4">
          <circle cx="1000" cy="420" r="14" fill="url(#dotGlow)" />
          <circle cx="1000" cy="420" r="3.5" fill="#00E676" />
        </g>
      </svg>

      <style>{`
        .route-path {
          animation: draw-route 8s linear infinite;
        }
        .route-path-2 { animation-duration: 11s; animation-delay: -2s; }
        .route-path-3 { animation-duration: 9.5s; animation-delay: -4s; }
        @keyframes draw-route {
          0% { stroke-dashoffset: 0; }
          100% { stroke-dashoffset: -160; }
        }
        .pulse-dot {
          animation: pulse-dot 2.4s ease-in-out infinite;
          transform-origin: center;
        }
        .pulse-dot-2 { animation-delay: 0.6s; }
        .pulse-dot-3 { animation-delay: 1.2s; }
        .pulse-dot-4 { animation-delay: 1.8s; }
        @keyframes pulse-dot {
          0%, 100% { opacity: 0.6; transform: scale(0.85); }
          50% { opacity: 1; transform: scale(1.15); }
        }
        @media (prefers-reduced-motion: reduce) {
          .route-path, .pulse-dot { animation: none; }
        }
      `}</style>
    </div>
  )
}
