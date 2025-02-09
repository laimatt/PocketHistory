import type { Place } from "./types"
import placesData from "../app/places.json"

export async function getNearbyPlaces(lat = 40.8075355, lng = -73.9625727): Promise<Place[]> {
  // Simulating an API call delay

  
  // await new Promise((resolve) => setTimeout(resolve, 500))

  return placesData as Place[]

  // The following code is kept but not used:
  const isServer = typeof window === "undefined"
  const fetchFunction = isServer ? fetch : fetch

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
  const url = `${backendUrl}/nearby_places?latitude=${lat}&longitude=${lng}`

  try {
    const res = await fetchFunction(url)
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    const data = await res.json()
    return data
  } catch (error) {
    console.error("Error fetching nearby places:", error)
    return []
  }
}

