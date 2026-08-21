export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://veganmotoclub.com"

export const seasonEmojis: Record<string, string> = {
  Summer: "☀️",
  "Mid season": "🌦",
  Winter: "❄️",
}

/**
 * Static category landing pages (/vegan-motorcycle-gloves etc.).
 * `category` must match the Notion Category multi-select values exactly.
 */
export interface CategoryPage {
  slug: string
  category: string
  title: string
  description: string
  intro: string[]
}

export const CATEGORY_PAGES: CategoryPage[] = [
  {
    slug: "vegan-motorcycle-gloves",
    category: "Gloves",
    title: "Vegan Motorcycle Gloves",
    description:
      "Leather-free motorcycle gloves with real protection: synthetic microfiber palms, knuckle armor, and CE-rated options for summer, winter, and the track.",
    intro: [
      "Motorcycle gloves are one of the easiest pieces of gear to buy vegan. Synthetic microfibers like Amara and Clarino have replaced leather palms across most major brands, and hard parts such as knuckle armor and palm sliders were never animal-derived in the first place.",
      "Every pair listed here is free of leather, suede, and wool linings. You'll find everything from ventilated summer gloves to insulated winter pairs and track gauntlets, with the protection level, season, and materials listed on each product.",
    ],
  },
  {
    slug: "vegan-motorcycle-jackets",
    category: "Jackets",
    title: "Vegan Motorcycle Jackets",
    description:
      "Textile motorcycle jackets without leather or wool: Cordura and mesh construction, CE armor pockets, and options for every season and riding style.",
    intro: [
      "Textile jackets are the mainstream of motorcycle gear, which makes vegan options plentiful. Abrasion-resistant fabrics like Cordura protect the outside, while CE-rated armor at the shoulders, elbows, and back handles impacts. The details to watch are the trims: some textile jackets still use leather patches or wool-blend liners.",
      "Every jacket in this list has been checked for animal-derived materials, from the shell down to the lining and badges. Filter by season, waterproofing, and protection level to narrow the list to your kind of riding.",
    ],
  },
  {
    slug: "vegan-motorcycle-boots",
    category: "Boots",
    title: "Vegan Motorcycle Boots",
    description:
      "Motorcycle boots made without leather: microfiber uppers, ankle and toe protection, and waterproof options from touring to track.",
    intro: [
      "Boots are the hardest category to buy vegan, because leather is still the default upper material for most brands. The alternatives have caught up: microfibers like Lorica and Clarino offer comparable abrasion resistance, and the protective structure of a boot (toe box, ankle cups, shank, sliders) is synthetic regardless.",
      "Everything listed here has leather-free uppers and linings. Check each product for waterproofing and protection details, and expect the same CE certification categories you'd look for in leather boots.",
    ],
  },
  {
    slug: "vegan-motorcycle-pants",
    category: "Pants",
    title: "Vegan Motorcycle Pants",
    description:
      "Vegan riding pants and jeans: aramid-lined denim, textile touring pants, and leather-free options with knee and hip armor.",
    intro: [
      "Riding pants divide into two families: textile pants built from abrasion-resistant fabrics, and riding jeans reinforced with aramid fibers like Kevlar. Both are naturally leather-free in most cases, though waist patches and trims can hide animal materials.",
      "The pants listed here are confirmed free of leather and wool. Most take CE knee and hip armor, and the listing shows season and waterproofing so you can match them to your commute or tour.",
    ],
  },
  {
    slug: "vegan-motorcycle-racing-suits",
    category: "Racing Suits",
    title: "Vegan Motorcycle Racing Suits",
    description:
      "One and two piece racing suits without kangaroo or cow leather: microfiber track suits with CE armor for trackdays and racing.",
    intro: [
      "Racing suits are traditionally kangaroo or cow leather, but a small group of manufacturers now builds track-rated suits from high-tenacity microfibers. These suits pass the same abrasion and burst tests required of leather, and some are raced professionally.",
      "This is the shortest list on the site because the market is young, but every suit here is genuinely track-capable and entirely animal-free.",
    ],
  },
  {
    slug: "vegan-motorcycle-protection",
    category: "Protection",
    title: "Vegan Motorcycle Armor & Protection",
    description:
      "Body armor, back protectors, and airbag vests free of animal materials, from CE Level 1 inserts to full airbag systems.",
    intro: [
      "Impact protection is the most naturally vegan category in motorcycling: armor inserts, back protectors, and airbag systems are engineered entirely from foams, plastics, and textiles. The occasional exceptions are leather trims and wool comfort padding on straps and carriers.",
      "Everything here is confirmed animal-free. Look for the CE rating on each product: Level 2 absorbs more impact energy than Level 1, and airbag vests add coverage no passive armor can match.",
    ],
  },
  {
    slug: "vegan-motorcycle-street-wear",
    category: "Street wear",
    title: "Vegan Motorcycle Street Wear",
    description:
      "Casual riding gear without animal materials: armored hoodies, riding shirts, and street clothing with abrasion-resistant linings.",
    intro: [
      "Street wear covers the casual end of protective gear: hoodies, flannels, and shirts with hidden aramid linings and low-profile armor. It trades some protection for comfort and looks, which makes it popular for short city rides.",
      "Each item listed is free of leather, wool, and down. Protection levels vary widely in this category, so check the armor and lining details before relying on a garment for serious riding.",
    ],
  },
]
