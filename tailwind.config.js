/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#EF6B00',    // Egg orange
        secondary: '#1F2937',  // Dark gray
        accent: '#FCD34D',     // Golden
      }
    },
  },
  plugins: [],
}
