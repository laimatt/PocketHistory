from dotenv import load_dotenv
import requests
import json
import googlemaps
import os
import shutil
import json
from groq import Groq

# def save_places_to_json(places_list, filename="places.json"):
#     try:
#         with open(filename, "w", encoding="utf-8") as f: # Use utf-8 encoding
#             json.dump(places_list, f, indent=2, ensure_ascii=False)  # Save as a JSON array, with indentation
#         print(f"Places saved to {filename}")
#     except Exception as e:
#         print(f"Error saving places to JSON: {e}")

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

def get_photo_from_reference(place, gmaps):
    if 'photos' in place:
        if 'photo_reference' in place['photos'][0]:
            photo = place['photos'][0]['photo_reference']
            local_filename = place['name'] + '.png'
            image = os.path.join(folder_path, local_filename)
            f = open(image, 'wb')
            for chunk in gmaps.places_photo(photo, max_width=1000):
                if chunk:
                    f.write(chunk)
            f.close()


# gets all nearby places, creates images for each place, and generates groq calls for descriptons
def get_nearby_places(folder_path, gmaps, location, json):
    
    if json:
        places_list = load_places_from_json("places_all.json")
    else:
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)  # Delete the folder and its contents
                print(f"Deleted folder: {folder_path}")
            except Exception as e:
                print(f"Error deleting folder {folder_path}: {e}")
        places = gmaps.places_nearby(
            location=location,
            radius=300,  # 2000 meters = 2 km
            type="history"  # Example: 'restaurant', 'cafe', 'hospital', etc.
        )
        places_list = places.get("results", [])  # Extract the list of places, handle missing "results"
        save_places_to_json(places_list)

    for place in places_list:

        location = place['name']
        address = place['vicinity']
        print(f"Name: {location}, Address: {address}")

        short_content_prompt = (f"give me a concise one phrase description about {location} located at {address} " + 
                                f"that intends to draw the user's interest. This should be no longer than 10 words.")
        long_content_prompt = (f"give me a brief, concise summary about {location} located at {address} " + 
                                f"that intends to draw the user's interest. this should be no longer than 3 sentences")
        place['short_description'] = call_groq(short_content_prompt)
        place['long_description'] = call_groq(long_content_prompt)

        append_place_to_json(place, "places.json")

        if not json:
            get_photo_from_reference(place, gmaps)

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

    print(description)
    return description

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GO_KEY"))

folder_path = r'C:\Users\laima\OneDrive\Documents\GitHub\pockethistory\images'
location = (40.8068, -73.9617)

get_nearby_places(folder_path, gmaps, location, True)
