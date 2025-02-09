from dotenv import load_dotenv
import requests
import json
import googlemaps
import os
import shutil
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from typing import Tuple
from groq import Groq
from pathlib import Path
from fastapi.responses import FileResponse


app = FastAPI()

origins = [  # Define allowed origins
    "http://localhost:3000",  # Your React app's origin
    # Add other origins as needed (e.g., your production domain)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # If you need to send cookies/credentials
    allow_methods=["*"],  # Allow all HTTP methods (or specify)
    allow_headers=["*"],  # Allow all headers (or specify)
)

def append_place_to_json(place, filename="places.json"):
    """Appends a single place dictionary to a JSON file.

    Args:
        place: A dictionary representing a single place.
        filename: The name of the JSON file.
    """

    try:
        if not os.path.exists(filename):  # Create file with empty list if it doesn't exist
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False) # Write an empty list initially

        with open(filename, "r+", encoding="utf-8") as f: # Open in read and write mode ("r+")
            try:
                data = json.load(f)  # Load existing data (list of places)
            except json.JSONDecodeError:
                data = [] # Handle case where the file is corrupted or doesn't contain valid JSON

            data.append(place)  # Append the new place

            f.seek(0)  # Go back to the beginning of the file
            json.dump(data, f, indent=2, ensure_ascii=False)  # Overwrite with updated list
            f.truncate() # Remove any remaining data from the previous write
        print(f"Place added to {filename}")
    except Exception as e:
        print(f"Error appending place to JSON: {e}")


def load_places_from_json(filename="places.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            places_list = json.load(f)
            return places_list
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def call_groq(content):
    client = Groq(
        api_key=os.getenv("GQ_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    description = chat_completion.choices[0].message.content.strip() # Remove leading/trailing whitespace
    # Check if the description is enclosed in quotes and remove them if they are:
    if description.startswith('"') and description.endswith('"'):
        description = description[1:-1]
    elif description.startswith("'") and description.endswith("'"):
        description = description[1:-1]

    # print(description)
    return description

def get_photo_from_reference(place, gmaps, folder_path): # folder_path as argument
    if 'photos' in place and place['photos']: #Check if photos key exists and is non empty
        if 'photo_reference' in place['photos'][0]:
            photo = place['photos'][0]['photo_reference']
            local_filename = place['name'].replace("/", " ") + '.png'  # Sanitize filename
            image = os.path.join(folder_path, local_filename)
            try:
                with open(image, 'wb') as f:
                    for chunk in gmaps.places_photo(photo, max_width=1000):
                        if chunk:
                            f.write(chunk)
            except Exception as e:
                print(f"Error saving image for {place['name']}: {e}")


def get_nearby_places(folder_path, gmaps, location, json_data_from_request=None):
    places_list = []

    if json_data_from_request:
        try:
            places_list = json.loads(json_data_from_request)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON data provided.")
    else:
        filename = r'C:\Users\laima\OneDrive\Documents\GitHub\pockethistory\places.json'
        if os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

        if os.path.exists(folder_path):
            # Improved folder deletion with retry mechanism:
            for i in range(5):  # Try 5 times
                try:
                    for item in os.listdir(folder_path):
                        item_path = os.path.join(folder_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                print(f"Deleted file: {item_path}")
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                                print(f"Deleted directory: {item_path}")
                        except Exception as e:
                            print(f"Error deleting {item_path}: {e}")
                    break  # Exit loop if successful
                except OSError as e:  # Catch specific OSError
                    if e.errno == 5: # Access is denied
                        print(f"Retrying folder deletion (attempt {i+1})...")
                        time.sleep(1)  # Wait 1 second before retrying
                    else: # Other OS error
                        raise # Re-raise if it's not access denied.
            else:  # This else is for the for loop (if it didn't break)
                raise HTTPException(status_code=500, detail=f"Could not delete folder: {folder_path} after multiple retries.")
        else:
            os.makedirs(folder_path)


        places = gmaps.places_nearby(
            location=location,
            radius=300,
            type="history"
        )
        places_list = places.get("results", [])

    for place in places_list:
        location_name = place['name']
        address = place['vicinity']
        print(f"Name: {location_name}, Address: {address}")

        short_content_prompt = (f"give me a concise one phrase description about {location_name} located at {address} " +
                                f"that intends to draw the user's interest. This should be no longer than 10 words.")
        long_content_prompt = (f"give me a brief, concise summary about {location_name} located at {address} " +
                               f"that intends to draw the user's interest. this should be no longer than 3 sentences")
        place['short_description'] = call_groq(short_content_prompt)
        place['long_description'] = call_groq(long_content_prompt)

        append_place_to_json(place, "places.json")

        if not json_data_from_request:
            get_photo_from_reference(place, gmaps, folder_path) # Pass folder_path

    return places_list


@app.get("/nearby_places")  # Define the FastAPI endpoint
async def nearby_places_endpoint(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location"),
    use_json_file: bool = Query(False, description="Whether to load from places.json"),
    json_data: str = Query(None, description="JSON string of places data to use instead of Google Maps API call")
):
    """
    Retrieves nearby places.
    """
    try:
        load_dotenv()
        gmaps = googlemaps.Client(key=os.getenv("GO_KEY"))
        
        folder_path = r'C:\Users\laima\OneDrive\Documents\GitHub\pockethistory\images'  # Your image folder path
        location = (latitude, longitude)

        if use_json_file:
            loaded_places = load_places_from_json("places.json")
            if loaded_places is None:
                raise HTTPException(status_code=500, detail="Could not load places from places.json")
            return loaded_places # Return the list of places

        places_list = get_nearby_places(folder_path, gmaps, location, json_data) # Pass the json_data

        return places_list  # Return the list of places

    except Exception as e:
        print(f"An error occurred: {e}") # Print to console for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")  # Return error to client

@app.get("/images/{filename}")
async def get_image(filename: str):
    """Serves an image from the 'images' folder."""
    folder_path = Path(r'C:\Users\laima\OneDrive\Documents\GitHub\pockethistory\images')
    file_path = folder_path / filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        return FileResponse(file_path)
    except Exception as e:
        print(f"Error serving image: {e}")
        raise HTTPException(status_code=500, detail="Error serving image")




# load_dotenv()
# gmaps = googlemaps.Client(key=os.getenv("GO_KEY"))

# folder_path = r'C:\Users\laima\OneDrive\Documents\GitHub\pockethistory\images'
# location = (40.8068, -73.9617)

# get_nearby_places(folder_path, gmaps, location, False)
