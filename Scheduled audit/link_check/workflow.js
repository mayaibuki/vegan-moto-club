export const meta = {
  name: 'vmc-store-link-audit',
  description: 'Verify every product store link and price, find replacements for broken links, confirm fixes',
  whenToUse: 'Vegan Moto Club store-link audit over harvested digests in Scheduled audit/link_check/runs/<date>',
  phases: [
    { title: 'Health triage', detail: 'Haiku: ambiguous or blocked pages, alive or dead', model: 'haiku' },
    { title: 'Match', detail: 'Sonnet: does the page show the exact product', model: 'sonnet' },
    { title: 'Price', detail: 'Haiku: regular price and currency of matched pages', model: 'haiku' },
    { title: 'Fix', detail: 'Sonnet: find the right link, brand store first', model: 'sonnet' },
    { title: 'Confirm', detail: 'Sonnet: adversarial check of every proposed link', model: 'sonnet' },
    { title: 'Discontinued check', detail: 'Opus: independent search before anything is called discontinued', model: 'opus' },
  ],
}

const RUN = args.run
const TOOL = args.tool
const norm = id => String(id || '').replace(/-/g, '').trim()
const dig = id => `${RUN}/digests/${norm(id)}.json`
const rowsOf = r => (r && Array.isArray(r.rows) ? r.rows : [])
const chunk = (a, n) => { const o = []; for (let i = 0; i < a.length; i += n) o.push(a.slice(i, i + n)); return o }
const byId = (list, id) => list.find(x => norm(x.page_id) === norm(id))

const LEVEL = { type: 'string', enum: ['high', 'medium', 'low'] }
const NUM_OR_NULL = { type: ['number', 'null'] }
const rowsSchema = (props, required) => ({
  type: 'object',
  properties: { rows: { type: 'array', items: { type: 'object', properties: props, required } } },
  required: ['rows'],
})
const TRIAGE = rowsSchema({
  page_id: { type: 'string' },
  verdict: { type: 'string', enum: ['ALIVE', 'DEAD', 'HOMEPAGE_OR_LISTING', 'UNCLEAR'] },
  reason: { type: 'string' },
}, ['page_id', 'verdict', 'reason'])
const MATCH = rowsSchema({
  page_id: { type: 'string' },
  verdict: { type: 'string', enum: ['MATCH', 'WRONG_PRODUCT', 'NOT_PRODUCT_PAGE', 'DEAD', 'DISCONTINUED_NOTICE', 'UNVERIFIABLE'] },
  confidence: LEVEL,
  page_product: { type: 'string' },
  evidence: { type: 'string' },
}, ['page_id', 'verdict', 'confidence', 'page_product', 'evidence'])
const PRICE = rowsSchema({
  page_id: { type: 'string' },
  regular_price: NUM_OR_NULL,
  currency: { type: 'string' },
  on_sale: { type: 'boolean' },
  confidence: LEVEL,
  source: { type: 'string' },
}, ['page_id', 'regular_price', 'currency', 'on_sale', 'confidence', 'source'])
const FIX = rowsSchema({
  page_id: { type: 'string' },
  outcome: { type: 'string', enum: ['FOUND', 'CURRENT_OK', 'SUCCESSOR_ONLY', 'NOT_FOUND'] },
  proposed_url: { type: 'string' },
  store_type: { type: 'string', enum: ['brand', 'retailer', 'none'] },
  successor: { type: 'string' },
  still_sold_at: { type: 'array', items: { type: 'string' } },
  regular_price: NUM_OR_NULL,
  currency: { type: 'string' },
  notes: { type: 'string' },
}, ['page_id', 'outcome', 'proposed_url', 'store_type', 'successor', 'still_sold_at', 'regular_price', 'currency', 'notes'])
const CONFIRM = rowsSchema({
  page_id: { type: 'string' },
  verdict: { type: 'string', enum: ['CONFIRMED', 'REJECTED'] },
  regular_price: NUM_OR_NULL,
  currency: { type: 'string' },
  confidence: LEVEL,
  reason: { type: 'string' },
}, ['page_id', 'verdict', 'regular_price', 'currency', 'confidence', 'reason'])
const DISC = rowsSchema({
  page_id: { type: 'string' },
  verdict: { type: 'string', enum: ['FOUND_LIVE', 'DISCONTINUED'] },
  proposed_url: { type: 'string' },
  store_type: { type: 'string', enum: ['brand', 'retailer', 'none'] },
  still_sold_at: { type: 'array', items: { type: 'string' } },
  successor: { type: 'string' },
  evidence: { type: 'string' },
}, ['page_id', 'verdict', 'proposed_url', 'store_type', 'still_sold_at', 'successor', 'evidence'])

