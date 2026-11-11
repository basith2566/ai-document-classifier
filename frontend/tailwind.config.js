/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f1f4f9',
          100: '#e1e7f0',
          200: '#c3cfe0',
          300: '#97aac5',
          400: '#657f9f',
          500: '#476084',
          600: '#364b6b',
          700: '#2a3a55',
          800: '#1b2a45',
          900: '#12203a',
          950: '#0a1428',
        },
        brand: { DEFAULT: '#2f5bea', dark: '#2447c2', soft: '#e8eefe' },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
