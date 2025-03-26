/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        playfair: ["Playfair Display", "serif"],
      },
      colors: {
        primary: "#4019cc",
        accent: "#cc61ff",
        accentDarker: "#9f3dce",
        main: "#6943f4",
        background: "#0b0b22",
        textPrimary: "#ffffff",
        textSecondary: "#d1c4e9",
      },
    },
  },
  plugins: [],
};
