import Link from "next/link"
import Image from "next/image"

interface LogoProps {
  size?: "sm" | "md" | "lg"
  href?: string
}

export function Logo({ size = "md", href = "/" }: LogoProps) {
  const sizes = {
    sm: { width: 30, height: 30 },
    md: { width: 40, height: 40 },
    lg: { width: 60, height: 60 },
  }

  const sizeClass = {
    sm: "h-[30px] w-auto",
    md: "h-[40px] w-auto",
    lg: "h-[60px] w-auto",
  }

  const logoElement = (
    <div className={`flex items-center gap-2 ${size !== "sm" ? "flex-col" : ""}`}>
      <Image
        src="/images/logo.svg"
        alt="Vegan Moto Club"
        width={sizes[size].width}
        height={sizes[size].height}
        className={sizeClass[size]}
        priority
      />
      {size === "lg" && (
        <span className="font-display text-center text-lg font-bold text-primary">
          VEGAN MOTO CLUB
        </span>
      )}
    </div>
  )

  if (href) {
    return <Link href={href}>{logoElement}</Link>
  }

  return logoElement
}
