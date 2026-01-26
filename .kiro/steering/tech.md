# Technology Stack

## Backend

- **Framework**: FastAPI (async web framework)
- **Language**: Python 3.11+
- **ORM**: Tortoise ORM (async)
- **Database**: MySQL 8.0 (supports master-slave read-write splitting)
- **Cache/Queue**: Redis 7.0
- **Authentication**: JWT (python-jose), bcrypt for password hashing
- **Task Scheduling**: APScheduler
- **Logging**: Custom system with module-based classification and auto-rotation
- **Email Integration**: Outlook API
- **Testing**: pytest, pytest-asyncio

### Key Backend Libraries

```
fastapi, tortoise-orm, uvicorn, aiomysql, aioredis, redis
python-jose[cryptography], passlib, bcrypt
APScheduler, loguru, httpx, aiohttp
```

## Frontend

- **Framework**: React 18
- **Language**: TypeScript 5
- **UI Library**: Ant Design 5
- **Router**: React Router v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Build Tool**: Vite 5
- **Date Handling**: dayjs
- **Styling**: Less + CSS Modules
- **Security**: DOMPurify for HTML sanitization
- **Deployment**: Docker (multi-stage build) + Nginx

## Deployment & Infrastructure

### Docker

- **Frontend Container**: Nginx Alpine (~30MB)
  - Multi-stage build (Node.js build → Nginx serve)
  - Only contains static files in production
  - Fast startup and excellent performance
  
- **Backend Container**: Python 3.11 Slim (~500MB)
  - FastAPI application
  - All Python dependencies included
  
- **Queue Worker Container**: Python 3.11 Slim (~500MB)
  - Redis queue processor
  - Separate from HTTP service

### Container Orchestration

- **Docker Compose**: Service orchestration
- **Networks**: Bridge network for inter-container communication
- **Volumes**: Log persistence to host machine
- **Health Checks**: Automatic service health monitoring

## Common Commands

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python db/init_roles_and_admin.py

# Start development server
python start.py

# Start queue worker
python start_queue_worker.py

# Run tests
pytest

# Database migrations
aerich migrate --name "description"
aerich upgrade
```

### Frontend

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Docker

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove services
docker-compose down

# Initialize database (first time only)
docker-compose run --rm backend-api python deploy_init.py

# Execute command in container
docker-compose exec backend-api python check_deployment.py

# Scale queue workers
docker-compose up -d --scale queue-worker=3
```

## Environment Configuration

### Backend (.env)

```env
# Database (Master)
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# Database (Slaves - optional, comma-separated)
DB_SLAVE_HOSTS=127.0.0.1:3308,127.0.0.1:3309

# Redis (optional)
REDIS_HOST=127.0.0.1
REDIS_PORT=6378
REDIS_PASSWORD=redis_fNmAxZ
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_DAYS=365

# Server
HOST=0.0.0.0
PORT=6080
DEBUG=False
WORKERS=1

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env.development)

```env
VITE_API_BASE_URL=http://localhost:6080
VITE_APP_TITLE=QYD管理系统
```

## API Documentation

- Swagger UI: `http://localhost:6080/docs`
- ReDoc: `http://localhost:6080/redoc`

## Build System Notes

- Backend uses `uvicorn` for ASGI server
- Frontend uses Vite for fast HMR and optimized builds
- Database migrations managed by `aerich` (Tortoise ORM)
- Logs auto-rotate hourly and compress to `.gz` format
