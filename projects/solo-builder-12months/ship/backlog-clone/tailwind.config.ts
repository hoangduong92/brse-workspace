import type { Config } from "tailwindcss"

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563EB",
          light: "#3B82F6",
          dark: "#1D4ED8",
        },
        secondary: {
          DEFAULT: "#64748B",
          light: "#94A3B8",
        },
        cta: {
          DEFAULT: "#F97316",
          hover: "#EA580C",
        },
        bg: {
          primary: "#FFFFFF",
          secondary: "#F8FAFC",
          tertiary: "#F1F5F9",
        },
        text: {
          primary: "#1E293B",
          secondary: "#475569",
          muted: "#64748B",
        },
        border: {
          DEFAULT: "#E2E8F0",
          focus: "#2563EB",
        },
        status: {
          open: "#6B7280",
          "in-progress": "#2563EB",
          resolved: "#16A34A",
          closed: "#9CA3AF",
        },
        issue: {
          bug: "#DC2626",
          feature: "#7C3AED",
          task: "#0891B2",
          improvement: "#059669",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
      animation: {
        "pulse-slow": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
}

export default config
