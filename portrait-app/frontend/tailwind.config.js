/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        cosmic: {
          950: '#03060f',
          900: '#050a1a',
          800: '#080f28',
          700: '#0d1840',
        },
        divine: {
          400: '#fde68a',
          500: '#f5c842',
          600: '#d4a017',
        },
      },
      fontFamily: {
        display: ['Georgia', 'serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
}
