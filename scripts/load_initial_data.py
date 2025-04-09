import os
import django
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineapp.settings')
django.setup()

from reservations.models import Movie, Theater, ShowTime
from reservations.movie_api import TMDBApiClient

def create_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('Superusuario creado: admin / admin123')

def create_theaters():
    theaters_data = [
        {'name': 'Sala 1 - VIP', 'capacity': 50},
        {'name': 'Sala 2 - 3D', 'capacity': 80},
        {'name': 'Sala 3 - Standard', 'capacity': 120},
        {'name': 'Sala 4 - IMAX', 'capacity': 100},
    ]
    
    for data in theaters_data:
        Theater.objects.get_or_create(
            name=data['name'],
            defaults={'capacity': data['capacity']}
        )
    
    print(f'Salas creadas: {Theater.objects.count()}')

def fetch_and_create_movies():
    api_client = TMDBApiClient()
    movies_data = api_client.get_now_playing()
    
    if not movies_data or 'results' not in movies_data:
        print('No se pudieron obtener películas desde la API')
        return
    
    count = 0
    for movie_data in movies_data['results'][:10]:  # Limitar a 10 películas
        processed_data = api_client.process_movie_data(movie_data)
        if processed_data:
            movie, created = Movie.objects.get_or_create(
                tmdb_id=processed_data['tmdb_id'],
                defaults={
                    'title': processed_data['title'],
                    'overview': processed_data['overview'],
                    'poster_path': processed_data['poster_path'],
                    'release_date': processed_data['release_date'] or datetime.date.today(),
                }
            )
            
            if created:
                count += 1
    
    print(f'Películas creadas: {count}')

def create_showtimes():
    movies = Movie.objects.all()
    theaters = Theater.objects.all()
    
    if not movies or not theaters:
        print('No hay películas o salas para crear horarios')
        return
    
    # Eliminar horarios existentes para evitar duplicados
    ShowTime.objects.all().delete()
    
    now = timezone.now()
    count = 0
    
    # Distribuir las películas entre las salas
    for i, movie in enumerate(movies):
        # Usar módulo para rotar las películas entre las salas disponibles
        theater = theaters[i % len(theaters)]
        
        # Crear horarios para matinée (12:00) con horarios ligeramente diferentes
        for day in range(7):
            # Ajustar la hora ligeramente para evitar conflictos
            hour = 12 + (i % 3)  # 12:00, 13:00, o 14:00 dependiendo de la película
            start_time = now.replace(hour=hour, minute=0, second=0, microsecond=0) + datetime.timedelta(days=day)
            end_time = start_time + datetime.timedelta(hours=2)  # Duración estimada de 2 horas
            
            ShowTime.objects.create(
                movie=movie,
                theater=theater,
                start_time=start_time,
                end_time=end_time,
                price=10.50 if "VIP" in theater.name else 8.00
            )
            count += 1
        
        # Crear horarios para función nocturna (18:00, 19:00, o 20:00)
        for day in range(7):
            # Ajustar la hora ligeramente para evitar conflictos
            hour = 18 + (i % 3)  # 18:00, 19:00, o 20:00 dependiendo de la película
            start_time = now.replace(hour=hour, minute=0, second=0, microsecond=0) + datetime.timedelta(days=day)
            end_time = start_time + datetime.timedelta(hours=2)  # Duración estimada de 2 horas
            
            ShowTime.objects.create(
                movie=movie,
                theater=theater,
                start_time=start_time,
                end_time=end_time,
                price=12.50 if "VIP" in theater.name else 10.00
            )
            count += 1
    
    print(f'Horarios creados: {count}')

def run():
    print('Cargando datos iniciales...')
    create_superuser()
    create_theaters()
    fetch_and_create_movies()
    create_showtimes()
    print('Datos iniciales cargados correctamente')

if __name__ == '__main__':
    run()