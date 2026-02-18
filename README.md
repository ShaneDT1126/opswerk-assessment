# OpsWerk - Technical Assessment

A Django REST Framework API for managing songs, playlists, and handling song purchases with dynamic payment gateways.

## 📋 Overview

This project implements a backend API system featuring:
- Full CRUD operations for songs
- Dynamic payment gateway selection based on transaction amount
- Playlist management with shuffle functionality

### Key Features

✅ **Song Model**
- Title, Length (seconds), Release Date, Price
- Input validation (positive values)
- Timestamp tracking (created_at, updated_at)

✅ **Payment Gateway System**
- **CheapPaymentGateway**: For transactions < $10
- **ExpensivePaymentGateway**: For transactions ≥ $10
- Automatic gateway selection based on total amount

✅ **Playlist Model**
- Song management via many-to-many relationships
- Total duration calculation
- Total price calculation
- Song shuffling capability

✅ **Comprehensive Testing**
- 28 Song tests (CRUD, validation, purchase logic)
- 25 Playlist tests (CRUD, shuffle, calculations)
- 53 tests total, all passing

## 🚀 Project Setup

### Prerequisites
- Python 3.10+
- Django 6.0+
- Django REST Framework

### Installation

1. **Clone and navigate to the project**:
```bash
cd backend
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
```

3. **Install dependencies**:
```bash
pip install -r ../requirements.txt
```

4. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Run tests**:
```bash
python manage.py test song_app.tests playlist_app.tests -v 2
```

6. **Start development server**:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Endpoints

### Songs

**List all songs**: `GET /api/songs/`
- Pagination: 20 items per page
- Response: 200 OK with list of songs

**Create a song**: `POST /api/songs/`
```json
{
  "title": "Song Title",
  "length": 180,
  "date_released": "2024-02-18T10:00:00Z",
  "price": "4.99"
}
```
- Response: 201 Created

**Retrieve a song**: `GET /api/songs/{id}/`
- Response: 200 OK with song details

**Update a song**: `PUT /api/songs/{id}/`
- Response: 200 OK with updated song

**Partial update**: `PATCH /api/songs/{id}/`
- Response: 200 OK

**Delete a song**: `DELETE /api/songs/{id}/`
- Response: 204 No Content

### Purchase Songs

**Purchase endpoint**: `POST /api/songs/purchase/`

Request:
```json
{
  "song_ids": [1, 2, 3]
}
```

Response (Success - 200 OK):
```json
{
  "success": true,
  "message": "Purchase completed successfully",
  "total_price": 19.50,
  "songs_purchased": [
    {
      "id": 1,
      "title": "Song 1",
      "length": 180,
      "date_released": "2024-02-18T10:00:00Z",
      "price": "4.99"
    }
  ],
  "payment_info": {
    "success": true,
    "gateway": "ExpensivePaymentGateway",
    "amount": 19.50,
    "transaction_id": "EXP-...-1950",
    "status": "completed"
  }
}
```

**Gateway Selection Logic**:
- Total < $10 → CheapPaymentGateway
- Total ≥ $10 → ExpensivePaymentGateway

Error Responses:
- `400 Bad Request`: Missing or invalid song_ids
- `404 Not Found`: One or more songs not found
- `500 Internal Server Error`: Payment processing error

### Playlists

**List all playlists**: `GET /api/playlists/`
- Response: 200 OK with paginated list

**Create a playlist**: `POST /api/playlists/`
```json
{
  "name": "My Playlist",
  "song_ids": [1, 2, 3]
}
```
- Response: 201 Created

**Retrieve a playlist**: `GET /api/playlists/{id}/`
- Includes total_duration and total_price calculations
- Response: 200 OK

**Update a playlist**: `PUT /api/playlists/{id}/`
```json
{
  "name": "Updated Playlist",
  "song_ids": [1, 3, 5]
}
```
- Response: 200 OK

**Shuffle playlist**: `POST /api/playlists/{id}/shuffle/`
- Randomly reorders songs in the playlist
- Response: 200 OK with shuffled playlist data

**Delete a playlist**: `DELETE /api/playlists/{id}/`
- Response: 204 No Content

## 📊 Response Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH, POST (purchase) |
| 201 | Created | Successful POST (create) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |

## 🧪 Testing

