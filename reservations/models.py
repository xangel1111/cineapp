from django.db import models
from django.contrib.auth.models import User
import uuid

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_date = models.DateField()
    
    def __str__(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    
    def __str__(self):
        return self.name

class ShowTime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE, related_name='showtimes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        unique_together = ('theater', 'start_time')
    
    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    def seats_available(self):
        seats_booked = Reservation.objects.filter(showtime=self).aggregate(
            total=models.Sum('num_seats')
        )['total'] or 0
        return self.theater.capacity - seats_booked

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
    ]
    
    reference_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    showtime = models.ForeignKey(ShowTime, on_delete=models.CASCADE, related_name='reservations')
    num_seats = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"Reserva {self.reference_code} - {self.user.username}"
    
    @property
    def total_price(self):
        return self.showtime.price * self.num_seats