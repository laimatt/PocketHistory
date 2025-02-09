"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import PlaceDetails from "../components/PlaceDetails"
import type { Place } from "../lib/types"

const Map = dynamic(() => import("../components/Map"), { ssr: false })

export default function Home() {
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null)

  return (
    <main className="h-screen flex flex-col">
      <div className="flex-1 relative">
        <Map onSelectPlace={setSelectedPlace} />
      </div>
      {selectedPlace && <PlaceDetails place={selectedPlace} onClose={() => setSelectedPlace(null)} />}
    </main>
  )
}