The project includes comprehensive test coverage:

### Test Categories

1. **Song Model Tests** (5 tests)
   - Creation, validation, ordering

2. **Song API Tests** (10 tests)
   - CRUD operations, HTTP responses

3. **Purchase API Tests** (7 tests)
   - Cheap gateway (< $10)
   - Expensive gateway (≥ $10)
   - Error handling

4. **Payment Gateway Tests** (6 tests)
   - Amount validation
   - Transaction processing
   - Gateway selection logic

5. **Playlist Model Tests** (8 tests)
   - Creation, duration/price calculations
   - Song management

6. **Playlist API Tests** (9 tests)
   - CRUD operations
   - Shuffle functionality

7. **Playlist Shuffle Tests** (6 tests)
   - Shuffle logic, edge cases

Run all tests:
```bash
python manage.py test song_app.tests playlist_app.tests -v 2
```

Run specific test class:
```bash
python manage.py test song_app.tests.SongModelTests -v 2
```

## 📁 Project Structure

```
backend/
├── manage.py
├── db.sqlite3
├── opswerk_assessment/          # Main project config
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── song_app/                    # Songs app
│   ├── models.py                # Song model
│   ├── views.py                 # Song viewset with purchase logic
│   ├── serializers.py           # Song serializer
│   ├── payment_gateways.py      # Payment gateway implementations
│   ├── tests.py                 # Comprehensive tests
│   └── migrations/
├── playlist_app/                # Playlists app
│   ├── models.py                # Playlist model
│   ├── views.py                 # Playlist viewset
│   ├── serializers.py           # Playlist serializer
│   ├── tests.py                 # Playlist tests
│   └── migrations/
```

## 🔧 Technical Details

### Models

**Song**
```python
- Title (CharField, 255 chars)
- Length (IntegerField, positive)
- Date Released (DateTimeField)
- Price (DecimalField, 10 digits, 2 decimal places, positive)
- Created At (DateTimeField, auto)
- Updated At (DateTimeField, auto)
```

**Playlist**
```python
- Name (CharField, 255 chars)
- Songs (ManyToManyField to Song)
- Created At (DateTimeField, auto)
- Updated At (DateTimeField, auto)
- get_total_duration()  # Sum of all song lengths
- get_total_price()     # Sum of all song prices
```

### Payment Gateway Interface

```python
class PaymentGateway(ABC):
    def process_payment(self, amount: Decimal, song_ids: List[int]) -> dict
```

Both implementations return:
```json
{
  "success": true,
  "gateway": "GatewayName",
  "amount": 10.50,
  "transaction_id": "...",
  "status": "completed",
  "song_ids": [1, 2, 3]
}
```

## 📝 Code Examples

### Create a Song
```bash
curl -X POST http://localhost:8000/api/songs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "length": 354,
    "date_released": "1975-10-31T00:00:00Z",
    "price": "1.29"
  }'
```

### Purchase Songs
```bash
curl -X POST http://localhost:8000/api/songs/purchase/ \
  -H "Content-Type: application/json" \
  -d '{"song_ids": [1, 2]}'
```

### Create and Shuffle Playlist
```bash
# Create playlist
curl -X POST http://localhost:8000/api/playlists/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Favorites",
    "song_ids": [1, 2, 3, 4, 5]
  }'

# Shuffle it
curl -X POST http://localhost:8000/api/playlists/1/shuffle/ \
  -H "Content-Type: application/json"
```

## 🎯 Bonus Features Implemented

✅ **Playlist Model** with:
- Complete CRUD operations
- Song management (add/remove)
- Total duration calculation
- Total price calculation
- Shuffle functionality

✅ **Advanced Features**:
- Input validation (MOD decorators for constraints)
- Proper HTTP status codes
- Comprehensive error handling
- Pagination support
- Timestamp tracking

## 💾 Database

SQLite is used for development. For production, consider:
- PostgreSQL
- MySQL
- AWS RDS

## 🐛 Error Handling

All endpoints include comprehensive error handling with appropriate HTTP status codes:
- **400**: Invalid request data
- **404**: Resource not found
- **500**: Internal server error

## 📄 License

This project is part of a technical assessment.

## 🙏 Acknowledgments

Built with:
- Django 6.0+
- Django REST Framework
- Python 3.10+
