import requests
from ..config import Config

class ScopusService:
    @staticmethod
    def search_articles(query, count, start=0):
        headers = {
            "X-ELS-APIKey": Config.API_KEY,
            "Accept": "application/json"
        }
        
        params = {
            "query": query,
            "count": count,
            "start": start,
            "sort": "relevancy"
        }
        
        response = requests.get(Config.SCOPUS_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
