export interface Place {
  place_id: string
  name: string
  geometry: {
    location: {
      lat: number
      lng: number
    }
  }
  photos?: {
    photo_reference: string
  }[]
  short_description: string
  long_description: string
  image_url: string
}

