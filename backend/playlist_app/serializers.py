from rest_framework import serializers
from playlist_app.models import Playlist
from song_app.models import Song
from song_app.serializers import SongSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for Playlist model with nested songs"""
    
    songs = SongSerializer(many=True, read_only=True)
    song_ids = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        many=True,
        write_only=True,
        source='songs'
    )
    total_duration = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = [
            'id',
            'name',
            'songs',
            'song_ids',
            'total_duration',
            'total_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_duration(self, obj):
        """Get total duration in seconds"""
        return obj.get_total_duration()
    
    def get_total_price(self, obj):
        """Get total price"""
        return float(obj.get_total_price())