const ABOUT = `Context: veganmotoclub.com is a catalog of vegan motorcycle gear. Each product row in its Notion database has a "View on Store" link and a price, and we are auditing every link. Do not edit any files and do not touch Notion: only report.`
const DIGEST = `A script already fetched every link. Each product has a digest JSON with: notion (what our database says: name, brand, category, gender, vegan_verified, url, price), health (bucket, HTTP status, final_url after redirects, redirect_chain, landed_on_listing), page (title, h1, og_title, canonical), product_data (jsonld Product data, shopify product data, meta_price), markers (text snippets matching soft-404 / discontinued / sold-out / bot-wall patterns), price_snippets (prices found in the page text; those starting with "[near title]" sit right after the product name) and text (the start of the visible page text). A shopify.price_note means the store catalog price could not be confirmed on the page: then ignore shopify prices.`
const SAME = `Same product means: same brand, same model, same generation/version and same gender line. Version markers must agree: "2" vs "3", "V2", "Evo", "Pro", "Air", "GTX", "H2O", "WP", and Lady/Ladies/Women/Stella are all meaningful ("Tech-Air 3" and "Tech-Air 3 V2" are different products). Colorway differences are fine. Notion names are often shortened (category words or "Women's" dropped), so read notion.gender and notion.category with the name; Unisex matches either gender.`
const TOOLS = `Tools: python3 "${TOOL}" --search <domain> "<query>" 2>/dev/null searches a Shopify store's products (for REV'IT! use the domain "revitsport.com/en-us" so results are US products; non-Shopify stores return an error). python3 "${TOOL}" --url "<url>" 2>/dev/null fetches a page and prints its digest (status, final URL, title/h1, structured product data, price snippets, stock). For web search, load the tools first with ToolSearch query "select:WebSearch,WebFetch".`
const REGULAR = `Regular price = the normal, non-sale price of the default variant. A struck-through, "was", "compare at" or "regular" price next to a lower price, a "-30%" badge or "Sale" means a sale, and the HIGHER price is the regular one. "[near title]" snippets show this, e.g. "$1,029.99 USD $720.99 USD" or "$299 $209.30 -30%". JSON-LD offers and meta prices are often the current sale price. Some stores (REV'IT!) run sales without a Shopify compare_at, so a single Shopify price can be a sale price. Ignore prices of other products, add-ons ("add for $74.99") and shipping thresholds.`
const BRAND_RULE = `The owner's rule for links: the brand's own store first. A major US retailer (RevZilla, Cycle Gear, Sportbike Track Gear, Motorcycle Superstore and similar) only for brands that do not sell online themselves, or when the brand never listed this product on its own store. If a brand that sells online no longer lists this product, it is probably discontinued: do not replace its link with a retailer's leftover stock; report the retailers in still_sold_at instead. The site is for US riders: when the brand has a US store (or a US market such as revitsport.com/en-us), the product must be listed there. A page on the brand's store for another country (ca.alpinestars.com, a /en-gb/ market and so on) is not a valid replacement; report it in still_sold_at. Brands with a single international store and no US store (Pando Moto, FIVE, Motogirl and similar) are fine as they are. Only the store's public shopping domain counts: checkout or "secure." subdomains, myshopify.com or CDN mirrors of a product the public store no longer lists do not; treat that product as unlisted.`

const triagePrompt = item => `${ABOUT} ${DIGEST}

You are the link-health triage step. The script could not classify these pages with confidence: no product data, soft-404 wording, a bot wall, a server error, or a redirect to a listing. Read the batch file ${item.path} (a JSON array of digests) and judge every row in it.

Verdicts:
- ALIVE: the page shows one specific product (its name in the title, h1 or text, with a price, sizes or an add-to-cart), even without structured data.
- DEAD: an error page, "page not found", "no longer exists", an expired site or an empty shell.
- HOMEPAGE_OR_LISTING: the store homepage, a category, collection or outlet listing, or search results instead of one product.
- UNCLEAR: a bot wall, a server error, a redirect notice ("You are being redirected") or too little content to tell.
Judge from the digest only (health, page, markers, text); do not browse. reason: under 20 words, quoting the decisive words. Return one row per page_id in the file.`

