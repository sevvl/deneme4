from core.gemini_client import GeminiClient
import json
from typing import Optional
import re # Added for regex extraction

class DiseaseAnalyzer:
    def __init__(self):
        self.gemini_client = GeminiClient()

    def analyze_grape_image(self, image_data: bytes) -> Optional[dict]:
        """
        Analyzes a grape image for diseases using the Gemini API.
        Returns a dictionary with disease detection results and confidence score.
        """
        json_example = {
            "disease_detected": "Powdery Mildew",
            "confidence_score": 0.95,
            "explanation": "The problem is \"powdery\" mildew and it's quite severe."
        }
        json_example_str = json.dumps(json_example)

        prompt = (
            f"You are an expert viticulturist AI. Analyze the provided image of grape leaves/plant for any signs of diseases or health issues. "
            f"Identify the disease, provide a confidence score (0.0 to 1.0), and a brief explanation. "
            f"Respond in STRICT JSON format with double quotes for keys and string values. ALL internal double quotes within string values MUST be escaped (e.g., \"your text\"). Fields: 'disease_detected', 'confidence_score', 'explanation'."
            f"Example: {json_example_str}"
            f"Eğer hastalık tespit edilmezse, 'disease_detected' alanını 'Sağlıklı', 'confidence_score' alanını 1.0 ve 'explanation' alanını 'Hastalık belirtisi tespit edilmedi.' olarak ayarlayın." # Changed to Turkish
            f"YANITINIZ SADECE JSON NESNESİ OLMALIDIR. BAŞKA HİÇBİR METİN VEYA MARKDOWN KOD BLOĞU İŞARETİ KULLANMAYIN. Örnek: {json_example_str}"
        )

        gemini_response = self.gemini_client.analyze_image(image_data, prompt)
        analysis_result = {"disease_detected": "Unknown", "confidence_score": 0.0, "explanation": "Failed to get response from AI."} # Default in case of no response

        if gemini_response:
            print(f"Debugging: Raw Gemini Response: {gemini_response}")
            cleaned_response = gemini_response.strip()

            # First attempt: Try to parse the response directly after stripping common markdown wrappers
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:].strip()
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3].strip()

            try:
                analysis_result = json.loads(cleaned_response)
                print(f"Debugging: Successfully parsed JSON directly: {cleaned_response}")
            except json.JSONDecodeError as e:
                print(f"Error parsing response directly as JSON: {e}. Trying regex extraction...")
                # Fallback to regex if direct parsing fails
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    try:
                        extracted_json_str = json_match.group(0).strip()
                        analysis_result = json.loads(extracted_json_str)
                        print(f"Debugging: Successfully parsed JSON with regex: {extracted_json_str}")
                    except json.JSONDecodeError as e_regex:
                        print(f"Error parsing regex extracted JSON: {e_regex}. Sticking with default error result.")
                        analysis_result = {"disease_detected": "Unknown", "confidence_score": 0.0, "explanation": f"AI yanıtı ayrıştırılamadı (regex de başarısız). Ham yanıt: {gemini_response}"}
                else:
                    print("Debugging: No JSON object found with regex. Sticking with default error result.")
                    analysis_result = {"disease_detected": "Unknown", "confidence_score": 0.0, "explanation": f"AI yanıtı ayrıştırılamadı. Ham yanıt: {gemini_response}"}
        else:
            print("Debugging: Gemini API returned None response.")

        return analysis_result, gemini_response # Always return raw response

