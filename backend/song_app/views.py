from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from song_app.models import Song
from song_app.serializers import SongSerializer
from song_app.payment_gateways import get_payment_gateway


class SongViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Song CRUD operations and purchase endpoint.
    
    Endpoints:
    - GET /api/songs/ - List all songs
    - POST /api/songs/ - Create a new song
    - GET /api/songs/{id}/ - Retrieve a song
    - PUT /api/songs/{id}/ - Update a song
    - PATCH /api/songs/{id}/ - Partial update a song
    - DELETE /api/songs/{id}/ - Delete a song
    - POST /api/songs/purchase/ - Purchase songs
    """
    
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    
    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """
        Purchase endpoint that processes payment for songs.
        
        Expected request body:
        {
            "song_ids": [1, 2, 3]  # List of song IDs to purchase
        }
        
        Returns:
            - If total price < $10: Uses CheapPaymentGateway
            - If total price >= $10: Uses ExpensivePaymentGateway
        """
        song_ids = request.data.get('song_ids', [])
        
        # Validate song_ids
        if not song_ids:
            return Response(
                {'error': 'Please provide song_ids list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(song_ids, list):
            return Response(
                {'error': 'song_ids must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch songs
        try:
            songs = Song.objects.filter(id__in=song_ids)
            
            if songs.count() != len(song_ids):
                missing_ids = set(song_ids) - set(songs.values_list('id', flat=True))
                return Response(
                    {'error': f'Songs not found for IDs: {missing_ids}'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate total price
            total_price = sum(
                (song.price for song in songs),
                Decimal('0.00')
            )
            
            # Get appropriate payment gateway
            gateway = get_payment_gateway(total_price)
            
            # Process payment
            payment_result = gateway.process_payment(total_price, song_ids)
            
            return Response(
                {
                    'success': True,
                    'message': 'Purchase completed successfully',
                    'total_price': float(total_price),
                    'songs_purchased': SongSerializer(songs, many=True).data,
                    'payment_info': payment_result
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
