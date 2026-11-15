# Width.ai Claude Humanizer Skill

A portable agent skill that rewrites AI-generated text into natural, human writing. It is built for long-form marketing content (blog posts, landing pages, product pages, and SOPs), where the rewrite has to stay persuasive and keep ranking, not just sound neutral. It still handles reference and technical text, where plain, neutral prose is the goal. Plain Markdown, so it runs in any harness that supports skill-style instructions.

This is the exact humanizer skill framework used in our blog post generation agentic framework. 

## Installation

### Skills CLI

Install globally with the cross-agent skills CLI so Humanizer is available in every project:

```bash
npx skills add Matt-Payne/content-humanizer --global
```

Update an existing install:

```bash
npx skills update humanizer --global
```

To install globally into every supported agent harness:

```bash
npx skills add Matt-Payne/content-humanizer --global --agent '*'
```

To target one configured harness, pass its agent name:

```bash
npx skills add Matt-Payne/content-humanizer --global --agent <agent-name>
```

Omit `--global` for a project-local install that can be committed and shared with collaborators. Start a new agent session or reload skills after installation.

### Claude Code plugin

Claude Code users can also install Humanizer as a plugin:

```
/plugin marketplace add Matt-Payne/content-humanizer
/plugin install humanizer@humanizer
```

The skill is then invoked as `/humanizer:humanizer`.

### Manual

Any agent harness that can load Markdown skill instructions can use the skill directly. The entry point is `SKILL.md`, which loads its detail on demand from the `references/` directory, so ship the whole skill directory together (not `SKILL.md` alone). Install it wherever your harness expects skill directories.

For example:

```bash
git clone https://github.com/Matt-Payne/content-humanizer.git /path/to/your/skills/humanizer
```

Or, if you already have this repo cloned, copy `SKILL.md` and its `references/` folder into the skill directory:

```bash
mkdir -p /path/to/your/skills/humanizer
cp -R SKILL.md references /path/to/your/skills/humanizer/
```

## Usage

Invoke the skill however your agent harness exposes installed skills. Common forms include a slash command or a direct request:

```
/humanizer

[paste your text here]
```

```
Please humanize this text: [your text]
```

Point it at a file and the skill rewrites it in place:

```
Humanize the prose in docs/launch-post.md
```

### Voice Calibration

To match your personal writing style, provide a sample of your own writing:

```
/humanizer

Here's a sample of my writing for voice matching:
[paste 2-3 paragraphs of your own writing]

Now humanize this text:
[paste AI text to humanize]
```

The skill will analyze your sentence rhythm, word choices, and quirks, then apply them to the rewrite instead of producing generic "clean" output.

## Overview

Humanizer detects and rewrites the tells of AI-generated writing. It works in two modes depending on what you point it at:

- **Marketing mode** (blog posts, landing pages, product pages, SOPs): keep the copy persuasive, scannable, and search-optimized while cutting the AI tells. Nine patterns switch from "delete" to "make it concrete and keep the sell," and a dedicated SEO/structure pass preserves the target keyword, heading hierarchy, links, images, and the call to action.
- **Reference mode** (docs, wikis, technical, legal): neutral, plain, and factual is the goal, so every pattern applies at full strength.