const matchPrompt = (item, ids) => `${ABOUT} ${DIGEST}

You are the product-match verifier. ${ids ? `Read these digest files and judge each one: ${ids.map(dig).join(', ')}.` : `Read the batch file ${item.path} (a JSON array of digests) and judge every row in it.`}

For each row decide whether the page a shopper lands on (health.final_url) shows the SAME product as the Notion row. ${SAME} A retailer page (RevZilla, Cycle Gear and so on) for the exact product counts.

Verdicts:
- MATCH: the same product.
- WRONG_PRODUCT: a real product page for a different product (another model, generation or gender line).
- NOT_PRODUCT_PAGE: the homepage, a category, collection or outlet listing, search results or a generic landing page.
- DEAD: an error page, "page not found" or an empty shell.
- DISCONTINUED_NOTICE: the right product page, but it explicitly says the product is discontinued, no longer available or no longer produced.
- UNVERIFIABLE: a bot wall, a server error or too little content to tell.

Rules: judge from the digest only; do not browse. health.bucket REDIRECTED means the store sent the shopper elsewhere, so compare what the final page shows. Sold-out markers usually come from a size selector ("Currently unavailable", "Notify me") and do NOT mean discontinued. page_product: the product name the page shows, or "" if none. evidence: under 25 words; quote the decisive title, h1 or structured name, and for anything but MATCH say what differs. confidence: high when the title, h1 or structured data clearly agree or clearly differ, medium on partial signals, low when guessing. Return one row per page_id.`

const pricePrompt = (item, ids) => `${ABOUT} ${DIGEST}

You read store prices. Each page_id below was already verified to show the right product. ${item.kind === 'match' ? `Read the batch file ${item.path} (a JSON array of digests) and handle ONLY these page_ids: ${ids.join(', ')}.` : `Read these digest files: ${ids.map(dig).join(', ')}.`}

For each, return the REGULAR price and its currency as the store shows it. ${REGULAR}
Where to read it, in order:
1. price_snippets starting with "[near title]": two prices side by side mean regular then sale. RevZilla writes "Current price is $ 349 . 99" (= 349.99) and adds a "was" price on sale.
2. product_data.shopify.default_regular (already uses compare_at when higher) with shopify.currency, unless shopify.price_note is set. Trust a higher regular price in the near-title snippets over it.
3. product_data.jsonld offers and meta_price, only when nothing above contradicts them.
currency: an ISO code. "€" = EUR, "£" = GBP, "A$" or "AU$" = AUD, "CA$" = CAD, "$" on a US store = USD; prefer shopify.currency or JSON-LD priceCurrency when present. European decimals "64,90 €" = 64.90.
No trustworthy price: regular_price null, confidence low. on_sale: true when the page shows a sale. source: what you used, e.g. "near-title '$299 $209.30 -30%'", "shopify.default_regular", "jsonld offer". confidence: high = structured data or one unambiguous price next to the title; medium = inferred from snippets; low = unclear. Return one row per listed page_id.`

