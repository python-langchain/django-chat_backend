# Django Chat Backend

A real-time chat application backend built with Django, Django REST Framework, and Django Channels. This project provides REST API endpoints for chat management and WebSocket support for real-time messaging.

## Features

- **User Authentication**: JWT-based authentication system
- **One-to-One Chats**: Create and manage private conversations between users
- **Real-time Messaging**: WebSocket support for instant message delivery
- **REST API**: Complete API for chat operations
- **Message History**: Paginated message retrieval with metadata support
- **PostgreSQL Database**: Robust data storage with optimized indexes
- **Redis Integration**: For WebSocket channel layers and caching

## Tech Stack

- **Backend Framework**: Django 5.x
- **API Framework**: Django REST Framework
- **Real-time Communication**: Django Channels
- **Database**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Authentication**: JWT (Simple JWT)
- **Containerization**: Docker & Docker Compose

## Project Structure

```
chat_backend/
├── chat/                   # Main chat application
│   ├── models.py          # Chat and Message models
│   ├── views.py           # REST API endpoints
│   ├── serializers.py     # DRF serializers
│   ├── consumers.py       # WebSocket consumers
│   ├── urls.py            # HTTP URL routing
│   ├── routing.py         # WebSocket URL routing
│   ├── utils.py           # Utility functions
│   ├── pagination.py      # Custom pagination classes
│   └── migrations/        # Database migrations
├── users/                 # User management application
├── chat_backend/          # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URL configuration
│   ├── asgi.py            # ASGI application
│   └── routing.py         # WebSocket routing
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker services configuration
└── manage.py             # Django management script
```

## API Endpoints

### Authentication
- `POST /auth/login/` - User login
- `POST /auth/register/` - User registration
- `POST /auth/refresh/` - Refresh JWT token

### Chat Management
- `POST /api/chat/start/` - Start a new chat with another user
- `GET /api/chat/chats/` - List all chats for authenticated user
- `GET /api/chat/chats/{chat_id}/messages/` - Get paginated messages from a chat
- `POST /api/chat/chats/{chat_id}/messages/` - Send a new message to a chat

### WebSocket Endpoints
- `ws://localhost:8000/ws/chats/{chat_id}/?token={jwt_token}` - Real-time chat connection

## Installation & Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chat_backend
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Local Development Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

4. **Start PostgreSQL and Redis**
   ```bash
   # Using Docker
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=chat_db -e POSTGRES_USER=chat_backend -e POSTGRES_PASSWORD=supersecret_backend_chat_yo123 postgres:13
   docker run -d --name redis -p 6379:6379 redis:7
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `1` |
| `SECRET_KEY` | Django secret key | Required |
| `ALLOWED_HOSTS` | Allowed host names | `*` |
| `POSTGRES_USER` | PostgreSQL username | `chat_backend` |
| `POSTGRES_PASSWORD` | PostgreSQL password | Required |
| `POSTGRES_DB` | PostgreSQL database name | `chat_db` |
| `REDIS_PASSWORD` | Redis password | Required |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/1` |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | Required |

## Usage Examples

### Starting a Chat
```bash
curl -X POST http://localhost:8000/api/chat/start/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

### Sending a Message
```bash
curl -X POST http://localhost:8000/api/chat/chats/1/messages/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello there!", "metadata": {"type": "text"}}'
```

### WebSocket Connection (JavaScript)
```javascript
const token = 'YOUR_JWT_TOKEN';
const chatId = 1;
const ws = new WebSocket(`ws://localhost:8000/ws/chats/${chatId}/?token=${token}`);

// Send a message
ws.send(JSON.stringify({
  type: 'message.send',
  content: 'Hello from WebSocket!',
  metadata: {}
}));

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};
```

## Database Schema

### Chat Model
- `id`: Primary key
- `pair_key`: Unique identifier for user pair (SHA256 hash)
- `participants`: Many-to-many relationship with User model
- `created_at`: Creation timestamp
- `updated_at`: Last activity timestamp

### Message Model
- `id`: Primary key
- `chat`: Foreign key to Chat
- `sender`: Foreign key to User
- `content`: Message text content
- `metadata`: JSON field for additional data
- `created_at`: Creation timestamp

## Performance Optimizations

- **Database Indexes**: Optimized queries with composite indexes on frequently queried fields
- **Pagination**: Built-in pagination for message history
- **Connection Pooling**: Efficient database connection management
- **Redis Caching**: Fast message broadcasting through Redis channels
- **Query Optimization**: Select_related and prefetch_related for efficient data loading

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **CORS Configuration**: Configurable cross-origin resource sharing
- **User Validation**: Participant verification for chat access
- **Input Sanitization**: Proper data validation and serialization
- **WebSocket Authentication**: Token-based WebSocket connection security

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test chat
python manage.py test users

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Production Deployment

1. **Set production environment variables**
   ```bash
   DEBUG=0
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com
   ```

2. **Configure production database and Redis**

3. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

4. **Use production WSGI/ASGI server**
   ```bash
   # Example with Gunicorn and Uvicorn
   gunicorn chat_backend.wsgi:application
   uvicorn chat_backend.asgi:application
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue in the GitHub repository or contact the development team.

---

**Note**: This is a development setup. For production deployment, ensure proper security configurations, use environment-specific settings, and follow Django production deployment best practices.