The pattern catalog is based on [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide, maintained by WikiProject AI Cleanup, drawn from thousands of observed instances of AI-generated text.

The skill runs a final "obviously AI generated" audit pass and a second rewrite to catch lingering AI-isms in the first draft. It also follows a no-fabrication rule: it never adds facts, names, numbers, dates, or citations that aren't in the source text; specificity has to come from the source or the author. In marketing content that extends to invented stats, testimonials, customers, and logos.

### Key Insight from Wikipedia

> "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."

## 33 Patterns Detected (with Before/After Examples)

### Content Patterns

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 1 | **Significance inflation** | "marked a pivotal moment in how modern teams work with data" | "We launched the dashboard in 2021" |
| 2 | **Notability / social proof** | "featured in TechCrunch, Forbes, Wired, and dozens of outlets" | Keep the real, specific proof; cut the vague pile-on |
| 3 | **Superficial -ing analyses** | "ensuring a smooth experience, fostering engagement, reflecting our commitment" | "walks new users through each step of setup" |
| 4 | **Promotional language** | "a vibrant, all-in-one platform with a breathtaking experience" | "Acme is a project management platform" |
| 5 | **Vague attributions** | "Experts agree AI is reshaping support" | Name a real source or cut the claim |
| 6 | **Formulaic challenges** | "Despite challenges... well-positioned to keep thriving" | Keep the real facts; cut the boosterism |

### Language Patterns

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 7 | **AI vocabulary** | "leverages a robust, intricate architecture... vibrant ecosystem" | "built for performance and relies on automation" |
| 8 | **Copula avoidance** | "serves as... boasts... features integrations" | "is... has... integrates with" |
| 9 | **Negative parallelisms / tailing negations** | "It's not just X, it's Y", "..., no guessing" | State the point directly |
| 10 | **Rule of three** | "innovation, inspiration, and insights" | Use natural number of items |
| 11 | **Synonym cycling** | "protagonist... main character... central figure... hero" | "protagonist" (repeat when clearest) |
| 12 | **False ranges** | "from the Big Bang to dark matter" | List topics directly |
| 13 | **Passive voice / subjectless fragments** | "No configuration file needed" | Name the actor when it helps clarity |

### Style Patterns

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 14 | **Em/en dashes** | "institutions—not the people—yet this continues—" | Cut them: periods, commas, colons, or parentheses |
| 15 | **Boldface overuse** | "**OKRs**, **KPIs**, **BMC**" | "OKRs, KPIs, BMC" |
| 16 | **Inline-header lists** | "**Performance:** Performance improved" | Convert to prose |
| 17 | **Title Case Headings** | "Strategic Negotiations And Partnerships" | "Strategic negotiations and partnerships" |
| 18 | **Emojis** | "🚀 Launch Phase: 💡 Key Insight:" | Remove emojis |
| 19 | **Curly quotes** | `said “the project”` | `said "the project"` |
| 26 | **Hyphenated word pairs** | “cross-functional, data-driven, client-facing” | Drop hyphens on common word pairs |
| 27 | **Persuasive authority tropes** | "At its core, what matters is..." | State the point directly |
| 28 | **Signposting announcements** | "Let's dive in", "Here's what you need to know" | Start with the content |
| 29 | **Fragmented headers** | "## Performance" + "Speed matters." | Let the heading do the work |
| 30 | **Diff-anchored writing** | "This function was added to replace..." | Describe what it does, not what changed |
| 31 | **Manufactured punchlines / staccato drama** | "It had no preference. No prior. No nostalgia." | Use varied sentence lengths and concrete claims |
| 32 | **Aphorism formulas** | "Symmetry is the language of trust" | Replace the formula with the actual claim |
| 33 | **Conversational rhetorical openers** | "Honestly? It depends..." | Remove the fake-candid setup |

### Communication Patterns

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 20 | **Chatbot artifacts** | "I hope this helps! Let me know if..." | Remove entirely |
| 21 | **Cutoff disclaimers** | "While details are limited in available sources..." | Find sources or remove |
| 22 | **Sycophantic tone** | "Great question! You're absolutely right!" | Respond directly |

### Filler and Hedging

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 23 | **Filler phrases** | "In order to", "Due to the fact that" | "To", "Because" |
| 24 | **Excessive hedging** | "could potentially possibly" | "may" |
| 25 | **Generic conclusions** | "The future looks bright" | Specific plans or facts |

## Full Example

*(Illustration note: the rewrite keeps the piece persuasive and on topic while cutting the AI tells. It invents no statistics, customers, or results; where the original leaned on a vague "studies show," the rewrite drops the fake citation instead of inventing a real one.)*

**Before (AI-sounding):**
> In today's fast-paced digital landscape, email marketing has become more crucial than ever for businesses looking to thrive. With inboxes more crowded than ever, standing out is no longer optional — it's essential.
>
> That's where segmentation comes in. By leveraging the power of data-driven segmentation, businesses can unlock unprecedented levels of engagement and drive meaningful results. Whether you're a scrappy startup or an established enterprise, segmentation is the key to transforming your email strategy.
>
> In this post, we'll dive into everything you need to know about email segmentation. From the basics to advanced strategies, we've got you covered. Let's get started!
>
> ## Why Segmentation Matters
>
> Segmentation matters. It's one of the most powerful tools in your marketing arsenal.
>
> At its core, segmentation is about delivering the right message to the right person at the right time. Studies show that segmented campaigns boost engagement, improve conversions, and foster lasting customer relationships. The benefits are clear: higher open rates, better click-through rates, and increased revenue.

**After (Humanized):**
> Most email lists get treated like one big group. You write one message, send it to everyone, and hope it lands. It usually doesn't.
>
> Segmentation is the fix, and it's simpler than it sounds. Instead of emailing your whole list the same thing, you split it into smaller groups based on what people actually do: what they bought, what they clicked, how long since they last opened anything. Then each group gets a message that fits.
>
> This post covers how to set that up, starting with the segments worth building first.
>
> ## Why segmentation is worth the effort
>
> A generic email asks everyone to care about the same thing at the same moment. Most won't. Someone who bought last week doesn't need the "come back" offer you're sending to people who haven't opened anything in six months.
>
> When the message matches where the reader actually is, more of them open it, more click, and fewer unsubscribe. You're not sending more email. You're sending email that's harder to ignore.

## References

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) - Primary source
- [WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup) - Maintaining organization

## Version History

