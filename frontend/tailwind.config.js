/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#090B10",
          900: "#11151D",
          800: "#1B222E",
          700: "#2B3545",
          600: "#3D4B60",
        },
        signal: {
          DEFAULT: "#00E5FF",
          dim: "#0099AA",
        },
        brand: {
          DEFAULT: "#7B61FF",
        },
        coral: {
          DEFAULT: "#FF4D4D",
        },
        success: {
          DEFAULT: "#00E676",
        },
        mist: "#A0ABC0",
      },
      fontFamily: {
        display: ["Sora", "system-ui", "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      borderRadius: {
        card: "24px",
      },
      boxShadow: {
        glow: "0 0 20px rgba(0,229,255,0.4)",
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
      },
    },
  },
  plugins: [],
}
