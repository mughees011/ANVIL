/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgBase: "#0A0B0E",
        bgPanel: "rgba(18, 20, 26, 0.75)",
        accentCyan: "#22D3EE",
        accentPurple: "#A855F7",
        accentGreen: "#22C55E",
        accentAmber: "#F59E0B",
        textPrimary: "#F1F5F9",
        textMuted: "#64748B"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      }
    },
  },
  plugins: [],
}