const fixPrompt = g => `${ABOUT} ${DIGEST}

You are a link fixer. These products' "View on Store" links are broken: they 404, land on a homepage or listing, show a different product, or the page says the product is discontinued. For each row find the live product page for EXACTLY the same product. ${SAME}

${g.rows ? `Rows (read each digest for the Notion data and what the current link returns):\n${g.rows.map(r => `- page_id ${r.page_id} | why: ${r.why} | digest: ${dig(r.page_id)}`).join('\n')}` : `Rows: every row in the batch file ${g.batchFile} (a JSON array of digests). The script found each link dead or redirected to the homepage; see health.bucket and health.reason.`}

${TOOLS}
${BRAND_RULE}
Search: first the brand's own store (store search with several phrasings: the model name with and without words like Jacket, Gloves, Women's, Ladies; a renamed handle such as "copy-of-..." usually means the product moved, so search by name), then WebSearch ("<brand> <model>", then site:<brand domain> "<model>"), then retailers when the rule allows. Before proposing a URL, open it with --url: it must be a product page (not a listing) for the same product.

Outcomes:
- FOUND: proposed_url = the canonical product page URL without tracking or search parameters (such as "?_pos="); store_type brand or retailer.
- CURRENT_OK: the current URL does work and shows the exact product (the script may have been blocked). proposed_url = the current URL, store_type as it is.
- SUCCESSOR_ONLY: the exact product is gone but the brand sells a newer version. Do NOT propose the successor: vegan status is specific to each product. successor = "<name> <url>", proposed_url "", store_type none.
- NOT_FOUND: the brand no longer lists the exact product and there is no valid replacement under the rule. proposed_url "", store_type none.
For every row list in still_sold_at any reputable retailer URLs still selling the exact product. For FOUND and CURRENT_OK give the regular (non-sale) price and currency if visible, else null. notes: under 40 words. Budget about 12 tool calls per row. Return one row per page_id.`

const confirmPrompt = list => `${ABOUT}

You are an adversarial checker. Another agent proposed replacement "View on Store" links. Try to REFUTE each one: a wrong link sends shoppers to a different product, so default to REJECTED when the evidence is not clear.

Rows (each digest file holds the Notion row under "notion"):
${list.map(x => `- page_id ${x.page_id} | proposed: ${x.proposed_url} | Notion row: ${dig(x.page_id)} | proposer notes: ${x.notes || ''}`).join('\n')}

${TOOLS}
Fetch each proposed URL yourself with --url (if it is blocked, try WebFetch). CONFIRMED only if ALL hold: HTTP 200 on a single product page (not a listing or homepage) after redirects; no discontinued notice; it is the same product as the Notion row; and the link follows the owner's rule below. ${SAME}
${BRAND_RULE}
Also read the regular price and currency. ${REGULAR} Use null if unclear.
reason: under 30 words, quoting the page title that decided it. Return one row per page_id.`

const discPrompt = list => `${ABOUT}

You are the last check before products are listed as discontinued. The owner will decide whether to trash these rows, so a false "discontinued" could delete a product that is still sold. Another agent found no live page for these exact products, or its proposed link was rejected. Search independently and thoroughly.

Rows (each digest file holds the Notion row under "notion" and what the old link returns):
${list.map(x => `- page_id ${x.page_id} | digest: ${dig(x.page_id)} | first search: ${x.outcome || '?'}${x.notes ? `, ${x.notes}` : ''}${x.successor ? ` | successor seen: ${x.successor}` : ''}${x.rejected ? ` | rejected candidate: ${x.proposed_url} (${x.rejected})` : ''}`).join('\n')}

${TOOLS}
For each row: store search on the brand's site with several phrasings; WebSearch with the model name, brand + model, the old URL's slug, with and without the category word; and major US retailers. Verify every candidate with --url. ${SAME}

Verdicts:
- FOUND_LIVE: the maker still sells the exact product to US riders: live on the brand's own US store (or its only store) on the public shopping domain, or, for brands that do not sell online themselves, a current listing at a major US retailer. proposed_url = that page; store_type.
- DISCONTINUED: the maker no longer sells it to US riders (gone from its own US store or current lineup), even if some retailers or the brand's store for another country still have it. List those retailers in still_sold_at (this matters for the owner's keep-or-trash decision), and in successor the newer model the brand sells instead, as "<name> <url>", if any. proposed_url "", store_type none.
evidence: under 40 words: what you searched and what you found. Return one row per page_id.`

