import requests
from django.conf import settings
from datetime import datetime

class TMDBApiClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_API_BASE_URL
    
    def get_now_playing(self, page=1):
        endpoint = f"{self.base_url}/movie/now_playing"
        params = {
            'api_key': self.api_key,
            'language': 'es-ES',
            'page': page
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None
    
    def get_movie_details(self, movie_id):
        endpoint = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'es-ES',
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None
    
    def search_movies(self, query, page=1):
        endpoint = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'language': 'es-ES',
            'query': query,
            'page': page
        }
        response = requests.get(endpoint, params=params)
        return response.json() if response.status_code == 200 else None
    
    def process_movie_data(self, movie_data):
        # Función auxiliar para procesar los datos de la película
        if not movie_data:
            return None
        
        # Convertir la fecha de lanzamiento a formato de fecha de Python
        release_date = None
        if 'release_date' in movie_data and movie_data['release_date']:
            try:
                release_date = datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        return {
            'tmdb_id': movie_data['id'],
            'title': movie_data['title'],
            'overview': movie_data['overview'] if 'overview' in movie_data else '',
            'poster_path': movie_data['poster_path'] if 'poster_path' in movie_data else None,
            'release_date': release_date
        }