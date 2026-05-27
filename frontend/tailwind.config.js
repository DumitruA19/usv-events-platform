/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Source Sans 3"', "ui-sans-serif", "system-ui", "sans-serif"],
        display: ['"Space Grotesk"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        ink: "#101828",
        mist: "#F6F7FB",
        paper: "#ffffff",
        haze: "#EEF4FF",
        usv: {
          50: "#eef6ff",
          100: "#d9ecff",
          200: "#b8dcff",
          300: "#86c3ff",
          400: "#4aa2ff",
          500: "#1c7cff",
          600: "#0b5fe6",
          700: "#0a4bb8",
          800: "#0b4195",
          900: "#0c377a",
        },
      },
      boxShadow: {
        lift: "0 10px 30px rgba(16, 24, 40, 0.08)",
        card: "0 8px 20px rgba(16, 24, 40, 0.06)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
