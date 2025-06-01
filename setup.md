# Django Docker Development Environment

A complete Django development environment using Docker Compose with MySQL database, phpMyAdmin interface, and Nginx reverse proxy.

## Features

- Django 4.2+ - Python web framework with user authentication
- MySQL 8.0 - Database server
- phpMyAdmin - Web-based MySQL administration
- Nginx - Reverse proxy and web server
- Django REST Framework - API development
- Django Allauth - User registration and authentication

## Quick Start

### Clone and setup
```bash
git clone <your-repo-url>
cd lol
cp .env.example .env
```

### Edit environment variables
Open `.env` and update the database credentials and Django secret key:
```env
DJANGO_SECRET_KEY=your-very-secret-key-here
MYSQL_DATABASE=learnonline
MYSQL_USER=myapp_user
MYSQL_PASSWORD=secure_password
MYSQL_ROOT_PASSWORD=root_secure_password
```

### Start the development environment
```bash
docker-compose up --build
```

### Complete the database setup
**Important:** After starting the containers for the first time, you need to set up the database:

```bash
# 1. Run Django migrations to create database tables
docker-compose exec django python manage.py migrate

# 2. Collect static files for proper admin styling
docker-compose exec django python manage.py collectstatic --noinput

# 3. Create a superuser account
docker-compose exec django python manage.py createsuperuser
```

## Access Points

- **Main Django App:** [http://localhost](http://localhost)
- **Django Admin:** [http://localhost/admin](http://localhost/admin)
- **phpMyAdmin:** [http://localhost:8088](http://localhost:8088)
- **Direct Django (development):** [http://localhost:8008](http://localhost:8008)
- **MySQL Database:** localhost:3307

## Project Structure

```
lol/
├── django/                 # Django application code
│   ├── Dockerfile         # Django container configuration
│   ├── lol/              # Django project directory
│   │   ├── __init__.py
│   │   ├── settings.py   # Django configuration
│   │   ├── urls.py       # URL routing
│   │   └── wsgi.py       # WSGI application
│   ├── manage.py         # Django management script
│   └── requirements.txt  # Python dependencies
├── docker-compose.yml    # Multi-container configuration
├── .env.example         # Environment variables template
├── .env                 # Your actual environment variables (create this)
├── .gitignore          # Git ignore rules
└── nginx.conf          # Nginx configuration
```

## Development Workflow

- Edit files in the `django/` directory
- Changes are automatically reflected (volume mounted)
- For new dependencies, add to `requirements.txt` and rebuild: `docker-compose up --build`
- View/edit data: Use phpMyAdmin at [http://localhost:8088](http://localhost:8088)
- Run migrations: `docker-compose exec django python manage.py migrate`
- Create apps: `docker-compose exec django python manage.py startapp myapp`

## Common Commands

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

## Built-in Features

- User registration and login (via Django Allauth)
- Password reset functionality
- Admin interface for user management
- Django REST Framework installed
- Ready for API endpoint creation
- Automatic API documentation available

## Development Features

- Hot reloading for Django code changes
- Database administration via phpMyAdmin
- Nginx reverse proxy for production-like setup

## Troubleshooting

### Port Conflicts
If you get a port conflict error:
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop Apache if it's running
sudo systemctl stop apache2
sudo systemctl disable apache2
```

This setup uses non-standard ports to avoid common conflicts:
- MySQL: Port 3307 (instead of 3306)
- Django direct access: Port 8008 (instead of 8000)

If you still have conflicts, you can modify the ports in `docker-compose.yml`

### Database Connection Issues
- Ensure your `.env` file has the correct database credentials
- Check if MySQL container is running: `docker-compose ps`
- View MySQL logs: `docker-compose logs db`
- If database container keeps restarting, reset the database volume:
  ```bash
  docker-compose down
  docker volume rm django_mysql_data  # or your volume name
  docker-compose up -d
  ```

### Admin Interface Styling Issues
If the Django admin looks unstyled, collect static files:
```bash
docker-compose exec django python manage.py collectstatic --noinput
```

### Fresh Database Setup
If you need to completely reset your database:
```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm django_mysql_data

# Start fresh
docker-compose up -d

# Wait for database to initialize, then run setup
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py collectstatic --noinput
docker-compose exec django python manage.py createsuperuser
```

## Next Steps

```bash
# Collect static files
docker-compose exec django python manage.py collectstatic
```

- Create your first Django app:
  ```bash
  docker-compose exec django python manage.py startapp myapp
  ```
- Add your app to `INSTALLED_APPS` in `settings.py`
- Create your models and run migrations
- Build your views and templates
- Set up API endpoints using Django REST Framework

## Production Notes

This setup is for development. For production:

- Set `DJANGO_DEBUG=False`
- Use a proper secret key
- Configure proper database credentials
- Set up SSL/HTTPS
- Use a production-grade database server
- Configure proper logging