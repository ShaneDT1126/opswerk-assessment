from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import timedelta

from playlist_app.models import Playlist
from song_app.models import Song


class PlaylistModelTests(TestCase):
    """Test cases for Playlist model"""
    
    def setUp(self):
        self.now = timezone.now()
        self.song1 = Song.objects.create(
            title='Song 1',
            length=180,
            date_released=self.now,
            price=Decimal('3.99')
        )
        self.song2 = Song.objects.create(
            title='Song 2',
            length=240,
            date_released=self.now,
            price=Decimal('4.99')
        )
        self.song3 = Song.objects.create(
            title='Song 3',
            length=200,
            date_released=self.now,
            price=Decimal('5.99')
        )
        self.playlist = Playlist.objects.create(name='My Playlist')
        self.playlist.songs.set([self.song1, self.song2, self.song3])
    
    def test_playlist_creation(self):
        """Test playlist creation"""
        self.assertEqual(self.playlist.name, 'My Playlist')
        self.assertEqual(self.playlist.songs.count(), 3)
    
    def test_playlist_string_representation(self):
        """Test playlist string representation"""
        self.assertEqual(str(self.playlist), 'My Playlist')
    
    def test_playlist_get_total_duration(self):
        """Test total duration calculation"""
        total_duration = self.playlist.get_total_duration()
        # 180 + 240 + 200 = 620 seconds
        self.assertEqual(total_duration, 620)
    
    def test_playlist_get_total_price(self):
        """Test total price calculation"""
        total_price = self.playlist.get_total_price()
        # 3.99 + 4.99 + 5.99 = 14.97
        self.assertEqual(total_price, Decimal('14.97'))
    
    def test_empty_playlist_duration(self):
        """Test total duration for empty playlist"""
        empty_playlist = Playlist.objects.create(name='Empty Playlist')
        self.assertEqual(empty_playlist.get_total_duration(), 0)
    
    def test_empty_playlist_price(self):
        """Test total price for empty playlist"""
        empty_playlist = Playlist.objects.create(name='Empty Playlist')
        self.assertEqual(empty_playlist.get_total_price(), Decimal('0.00'))
    
    def test_playlist_add_songs(self):
        """Test adding songs to playlist"""
        new_song = Song.objects.create(
            title='New Song',
            length=150,
            date_released=self.now,
            price=Decimal('2.99')
        )
        self.playlist.songs.add(new_song)
        self.assertEqual(self.playlist.songs.count(), 4)
    
    def test_playlist_remove_songs(self):
        """Test removing songs from playlist"""
        self.playlist.songs.remove(self.song1)
        self.assertEqual(self.playlist.songs.count(), 2)
    
    def test_multiple_playlists_same_song(self):
        """Test that same song can be in multiple playlists"""
        playlist2 = Playlist.objects.create(name='Another Playlist')
        playlist2.songs.add(self.song1)
        
        self.assertIn(self.song1, self.playlist.songs.all())
        self.assertIn(self.song1, playlist2.songs.all())


