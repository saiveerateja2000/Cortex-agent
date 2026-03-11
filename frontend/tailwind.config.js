/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        cortex: {
          50:  '#f0f4ff',
          100: '#dde8ff',
          200: '#c4d4ff',
          300: '#a0b8ff',
          400: '#7591ff',
          500: '#4f64ff',
          600: '#3a43f5',
          700: '#2f33e0',
          800: '#272cb5',
          900: '#252c8f',
        },
      },
    },
  },
  plugins: [],
}
