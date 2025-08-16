# Secure Dating App Backend

A modular Django backend for a secure dating application with facial verification, real-time chat, and comprehensive matching system.

## Features

### 🔐 Authentication & Security
- **Clerk Integration**: Seamless authentication with Clerk
- **Facial Verification**: 3-image login verification to prevent catfishing
- **Image Similarity Checking**: Profile photos verified against login images
- **PostgreSQL with pgvector**: Efficient similarity search using embeddings

### 👤 Profile Management
- **Rich Profiles**: 5 photos max, bio, interests, prompt answers
- **Image Verification**: All profile photos verified against login embeddings
- **Prompt System**: Customizable questions and answers

### 💕 Matching System
- **Swipe Mechanics**: Like/dislike with mutual match detection
- **Smart Filtering**: Exclude already swiped users
- **Match Management**: Track and manage user matches

### 💬 Real-time Chat
- **Private Messaging**: 1-to-1 chat between matched users
- **Group Chatrooms**: Multi-user chat with liked users
- **Female-First Messaging**: Only female users can initiate conversations
- **WebSocket Support**: Real-time messaging with Django Channels

### 🛡️ Moderation
- **User Reporting**: Comprehensive reporting system
- **Blocking System**: User-level blocking functionality
- **Admin Controls**: Ban/unban users with expiration dates

## Architecture

### Apps Structure
```
├── core/           # Shared utilities, base models, constants
├── accounts/       # Clerk auth, user management, verification
├── profiles/       # Profile creation, photo verification
├── matching/       # Swipe logic, match detection
├── chat/          # Messaging, WebSocket consumers
└── moderation/    # Reporting, blocking, banning
```

### Technology Stack
- **Backend**: Django 5.2.5 (without DRF)
- **Database**: PostgreSQL with pgvector extension
- **Real-time**: Django Channels + Redis
- **Image Processing**: PIL, NumPy
- **Authentication**: Clerk integration

## Setup Instructions

### 1. Prerequisites
```bash
# Install PostgreSQL and Redis
sudo apt-get install postgresql postgresql-contrib redis-server

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Start PostgreSQL
sudo service postgresql start

# Run setup script
sudo -u postgres psql -f setup_postgres.sql
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 4. Django Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### 5. Redis Setup (for WebSockets)
```bash
# Start Redis server
redis-server

# Test Redis connection
redis-cli ping
```

## API Endpoints

### Authentication
- `POST /api/accounts/clerk-webhook/` - Clerk webhook handler
- `POST /api/accounts/login-verification/` - Upload verification images
- `GET /api/accounts/profile/` - Get user profile
- `POST /api/accounts/logout/` - Logout user

### Profiles
- `GET /api/profiles/` - Get current user profile
- `POST /api/profiles/update/` - Update profile
- `POST /api/profiles/upload-photos/` - Upload profile photos
- `POST /api/profiles/prompt-answers/` - Save prompt answers
- `GET /api/profiles/questions/` - Get prompt questions
- `GET /api/profiles/<user_id>/` - Get another user's profile

### Matching
- `POST /api/matching/swipe/` - Swipe on user
- `GET /api/matching/potential/` - Get potential matches
- `GET /api/matching/matches/` - Get user matches
- `GET /api/matching/liked/` - Get liked users

### Chat
- `POST /api/chat/send/` - Send message
- `GET /api/chat/rooms/` - Get chat rooms
- `GET /api/chat/rooms/<id>/messages/` - Get chat messages
- `POST /api/chat/create-private/` - Create private chat

### Moderation
- `POST /api/moderation/report/` - Report user
- `POST /api/moderation/block/` - Block user
- `POST /api/moderation/unblock/` - Unblock user
- `GET /api/moderation/blocked/` - Get blocked users

## WebSocket Endpoints

### Real-time Chat
```javascript
// Connect to chat room
const socket = new WebSocket('ws://localhost:8000/ws/chat/ROOM_ID/');

// Send message
socket.send(JSON.stringify({
    'type': 'message',
    'content': 'Hello!'
}));
```

## Image Verification Flow

### 1. Login Verification
```python
# User captures 3 images during login
images = ['base64_image_1', 'base64_image_2', 'base64_image_3']

# Generate embeddings and store
embeddings = [generate_face_embedding(img) for img in images]
user.login_embeddings = embeddings
```

### 2. Profile Photo Verification
```python
# When uploading profile photos
new_embedding = generate_face_embedding(profile_photo)
is_valid = validate_image_similarity([new_embedding], user.login_embeddings)

if not is_valid:
    raise ValueError("Photo doesn't match verification images")
```

## Security Features

### Image Verification
- Facial embeddings stored as 512-dimensional vectors
- Cosine similarity threshold of 0.8 for verification
- All profile photos must match login verification images

### User Privacy
- Blocked users cannot see each other's profiles
- Only matched users can message each other
- Female-first messaging policy

### Data Protection
- Secure password handling with Django's built-in system
- CSRF protection on all POST endpoints
- Input validation and sanitization

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Format code
ruff format .

# Lint code
ruff check .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Production Deployment

### Environment Variables
```bash
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
```

### Static Files
```bash
python manage.py collectstatic
```

### ASGI Server
```bash
# Using Daphne
daphne -b 0.0.0.0 -p 8000 profile_guard.asgi:application

# Using Uvicorn
uvicorn profile_guard.asgi:application --host 0.0.0.0 --port 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.