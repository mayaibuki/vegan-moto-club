"use client"

import { useEffect } from "react"

export function InstagramGallery() {
  useEffect(() => {
    // Load the Behold widget script
    const script = document.createElement("script")
    script.type = "module"
    script.src = "https://w.behold.so/widget.js"
    document.head.appendChild(script)

    return () => {
      // Cleanup: remove script on unmount
      if (document.head.contains(script)) {
        document.head.removeChild(script)
      }
    }
  }, [])

  return (
    <div className="w-full">
      <behold-widget feed-id="IMLk3Wl3QEREHuhbK7uK" />
    </div>
  )
}
