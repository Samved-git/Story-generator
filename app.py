import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Check if google_api_key is available in secrets and show debug info
if "google_api_key" not in st.secrets:
    st.error(
        "Google API key missing! Please add 'google_api_key' to your "
        ".streamlit/secrets.toml file or via Streamlit Cloud Secrets. The app cannot run without it."
    )
    st.stop()
else:
    # Display part of the key for debugging (remove this in production)
    st.write("Google API key loaded, starts with:", st.secrets["google_api_key"][:8] + "...")

GOOGLE_API_KEY = st.secrets["google_api_key"]
GEMINI_IMG_GEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
GEMINI_TEXT_GEN_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_image(prompt: str):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": GOOGLE_API_KEY}
        response = requests.post(GEMINI_IMG_GEN_URL, json=payload, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        img_b64 = data["candidates"][0]["content"]["parts"][0]["inline_data"]["data"]
        img_bytes = BytesIO(bytes.fromhex(img_b64))
        pil_img = Image.open(img_bytes)
        return pil_img
    except Exception as e:
        st.error(f"Failed to generate image: {str(e)}")
        return None

def generate_story(image: Image, topic: str):
    try:
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        img_bytes = buf.read()
        img_b64 = img_bytes.hex()
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Write a short story about this image related to the topic: {topic}."},
                        {"inline_data": {"mime_type": "image/png", "data": img_b64}}
                    ]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}
        params = {"key": GOOGLE_API_KEY}
        response = requests.post(GEMINI_TEXT_GEN_URL, json=payload, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        story = data["candidates"][0]["content"]["parts"][0]["text"]
        return story
    except Exception as e:
        st.error(f"Failed to generate story: {str(e)}")
        return None

st.title("🎨 AI Story Generator (Gemini)")
st.write("Generate an image and story from your topic!")

topic = st.text_input("What's your story about?", placeholder="e.g., A cat playing the piano")

if st.button("Generate", type="primary"):
    if topic:
        with st.spinner("Creating your story..."):
            image = generate_image(f"An image related to {topic}")
            if image:
                st.image(image, caption="Generated Image")
                story = generate_story(image, topic)
                if story:
                    st.write("### Your Story")
                    st.write(story)
    else:
        st.warning("Please enter a topic first!")
