from rest_framework import serializers
from song_app.models import Song


class SongSerializer(serializers.ModelSerializer):
    """Serializer for Song model"""
    
    class Meta:
        model = Song
        fields = [
            'id',
            'title',
            'length',
            'date_released',
            'price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
