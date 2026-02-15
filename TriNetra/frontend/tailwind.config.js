/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./login.html",
    "./autosar.html",
    "./chronos.html",
    "./hydra.html",
    "./js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#00ff87',
        secondary: '#00d4ff',
        dark: '#0a0a0f',
        'dark-secondary': '#1a1a2e',
        'dark-accent': '#16213e'
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      }
    }
  },
  plugins: [],
}
