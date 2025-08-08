import requests
import os

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_current_weather(self, city: str, country_code: str = "TR") -> dict:
        try:
            params = {
                "q": f"{city},{country_code}",
                "appid": self.api_key,
                "units": "metric", # Celsius
                "lang": "tr"       # Turkish language
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            weather_data = response.json()
            return weather_data
        except requests.exceptions.RequestException as e:
            print(f"Weather service error: {e}")
            return {}

    def parse_weather_data(self, weather_data: dict) -> str:
        if not weather_data:
            return "Hava durumu bilgisi alınamadı."

        main_weather = weather_data.get('weather', [{}])[0].get('description', 'Bilinmiyor')
        temperature = weather_data.get('main', {}).get('temp', 'Bilinmiyor')
        humidity = weather_data.get('main', {}).get('humidity', 'Bilinmiyor')
        wind_speed = weather_data.get('wind', {}).get('speed', 'Bilinmiyor')

        return (
            f"Mevcut Hava Durumu: {main_weather}, "
            f"Sıcaklık: {temperature}°C, "
            f"Nem: %{humidity}, "
            f"Rüzgar Hızı: {wind_speed} m/s."
        )

# Example Usage (for testing purposes, remove in production app.py)
# if __name__ == "__main__":
#     # You should get your API key from OpenWeatherMap (https://openweathermap.org/api)
#     # and set it as an environment variable or in a config file.
#     OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
#     if not OPENWEATHER_API_KEY:
#         print("Please set the OPENWEATHER_API_KEY environment variable.")
#     else:
#         weather_service = WeatherService(OPENWEATHER_API_KEY)
#         city_name = "Ankara"
#         weather = weather_service.get_current_weather(city_name)
#         if weather:
#             parsed_info = weather_service.parse_weather_data(weather)
#             print(f"Hava durumu {city_name} için: {parsed_info}")
#         else:
#             print(f"{city_name} için hava durumu bilgisi alınamadı.") 