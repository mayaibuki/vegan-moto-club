"use client"

// Site-wide animated grain gradient behind all content. Loaded from layout.tsx with
// next/dynamic (ssr: false); until it mounts, the body's bg-background shows instead.

import { useEffect, useState } from "react"
import { GrainGradient } from "@paper-design/shaders-react"

// Same tint as the bg-primary/15 utility.
const PRIMARY_ALPHA = 0.15

/**
 * "77.9 54.4% 47.4%" -> "hsla(78, 54%, 47%, 1)".
 * The shader's colour parser only accepts comma-separated integer hsl(a),
 * so values are rounded (max error ~0.5% lightness).
 */
function tripletToHsla(triplet: string, alpha = 1): string {
  const [h = "0", s = "0%", l = "0%"] = triplet.trim().split(/[\s,]+/)
  const n = (v: string) => Math.round(parseFloat(v)) || 0
  return `hsla(${n(h)}, ${n(s)}%, ${n(l)}%, ${alpha})`
}

// Reads the live token values, so light/dark come from tokens.css.
function readColors() {
  const styles = getComputedStyle(document.documentElement)
  return {
    back: tripletToHsla(styles.getPropertyValue("--background")),
    front: tripletToHsla(styles.getPropertyValue("--primary"), PRIMARY_ALPHA),
  }
}

function supportsWebGL2(): boolean {
  try {
    return !!document.createElement("canvas").getContext("webgl2")
  } catch {
    return false
  }
}

export default function ShaderBackground() {
  const [colors, setColors] = useState<{ back: string; front: string } | null>(null)
  const [reducedMotion, setReducedMotion] = useState(false)

  // Re-read colours when the Navbar toggles the .dark class on <html>.
  // Stays null (renders nothing) without WebGL2, which the shader requires.
  useEffect(() => {
    if (!supportsWebGL2()) return
    const update = () => setColors(readColors())
    update()
    const observer = new MutationObserver(update)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] })
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)")
    const update = () => setReducedMotion(mq.matches)
    update()
    mq.addEventListener("change", update)
    return () => mq.removeEventListener("change", update)
  }, [])

  if (!colors) return null

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10">
      <GrainGradient
        width="100%"
        height="100%"
        colors={[colors.front]}
        colorBack={colors.back}
        softness={1}
        intensity={1}
        noise={1}
        shape="corners"
        speed={reducedMotion ? 0 : 1}
      />
    </div>
  )
}
