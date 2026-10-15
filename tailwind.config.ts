import type { Config } from 'tailwindcss'
import animate from 'tailwindcss-animate'

const config: Config = {
  future: { hoverOnlyWhenSupported: true },
  darkMode: ["class"],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'var(--font-dm-sans)',
          'system-ui',
          '-apple-system',
          'sans-serif',
        ],
        serif: ['var(--font-redaction)', 'Georgia', 'serif'],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          text: "hsl(var(--primary-text))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
          text: "hsl(var(--destructive-text))",
        },
        success: {
          DEFAULT: "hsl(var(--success))",
          foreground: "hsl(var(--success-foreground))",
          text: "hsl(var(--success-text))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      maxHeight: {
        // Bottom sheet height (filters below lg)
        sheet: "85dvh",
      },
      zIndex: {
        // Stacking tokens from tokens.css (--z-*)
        sticky: "var(--z-sticky)",
        overlay: "var(--z-overlay)",
      },
      gridTemplateRows: {
        // Collapse wrapper rows (PromoBanner): animate open -> closed to collapse to zero height
        open: "1fr",
        closed: "0fr",
      },
      scale: {
        // Press feedback on cards (motion.md)
        98: "0.98",
      },
      aspectRatio: {
        "4/3": "4 / 3",
      },
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [animate],
}
export default config
