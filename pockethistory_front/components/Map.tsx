"use client"

import { useState, useEffect, useRef } from "react"
import { GoogleMap, useJsApiLoader, OverlayView } from "@react-google-maps/api"
import type { Place } from "../lib/types"
import { getNearbyPlaces } from "../lib/api"
import PlaceDetails from "./PlaceDetails"

interface MapProps {
  onSelectPlace?: (place: Place) => void
}

const mapContainerStyle = {
  width: "100%",
  height: "100%",
}

const getDefaultCenter = (places: Place[]) => {
  if (places.length > 0) {
    return {
      lat: places[0].geometry.location.lat,
      lng: places[0].geometry.location.lng,
    }
  }
  return { lat: 51.505, lng: -0.09 }
}

const options = {
  disableDefaultUI: true,
  zoomControl: true,
}

export default function Map({ onSelectPlace }: MapProps) {
  const [places, setPlaces] = useState<Place[]>([])
  const [center, setCenter] = useState<google.maps.LatLngLiteral>({ lat: 51.505, lng: -0.09 })
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null)
  const mapRef = useRef<google.maps.Map | null>(null)
  const { isLoaded, loadError } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!,
  })

  useEffect(() => {
    getNearbyPlaces().then((fetchedPlaces) => {
      setPlaces(fetchedPlaces)
      setCenter(getDefaultCenter(fetchedPlaces))
    })
  }, [])

  const handleMarkerClick = (place: Place) => {
    if (onSelectPlace) {
      onSelectPlace(place)
    }
  }

  const onMapLoad = (map: google.maps.Map) => {
    mapRef.current = map
  }

  if (loadError) return <div>Error loading maps</div>
  if (!isLoaded) return <div>Loading...</div>

  return (
    <div className="relative w-full h-screen">
      <GoogleMap mapContainerStyle={mapContainerStyle} zoom={15} center={center} options={options} onLoad={onMapLoad}>
        {places.map((place) => (
          <OverlayView
            key={place.place_id}
            position={{
              lat: place.geometry.location.lat,
              lng: place.geometry.location.lng,
            }}
            mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
          >
            <div
              className="bg-white border border-gray-300 rounded-lg p-2 shadow-md cursor-pointer"
              style={{ width: "200px" }}
              onClick={() => handleMarkerClick(place)}
            >
              <div className="flex items-start space-x-2">
                <img
                  src={place.image_url || "/placeholder.svg"}
                  alt={place.name}
                  className="w-12 h-12 object-cover rounded"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.src = "/placeholder.svg"
                  }}
                />
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold truncate">{place.name}</h3>
                  <p className="text-xs text-gray-600 line-clamp-2">{place.short_description}</p>
                </div>
              </div>
            </div>
          </OverlayView>
        ))}
      </GoogleMap>
      {selectedPlace && <PlaceDetails place={selectedPlace} onClose={() => setSelectedPlace(null)} />}
    </div>
  )
}

