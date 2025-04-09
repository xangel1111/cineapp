from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404

from .models import Movie, ShowTime, Reservation
from .forms import CustomUserCreationForm, ReservationForm, MovieSearchForm
from .movie_api import TMDBApiClient

# Función auxiliar para obtener o crear una película desde la API
def get_or_create_movie_from_api(tmdb_id):
    api_client = TMDBApiClient()
    movie_data = api_client.get_movie_details(tmdb_id)
    
    if not movie_data:
        return None
    
    processed_data = api_client.process_movie_data(movie_data)
    
    # Intentar encontrar la película en la base de datos
    try:
        movie = Movie.objects.get(tmdb_id=processed_data['tmdb_id'])
        # Actualizar la información en caso de que haya cambiado
        for key, value in processed_data.items():
            setattr(movie, key, value)
        movie.save()
    except Movie.DoesNotExist:
        # Crear una nueva película si no existe
        movie = Movie.objects.create(**processed_data)
    
    return movie

# Vista de la página principal
def home(request):
    api_client = TMDBApiClient()
    movies_data = api_client.get_now_playing()
    
    context = {
        'movies': [],
    }
    
    if movies_data and 'results' in movies_data:
        context['movies'] = movies_data['results'][:6]  # Mostrar solo las primeras 6 películas
    
    return render(request, 'reservations/home.html', context)

# Vista para listar películas
def movie_list(request):
    form = MovieSearchForm(request.GET)
    api_client = TMDBApiClient()
    
    if form.is_valid() and form.cleaned_data['query']:
        query = form.cleaned_data['query']
        movies_data = api_client.search_movies(query)
    else:
        movies_data = api_client.get_now_playing()
    
    movies = []
    if movies_data and 'results' in movies_data:
        movies = movies_data['results']
    
    # Paginación
    paginator = Paginator(movies, 12)  # 12 películas por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj
    }
    
    return render(request, 'reservations/movie_list.html', context)

# Vista de detalle de película
def movie_detail(request, tmdb_id):
    # Obtenemos o creamos la película en nuestra BD
    movie = get_or_create_movie_from_api(tmdb_id)
    
    if not movie:
        raise Http404("Película no encontrada")
    
    # Obtener los horarios disponibles para esta película
    showtimes = ShowTime.objects.filter(movie=movie).order_by('start_time')
    
    context = {
        'movie': movie,
        'showtimes': showtimes
    }
    
    return render(request, 'reservations/movie_detail.html', context)

# Vista para crear reserva
@login_required
def create_reservation(request, showtime_id):
    showtime = get_object_or_404(ShowTime, pk=showtime_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            num_seats = form.cleaned_data['num_seats']
            
            # Verificar disponibilidad
            available_seats = showtime.seats_available()
            if num_seats > available_seats:
                messages.error(request, f"Solo hay {available_seats} asientos disponibles.")
                return redirect('showtime_detail', showtime_id=showtime.id)
            
            # Crear reserva
            with transaction.atomic():
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.showtime = showtime
                reservation.save()
                
                messages.success(request, f"¡Reserva creada con éxito! Código: {reservation.reference_code}")
                return redirect('reservation_detail', reservation_id=reservation.id)
    else:
        form = ReservationForm()
    
    context = {
        'form': form,
        'showtime': showtime
    }
    
    return render(request, 'reservations/create_reservation.html', context)

# Vista de detalle de horario
def showtime_detail(request, showtime_id):
    showtime = get_object_or_404(ShowTime, pk=showtime_id)
    form = ReservationForm()
    
    context = {
        'showtime': showtime,
        'form': form
    }
    
    return render(request, 'reservations/showtime_detail.html', context)

# Vista de detalle de reserva
@login_required
def reservation_detail(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
    
    context = {
        'reservation': reservation
    }
    
    return render(request, 'reservations/reservation_detail.html', context)

# Vista para listar reservas del usuario
@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reservations': reservations
    }
    
    return render(request, 'reservations/user_reservations.html', context)

# Vista para cancelar reserva
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)
    
    if reservation.status == 'CONFIRMED':
        messages.error(request, "No se puede cancelar una reserva ya confirmada.")
        return redirect('reservation_detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        reservation.status = 'CANCELLED'
        reservation.save()
        messages.success(request, "Reserva cancelada con éxito.")
        return redirect('user_reservations')
    
    context = {
        'reservation': reservation
    }
    
    return render(request, 'reservations/cancel_reservation.html', context)

# Vista de registro de usuario
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "¡Registro exitoso! Bienvenido/a.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})