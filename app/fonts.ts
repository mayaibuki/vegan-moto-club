import { DM_Sans } from "next/font/google"
import localFont from "next/font/local"

export const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})

// Redaction (open licence) for display headings. The clean cut is the default;
// the _10/_20/_35 cuts are progressively pixelated and are swapped in by
// DegradeOnScroll as a heading rises toward the top of the viewport.
export const redaction = localFont({
  src: [
    { path: "../webfonts/Redaction-Regular.woff2", weight: "400", style: "normal" },
    { path: "../webfonts/Redaction-Bold.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-redaction",
  display: "swap",
  adjustFontFallback: "Times New Roman",
})

export const redaction10 = localFont({
  src: [
    { path: "../webfonts/Redaction_10-Regular.woff2", weight: "400", style: "normal" },
    { path: "../webfonts/Redaction_10-Bold.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-redaction-10",
  display: "swap",
  adjustFontFallback: "Times New Roman",
})

export const redaction20 = localFont({
  src: [
    { path: "../webfonts/Redaction_20-Regular.woff2", weight: "400", style: "normal" },
    { path: "../webfonts/Redaction_20-Bold.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-redaction-20",
  display: "swap",
  adjustFontFallback: "Times New Roman",
})

export const redaction35 = localFont({
  src: [
    { path: "../webfonts/Redaction_35-Regular.woff2", weight: "400", style: "normal" },
    { path: "../webfonts/Redaction_35-Bold.woff2", weight: "700", style: "normal" },
  ],
  variable: "--font-redaction-35",
  display: "swap",
  adjustFontFallback: "Times New Roman",
})

export const fontVariables = [
  dmSans.variable,
  redaction.variable,
  redaction10.variable,
  redaction20.variable,
  redaction35.variable,
].join(" ")
