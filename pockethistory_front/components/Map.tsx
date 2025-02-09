"use client"

import { useState, useCallback, useEffect } from "react"
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from "@react-google-maps/api"
import type { Place } from "../lib/types"
import { getNearbyPlaces } from "../lib/api"
import PlaceDetails from "./PlaceDetails"

interface MapProps {
  onSelectPlace: (place: Place) => void
}

const mapContainerStyle = {
  width: "100%",
  height: "100%",
}

const center = {
  lat: 40.8075355,
  lng: -73.9625727,
}

const options = {
  disableDefaultUI: false,
  zoomControl: true,
}

export default function Map({ onSelectPlace }: MapProps) {
  const [places, setPlaces] = useState<Place[]>([])
  const [selectedMarker, setSelectedMarker] = useState<Place | null>(null)
  const { isLoaded } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
  })

  useEffect(() => {
    getNearbyPlaces().then(setPlaces)
  }, [])

  
  const handleMarkerClick = (place: Place) => {
    setSelectedMarker(place)
    if (onSelectPlace) {
      onSelectPlace(place)
    }
  }

  if (!isLoaded) return <div>Loading...</div>

  return (
    <div className="relative w-full h-screen">
      <GoogleMap mapContainerStyle={mapContainerStyle} zoom={15} center={center} options={options}>
        {places.map((place) => (
          <Marker
            key={place.place_id}
            position={{
              lat: place.geometry.location.lat,
              lng: place.geometry.location.lng,
            }}
            onClick={() => handleMarkerClick(place)}
            icon={{
              url:
                "data:image/svg+xml;charset=UTF-8," +
                encodeURIComponent(`
                <svg xmlns="http://www.w3.org/2000/svg" width="200" height="80" viewBox="0 0 200 80">
                  <rect width="200" height="80" rx="4" ry="4" fill="white" stroke="gray" stroke-width="1"/>
                  <image href="${place.image_url || "/placeholder.svg"}" x="5" y="5" width="50" height="50"/>
                  <text x="60" y="20" font-family="Arial" font-size="12" font-weight="bold">${place.name}</text>
                  <text x="60" y="40" font-family="Arial" font-size="10" width="135">${place.short_description}</text>
                </svg>
              `),
              scaledSize: new google.maps.Size(200, 80),
              anchor: new google.maps.Point(100, 80),
            }}
          />
        ))}
      </GoogleMap>
      {selectedMarker && <PlaceDetails place={selectedMarker} onClose={() => setSelectedMarker(null)} />}
    </div>
  )
}

