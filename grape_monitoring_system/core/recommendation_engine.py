from core.gemini_client import GeminiClient
from models.analysis import Analysis
from models.recommendation import Recommendation
from datetime import date
import json
import re # Import regex module
from typing import Optional, List
from services.weather_service import WeatherService # Import WeatherService
from config.settings import OPENWEATHER_API_KEY # Import OPENWEATHER_API_KEY

class RecommendationEngine:
    # Define a dictionary for chemical drug recommendations based on disease
    # This can be expanded or moved to a configuration file/database later
    CHEMICAL_DRUG_RECOMMENDATIONS = {
        "Mildew": [
            {"name": "Kükürt Bazlı Fungisitler", "description": "Kükürt içeren fungisitler, özellikle erken evrelerde ve düşük hastalık basıncında etkili olabilir."},
            {"name": "Bakır Bazlı Fungisitler", "description": "Bordo bulamacı gibi bakır içeren ürünler, hem koruyucu hem de tedavi edici etki gösterir."},
            {"name": "Sistemik Fungisitler (Örn: Triazoller)", "description": "Hastalığın bitki içine nüfuz ettiği durumlarda sistemik etkili fungisitler tercih edilebilir."}
        ],
        "Botrytis": [
            {"name": "Botrytis Fungisitleri", "description": "Botrytis kontrolü için spesifik fungisitler (örn: Cyprodinil + Fludioxonil içerenler) kullanılmalıdır."},
            {"name": "Trichoderma Harzianum", "description": "Biyolojik mücadele için faydalı mantarlar (örn: Trichoderma harzianum) kullanılabilir."}
        ],
        "Black Rot": [
            {"name": "Mancozeb", "description": "Koruyucu olarak Mancozeb içerikli fungisitler uygulanabilir."},
            {"name": "Myclobutanil", "description": "Hastalık görüldüğünde Myclobutanil gibi sistemik fungisitler kullanılabilir."}
        ],
        "Leaf Blight": [
            {"name": "Pyraclostrobin + Boscalid", "description": "Yaprak yanıklığı için geniş spektrumlu fungisitler etkili olabilir."},
            {"name": "Chlorothalonil", "description": "Koruyucu amaçlı chlorothalonil uygulamaları düşünülebilir."}
        ],
        "Rust": [
            {"name": "Mancozeb", "description": "Pas hastalığına karşı Mancozeb veya çinko içeren fungisitler kullanılabilir."}
        ],
        "Anthracnose": [
            {"name": "Mancozeb", "description": "Antraknoz için koruyucu olarak mancozeb etkili olabilir."},
            {"name": "Azoxystrobin", "description": "Sistemik koruma için azoxystrobin gibi strobilurin fungisitler kullanılabilir."}
        ]
    }

    def __init__(self):
        self.gemini_client = GeminiClient()
        self.weather_service = WeatherService(OPENWEATHER_API_KEY) # Initialize WeatherService

    def generate_recommendations(self, analysis: Analysis) -> List[Recommendation]:
        """
        Generates recommendations based on the analysis results.
        Prioritizes structured JSON from Gemini, falls back to text parsing if needed.
        """
        if analysis.disease_detected == "Healthy":
            return [Recommendation(
                analysis_id=analysis.id,
                recommendation_type="prevention",
                description="Üzüm bitkiniz sağlıklı. Sağlığını korumak için düzenli gözlem ve iyi kültürel uygulamalara devam edin.",
                priority=1,
                implementation_date=date.today()
            )]

        # Define the desired JSON structure for recommendations
        recommendation_example = [
            {
                "type": "tedavi",
                "description": "3 hafta boyunca haftalık Bakır bazlı fungisit uygulayın.",
                "priority": 4,
                "implementation_date": str(date.today())
            },
            {
                "type": "budama",
                "description": "Ciddi şekilde enfekte olmuş tüm yaprakları çıkarın ve uygun şekilde imha edin.",
                "priority": 5,
                "implementation_date": str(date.today())
            },
            {
                "type": "önleme",
                "description": "Uygun hava sirkülasyonu sağlayın ve aşırı sulamadan kaçının.",
                "priority": 3,
                "implementation_date": str(date.today())
            }
        ]
        recommendation_example_str = json.dumps(recommendation_example, indent=2, ensure_ascii=False)

        # Fetch weather data
        city = "Izmir" # TODO: Make city dynamic (e.g., from user profile or image metadata)
        current_weather_data = self.weather_service.get_current_weather(city)
        weather_info = self.weather_service.parse_weather_data(current_weather_data)

        prompt = (
            f"Analiz sonucu: Tespit Edilen Hastalık - {analysis.disease_detected} (Güven: {analysis.confidence_score * 100:.2f}%). " if analysis.confidence_score is not None else f"Analiz sonucu: Tespit Edilen Hastalık - {analysis.disease_detected} (Güven: Bilinmiyor). "
            f"Mevcut hava durumu: {weather_info}. " # Add weather info to the prompt
            f"Bir uzman bağcı olarak, {analysis.disease_detected} için 3-5 pratik ve uygulanabilir tedavi, budama veya önleme önerisi sunun. "
            f"Önerilerde spesifik ticari ürün isimleri yerine, aktif madde türleri (örn: 'Bakır bazlı fungisitler', 'Kükürt içerikli ürünler') veya genel ilaç kategorilerini belirtin. "
            f"Yanıtınız SADECE bir JSON nesne dizisi OLMALIDIR. Başka hiçbir giriş veya sonuç metni, açıklama veya markdown kod bloğu işareti (```json gibi) KULLANMAYIN. Dizideki her nesnenin şu alanları OLMALIDIR: 'type' (tür: 'tedavi', 'budama', 'önleme' gibi), 'description' (detaylı açıklama), 'priority' (1-5 arası bir tam sayı, 5 en yüksek), ve 'implementation_date' (YYYY-MM-DD formatında)." # Added stricter instruction for ONLY JSON
            f"Örnek: {recommendation_example_str}"
        )

        gemini_response_stream = self.gemini_client.generate_text_stream(prompt)
        gemini_response = ""
        if gemini_response_stream:
            for chunk in gemini_response_stream:
                gemini_response += chunk.text

        recommendations = []
        if gemini_response:
            try:
                print(f"Debugging (RecommendationEngine): Raw Gemini Response: {gemini_response}")
                cleaned_response = gemini_response.strip()

                # First attempt: Try to parse the response directly after stripping common markdown wrappers
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:].strip()
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3].strip()

                try:
                    parsed_recommendations = json.loads(cleaned_response)
                    print(f"Debugging: Successfully parsed JSON directly: {cleaned_response}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing response directly as JSON: {e}. Trying regex extraction...")
                    # Fallback to regex if direct parsing fails
                    json_match = re.search(r'\[.*\]', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            extracted_json_str = json_match.group(0).strip()
                            parsed_recommendations = json.loads(extracted_json_str)
                            print(f"Debugging: Successfully parsed JSON with regex: {extracted_json_str}")
                        except json.JSONDecodeError as e_regex:
                            print(f"Error parsing regex extracted JSON: {e_regex}. Proceeding with plain text parsing fallback.")
                            parsed_recommendations = [] # Set to empty to trigger plain text fallback
                    else:
                        print("Debugging: No JSON array found with regex. Proceeding with plain text parsing fallback.")
                        parsed_recommendations = [] # Set to empty to trigger plain text fallback

                if not isinstance(parsed_recommendations, list):
                    parsed_recommendations = [parsed_recommendations]

                for rec_data in parsed_recommendations:
                    if all(k in rec_data for k in ['type', 'description', 'priority', 'implementation_date']):
                        try:
                            impl_date = date.fromisoformat(rec_data['implementation_date'])
                        except ValueError:
                            impl_date = date.today()

                        recommendations.append(Recommendation(
                            analysis_id=analysis.id,
                            recommendation_type=rec_data['type'],
                            description=rec_data['description'],
                            priority=int(rec_data['priority']),
                            implementation_date=impl_date
                        ))
                    else:
                        print(f"Warning: Malformed recommendation object received: {rec_data}")
                        recommendations.append(Recommendation(
                            analysis_id=analysis.id,
                            recommendation_type="hata",
                            description="Yapay Zekadan hatalı öneri alındı. Eksik alanlar var veya format yanlış.",
                            priority=1,
                            implementation_date=date.today()
                        ))
            except (json.JSONDecodeError, ValueError, SyntaxError) as e:
                print(f"Error decoding JSON from Gemini recommendations: {e}")
                print(f"Problematic Gemini Response (Recommendations): {gemini_response}")
                print("Attempting fallback plain text parsing for recommendations...")
                fallback_recommendations = self._parse_plain_text_recommendations(gemini_response, analysis.id)
                if fallback_recommendations:
                    recommendations.extend(fallback_recommendations)
                else:
                    recommendations.append(Recommendation(
                        analysis_id=analysis.id,
                        recommendation_type="hata",
                        description=f"Öneriler oluşturulamadı. Lütfen tekrar deneyin veya bir uzmana danışın. Detay: {e}",
                        priority=5,
                        implementation_date=date.today()
                    ))
        else:
            recommendations.append(Recommendation(
                analysis_id=analysis.id,
                recommendation_type="hata",
                description="Yapay Zekadan yanıt alınamadı. API bağlantısını kontrol edin.",
                priority=5,
                implementation_date=date.today()
            ))

        # Add chemical drug recommendations if applicable
        if analysis.disease_detected in self.CHEMICAL_DRUG_RECOMMENDATIONS and analysis.disease_detected != "Healthy":
            for drug_rec in self.CHEMICAL_DRUG_RECOMMENDATIONS[analysis.disease_detected]:
                recommendations.append(Recommendation(
                    analysis_id=analysis.id,
                    recommendation_type="kimyasal_ilac",
                    description=f"{drug_rec['name']}: {drug_rec['description']}",
                    priority=5, # High priority for chemical recommendations
                    implementation_date=date.today()
                ))

        return recommendations, gemini_response # Return raw response here

    def _parse_plain_text_recommendations(self, text: str, analysis_id: Optional[int]) -> List[Recommendation]:
        """
        Attempts to parse recommendations from a plain text response.
        Looks for bullet points or numbered lists and tries to extract a title/description.
        """
        parsed_recs = []
        # Split by newlines and look for common list starters
        lines = text.split('\n')
        current_rec_title = "Genel Öneri"
        current_rec_description = []

        # Regex to find bullet points or numbered lists, and capture text after them
        # Example: * Treatment: Apply fungicide -> group 1: Treatment, group 2: Apply fungicide
        # Example: 1. Pruning: Remove leaves -> group 1: Pruning, group 2: Remove leaves
        # Example: - General Advice: Check plant daily -> group 1: General Advice, group 2: Check plant daily
        # Also handle bold text like **Treatment:** or simple sentences

        # Regex to capture potential title and description
        # Group 1: list marker (optional), Group 2: potential title, Group 3: description
        recommendation_pattern = re.compile(r'^\s*(?:[*-]|\d+\.)?\s*(?:\*\*(.+?):\*\*|(.+?):)?\s*(.*)')
        
        for line in lines:
            line = line.strip()
            if not line: # Skip empty lines
                continue

            match = recommendation_pattern.match(line)
            if match:
                potential_title_bold = match.group(1)
                potential_title_plain = match.group(2)
                description_part = match.group(3)

                title = potential_title_bold or potential_title_plain
                
                if title:
                    # If a new title is found, finalize the previous recommendation if it exists
                    if current_rec_description:
                        parsed_recs.append(Recommendation(
                            analysis_id=analysis_id,
                            recommendation_type=current_rec_title.lower().replace(' ', '_').replace(':', '')[:20] if current_rec_title else "genel_oneri",
                            description=" ".join(current_rec_description).strip(),
                            priority=3, # Default priority for parsed text
                            implementation_date=date.today()
                        ))
                    current_rec_title = title.strip()
                    current_rec_description = [description_part.strip()] if description_part else []
                elif current_rec_description: # Continue current description if no new title
                    current_rec_description.append(line) # Add the whole line to description
                else: # Start a new general recommendation if no title and no current description
                    current_rec_title = "Genel Öneri"
                    current_rec_description = [line]
            elif current_rec_description: # If no match but part of current description
                current_rec_description.append(line)
            else:
                # Handle lines that are just plain text not matching a pattern, as a general advice
                if not parsed_recs and not current_rec_description: # Only add if no recs yet and no current description
                    current_rec_title = "Genel Bilgi"
                    current_rec_description = [line]

        # Add the last accumulated recommendation
        if current_rec_description:
            parsed_recs.append(Recommendation(
                analysis_id=analysis_id,
                recommendation_type=current_rec_title.lower().replace(' ', '_').replace(':', '')[:20] if current_rec_title else "genel_oneri",
                description=" ".join(current_rec_description).strip(),
                priority=3,
                implementation_date=date.today()
            ))

        return parsed_recs