async function fixChain(item, g, gi) {
  const tag = `${item.label}.${gi + 1}`
  const f = await agent(fixPrompt(g), { label: `fix:${tag}`, phase: 'Fix', model: 'sonnet', effort: 'medium', schema: FIX })
  const fixes = rowsOf(f)
  const proposable = x => ['FOUND', 'CURRENT_OK'].includes(x.outcome) && x.proposed_url
  const toConfirm = fixes.filter(proposable)
  let confirm = []
  if (toConfirm.length) {
    const c = await agent(confirmPrompt(toConfirm), { label: `confirm:${tag}`, phase: 'Confirm', model: 'sonnet', effort: 'medium', schema: CONFIRM })
    confirm = rowsOf(c).map(r => ({ ...r, proposed_url: (byId(toConfirm, r.page_id) || {}).proposed_url || '' }))
  }
  const rejected = toConfirm.filter(x => !confirm.some(c => norm(c.page_id) === norm(x.page_id) && c.verdict === 'CONFIRMED'))
  const needDisc = [
    ...fixes.filter(x => !proposable(x)),
    ...rejected.map(x => ({ ...x, rejected: (byId(confirm, x.page_id) || {}).reason || 'not confirmed' })),
  ]
  let disc = []
  if (needDisc.length) {
    const d = await agent(discPrompt(needDisc), { label: `disc:${tag}`, phase: 'Discontinued check', model: 'opus', effort: 'high', schema: DISC })
    disc = rowsOf(d)
    const live = disc.filter(x => x.verdict === 'FOUND_LIVE' && x.proposed_url)
    if (live.length) {
      const list = live.map(x => ({ page_id: x.page_id, proposed_url: x.proposed_url, notes: x.evidence }))
      const c2 = await agent(confirmPrompt(list), { label: `confirm2:${tag}`, phase: 'Confirm', model: 'sonnet', effort: 'medium', schema: CONFIRM })
      confirm.push(...rowsOf(c2).map(r => ({ ...r, proposed_url: (byId(list, r.page_id) || {}).proposed_url || '' })))
    }
  }
  return { fix: fixes, confirm, disc }
}

async function doItem(item) {
  const out = { label: item.label, kind: item.kind, triage: [], match: [], price: [], fix: [], confirm: [], disc: [], routed_to_fix: [] }
  let matchIds = null
  const toFix = []
  if (item.kind === 'triage') {
    const t = await agent(triagePrompt(item), { label: `triage:${item.label}`, phase: 'Health triage', model: 'haiku', effort: 'low', schema: TRIAGE })
    out.triage = rowsOf(t)
    matchIds = []
    for (const r of out.triage) {
      if (r.verdict === 'ALIVE' || r.verdict === 'UNCLEAR') matchIds.push(r.page_id)
      else toFix.push({ page_id: r.page_id, why: `${r.verdict}: ${r.reason}` })
    }
  }
  if (item.kind === 'match' || (matchIds && matchIds.length)) {
    const m = await agent(matchPrompt(item, matchIds), { label: `match:${item.label}`, phase: 'Match', model: 'sonnet', effort: 'medium', schema: MATCH })
    out.match = rowsOf(m)
    for (const r of out.match) if (r.verdict !== 'MATCH') toFix.push({ page_id: r.page_id, why: `${r.verdict} (${r.confidence}): ${r.evidence}` })
  }
  out.routed_to_fix = toFix
  const matched = out.match.filter(r => r.verdict === 'MATCH').map(r => r.page_id)
  const groups = item.kind === 'fix' ? [{ batchFile: item.path }] : chunk(toFix, 5).map(rows => ({ rows }))
  const jobs = [
    () => matched.length
      ? agent(pricePrompt(item, matched), { label: `price:${item.label}`, phase: 'Price', model: 'haiku', effort: 'low', schema: PRICE })
      : Promise.resolve(null),
    ...groups.map((g, gi) => () => fixChain(item, g, gi)),
  ]
  const res = await parallel(jobs)
  out.price = rowsOf(res[0])
  for (const fr of res.slice(1)) if (fr) { out.fix.push(...fr.fix); out.confirm.push(...fr.confirm); out.disc.push(...fr.disc) }
  return out
}

const items = [
  ...(args.triage || []).map(l => ({ kind: 'triage', label: l, path: `${RUN}/batches/${l}.json` })),
  ...(args.match || []).map(l => ({ kind: 'match', label: l, path: `${RUN}/batches/${l}.json` })),
  ...(args.fix || []).map(l => ({ kind: 'fix', label: l, path: `${RUN}/batches/${l}.json` })),
]
log(`${items.length} batches: ${items.map(i => i.label).join(', ')}`)
const results = (await pipeline(items, (x, item) => doItem(item))).filter(Boolean)
const count = k => results.reduce((n, r) => n + (r[k] || []).length, 0)
log(`verdicts: triage ${count('triage')}, match ${count('match')}, price ${count('price')}, fix ${count('fix')}, confirm ${count('confirm')}, disc ${count('disc')}`)
return { results }
