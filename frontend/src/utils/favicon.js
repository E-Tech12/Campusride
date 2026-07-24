export function loadCampusRideFavicon() {
  const svg = `
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 100 100"
  >
    <defs>
      <linearGradient
        id="grad"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="100%"
      >
        <stop offset="0%" stop-color="#22c55e"/>
        <stop offset="100%" stop-color="#84cc16"/>
      </linearGradient>
    </defs>

    <rect
      width="100"
      height="100"
      rx="24"
      fill="#0f172a"
    />

    <path
      d="
      M50 12
      C72 12 88 28 88 50
      C88 74 66 90 50 96
      C34 90 12 74 12 50
      C12 28 28 12 50 12
      Z
      "
      fill="url(#grad)"
    />

    <path
      d="
      M38 34
      H56
      C66 34 72 40 72 48
      C72 57 66 63 56 63
      H48
      L67 82
      "
      fill="none"
      stroke="#ffffff"
      stroke-width="8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />

    <circle
      cx="50"
      cy="50"
      r="5"
      fill="#0f172a"
    />
  </svg>
  `;

  const favicon =
    "data:image/svg+xml;charset=utf-8," +
    encodeURIComponent(svg);

  let link =
    document.querySelector("link[rel='icon']");

  if (!link) {
    link = document.createElement("link");
    link.rel = "icon";
    document.head.appendChild(link);
  }

  link.href = favicon;

  document.title =
    "CampusRide | Smart Campus Transportation";
}