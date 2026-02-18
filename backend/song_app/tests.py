from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import timedelta

from song_app.models import Song
from song_app.payment_gateways import (
    CheapPaymentGateway,
    ExpensivePaymentGateway,
    get_payment_gateway
)


class SongModelTests(TestCase):
    """Test cases for Song model"""
    
    def setUp(self):
        self.now = timezone.now()
        self.song1 = Song.objects.create(
            title='Test Song 1',
            length=180,
            date_released=self.now,
            price=Decimal('4.99')
        )
        self.song2 = Song.objects.create(
            title='Test Song 2',
            length=240,
            date_released=self.now - timedelta(days=1),
            price=Decimal('5.99')
        )
    
    def test_song_creation(self):
        """Test song creation with valid data"""
        self.assertEqual(self.song1.title, 'Test Song 1')
        self.assertEqual(self.song1.length, 180)
        self.assertEqual(self.song1.price, Decimal('4.99'))
    
    def test_song_string_representation(self):
        """Test song string representation"""
        expected = 'Test Song 1 - $4.99'
        self.assertEqual(str(self.song1), expected)
    
    def test_song_invalid_length(self):
        """Test that song length must be positive"""
        song = Song(
            title='Invalid Song',
            length=-100,
            date_released=self.now,
            price=Decimal('4.99')
        )
        with self.assertRaises(ValidationError):
            song.full_clean()
    
    def test_song_invalid_price(self):
        """Test that song price must be positive"""
        song = Song(
            title='Invalid Song',
            length=180,
            date_released=self.now,
            price=Decimal('-1.00')
        )
        with self.assertRaises(ValidationError):
            song.full_clean()
    
    def test_song_ordering(self):
        """Test that songs are ordered by created_at descending"""
        songs = Song.objects.all()
        self.assertEqual(songs[0].id, self.song2.id)  # Most recent first


