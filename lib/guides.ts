import type { FaqItem } from "@/lib/notion"

export interface GuideSection {
  heading: string
  paragraphs: string[]
}

export interface Guide {
  slug: string
  title: string
  /** Meta description and the lead paragraph. Answer first. */
  description: string
  datePublished: string
  dateModified: string
  sections: GuideSection[]
  faq: FaqItem[]
  /** CATEGORY_PAGES slugs linked from the page. */
  relatedCategories: string[]
  sources: { label: string; url: string }[]
}

// Copy follows docs/brand-voice.md: digits, standards named as printed, no dashes,
// no safety promises. Every guide answers its question in the first sentence.
export const GUIDES: Guide[] = [
  {
    slug: "is-cordura-vegan",
    title: "Is Cordura vegan?",
    description:
      "Cordura is a synthetic fabric, so the material itself contains no animal products. Whether a Cordura jacket or pant is vegan depends on the trims, liners and patches around it.",
    datePublished: "2026-11-03",
    dateModified: "2026-11-03",
    sections: [
      {
        heading: "What Cordura is",
        paragraphs: [
          "Cordura is a brand name, not a single fabric. It belongs to Invista and covers a family of woven textiles, most of them made from nylon 6,6, with polyester, cotton blends and denim variants in the range. The fibers are made from petroleum feedstock in a chemical plant. No animal is involved in making the yarn.",
          "In motorcycle gear the two numbers you will see most are 500D and 1000D. The D stands for denier, a measure of yarn thickness. A higher number means a heavier yarn and, as a rule, a tougher but stiffer fabric. 500D is common on street jackets, 1000D on adventure and touring shells. Cordura Denim, used in riding jeans, is a cotton blend with nylon spun into the yarn.",
        ],
      },
      {
        heading: "Why the fabric is not the whole answer",
        paragraphs: [
          "A garment is more than its shell. Makers add leather to high wear points such as the shoulders, the inside of the knees on pants, and the waist patch on jeans. Winter liners are sometimes wool blends. Collars can carry a suede-feel trim that is real suede. These parts are small and rarely listed on the hang tag, which is where a Cordura jacket stops being vegan.",
          "Adhesives and dyes are the last layer of the question. Most seam tapes and laminates in riding gear use synthetic glues, and makers almost never state the chemistry. If that matters to you, ask the maker directly. We record what the maker says and what the materials list shows, and we do not claim more than that.",
        ],
      },
      {
        heading: "How Cordura relates to protection ratings",
        paragraphs: [
          "A fabric name tells you nothing about certification. Protective clothing is tested as a finished garment under EN 17092, which assigns an abrasion class of AAA, AA or A to jackets and pants, with B and C for garments that carry no impact protection. Two jackets can both be 500D Cordura and land in different classes because of their seams, their construction and where the armor sits.",
          "Read the class on the inside label, then look at the materials list. For abrasion, the class is the number that matters. For vegan status, the materials list is.",
        ],
      },
      {
        heading: "What to check before buying",
        paragraphs: [
          "Look at the full materials list, including the liner, the trims and any reinforcement panels. Check the waist patch on jeans and the shoulder panels on jackets. Where the list says only polyamide, polyester, cotton or aramid, the garment is leather-free and wool-free. Where it is silent, ask.",
          "Every jacket and pant on this site has been checked for animal materials down to the lining and the badges, and each listing shows the EN 17092 class the maker prints.",
        ],
      },
    ],
    faq: [
      {
        question: "Is Cordura the same as nylon?",
        answer:
          "Cordura is a branded family of fabrics, most of them nylon 6,6, and some polyester or cotton blends. Plain nylon fabric without the brand can be just as synthetic but is not tested or certified under the Cordura name.",
      },
      {
        question: "Is a Cordura jacket automatically vegan?",
        answer:
          "No. The shell is synthetic, but shoulder patches, knee panels, waist patches on jeans and winter liners can be leather or wool. Check the full materials list, not the fabric name.",
      },
      {
        question: "Does 1000D Cordura mean a higher protection class?",
        answer:
          "Not on its own. EN 17092 rates the finished garment, including seams and construction. A 1000D shell often reaches AA or AAA, but the class on the label is the only reliable figure.",
      },
    ],
    relatedCategories: ["vegan-motorcycle-jackets", "vegan-motorcycle-pants", "vegan-motorcycle-street-wear"],
    sources: [
      { label: "Cordura fabric technologies, Invista", url: "https://www.cordura.com/en/technologies" },
      { label: "EN 17092 series overview, CEN", url: "https://standards.cencenelec.eu/" },
    ],
  },
  {
    slug: "are-motorcycle-boots-vegan",
    title: "Are motorcycle boots vegan?",
    description:
      "Most motorcycle boots are not vegan, because leather is still the default upper material. A growing number use synthetic microfiber uppers instead, and they are tested to the same EN 13634 standard.",
    datePublished: "2026-11-03",
    dateModified: "2026-11-03",
    sections: [
      {
        heading: "Why leather is still the default",
        paragraphs: [
          "Boots are the hardest category to buy vegan. Leather uppers are cheap to source, easy to stitch and familiar to the factories that make riding boots, so most catalogs still default to cowhide. The protective parts of a boot were never leather: the toe box, heel cup, ankle cups, shank and sliders are plastic, and the sole is rubber or polyurethane.",
          "That split matters. The question is only ever about the upper, the lining and the small parts, not about the structure that protects your foot.",
        ],
      },
      {
        heading: "What replaces leather",
        paragraphs: [
          "Two synthetic microfibers do most of the work. Lorica is a polyurethane coated microfiber made in Italy and used in race and touring boots. Clarino, made by Kuraray, is a similar material found in gloves and boots. Both are lighter than cowhide, dry faster and do not stretch out over time. Abrasion resistance is comparable, which is why boots built from them pass the same tests.",
          "Beyond the upper, look at the lining, which can be a leather sock in otherwise synthetic boots, and at the welt and laces. Glues in boots are almost always synthetic, but makers rarely state it.",
        ],
      },
      {
        heading: "Reading the EN 13634 code",
        paragraphs: [
          "Certified boots carry EN 13634:2017 and a code of 4 digits. The first is shoe height: 1 for a boot that covers the ankle, 2 for one that reaches higher up the shin. The next 3 are abrasion resistance, impact cut resistance and transverse rigidity, each scored 1 or 2, with 2 the higher level. A code of 2 2 2 2 is the highest the standard offers.",
          "Optional markings follow the code. IPA and IPS mean impact protection at the ankle and shin was tested, WR means water resistance, and FO means the sole resists fuel and oil. A synthetic boot carries the same code as a leather one, so compare codes, not materials.",
        ],
      },
      {
        heading: "What to check before buying",
        paragraphs: [
          "Look for a materials line that names microfiber, polyurethane, textile or synthetic for the upper and the lining. Check product photos for stitched leather panels at the heel and toe, which some makers add to microfiber boots. Ask about the lining if it is not listed.",
          "Everything in our boots category has leather-free uppers and linings, with the EN 13634 code and waterproofing listed on each product.",
        ],
      },
    ],
    faq: [
      {
        question: "Are microfiber boots as abrasion resistant as leather?",
        answer:
          "The EN 13634 abrasion test does not care about the material. Microfiber boots that pass with a 2 in the abrasion slot met the same requirement as a leather boot with a 2. Compare codes rather than materials.",
      },
      {
        question: "What does a 2 2 2 2 code mean?",
        answer:
          "Height above the ankle, and the higher level in each of abrasion resistance, impact cut resistance and transverse rigidity. It is the top score under EN 13634:2017.",
      },
      {
        question: "Which parts of a synthetic boot can still be leather?",
        answer:
          "The lining, heel and toe reinforcement panels and the welt. Makers do not always list them, so check photos and ask.",
      },
    ],
    relatedCategories: ["vegan-motorcycle-boots", "vegan-motorcycle-protection"],
    sources: [
      { label: "EN 13634:2017 protective footwear for motorcycle riders, CEN", url: "https://standards.cencenelec.eu/" },
      { label: "Lorica microfiber, Lorica Sud", url: "https://www.loricasud.it/" },
    ],
  },
  {
    slug: "textile-vs-leather-motorcycle-safety",
    title: "Is textile as safe as leather?",
    description:
      "A textile garment and a leather garment with the same EN 17092 class passed the same tests. The class on the label is the comparison that holds up, and this guide explains what that class measures.",
    datePublished: "2026-11-03",
    dateModified: "2026-11-03",
    sections: [
      {
        heading: "What the standard tests",
        paragraphs: [
          "EN 17092 is the European standard for protective motorcycle garments. Part 1 describes the test methods and parts 2 to 6 define the classes. A garment is tested as a whole: impact abrasion on a Darmstadt machine, which drops a sample onto a moving abrasive surface at a set speed, seam strength, tear strength, and the fit and coverage of the impact protectors.",
          "Each zone of the garment has its own requirement. The shoulders, elbows, hips and knees must survive longer than the back of a sleeve, which is why a jacket that uses a lighter fabric on the torso can still reach a high class.",
        ],
      },
      {
        heading: "The classes",
        paragraphs: [
          "AAA, defined in EN 17092-2, is the highest abrasion class and the one race suits and the toughest road gear are built to. AA, in EN 17092-3, is the middle class and the one most street jackets and pants target. A, in EN 17092-4, is the lightest class with impact protectors. B in part 5 is abrasion only with no protectors, and C in part 6 covers protector-holding garments such as armored base layers.",
          "A leather jacket can be A and a textile jacket can be AAA. The class is printed on the inside label with the part number, for example EN 17092-3 class AA.",
        ],
      },
      {
        heading: "Where each material tends to win",
        paragraphs: [
          "Leather slides well on tarmac and stays stable at the speeds seen on a race track, which is why track suits remain mostly leather and why the vegan racing suit list is short. Textile shells are lighter, carry waterproof membranes and ventilation, and usually leave more room for armor coverage. On the street, where most crashes happen below highway speed, the armor and the fit do more of the work than the shell.",
          "Neither material protects without the impact protectors. EN 1621-1 rates limb armor and EN 1621-2 rates back protectors, each at Level 1 or Level 2. Level 2 passes less force through to the body: 20 kN against 35 kN at the limbs and 9 kN against 18 kN at the back, averaged over the test strikes.",
        ],
      },
      {
        heading: "How to compare two garments",
        paragraphs: [
          "Read the EN 17092 class first and ignore the fabric name. Then check which armor is included, at which level, and whether the back protector pocket is filled or sold empty. Finally, check the fit: armor that moves off the joint protects nothing.",
          "A rating is a test result, not a guarantee. It tells you how the garment behaved on a machine, under defined conditions, and that is the fairest comparison available to a rider in a shop.",
        ],
      },
    ],
    faq: [
      {
        question: "Can a textile jacket be AAA?",
        answer:
          "Yes. AAA is a test result under EN 17092-2, and several textile and microfiber garments carry it. Leather is not required by the standard.",
      },
      {
        question: "What is the difference between AA and A?",
        answer:
          "Both include impact protectors. AA requires more abrasion time and higher seam and tear strength than A in each zone. AA is the usual target for street jackets and pants.",
      },
      {
        question: "Do I still need armor in a AAA garment?",
        answer:
          "AAA, AA and A all require impact protectors to pass. The class covers abrasion and seams; EN 1621 armor handles impact. Check both the class and the armor level.",
      },
    ],
    relatedCategories: ["vegan-motorcycle-jackets", "vegan-motorcycle-pants", "vegan-motorcycle-racing-suits", "vegan-motorcycle-protection"],
    sources: [
      { label: "EN 17092 series, protective garments for motorcycle riders, CEN", url: "https://standards.cencenelec.eu/" },
      { label: "EN 1621-1 and EN 1621-2 impact protectors, CEN", url: "https://standards.cencenelec.eu/" },
    ],
  },
]

export function getGuide(slug: string): Guide | undefined {
  return GUIDES.find((guide) => guide.slug === slug)
}
