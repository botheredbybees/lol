# Django Docker Development Environment

A complete Django development environment using Docker Compose with MySQL database, phpMyAdmin interface, and Nginx reverse proxy.

## What's Included

- **Django 4.2+** - Python web framework with user authentication
- **MySQL 8.0** - Database server
- **phpMyAdmin** - Web-based MySQL administration
- **Nginx** - Reverse proxy and web server
- **Django REST Framework** - API development
- **Django Allauth** - User registration and authentication

## Quick Start

1. **Clone and setup**
   ```bash
   git clone <your-repo-url>
   cd lol
   cp .env.example .env
   ```

2. **Edit environment variables**
   Open `.env` and update the database credentials and Django secret key:
   ```bash
   DJANGO_SECRET_KEY=your-very-secret-key-here
   MYSQL_DATABASE=myapp_db
   MYSQL_USER=myapp_user
   MYSQL_PASSWORD=secure_password
   MYSQL_ROOT_PASSWORD=root_secure_password
   ```

3. **Start the development environment**
   ```bash
   docker-compose up --build
   ```

4. **Run Django migrations** (in a new terminal)
   ```bash
   docker-compose exec django python manage.py migrate
   docker-compose exec django python manage.py createsuperuser
   ```

## Access Your Application

- **Main Django App**: http://localhost
- **Django Admin**: http://localhost/admin
- **phpMyAdmin**: http://localhost:8088
- **Direct Django (development)**: http://localhost:8008
- **MySQL Database**: localhost:3307

## Project Structure

```
lol/
├── django/                    # Django application code
│   ├── Dockerfile            # Django container configuration
│   ├── lol/                  # Django project directory
│   │   ├── __init__.py
│   │   ├── settings.py       # Django configuration
│   │   ├── urls.py          # URL routing
│   │   └── wsgi.py          # WSGI application
│   ├── manage.py            # Django management script
│   └── requirements.txt     # Python dependencies
├── docker-compose.yml       # Multi-container configuration
├── .env.example            # Environment variables template
├── .env                    # Your actual environment variables (create this)
├── .gitignore             # Git ignore rules
└── nginx.conf             # Nginx configuration
```

## Development Workflow

### Making Changes to Django Code
- Edit files in the `django/` directory
- Changes are automatically reflected (volume mounted)
- For new dependencies, add to `requirements.txt` and rebuild: `docker-compose up --build`

### Database Management
- **View/edit data**: Use phpMyAdmin at http://localhost:8088
- **Run migrations**: `docker-compose exec django python manage.py migrate`
- **Create apps**: `docker-compose exec django python manage.py startapp myapp`

### Common Docker Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs django

# Stop services
docker-compose down

# Rebuild containers
docker-compose up --build

# Access Django shell
docker-compose exec django python manage.py shell

# Run Django commands
docker-compose exec django python manage.py <command>
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key (change this!) | `fallback_secret_key` |
| `DJANGO_DEBUG` | Enable debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Allowed hostnames | `localhost 127.0.0.1 django nginx` |
| `MYSQL_DATABASE` | Database name | `mydatabase` |
| `MYSQL_USER` | Database user | `myuser` |
| `MYSQL_PASSWORD` | Database password | `mypassword` |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | `rootpassword` |

## Features Included

### User Authentication
- User registration and login (via Django Allauth)
- Password reset functionality
- Admin interface for user management

### API Development
- Django REST Framework installed
- Ready for API endpoint creation
- Automatic API documentation available

### Development Tools
- Hot reloading for Django code changes
- Database administration via phpMyAdmin
- Nginx reverse proxy for production-like setup

## Troubleshooting

### Port 80 Already in Use
If you get a port conflict error:
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop Apache if it's running
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### Other Port Conflicts
This setup uses non-standard ports to avoid common conflicts:
- **MySQL**: Port 3307 (instead of 3306)
- **Django direct access**: Port 8008 (instead of 8000)

If you still have conflicts, you can modify the ports in `docker-compose.yml`

### Database Connection Issues
- Ensure your `.env` file has the correct database credentials
- Check if MySQL container is running: `docker-compose ps`
- View MySQL logs: `docker-compose logs db`

### Django Static Files
```bash
# Collect static files
docker-compose exec django python manage.py collectstatic
```

## Next Steps

1. Create your first Django app: `docker-compose exec django python manage.py startapp myapp`
2. Add your app to `INSTALLED_APPS` in `settings.py`
3. Create your models and run migrations
4. Build your views and templates
5. Set up API endpoints using Django REST Framework

## Production Deployment

This setup is for development. For production:
- Set `DJANGO_DEBUG=False`
- Use a proper secret key
- Configure proper database credentials
- Set up SSL/HTTPS
- Use a production-grade database server
- Configure proper logging
