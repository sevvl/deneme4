# core/web_search.py

import requests
from bs4 import BeautifulSoup

def duckduckgo_search(query, max_results=5):
    url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, data=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for link in soup.find_all('a', class_='result__a', limit=max_results):
            title = link.get_text()
            href = link.get('href')
            results.append({"title": title, "url": href})

        return results

    except Exception as e:
        return [{"title": "Arama hatası", "url": str(e)}]