class SongAPITests(APITestCase):
    """Test cases for Song API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
        self.song1 = Song.objects.create(
            title='Song 1',
            length=180,
            date_released=self.now,
            price=Decimal('4.99')
        )
        self.song2 = Song.objects.create(
            title='Song 2',
            length=240,
            date_released=self.now,
            price=Decimal('5.99')
        )
        self.song3 = Song.objects.create(
            title='Song 3',
            length=200,
            date_released=self.now,
            price=Decimal('8.99')
        )
    
    def test_list_songs(self):
        """Test listing all songs"""
        response = self.client.get('/api/songs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_create_song(self):
        """Test creating a new song"""
        data = {
            'title': 'New Song',
            'length': 300,
            'date_released': self.now.isoformat(),
            'price': '7.99'
        }
        response = self.client.post('/api/songs/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Song')
        self.assertEqual(Song.objects.count(), 4)
    
    def test_retrieve_song(self):
        """Test retrieving a specific song"""
        response = self.client.get(f'/api/songs/{self.song1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Song 1')
    
    def test_update_song(self):
        """Test updating a song (PUT)"""
        data = {
            'title': 'Updated Song',
            'length': 300,
            'date_released': self.now.isoformat(),
            'price': '7.99'
        }
        response = self.client.put(f'/api/songs/{self.song1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Song')
    
    def test_partial_update_song(self):
        """Test partial updating a song (PATCH)"""
        data = {'title': 'Partially Updated'}
        response = self.client.patch(f'/api/songs/{self.song1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Partially Updated')
    
    def test_delete_song(self):
        """Test deleting a song"""
        response = self.client.delete(f'/api/songs/{self.song1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Song.objects.count(), 2)
    
    def test_retrieve_nonexistent_song(self):
        """Test retrieving a non-existent song"""
        response = self.client.get('/api/songs/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PurchaseAPITests(APITestCase):
    """Test cases for purchase endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.now = timezone.now()
        # Create songs with different prices
        self.cheap_song1 = Song.objects.create(
            title='Cheap Song 1',
            length=180,
            date_released=self.now,
            price=Decimal('3.00')
        )
        self.cheap_song2 = Song.objects.create(
            title='Cheap Song 2',
            length=200,
            date_released=self.now,
            price=Decimal('4.00')
        )
        self.expensive_song = Song.objects.create(
            title='Expensive Song',
            length=240,
            date_released=self.now,
            price=Decimal('12.00')
        )
    
    def test_purchase_cheap_songs(self):
        """Test purchase with total < $10 uses CheapPaymentGateway"""
        # 3.00 + 4.00 = 7.00 < 10.00
        data = {
            'song_ids': [self.cheap_song1.id, self.cheap_song2.id]
        }
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['total_price'], 7.00)
        self.assertEqual(response.data['payment_info']['gateway'], 'CheapPaymentGateway')
    
    def test_purchase_expensive_songs(self):
        """Test purchase with total >= $10 uses ExpensivePaymentGateway"""
        # 3.00 + 4.00 + 12.00 = 19.00 >= 10.00
        data = {
            'song_ids': [self.cheap_song1.id, self.cheap_song2.id, self.expensive_song.id]
        }
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['total_price'], 19.00)
        self.assertEqual(response.data['payment_info']['gateway'], 'ExpensivePaymentGateway')
    
    def test_purchase_exactly_10_dollars(self):
        """Test purchase with total == $10 uses ExpensivePaymentGateway"""
        song1 = Song.objects.create(
            title='5 Dollar Song',
            length=180,
            date_released=self.now,
            price=Decimal('5.00')
        )
        song2 = Song.objects.create(
            title='5 Dollar Song 2',
            length=200,
            date_released=self.now,
            price=Decimal('5.00')
        )
        data = {'song_ids': [song1.id, song2.id]}
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], 10.00)
        self.assertEqual(response.data['payment_info']['gateway'], 'ExpensivePaymentGateway')
    
    def test_purchase_single_song(self):
        """Test purchasing a single song"""
        data = {'song_ids': [self.cheap_song1.id]}
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['total_price'], 3.00)
    
    def test_purchase_no_song_ids(self):
        """Test purchase without song_ids"""
        response = self.client.post('/api/songs/purchase/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_purchase_invalid_song_ids(self):
        """Test purchase with invalid song IDs"""
        data = {'song_ids': [9999, 8888]}
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_purchase_song_ids_not_list(self):
        """Test purchase with non-list song_ids"""
        data = {'song_ids': 'not-a-list'}
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_purchase_returns_song_details(self):
        """Test that purchase response includes song details"""
        data = {'song_ids': [self.cheap_song1.id]}
        response = self.client.post('/api/songs/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('songs_purchased', response.data)
        self.assertEqual(len(response.data['songs_purchased']), 1)
        self.assertEqual(response.data['songs_purchased'][0]['title'], 'Cheap Song 1')


class PaymentGatewayTests(TestCase):
    """Test cases for payment gateways"""
    
    def test_cheap_gateway_valid_amount(self):
        """Test CheapPaymentGateway with valid amount"""
        gateway = CheapPaymentGateway()
        result = gateway.process_payment(Decimal('9.99'), [1, 2])
        self.assertTrue(result['success'])
        self.assertEqual(result['gateway'], 'CheapPaymentGateway')
        self.assertEqual(result['amount'], 9.99)
    
    def test_cheap_gateway_too_high_amount(self):
        """Test CheapPaymentGateway rejects amount >= $10"""
        gateway = CheapPaymentGateway()
        with self.assertRaises(ValueError):
            gateway.process_payment(Decimal('10.00'), [1])
    
    def test_expensive_gateway_valid_amount(self):
        """Test ExpensivePaymentGateway with valid amount"""
        gateway = ExpensivePaymentGateway()
        result = gateway.process_payment(Decimal('10.00'), [1, 2])
        self.assertTrue(result['success'])
        self.assertEqual(result['gateway'], 'ExpensivePaymentGateway')
        self.assertEqual(result['amount'], 10.00)
    
    def test_expensive_gateway_too_low_amount(self):
        """Test ExpensivePaymentGateway rejects amount < $10"""
        gateway = ExpensivePaymentGateway()
        with self.assertRaises(ValueError):
            gateway.process_payment(Decimal('9.99'), [1])
    
    def test_get_payment_gateway_cheap(self):
        """Test gateway factory for cheap purchase"""
        gateway = get_payment_gateway(Decimal('5.00'))
        self.assertIsInstance(gateway, CheapPaymentGateway)
    
    def test_get_payment_gateway_expensive(self):
        """Test gateway factory for expensive purchase"""
        gateway = get_payment_gateway(Decimal('15.00'))
        self.assertIsInstance(gateway, ExpensivePaymentGateway)
    
    def test_get_payment_gateway_boundary(self):
        """Test gateway factory at boundary ($10)"""
        gateway = get_payment_gateway(Decimal('10.00'))
        self.assertIsInstance(gateway, ExpensivePaymentGateway)
    
    def test_transaction_id_uniqueness(self):
        """Test that each transaction gets a unique ID"""
        gateway = CheapPaymentGateway()
        result1 = gateway.process_payment(Decimal('5.00'), [1])
        result2 = gateway.process_payment(Decimal('5.00'), [2])
        self.assertNotEqual(result1['transaction_id'], result2['transaction_id'])
