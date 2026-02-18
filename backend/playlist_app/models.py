from django.db import models
from song_app.models import Song


class Playlist(models.Model):
    """
    Playlist model with:
    - Name (string)
    - Songs (references to Song instances)
    """
    
    name = models.CharField(max_length=255)
    songs = models.ManyToManyField(
        Song,
        related_name='playlists',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    
    def get_total_duration(self):
        """Get total duration of all songs in seconds"""
        return sum(song.length for song in self.songs.all())
    
    def get_total_price(self):
        """Get total price of all songs in playlist"""
        from decimal import Decimal
        return sum(
            (song.price for song in self.songs.all()),
            Decimal('0.00')
        )
