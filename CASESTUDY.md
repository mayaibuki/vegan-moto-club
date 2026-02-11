# Case Study: Building Vegan Moto Club with Vibe Engineering

How one designer and an AI coding agent built a full production website — without Figma, without a dev team, and without trusting the process. And why years of domain expertise made it possible.

## Sources

This case study maps the Vegan Moto Club project against four frameworks:

1. **Phil Morton** — [How vibe engineering will turn the product design process (and tooling) upside down](https://www.philmorton.co/how-vibe-engineering-will-turn-the-product-design-process-and-tooling-upside-down/) (Jan 21, 2026)
2. **Phil Morton** — [What the vibe engineering workflow tells us about the future of UX roles](https://www.philmorton.co/what-the-vibe-engineering-workflow-tells-us-about-the-future-of-ux-roles/) (Jan 28, 2026)
3. **Jenny Wen** — [Don't Trust the Process](https://www.youtube.com/watch?v=4u94juYwLLM), Hatch Conference, Berlin (Sep 2025)
4. **James Harrison** — [The return of the intuitive designer in the age of AI](https://uxdesign.cc/the-return-of-the-intuitive-designer-in-the-age-of-ai-6f0ea728d1d0), UX Collective (Feb 2026)

---

## The Frameworks

### Morton: Vibe Engineering and the Workflow

Phil Morton argues across two articles that AI coding agents have reached the point where a single developer — or designer — can do the work of an entire team. The bottleneck is no longer code. It's the handoff.

The traditional workflow — design in Figma, hand off specs, developers implement — is slow and lossy. Morton proposes starting in code instead. Use a production-ready component library like shadcn, style it to your brand, and build directly. No Figma-to-code translation layer. No pixel-perfect spec documents that go stale the moment they're written.

He identifies a new skillset designers need: task decomposition for AI agents, precise instruction writing, error detection, version control comfort, and continuous learning. He predicts two career paths emerging: **generalist builders** who work end-to-end from research through production, and **visual specialists** focused on novel brand identity and differentiated UI.

In his second article, Morton gets concrete about the process. AI coding agents have three fundamental constraints: **no long-term memory** (each conversation starts fresh — context must be provided), **limited short-term memory** (context windows fill up and performance degrades), and they work best with **constrained, small tasks** (single large prompts fail). These constraints shape a natural 4-step workflow:

1. **Break down** — Decompose features into the smallest possible tasks
2. **Plan** — Use plan mode before coding; review and question the plan
3. **Code** — The fastest step, once planning is done right
4. **Review** — Never assume completeness; catch errors before production

Morton's key insight is that the bottleneck is *what* to build, not *how* to build it. AI coding agents can only go as fast as humans can give them direction. This elevates UX skills rather than diminishing them — customer-facing work requires rigorous thinking, and teams may need *more* UX capacity to keep up with engineering velocity. Individual hours feel slow, but the compound effect is that weekly progress appears 10x accelerated.

### Wen: Don't Trust the Process

Jenny Wen — Design Lead at Anthropic, formerly Director of Design at Figma — challenges the sacred design process itself. The sequential ritual of research, personas, journey maps, problem statements, ideation, wireframes, and prototyping was built for consultancies that needed to learn a client's business from scratch. It doesn't fit the reality of modern product teams.

Her central argument: in a world where anyone can make anything, what matters is choosing and curating *what* to build, not following a predetermined process for *how* to build it. AI has made prototyping fast and cheap, which means exploring wrong directions is no longer expensive. Designers should lean into craft, taste, and intuition. The user doesn't care about your process artifacts. They care about the end experience.

### Harrison: The Intuitive Designer

James Harrison completes the picture by explaining what makes a designer capable of skipping the process in the first place: **intuition built from experience**.

Harrison describes design intuition as thinking that you know without knowing why you do — a form of expertise where the brain unconsciously compares stored memories, patterns, and mental schemas against a current scenario. It's not guessing. It's the accumulated weight of every design decision you've made, every user you've observed, every product you've shipped.

He argues that UX design is deep inside a de-skilling cycle. The parts of design that have been systematized — following a process, operating design software, producing deliverables — are exactly the parts AI automates. What remains after de-skilling is what couldn't be systematized in the first place: intuition. Harrison frames this as a shift from a knowledge economy to an **intuition economy**. AI can think of faster horses. Intuition can think of cars.

The implication is pointed: if your skillset is centered around your diligence in following a process, or your ability to operate design software, things don't look great. Following a recipe doesn't make you a great chef. But if you've spent years building mental schemas in a domain — accumulating the kind of expertise that lets you know the right answer before you can articulate why — then AI doesn't replace you. It amplifies you.

**How the four frameworks connect:** Morton's first article tells us *what tools* designers will use in this new era (code-first, with AI agents). His second article tells us *what process* to follow (break down → plan → code → review — shaped by the agent's own constraints). Wen tells us *why* designers should stop over-planning and start building (because the cost of iteration is near zero). Harrison tells us *who* can actually pull this off — designers with enough accumulated experience that their intuition is worth trusting.

---

## The Project

**Vegan Moto Club** is a community for vegan motorcycle riders. The site catalogs cruelty-free motorcycle gear — jackets, gloves, boots, pants, racing suits — pulled from a Notion database of 220+ products.

**The designer:** Maya is an experienced product designer who has run the Vegan Moto Club for several years. He knows the community. He knows the riders. He knows which brands make credible vegan gear and which don't. He's answered the questions, moderated the Discord, curated the database, and watched how people actually use the product catalog. This isn't a designer exploring an unfamiliar domain. This is someone with years of accumulated mental schemas about what vegan riders need and how they browse for gear.

Harrison would call this the foundation of design intuition — the kind that lets you skip the formal process steps because you've already internalized what they would have revealed.

**The problem:** The existing website used Super.so, a Notion-to-website wrapper. It was limited in customization, slow, and couldn't support filtering, search, or dynamic features.

**The solution:** Replace it with a custom Next.js website that reads directly from the existing Notion databases (Products, Events, Blog) via the Notion API. Keep Notion as the CMS. Deploy on Vercel.

**The constraint:** One person. No developer. No design team. No Figma license. Just deep domain expertise, a clear vision, and an AI coding agent (Claude) to build it.

---

## Mapping the Build to the Frameworks

### Phases 1-2: Starting in Code, Not in Figma

Morton's core argument is that teams should start with a coded component library instead of designing screens in Figma. This project did exactly that. The very first step was initializing a Next.js 14 project with shadcn/ui and Tailwind CSS. No wireframes. No mockups. The component library *was* the design system from day one.

shadcn/ui provided accessible, production-ready components: Card, Button, Input, Badge, Checkbox, RadioGroup, Label. These became the building blocks for every page — product cards, filter sidebars, event listings, blog layouts.

Wen's framework applies here too. There were no personas. No journey maps. No problem statements. The designer already knew the users (vegan riders), already knew the problem (the Super.so site was too limited), and already knew the solution (custom Next.js site with Notion API). So he skipped the process and started building.

Harrison explains *why* this worked. A designer new to the vegan motorcycle gear space would have needed those process steps — the research, the personas, the journey maps — to build the mental model they were missing. Maya didn't need them. He'd built that mental model over years of running the club. The personas were people he'd talked to. The journey map was something he'd watched happen. The problem statement was something he lived with every time a rider asked him why the site was so hard to filter. His intuition was already loaded with the answers that process is designed to extract.

### Phase 3: Notion API Integration

The AI agent handled the technical plumbing that would traditionally require a backend developer: setting up the Notion API client, mapping database properties to TypeScript interfaces, implementing caching with `unstable_cache` for ISR, building functions to fetch and filter 220+ products, events, and blog posts.

This is what Morton means when he says AI agents make a single person capable of doing the work of ten. The designer described *what* data they needed. The agent figured out *how* to get it.

### Phase 3 (Design): Brand Identity Through Conversation

The design system was established through iterative conversation, not through mood boards or style tiles. The designer specified: Stone base color, Lime accent, DM Sans font, warm grey palette with a bright green highlight. The AI agent translated these preferences into CSS custom properties, Tailwind configuration, and component styling.

These weren't arbitrary choices. Maya had spent years developing an aesthetic sense for the brand — what felt right for a community that's equal parts motorcycle culture and ethical activism. The warm greys with a bright lime accent reflect that identity: grounded and approachable, with an edge. That kind of brand intuition doesn't come from a mood board exercise. It comes from Harrison's mental schemas — years of pattern recognition about what resonates with this specific community.

### Phases 4-7: Git, GitHub, Vercel

The AI agent managed the full DevOps pipeline: initializing the Git repository, configuring GitHub, resolving dependency conflicts (`@radix-ui/react-slot` version mismatch on first Vercel build), setting up environment variables, and deploying to production.

A designer working alone wouldn't traditionally touch any of this. With an AI agent, it became a series of conversational requests.

### Phase 8: Debugging — Agent Oversight in Action

When the site deployed to Vercel, products didn't load. The cause: environment variable names didn't match between the code (`NOTION_API_KEY`) and Vercel (`NEXT_PUBLIC_NOTION_API_KEY`). Then the API key value itself had wrapping double quotes, making it an invalid HTTP header. Then Notion property names in the code didn't match the actual database schema ("Name" vs. "Name of product").

This phase maps directly to Morton's required skillset: **agent oversight and error detection**. The designer couldn't write the fix, but he could identify that something was wrong, provide context (build logs, error messages), and direct the agent to investigate. The agent found root causes and proposed solutions. The designer validated them.

Wen would call this the value of prototyping over planning. If the team had spent weeks writing a perfect integration spec, they still would have discovered these mismatches at deployment. Instead, they discovered them in minutes by building and deploying immediately. The cost of being wrong was near zero.

### Phase 9: Site Audit

The AI agent conducted a comprehensive audit across performance, accessibility, SEO, and code quality — the kind of work that would traditionally require separate specialists or expensive tooling.

Results included: wrapping React components in `React.memo`, adding `useCallback` to event handlers, fixing heading hierarchy for screen readers, adding ARIA labels on external links, correcting JSON-LD currency codes, and replacing ~20 `any` types with proper TypeScript interfaces.

This is Morton's force multiplier in action. One person plus an AI agent produced the output of a performance engineer, an accessibility specialist, an SEO consultant, and a code reviewer — in a single session.

### Phase 10: Design Iteration Through Visual Intent

This phase is where the designer-as-builder model becomes most visible. The designer shared a screenshot of a reference layout and said: update the hero section to match this. The AI agent interpreted the visual intent and built a two-column layout with text left, image right, responsive breakpoints, and specific copy.

Then the iteration began. The designer directed changes through conversational feedback:
- Heading: changed three times, from generic to the final "Ride motorcycles, not animals"
- Grid columns: adjusted twice, from 6 breakpoints down to 3 (2 / 3 / 4 column stops)
- Staff picks count: 6 on mobile, 8 on desktop, using a CSS-only `hidden lg:block` pattern
- Dynamic badge: "Last updated" derived from Notion data instead of hardcoded

This is what Morton calls collapsing the distance between intent and reality. The designer described what he wanted. The agent built it. The designer refined it. No handoff. No spec document. No waiting for a sprint.

Harrison's framework illuminates why the iteration was so efficient. The heading change — from "Solve your user's main problem" to "Connect with other vegans who ride" to "Ride motorcycles, not animals" — wasn't a random walk. It was intuition refining itself. Maya knew the community's voice. He knew the ethos. Each iteration moved closer to something he could already feel was right but hadn't yet articulated. That's exactly Harrison's description of intuition in action: the brain comparing stored patterns against a current scenario, reaching a judgment before the reasoning catches up.

The grid column refinement tells the same story. The first request was six breakpoints. After seeing it, Maya immediately knew it was overengineered and simplified to three. That's not process. That's pattern recognition from someone who has spent years looking at product grids and knows what works.

### Phase 11: Native Form + Spam Protection

The designer asked to replace a Notion iframe embed with a native form using the site's existing shadcn/ui components. From a single conversational prompt, the AI agent built:

- A POST API route (`app/api/suggest/route.ts`) with URL validation and rate limiting
- A client component (`components/SuggestProductForm.tsx`) with four states (idle, submitting, success, error)
- Bot spam protection: a honeypot field invisible to humans but auto-filled by bots, a timing check that rejects submissions faster than 2 seconds, and server-side honeypot validation
- Integration with the Notion products database
- Placement on three pages: home, about, and every product detail page

This is a full-stack feature — frontend, backend, security, database integration — delivered through conversation. No user story. No technical spec. No sprint planning.

The decision to replace the iframe in the first place was intuition. Maya knew from running the community that a clunky embedded form created friction. He'd seen people bounce off it. He didn't need analytics or a usability study to tell him — he'd watched it happen. Harrison would recognize this as intuition interrogating the requirements: not just solving the stated problem, but questioning whether the problem was framed correctly in the first place.

---

## The Workflow: How It Was Built

The theoretical frameworks above explain *why* this project worked. But what did the process actually look like, day to day? Morton's second article provides the structure: a 4-step workflow shaped by the constraints of AI coding agents themselves.

### Step 1: Break Down

Morton warns that AI agents work best with constrained, small tasks. Asking an agent to "build me a website" in one prompt is a recipe for failure. The skill is in decomposition — breaking a large vision into discrete, agent-executable pieces.

Maya applied this instinctively throughout the project. The full website redesign was never a single request. It was decomposed into 11 phases, each with its own scope:

- **Project-level breakdown:** Phase 1 (Notion API setup) → Phase 2 (Next.js scaffold + shadcn/ui) → Phase 3 (data integration + design system) → Phase 4-7 (Git, deployment, environment config) → Phase 8 (debugging) → Phase 9 (audit) → Phase 10 (design iteration) → Phase 11 (native form)

- **Feature-level breakdown:** Phase 10 wasn't "redesign the homepage." It was a series of discrete requests, each small enough for the agent to execute cleanly: hero layout from screenshot → hero copy refinement → grid column counts per breakpoint → staff picks responsive count → dynamic "last updated" badge → product sort order. Six separate conversations, each with a clear, contained scope.

- **Iteration-level breakdown:** Phase 11 wasn't "add a form." It was: replace iframe with native shadcn/ui form → add form to about and product pages → add spam protection (honeypot + timing check). Each step built on the previous one, but each was a self-contained request.

This maps directly to Morton's insight about agent constraints. Each conversation starts fresh with no long-term memory. Context windows are limited. Breaking work into small tasks respects those constraints and produces better output.

### Step 2: Plan

Morton emphasizes planning before coding — using Claude Code's plan mode to design the approach, reviewing the plan, and questioning it before any code is written.

This happened repeatedly throughout the project:

- **Phase 11 (native form):** Before any code was written, a full plan was designed and reviewed: the API route structure, the client component architecture, which shadcn/ui components to use, how to map form data to Notion database properties, what states the form would have (idle, submitting, success, error). Maya reviewed and approved the plan before implementation began.

- **Phase 11 (spam protection + multi-page):** Again, the plan was written first: honeypot field design, timing check mechanism, server-side validation, unique DOM IDs for multi-page rendering. Plan reviewed, then approved, then built.

- **Phase 10 (hero redesign):** The screenshot served as a visual plan. Maya provided a reference layout, described what to match and what to change, and the agent proposed an implementation approach before building.

- **Phase 9 (site audit):** The agent structured the audit into four categories (performance, accessibility, SEO, code quality) before executing. This was planning at the task level — organizing the review approach before diving in.

Morton notes that complex features can consume an entire conversation just for planning. That's exactly what happened with the native form — the plan was detailed enough that the subsequent coding step was fast and accurate.

### Step 3: Code

Morton describes coding as the fastest step once planning is done right. This held true throughout the project.

- **Phase 11:** After the native form plan was approved, the full implementation — API route, client component, honeypot logic, Notion integration — was built in a single pass. Three files created, two files modified, build passing on the first attempt.

- **Phase 3:** The Notion API integration, TypeScript interfaces, caching layer, and data fetching functions were generated directly from clear specifications about which database fields to map.

- **Phase 10:** Each design iteration (hero layout, grid columns, staff picks count) was implemented within minutes of the request. The agent already had context from the plan; it just needed to write the code.

The pattern is consistent: when the break-down and planning steps were done well, coding was fast. When they were rushed — like the initial deployment in Phase 4 that led to the Phase 8 debugging spiral — the coding step produced errors that had to be caught in review.

### Step 4: Review

Morton insists that you should never assume the agent's code is complete or correct. This was validated repeatedly:

- **Build-breaking errors caught:** The `lastEditedTime` field was added to the products list fetch but missed in the single-product fetch function. The Vercel build broke. Maya caught it, directed the agent to fix it, and pushed again.

- **Environment variable mismatch:** Code referenced `NOTION_API_KEY`. Vercel had `NEXT_PUBLIC_NOTION_API_KEY`. Then the value itself had wrapping double quotes, making it an invalid HTTP header. Three bugs, discovered through review after deployment.

- **Design review:** Grid columns were reviewed and redirected (6 breakpoints → 3). Hero copy was reviewed and changed (three iterations). The Notion iframe was reviewed and replaced entirely. Every Phase 10 change went through a visual review cycle — build, check the result in the browser, redirect if needed.

- **Structured review (Phase 9):** Maya directed a full site audit as a formal review pass across performance, accessibility, SEO, and code quality. This is the review step elevated to an entire project phase — using the agent itself as a reviewer.

### The Compound Effect

Morton observes that individual hours feel slow — adjusting grid columns, refining hero copy, debugging an environment variable — but weekly progress appears 10x accelerated.

This project validates that pattern. Each session was iterative: try something, review it, adjust, try again. But the aggregate output across 11 phases was a complete production website with 220+ products, 7 page types, Notion API integration, filtered search, responsive design, performance optimization, accessibility compliance, spam-protected forms, and production deployment on Vercel. That's the compound effect: small loops stacking into something that would have taken a traditional team months.

---

## Skills the Designer Demonstrated

### From Morton's Required Skillset

| Skill | Evidence |
|-------|----------|
| **Task decomposition** | Broke work into discrete, agent-executable requests: "change grid to 4 cols on lg", "sort by last_edited_time", "replace iframe with native form" |
| **Precise instructions** | Specified exact breakpoint behavior: "default 2 cols, md 3 cols, lg/xl/2xl capped at 4 cols" |
| **Agent oversight** | Caught wrong grid columns, incorrect hero copy, env var mismatches, quoted API key values, wrong Notion embed URL format |
| **Error detection** | Identified that products weren't loading on Vercel, provided build logs for debugging |
| **Version control comfort** | Reviewed git status, understood commit history, directed pushes to GitHub |
| **Continuous learning** | Adapted from Notion iframe to native form when the iframe approach proved limiting |

### From Morton's Workflow

| Step | Evidence |
|------|----------|
| **Break down** | Decomposed full redesign into 11 phases. Decomposed Phase 10 into 6 discrete requests. Decomposed Phase 11 into 3 sequential steps. |
| **Plan** | Used plan mode for native form, spam protection, and multi-page form. Provided screenshots as visual plans for hero redesign. |
| **Code** | Fastest step after planning — full-stack form feature built in a single pass after approved plan |
| **Review** | Caught build errors, env var bugs, design mismatches. Directed Phase 9 as a structured review pass. |

### From Wen's Thesis

| Principle | Evidence |
|-----------|----------|
| **Taste and curation** | Chose Stone + Lime palette, DM Sans font, warm grey aesthetics. Iterated hero heading three times until it felt right. |
| **Start from solutions** | Already knew the answer: Next.js + Notion API + Vercel. Didn't need discovery research to validate it. |
| **Prototype over process** | The production site was the first and only artifact. No wireframes, no mockups, no intermediate deliverables. |
| **Craft in the details** | Specified "hidden lg:block" for responsive product counts, dynamic "Last updated" from Notion timestamps, honeypot spam protection |
| **Trust intuition** | Directed design changes through screenshots and instinct, not through user testing or A/B experiments |

### From Harrison's Intuitive Designer

| Principle | Evidence |
|-----------|----------|
| **Domain expertise as intuition** | Years of running Vegan Moto Club — knew the users, the gear landscape, the community culture, and the pain points without needing formal research |
| **Mental schemas from experience** | Immediately knew the right grid layout, the right hero tone, and which product sorting made sense — decisions that would require research for someone new to the domain |
| **Intuition interrogating the problem** | Replaced the iframe form not because of data, but because he'd seen users struggle with it. Questioned requirements, not just solutions. |
| **Critical self-assessment** | Didn't blindly trust first instincts. Iterated the hero heading three times. Revised grid breakpoints after seeing the result. Good intuition includes knowing when your first answer isn't right. |
| **Pattern recognition** | Recognized that 6 breakpoints was overengineered after one look. Knew Stone + Lime would resonate with the community. Chose "Ride motorcycles, not animals" because it matched the voice he'd cultivated over years. |

---

## What This Proves

This project is a working example of the future all four frameworks describe — and a demonstration of why they are complementary, not competing.

**Morton's vision holds — both the tools and the workflow.** A designer with no traditional coding skills built a production website across 11 phases using an AI coding agent. The work spanned frontend, backend, API integration, DevOps, performance optimization, accessibility compliance, and security — the output of what would have been a team of five or more. The key enabler was starting with a coded design system (shadcn/ui) and working directly in code from day one. The 4-step workflow (break down → plan → code → review) wasn't imposed as a methodology — it emerged naturally from the constraints of the agent itself. Every phase followed the same loop: decompose the work, plan the approach, let the agent code, review the output.

**Wen's thesis holds.** No part of this project followed a traditional design process. There were no personas, no journey maps, no problem statements, no wireframes. The designer knew what to build, started building it, and iterated based on craft and taste. Wrong directions (Shopify CDN whitelisting, Notion iframe embeds, initial grid layouts) were explored and abandoned cheaply. The cost of being wrong was minutes, not months.

**Harrison's thesis holds — and it's the one that explains the other two.** Morton's tools and Wen's philosophy only work when the designer has something real to bring to the table. You can skip the process when you already carry the insights the process is designed to produce. Maya could skip personas because he already knew his users. He could skip journey maps because he'd watched the journey happen. He could trust his instinct on brand, layout, copy, and interaction patterns because he'd built the mental schemas over years of running the community.

Harrison warns that not all intuition is good intuition — and this project shows what good intuition looks like in practice. It's not about never being wrong. Maya's first hero heading wasn't right. His first grid layout was overengineered. His first approach to the suggestion form (Notion iframe) was clunky. But he recognized each of these quickly, redirected the agent, and iterated toward something better. That's the critical distinction Harrison draws: intuition isn't blind confidence. It's expertise combined with the self-awareness to know when your first answer needs refining.

**The synthesis:** Morton gives designers the tools and the workflow to build without a dev team. Wen gives them permission to skip the process. Harrison explains who actually can — designers whose intuition has been forged through years of domain experience. Together, they describe a world where the designer's value isn't in following a process or producing artifacts. It's in the accumulated expertise that lets them know what's worth building, the taste to recognize when it's right, and the AI-powered tools to make it real in hours instead of months.

This project took days, not months. One person, not a team. Zero Figma files. And the site is live, serving 220+ products to a real community of vegan motorcycle riders — built by someone who knew exactly what that community needed, because he'd been part of it for years.

That's vibe engineering. And it runs on intuition.

---

**Project:** [Vegan Moto Club](https://vegan-moto-club.vercel.app) | [GitHub](https://github.com/mayaibuki/vegan-moto-club)
**Built with:** Next.js 14, Notion API, shadcn/ui, Tailwind CSS, Vercel, Claude
**Date:** February 2026
