/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgBase: "#0A0B0C",
        bgPanel: "#131517",
        line: "#262A2E",
        ink: "#E8E6E1",
        inkMuted: "#8A8F94",
        signal: "#3DDC97",
        retry: "#E8A33D",
        fail: "#E85D4C",
        data: "#8B7FD1"
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        heading: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      }
    },
  },
  plugins: [],
}
