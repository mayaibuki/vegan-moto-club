import type { Metadata, Viewport } from "next"
import { DM_Sans } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { SpeedInsights } from "@vercel/speed-insights/next"
import { Navbar } from "@/components/Navbar"
import { Footer } from "@/components/Footer"
import { AgentationWrapper } from "@/components/AgentationWrapper"
import "./globals.css"
import { SITE_URL } from "@/lib/constants"

const dmSans = DM_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-dm-sans",
})

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Vegan Moto Club - Cruelty-Free Motorcycle Gear",
    template: "%s | Vegan Moto Club",
  },
  description:
    "A curated database of vegan motorcycle gear for compassionate riders. Find ethical alternatives to animal-based protective wear.",
  keywords: [
    "vegan motorcycle gear",
    "cruelty-free motorcycle",
    "vegan leather jacket",
    "synthetic motorcycle gear",
    "ethical riding gear",
    "animal-free motorcycle",
    "vegan riding boots",
    "vegan motorcycle gloves",
  ],
  authors: [{ name: "Vegan Moto Club" }],
  creator: "Vegan Moto Club",
  publisher: "Vegan Moto Club",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: SITE_URL,
    siteName: "Vegan Moto Club",
    title: "Vegan Moto Club - Cruelty-Free Motorcycle Gear",
    description:
      "A curated database of vegan motorcycle gear for compassionate riders. Find ethical alternatives to animal-based protective wear.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Vegan Moto Club - Cruelty-Free Motorcycle Gear",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Vegan Moto Club - Cruelty-Free Motorcycle Gear",
    description:
      "A curated database of vegan motorcycle gear for compassionate riders. Find ethical alternatives to animal-based protective wear.",
    images: ["/og-image.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: SITE_URL,
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#84b13d" },
    { media: "(prefers-color-scheme: dark)", color: "#a8d357" },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning className={dmSans.variable}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                if (localStorage.getItem('theme') === 'dark' ||
                  (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                  document.documentElement.classList.add('dark');
                }
              } catch (e) {}
            `,
          }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              name: "Vegan Moto Club",
              url: SITE_URL,
              logo: `${SITE_URL}/logo.png`,
              description:
                "A curated database of vegan motorcycle gear for compassionate riders. Find ethical alternatives to animal-based protective wear.",
              sameAs: ["https://www.instagram.com/veganmotoclub", "https://discord.gg/GN4jkBRnut"],
            }),
          }}
        />
      </head>
      <body className={dmSans.className}>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary focus:text-primary-foreground focus:px-4 focus:py-2 focus:rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          Skip to main content
        </a>
        <div className="min-h-screen flex flex-col bg-stone-50 dark:bg-stone-950">
          <Navbar />
          <main id="main-content" className="flex-1 max-w-7xl mx-auto w-full px-4 py-8" tabIndex={-1}>
            {children}
          </main>
          <Footer />
        </div>
        <AgentationWrapper />
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  )
}
