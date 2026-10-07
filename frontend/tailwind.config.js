/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["selector", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9f4",
          100: "#dcf1e3",
          200: "#b8e2c8",
          300: "#8cceaa",
          400: "#5cb586",
          500: "#38996a",
          600: "#277b54",
          700: "#206245",
          800: "#1c4e39",
          900: "#18402f",
        },
        accent: {
          500: "#e08a1e",
          600: "#c26e0f",
        },
      },
      fontSize: {
        base: ["1.05rem", "1.6rem"],
      },
    },
  },
  plugins: [],
};
