import { Card, CardContent } from "@/components/ui/card"

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-10">
      <div className="space-y-2">
        <h1 className="text-3xl md:text-4xl font-bold">About Vegan Moto Club</h1>
        <p className="text-lg text-muted-foreground">
          Building a compassionate community of riders
        </p>
      </div>

      <Card>
        <CardContent className="p-6 md:p-8 space-y-8">
          <section className="space-y-3">
            <h2 className="text-xl md:text-2xl font-semibold">Our Mission</h2>
            <p className="text-muted-foreground leading-relaxed">
              The Vegan Moto Club is dedicated to providing riders with
              comprehensive information about cruelty-free motorcycle gear.
              We believe that you don't have to compromise on performance or
              style to make ethical choices.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl md:text-2xl font-semibold">What We Do</h2>
            <p className="text-muted-foreground leading-relaxed">
              We curate and maintain a database of vegan motorcycle gear from
              ethical brands around the world. Every product in our database has
              been verified to be made without any animal products or
              animal-derived materials.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl md:text-2xl font-semibold">Why Vegan Gear?</h2>
            <p className="text-muted-foreground leading-relaxed">
              Traditional motorcycle gear often relies on leather and other
              animal-derived materials. Modern synthetic alternatives offer equal or
              superior performance while eliminating the need for animal exploitation.
              By choosing vegan gear, riders can protect themselves and the planet.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl md:text-2xl font-semibold">Our Community</h2>
            <p className="text-muted-foreground leading-relaxed">
              We're building a community of compassionate riders who believe that
              performance and ethics go hand in hand. Join us on Discord or follow
              us on social media to connect with other vegan riders worldwide.
            </p>
          </section>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6 md:p-8">
          <h2 className="text-xl md:text-2xl font-semibold mb-5">Get Involved</h2>
          <div className="space-y-4 text-muted-foreground leading-relaxed">
            <p>
              <strong className="text-foreground">Found a great vegan brand?</strong> Submit it through our
              product suggestion form on the home page.
            </p>
            <p>
              <strong className="text-foreground">Have questions?</strong> Reach out to us on Discord or through
              our social media channels.
            </p>
            <p>
              <strong className="text-foreground">Want to contribute?</strong> We're always looking for community
              members to help expand our database and share their experiences.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
