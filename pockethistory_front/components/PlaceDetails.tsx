"use client"

import { useState } from "react"
import type { Place } from "../lib/types"

interface PlaceDetailsProps {
  place: Place
  onClose: () => void
}

export default function PlaceDetails({ place, onClose }: PlaceDetailsProps) {
  const [question, setQuestion] = useState("")

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-4xl rounded-lg shadow-lg overflow-hidden flex flex-col">
        <button onClick={onClose} className="absolute top-2 right-2 text-gray-500 hover:text-gray-700">
          &times;
        </button>
        <div className="h-1/3 bg-gray-200">
          <img src={place.image_url || "/placeholder.svg"} alt={place.name} className="w-full h-full object-cover" />
        </div>
        <div className="h-1/3 p-4 overflow-y-auto">
          <h2 className="text-2xl font-bold mb-2">{place.name}</h2>
          <p className="text-gray-700">{place.long_description}</p>
        </div>
        <div className="h-1/3 p-4 bg-gray-100">
          <h3 className="text-lg font-semibold mb-2">Ask a question about {place.name}</h3>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full h-24 p-2 border rounded-md resize-none"
            placeholder="Type your question here..."
          />
          <button className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
            Submit Question
          </button>
        </div>
      </div>
    </div>
  )
}

