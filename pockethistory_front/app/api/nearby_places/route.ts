import { NextResponse } from "next/server"

// NOTE: This API route is kept for reference but is not being used in the current implementation.
// The app is using dummy data from places.json instead.

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const latitude = searchParams.get("latitude")
  const longitude = searchParams.get("longitude")

  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"
  const url = `${backendUrl}/nearby_places?latitude=${latitude}&longitude=${longitude}`

  try {
    const res = await fetch(url)
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`)
    }
    const data = await res.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Error fetching from backend:", error)
    return NextResponse.json({ error: "Failed to fetch nearby places" }, { status: 500 })
  }
}

