import google.generativeai
import os
from config.settings import GEMINI_API_KEY

google.generativeai.configure(api_key=GEMINI_API_KEY)

class GeminiClient:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        self.vision_model = google.generativeai.GenerativeModel('gemini-1.5-flash') # Updated model for image analysis
        self.text_model = google.generativeai.GenerativeModel('gemini-1.5-flash') # Updated model for text-only generation (consistency)

    def analyze_image(self, image_data: bytes, prompt: str):
        try:
            # Assuming image_data is raw bytes of the image
            image_part = {
                'mime_type': 'image/jpeg', # Or image/png, etc., depending on actual image type
                'data': image_data
            }
            response = self.vision_model.generate_content([prompt, image_part])
            # You might need to parse response.text or response.parts based on the expected output format
            return response.text
        except Exception as e:
            print(f"Error analyzing image with Gemini API in GeminiClient: {e}")
            return None

    def generate_text_stream(self, prompt: str):
        try:
            response = self.text_model.generate_content(prompt, stream=True)
            return response
        except Exception as e:
            print(f"Error generating text with Gemini API in GeminiClient: {e}")
            return None

