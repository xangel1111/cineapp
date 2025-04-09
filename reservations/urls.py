from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Página principal
    path('', views.home, name='home'),
    
    # Películas
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    
    # Horarios y reservas
    path('showtimes/<int:showtime_id>/', views.showtime_detail, name='showtime_detail'),
    path('showtimes/<int:showtime_id>/reserve/', views.create_reservation, name='create_reservation'),
    path('reservations/', views.user_reservations, name='user_reservations'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    
    # Autenticación
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]