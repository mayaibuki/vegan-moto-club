import type { FaqItem } from "@/lib/notion"
import { JsonLd } from "@/components/JsonLd"
import { faqPageJsonLd } from "@/lib/seo"

interface FaqSectionProps {
  items: FaqItem[]
  title?: string
  /** Heading level for the section title. Pages whose h1 is the section use "h2" (default). */
  headingLevel?: "h2" | "h3"
  /** Emit FAQPage JSON-LD for these items. Turn off when the page combines several sections into one block. */
  withSchema?: boolean
  id?: string
}

/**
 * Always-open list of questions and answers. The text stays visible so search
 * engines and AI crawlers can quote it; the JSON-LD is built from the same items.
 * Renders nothing when there are no items.
 */
export function FaqSection({ items, title = "Common questions", headingLevel = "h2", withSchema = true, id = "faq" }: FaqSectionProps) {
  if (items.length === 0) return null
  const Heading = headingLevel
  const Question = headingLevel === "h2" ? "h3" : "h4"
  const headingId = `${id}-heading`
  return (
    <section aria-labelledby={headingId} className="space-y-6 max-w-3xl">
      {withSchema && <JsonLd data={faqPageJsonLd(items)} />}
      <Heading id={headingId} className={headingLevel === "h2" ? "h-section" : "text-lg font-semibold"}>
        {title}
      </Heading>
      <dl className="space-y-6">
        {items.map((item) => (
          <div key={item.question} className="space-y-2">
            <dt>
              <Question className="text-lg font-semibold text-balance">{item.question}</Question>
            </dt>
            <dd className="text-base text-muted-foreground leading-relaxed max-w-prose text-pretty">
              {item.answer}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
