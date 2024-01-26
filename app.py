import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL.Image
import streamlit as st
import requests

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-pro-vision')

def upload_image():
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
    return uploaded_image


def image_to_text(uploaded_image):

    img = PIL.Image.open(uploaded_image)

    response = model.generate_content(["Find out the name of the exact location given in the image", img])

    return response.text

def get_exact_location(details):
    data = {
        "contents" : {
            "role" : "user",
            "parts" : {
                "text" : details
            }
        },
        "tools" : [
            {
                "function_declarations" : [
                    {
                        "name" : "get_exact_location",
                        "description" : "Find out the exact location in the given context provide pip point location instead of broad location like city",
                        "parameters" : {
                            "type" : "object",
                            "properties" : {
                                "location" : {
                                    "type" : "string",
                                    "description" : "The exact location, city, country e.g. Taj Mahal, Agra, India"
                                }
                            },
                        "required" : ["location"]
                        },
                    }
                ]
            }
        ]
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"


    response = requests.post(url, json=data)

    response = response.json()

    if "content" not in response["candidates"][0]:
        print("ERROR: No content in response")

    message = response["candidates"][0]["content"]["parts"]

    if "functionCall" in message[0]:
        function_response = message[0]["functionCall"]["args"]
        return function_response["location"]

def show_google_map(location):
    google_maps_url = f"https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAP_API_KEY}&q={location}"
    st.components.v1.html(f'<iframe width="100%" height="500" src="{google_maps_url}"></iframe>', height=600)


def main():
    
    st.title("Location finder")

    uploaded_image = upload_image()

    if uploaded_image is not None:

        location_details = image_to_text(uploaded_image)

        location = get_exact_location(location_details)

        if location:
            show_google_map(location)
        else:
            st.error("Error getting location from the image.")

        
if __name__ == "__main__":
    main()


