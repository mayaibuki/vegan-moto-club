import type { Metadata } from "next"
import { SuggestProductForm } from "@/components/SuggestProductForm"
import { InstagramGallery } from "@/components/InstagramGallery"

export const metadata: Metadata = {
  title: "About",
  description:
    "The Vegan Moto Club is a community that started in the San Francisco Bay Area, with a focus on animal liberation and having fun.",
  openGraph: {
    title: "About | Vegan Moto Club",
    description:
      "The Vegan Moto Club is a community that started in the San Francisco Bay Area, with a focus on animal liberation and having fun.",
    url: "/about",
  },
  alternates: {
    canonical: "/about",
  },
}

const organizations = [
  { name: "31 Cats", url: "https://31cats.com" },
  { name: "ACT UP", url: "https://actupny.org/" },
  { name: "Agriculture Fairness Alliance", url: "https://www.agriculturefairnessalliance.org/" },
  { name: "Black Lives Matter", url: "https://blacklivesmatter.com/" },
  { name: "Consistent Anti-oppression", url: "http://www.consistentantioppression.com/" },
  { name: "Direct Action Everywhere", url: "https://www.directactioneverywhere.com/" },
  { name: "Dykes On Bikes", url: "https://www.dykesonbikes.org" },
  { name: "Extinction Rebellion", url: "https://rebellion.global/" },
  { name: "Factory Farming Awareness Coalition", url: "https://www.ffacoalition.org/" },
  { name: "Farm Transparency Project", url: "https://www.farmtransparency.org/" },
  { name: "Food Not Bombs", url: "http://foodnotbombs.net/" },
  { name: "In Defense of Animals", url: "https://www.idausa.org/" },
  { name: "Mercy For Animals", url: "https://animalequality.org/" },
  { name: "PETA", url: "https://www.peta.org/" },
  { name: "Queer Design Club", url: "https://www.queerdesign.club" },
  { name: "Queers On Gears", url: "https://www.instagram.com/queersongears/" },
  { name: "Rose's Law", url: "https://www.roseslaw.org/" },
  { name: "Sea Shepherd", url: "https://seashepherd.org" },
  { name: "Sunrise Movement", url: "https://www.sunrisemovement.org" },
  { name: "The Moto Social", url: "https://themotosocial.com" },
  { name: "The Save Movement", url: "https://thesavemovement.org/" },
  { name: "Vegan Hacktivists", url: "https://veganhacktivists.org/" },
  { name: "Voicot", url: "https://www.voicot.com/" },
  { name: "We Animals", url: "https://weanimalsmedia.org/" },
  { name: "Women Who Design", url: "https://womenwho.design/" },
]

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-10">
      <div className="space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold">About Vegan Moto Club</h1>
        <p className="text-lg text-muted-foreground leading-relaxed">
          The Vegan Moto Club is a community that started in the San Francisco Bay Area,
          with a focus on animal liberation and having fun.
        </p>
        <p className="text-lg text-muted-foreground leading-relaxed">
          Whether you are an experienced motorcyclist or you just like how motorcycles look,
          this is your place to find friends that don't eat other friends, and find vegan
          motorcycle gear.
        </p>
      </div>

      <InstagramGallery />

      <div className="space-y-6">
        <div className="space-y-2">
          <h2 className="text-2xl md:text-3xl font-semibold">Our Mission</h2>
          <p className="text-muted-foreground leading-relaxed">
            The Vegan Moto Club is dedicated to providing riders with comprehensive information
            about cruelty-free motorcycle gear. We believe that you don't have to compromise on
            performance or style to make ethical choices.
          </p>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl md:text-3xl font-semibold">Why Vegan Gear?</h2>
          <p className="text-muted-foreground leading-relaxed">
            Traditional motorcycle gear often relies on leather and other animal-derived materials.
            Modern synthetic alternatives offer equal or superior performance while eliminating the
            need for animal exploitation. By choosing vegan gear, riders can protect themselves and
            the planet without sacrificing animals.
          </p>
        </div>

        <div className="space-y-2">
          <h2 className="text-2xl md:text-3xl font-semibold">Our Community</h2>
          <p className="text-muted-foreground leading-relaxed">
            We're building a community of compassionate riders who believe that performance and
            ethics go hand in hand. Join us on{" "}
            <a
              href="https://discord.gg/GN4jkBRnut"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground hover:underline font-medium"
            >
              Discord
            </a>
            {" "}or follow us on{" "}
            <a
              href="https://www.instagram.com/veganmotoclub/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground hover:underline font-medium"
            >
              Instagram
            </a>
            {" "}to connect with other vegan riders worldwide.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h2 className="text-2xl md:text-3xl font-semibold">We are intersectional</h2>
          <h3 className="text-base md:text-lg font-medium text-muted-foreground mt-1">
            The animal liberation movement is by animals, for animals.
          </h3>
        </div>
        <p className="text-muted-foreground leading-relaxed">
          And as allies of animals, we fight with them against speciesism, but we also
          fight against Ableism, Adultism, Ageism, Anthropocentrism, Antisemitism,
          Authoritarianism, Binarism, Biphobia, Biological Classism, Capitalism, Casteism,
          Cis-Hetero-Patriarchy, Cisheteronormativity, Cissexism, Classism, Climate Breakdown,
          Colonialism, Colourism, Cultural Appropriation, Dyadism, Ecocide, Ethno-centrism,
          Fascism, Hero Worship, Heterosexism, Homophobia, Human Supremacy, Imperialism,
          Islamophobia, Lesbophobia, Lookism, Misogynoir, Misogyny, Misothery, Nativism,
          Rape Culture, Racism, Religious Discrimination, Sanism, Saviourism, Sexism, Sizeism,
          The Prison System, Tokenism, Trans/Homo-antagonism, Transphobia, Transmisogyny, War,
          Weightism, White Supremacy, Whorephobia, Xenophobia, and Zionism.
        </p>
      </div>

      <div className="space-y-5">
        <div>
          <h2 className="text-2xl md:text-3xl font-semibold">Special thanks to</h2>
          <p className="text-muted-foreground mt-1">
            The organizations that are fighting to end oppression and/or have inspired
            this project:
          </p>
        </div>
        <ul className="columns-2 md:columns-3 gap-x-8 space-y-0 list-none">
          {organizations.map((org) => (
            <li key={org.name} className="text-sm py-1 break-inside-avoid">
              <a
                href={org.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                {org.name}
              </a>
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl md:text-3xl font-semibold">Get Involved</h2>
        <ul className="text-muted-foreground leading-relaxed space-y-2">
          <li>
            <span className="font-semibold text-foreground">Found a great vegan brand?</span> Submit
            it through our product suggestion form below.
          </li>
          <li>
            <span className="font-semibold text-foreground">Have questions?</span> Reach out to us
            on Discord or on Instagram.
          </li>
          <li>
            <span className="font-semibold text-foreground">Want to contribute?</span> We're always
            looking for community members to help expand our database and share their experiences.
          </li>
        </ul>
      </div>

      <SuggestProductForm id="about" />
    </div>
  )
}
