from django.db import models
from django.core.validators import MinValueValidator


class Song(models.Model):
    """
    Song model with required attributes:
    - Title (string)
    - Length (int in seconds)
    - Date Released (datetime)
    - Price (decimal, positive amount)
    """
    
    title = models.CharField(max_length=255)
    length = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Length of the song in seconds"
    )
    date_released = models.DateTimeField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price of the song"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - ${self.price}"
