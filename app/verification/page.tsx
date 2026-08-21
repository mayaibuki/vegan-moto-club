import type { Metadata } from "next"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export const metadata: Metadata = {
  title: "How We Verify Vegan Gear",
  description:
    "What the verification badges on Vegan Moto Club mean: how we confirm motorcycle gear is free of leather, wool, and other animal materials.",
  openGraph: {
    title: "How We Verify Vegan Gear | Vegan Moto Club",
    description:
      "What the verification badges on Vegan Moto Club mean: how we confirm motorcycle gear is free of leather, wool, and other animal materials.",
    url: "/verification",
  },
  alternates: {
    canonical: "/verification",
  },
}

const TIERS = [
  {
    label: "Verified Vegan by us",
    badgeVariant: "default" as const,
    heading: "Verified by us",
    body: "We checked the product ourselves: materials lists, manufacturer documentation, and where possible the physical product. This is our strongest tier. If we got something wrong, we want to know.",
  },
  {
    label: "Confirmed Vegan by maker",
    badgeVariant: "default" as const,
    heading: "Confirmed by the maker",
    body: "The manufacturer has stated, in their product documentation or directly to us, that the product contains no animal-derived materials. We record the source and revisit if the product is revised.",
  },
  {
    label: "Verified Vegan by AI",
    badgeVariant: "outline" as const,
    heading: "Materials screened, pending confirmation",
    body: "An automated review of the published materials list found no animal-derived components, but neither we nor the maker have confirmed it yet. Treat this as a strong indication, not a guarantee. These products are in the queue for manual verification.",
  },
  {
    label: "Waiting for confirmation as Vegan",
    badgeVariant: "destructive" as const,
    heading: "Waiting for confirmation",
    body: "The product appears to be free of animal materials, but we're still waiting on the maker or our own review to confirm details like adhesives, liners, and trims. Check the materials on the product page and with the retailer before buying if this matters to you.",
  },
]

export default function VerificationPage() {
  return (
    <div className="max-w-3xl space-y-10">
      <div className="space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold">How we verify vegan gear</h1>
        <p className="text-lg text-muted-foreground">
          Every product in our database carries a verification badge. This page
          explains what each badge means and how a product earns it.
        </p>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">What counts as vegan gear</h2>
        <p className="text-muted-foreground">
          We list gear made without animal-derived materials: no leather, suede,
          wool, silk, down, or animal-based adhesives. Hard parts like armor,
          buckles, and sliders are synthetic across the industry; the animal
          materials usually hide in uppers, palms, liners, trims, and patches.
          That&apos;s where we look.
        </p>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">The four verification tiers</h2>
        <div className="space-y-4">
          {TIERS.map((tier) => (
            <Card key={tier.label}>
              <CardContent className="pt-6 space-y-2">
                <div className="flex flex-wrap items-center gap-3">
                  <Badge variant={tier.badgeVariant}>
                    <span aria-hidden="true">✓</span> {tier.label}
                  </Badge>
                  <h3 className="font-semibold">{tier.heading}</h3>
                </div>
                <p className="text-muted-foreground">{tier.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold">Spotted an error?</h2>
        <p className="text-muted-foreground">
          Manufacturers change materials between production runs, and we&apos;d
          rather correct a listing than defend it. If you know something we
          don&apos;t about a product, tell us on Discord and we&apos;ll review
          it.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Button asChild>
            <a
              href="https://discord.gg/J3vDjQvXPn"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Report a correction on Discord (opens in new tab)"
            >
              Report a correction on Discord
              <span className="sr-only"> (opens in new tab)</span>
            </a>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/products">Browse the catalog</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
