from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
import random

from playlist_app.models import Playlist
from playlist_app.serializers import PlaylistSerializer


class PlaylistViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Playlist CRUD operations and playlist management.
    
    Endpoints:
    - GET /api/playlists/ - List all playlists
    - POST /api/playlists/ - Create a new playlist
    - GET /api/playlists/{id}/ - Retrieve a playlist
    - PUT /api/playlists/{id}/ - Update a playlist
    - PATCH /api/playlists/{id}/ - Partial update a playlist
    - DELETE /api/playlists/{id}/ - Delete a playlist
    - POST /api/playlists/{id}/shuffle/ - Shuffle songs in playlist
    """
    
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    
    @action(detail=True, methods=['post'])
    def shuffle(self, request, pk=None):
        """
        Shuffle the order of songs in the playlist.
        
        Note: This reorders the songs in the many-to-many relationship.
        For a true shuffle order, a through model with an order field 
        would be more appropriate.
        """
        try:
            playlist = Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            raise NotFound("Playlist not found")
        
        songs = list(playlist.songs.all())
        
        if len(songs) < 2:
            return Response(
                {'message': 'Playlist has fewer than 2 songs, no shuffle needed'},
                status=status.HTTP_200_OK
            )
        
        # Shuffle the songs list
        random.shuffle(songs)
        
        # Clear and re-add in shuffled order
        # Note: In a production app, you'd want to use a through model with ordering
        playlist.songs.clear()
        playlist.songs.set(songs)
        
        return Response(
            {
                'message': 'Playlist shuffled successfully',
                'playlist': PlaylistSerializer(playlist).data
            },
            status=status.HTTP_200_OK
        )