- **2.12.1** - Added a second set of rewrite examples to `references/examples.md` (catalog data and product content, including a full hook rewrite), several with the editor's reasoning for the change. Grouped the examples into sets and added a short summary of the recurring edits (point the sentence at the reader, swap vague stand-ins for the concrete thing, name the consequence, soften indefensible absolutes). Broadened the brand caveat to cover named products. No change to the 33 patterns.
- **2.12.0** - Added `references/examples.md`, a standalone bank of before/after rewrite examples (original text and the preferred revision) used as concrete models of the target voice and rewrite style. Wired it into `SKILL.md`'s reference map and the package validator (`REFERENCES` and `LINE_BUDGETS`). The examples carry brand-specific positioning, so a header directs the skill to borrow the editing style, not the facts, keeping the no-fabrication rule intact. No change to the 33 patterns.
- **2.11.0** - Restructured into progressive disclosure. `SKILL.md` is now a lean always-loaded router (task, content-type routing, invocation modes, process, and a reference map); the detail moved into `references/patterns.md` (the 33-pattern catalog), `references/seo-preservation.md`, `references/voice.md`, and `references/detection.md`, which are read on demand. The package validator now enforces per-file line budgets and checks that every reference file exists and is wired into `SKILL.md`. Behavior and the 33 patterns are unchanged; the whole skill directory (including `references/`) must now ship together.
- **2.10.0** - Added long-form marketing awareness. A new "Content Types" section distinguishes reference/technical text (neutral is correct) from marketing content (blog posts, landing pages), and nine patterns (#1, #2, #4, #10, #15, #16, #17, #18, #25) now carry "In marketing copy" carve-outs that switch them from "delete" to "make it concrete and keep the sell." Added marketing false-positive guards (persuasive tone, brand-style title case, real social proof, keywords and heading structure) and tightened the no-fabrication rule for marketing claims (stats, testimonials, customers, logos, counts, capabilities). Swapped the content-pattern examples (#1-8) and the full worked example from encyclopedic topics (towns, rivers, cuisine) to marketing content (SaaS blogs and landing pages), keeping the rewrites fabrication-free. Added an SEO and structure-preservation module (target keyword placement, heading hierarchy, links, images and alt text, snippet/FAQ structure, meta and frontmatter, CTA, and topical depth) so humanizing marketing content doesn't strip what makes it rank. No change to the 33 patterns.
- **2.9.1** - Improved distribution and portability: removed nonportable frontmatter and tool preapprovals, made global installation the documented default, added package validation, and removed the duplicated long-form example from the runtime prompt. No change to the 33 patterns.
- **2.9.0** - Added a no-fabrication rule: rewrites may not invent facts, names, dates, or citations not present in the source, and every example that modeled invented specifics was re-cut to use only source information (fixes #187). Replaced paragraph-count parity with an information-over-shape rule, made a user's voice sample outrank the em dash ban, and added invocation modes (pasted text / file / embedded). No change to the 33 patterns.
- **2.8.3** - Moved the skill version from the unsupported top-level frontmatter key to `metadata.version` for Agent Skills and Claude compatibility. No change to the 33 patterns.
- **2.8.2** - Replaced the full before/after example with a first-person Lisbon trip recap. The after now keeps the same topic, perspective, and rough length as the before while removing the AI tells without becoming clipped or slogan-like. No change to the 33 patterns.
- **2.8.1** - Added cross-agent installation docs, optional Claude Code plugin packaging, and a compact secondhand-text false-positive guard. No change to the 33 patterns.
- **2.8.0** - Added style/cadence patterns #31-33 for manufactured punchlines, aphorism formulas, and conversational rhetorical openers; expanded #20 to catch offer-to-continue chatbot closers. 33 patterns total.
- **2.7.0** - Added pattern #30 (diff-anchored writing); made em/en dashes a hard cut rather than "overuse"; expanded #21 to cover speculative gap-filling ("maintains a low profile"). 30 patterns total.
- **2.6.0** - Cleanup pass: consolidated the duplicated workflow sections, gated the personality guidance to content where voice is wanted, removed the model-fingerprinting subsection, and condensed the worked example. No change to the 29 patterns.
- **2.5.1** - Added a passive-voice / subjectless-fragment rule, raising the total to 29 patterns
- **2.5.0** - Added patterns for persuasive framing, signposting, and fragmented headers; expanded negative parallelisms to cover tailing negations; tightened wording around em dash overuse; fixed frontmatter wording to use "filler phrases"
- **2.4.0** - Added voice calibration: match the user's personal writing style from samples
- **2.3.0** - Added pattern #25: hyphenated word pair overuse
- **2.2.0** - Added a final "obviously AI generated" audit + second-pass rewrite prompts
- **2.1.1** - Fixed pattern #18 example (curly quotes vs straight quotes)
- **2.1.0** - Added before/after examples for all 24 patterns
- **2.0.0** - Complete rewrite based on raw Wikipedia article content
- **1.0.0** - Initial release

## License

MIT
