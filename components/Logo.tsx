import Link from "next/link"
import Image from "next/image"

interface LogoProps {
  size?: "sm" | "md" | "lg"
  href?: string
}

export function Logo({ size = "md", href = "/" }: LogoProps) {
  const sizes = {
    sm: { width: 32, height: 32 },
    md: { width: 40, height: 40 },
    lg: { width: 64, height: 64 },
  }

  const sizeClass = {
    sm: "h-8 w-auto",
    md: "h-10 w-auto",
    lg: "h-16 w-auto",
  }

  const logoElement = (
    <div className={`flex items-center gap-2 ${size !== "sm" ? "flex-col" : ""}`}>
      <Image
        src="/images/logo.png"
        alt="Vegan Moto Club"
        width={sizes[size].width}
        height={sizes[size].height}
        className={sizeClass[size]}
        priority
      />
    </div>
  )

  if (href) {
    return <Link href={href}>{logoElement}</Link>
  }

  return logoElement
}
