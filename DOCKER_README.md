# Dockerized Django Blog Application

This Django blog application is now fully Dockerized with PostgreSQL database, including health checks and proper service orchestration.

## 🏗️ Architecture

The application consists of two main services:

- **Web Service**: Django application running on Gunicorn (port 8000)
- **Database Service**: PostgreSQL 15 database (port 5432)

## 📁 Project Structure

```
blog-penny/
├── src/                    # Django application source code
├── docker/
│   ├── entrypoint.sh      # Container startup script
│   └── postgres/
│       └── init.sql       # PostgreSQL initialization script
├── .env                   # Development environment variables
├── .env.production       # Production environment variables
├── .dockerignore         # Docker ignore patterns
├── docker-compose.yml    # Service orchestration
├── Dockerfile           # Django application container
└── requirements.txt     # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Development Setup

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/blog-penny
   ```

2. **Start the services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Django App: http://localhost:8000
   - Django Admin: http://localhost:8000/admin
   - PostgreSQL: localhost:5432

### Production Setup

1. **Use production environment**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
   ```

## 🔧 Configuration

### Environment Variables

#### Development (.env)
```bash
DEBUG=1
SECRET_KEY=django-insecure-development-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,web
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

#### Production (.env.production)
```bash
DEBUG=0
SECRET_KEY=your-production-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=secure-production-password
DB_HOST=db
DB_PORT=5432
```

### Database Configuration

The PostgreSQL service uses:
- **Image**: `postgres:15-alpine`
- **Database**: `blog_db`
- **User**: `postgres`
- **Password**: `postgres`
- **Port**: `5432`
- **Data Persistence**: Docker volume `postgres_data`

## 🛠️ Development Workflow

### Common Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build

# Run Django management commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate

# Database access
docker-compose exec db psql -U postgres -d blog_db
```

### Running Tests

```bash
# Run Django tests
docker-compose exec web python manage.py test

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

## 🏥 Health Checks

Both services include health checks:

- **Database**: `pg_isready -U postgres`
- **Web**: HTTP check to `http://localhost:8000/`

Services will wait for dependencies to be healthy before starting.

## 📦 Volumes and Data Persistence

- **postgres_data**: PostgreSQL database files
- **static_volume**: Django static files
- **media_volume**: User uploaded media files
- **.**: Source code (mounted for development)

## 🔒 Security Notes

⚠️ **Important**: Before production deployment:

1. **Change all default passwords**
2. **Update SECRET_KEY with a secure random value**
3. **Configure proper ALLOWED_HOSTS**
4. **Set DEBUG=0**
5. **Use environment-specific .env files**
6. **Consider using Docker secrets for sensitive data**

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   docker-compose down
   sudo lsof -i :8000  # Check what's using port 8000
   sudo lsof -i :5432  # Check what's using port 5432
   ```

2. **Database connection errors**:
   ```bash
   # Check database service status
   docker-compose ps db
   
   # View database logs
   docker-compose logs db
   ```

3. **Permission issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

4. **Build failures**:
   ```bash
   # Clean build and restart
   docker-compose down --volumes --remove-orphans
   docker system prune -a
   docker-compose up --build
   ```

### Debug Mode

To enable debug mode in the container:
```bash
docker-compose exec web bash
# Now you can run any Django command interactively
```

## 🔄 Updates and Maintenance

### Updating Dependencies

1. **Update requirements.txt**
2. **Rebuild the image**:
   ```bash
   docker-compose up --build
   ```

### Database Migrations

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Backup and Restore

```bash
# Backup database
docker-compose exec db pg_dump -U postgres blog_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres blog_db < backup.sql
```

## 🌐 Production Deployment

For production deployment:

1. **Use a reverse proxy** (Nginx)
2. **Enable HTTPS** (Let's Encrypt)
3. **Use environment variables** for all sensitive data
4. **Implement logging and monitoring**
5. **Set up automated backups**
6. **Use multi-stage builds for optimization**
7. **Consider using a managed database service**

## 📊 Performance Optimization

- **Gunicorn workers**: Currently 3 workers, 2 threads each
- **Static files**: Served via WhiteNoise in production
- **Database**: Optimized PostgreSQL with proper indexing
- **Container**: Multi-stage build for smaller image size

## 🔍 Monitoring

To monitor the services:

```bash
# View resource usage
docker stats

# Check service health
docker-compose ps

# View detailed logs
docker-compose logs --details web
docker-compose logs --details db