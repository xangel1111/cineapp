from django.contrib import admin
from .models import Movie, Theater, ShowTime, Reservation

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'tmdb_id')
    search_fields = ('title',)

@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(ShowTime)
class ShowTimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'start_time', 'price', 'seats_available')
    list_filter = ('movie', 'theater')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reference_code', 'user', 'showtime', 'num_seats', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'showtime__movie')
    search_fields = ('user__username', 'reference_code')
    readonly_fields = ('reference_code', 'created_at')