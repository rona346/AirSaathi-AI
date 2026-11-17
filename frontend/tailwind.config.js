/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aqi: {
          good: "#10B981",        // 0-50 Green
          satisfactory: "#84CC16",// 51-100 Lime
          moderate: "#EAB308",    // 101-200 Yellow
          poor: "#F97316",        // 201-300 Orange
          verypoor: "#EF4444",    // 301-400 Red
          severe: "#991B1B",      // 401-500 Maroon
          hazardous: "#6B21A8",   // 500+ Purple
        },
      },
    },
  },
  plugins: [],
}
