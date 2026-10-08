/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'gov-blue': '#1e3a8a',
        'gov-blue-dark': '#0f172a',
        'gov-gold': '#d97706',
        'gov-gold-light': '#fef3c7',
      }
    },
  },
  plugins: [],
}