class PlaylistAPITests(APITestCase):
    """Test cases for Playlist API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
        self.song1 = Song.objects.create(
            title='Song 1',
            length=180,
            date_released=self.now,
            price=Decimal('3.99')
        )
        self.song2 = Song.objects.create(
            title='Song 2',
            length=240,
            date_released=self.now,
            price=Decimal('4.99')
        )
        self.playlist = Playlist.objects.create(name='My Playlist')
        self.playlist.songs.set([self.song1, self.song2])
    
    def test_list_playlists(self):
        """Test listing all playlists"""
        response = self.client.get('/api/playlists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_playlist(self):
        """Test creating a new playlist"""
        data = {
            'name': 'New Playlist',
            'song_ids': [self.song1.id]
        }
        response = self.client.post('/api/playlists/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Playlist')
        self.assertEqual(Playlist.objects.count(), 2)
    
    def test_create_empty_playlist(self):
        """Test creating a playlist with no songs"""
        data = {
            'name': 'Empty Playlist',
            'song_ids': []
        }
        response = self.client.post('/api/playlists/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Empty Playlist')
    
    def test_retrieve_playlist(self):
        """Test retrieving a specific playlist"""
        response = self.client.get(f'/api/playlists/{self.playlist.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Playlist')
        self.assertEqual(len(response.data['songs']), 2)
    
    def test_retrieve_playlist_includes_totals(self):
        """Test that retrieve includes total_duration and total_price"""
        response = self.client.get(f'/api/playlists/{self.playlist.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 180 + 240 = 420 seconds
        self.assertEqual(response.data['total_duration'], 420)
        # 3.99 + 4.99 = 8.98
        self.assertAlmostEqual(response.data['total_price'], 8.98, places=2)
    
    def test_update_playlist_name(self):
        """Test updating playlist name"""
        data = {
            'name': 'Updated Playlist',
            'song_ids': [self.song1.id]
        }
        response = self.client.put(f'/api/playlists/{self.playlist.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Playlist')
    
    def test_update_playlist_songs(self):
        """Test updating playlist songs"""
        new_song = Song.objects.create(
            title='New Song',
            length=150,
            date_released=self.now,
            price=Decimal('2.99')
        )
        data = {
            'name': 'My Playlist',
            'song_ids': [self.song1.id, new_song.id]
        }
        response = self.client.put(f'/api/playlists/{self.playlist.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['songs']), 2)
    
    def test_partial_update_playlist(self):
        """Test partial updating a playlist (PATCH)"""
        data = {'name': 'Partially Updated'}
        response = self.client.patch(f'/api/playlists/{self.playlist.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated')
    
    def test_delete_playlist(self):
        """Test deleting a playlist"""
        response = self.client.delete(f'/api/playlists/{self.playlist.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Playlist.objects.count(), 0)
    
    def test_retrieve_nonexistent_playlist(self):
        """Test retrieving a non-existent playlist"""
        response = self.client.get('/api/playlists/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PlaylistShuffleTests(APITestCase):
    """Test cases for playlist shuffle endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
        self.songs = []
        for i in range(5):
            song = Song.objects.create(
                title=f'Song {i+1}',
                length=180 + (i * 20),
                date_released=self.now,
                price=Decimal('3.99')
            )
            self.songs.append(song)
        
        self.playlist = Playlist.objects.create(name='Shuffle Playlist')
        self.playlist.songs.set(self.songs)
    
    def test_shuffle_playlist(self):
        """Test shuffling a playlist"""
        response = self.client.post(f'/api/playlists/{self.playlist.id}/shuffle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('playlist', response.data)
    
    def test_shuffle_returns_playlist_data(self):
        """Test that shuffle returns updated playlist"""
        response = self.client.post(f'/api/playlists/{self.playlist.id}/shuffle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['playlist']['songs']), 5)
    
    def test_shuffle_playlist_with_single_song(self):
        """Test shuffling playlist with only one song"""
        single_song_playlist = Playlist.objects.create(name='Single Song Playlist')
        single_song_playlist.songs.add(self.songs[0])
        
        response = self.client.post(f'/api/playlists/{single_song_playlist.id}/shuffle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_shuffle_empty_playlist(self):
        """Test shuffling an empty playlist"""
        empty_playlist = Playlist.objects.create(name='Empty Playlist')
        
        response = self.client.post(f'/api/playlists/{empty_playlist.id}/shuffle/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_shuffle_nonexistent_playlist(self):
        """Test shuffling a non-existent playlist"""
        response = self.client.post('/api/playlists/9999/shuffle/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_shuffle_preserves_all_songs(self):
        """Test that shuffle preserves all songs in playlist"""
        song_ids_before = set(self.playlist.songs.values_list('id', flat=True))
        
        self.client.post(f'/api/playlists/{self.playlist.id}/shuffle/')
        
        self.playlist.refresh_from_db()
        song_ids_after = set(self.playlist.songs.values_list('id', flat=True))
        
        self.assertEqual(song_ids_before, song_ids_after)
