# hirenow-core-api

Django REST API backend for HireNow — **single app (core)** with controllers, models, services, serializers.

## Structure

```
hirenow-core-api/
├── config/                    # Django project (urls, wsgi, asgi)
├── core/                      # Single app
│   ├── controllers/           # API controllers
│   │   ├── AuthController.py
│   │   ├── UserController.py
│   │   ├── WorkerController.py
│   │   ├── ReviewController.py
│   │   └── CategoryController.py
│   ├── models/                # DB models
│   │   ├── User.py
│   │   ├── Worker.py
│   │   ├── Review.py
│   │   ├── Category.py
│   │   └── OTP.py
│   ├── services/              # Business logic
│   │   ├── AuthService.py
│   │   ├── OTPService.py
│   │   ├── DistanceService.py
│   │   └── UploadService.py
│   ├── serializers/
│   │   ├── UserSerializer.py
│   │   ├── WorkerSerializer.py
│   │   ├── ReviewSerializer.py
│   │   └── CategorySerializer.py
│   ├── settings/              # base, development, production
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
├── services/                 # Global services
│   ├── ResponseService.py
│   └── PermissionService.py
├── manage.py
├── requirements.txt
└── .env
```

## Setup

1. **Venv & install**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create MySQL database**
   ```sql
   CREATE DATABASE HireNow;
   ```

3. **Configure**  
   Edit `core/settings/development.py` for DB credentials (or use env in production).

4. **Migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run**
   ```bash
   python manage.py runserver
   ```

## API

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/login/` | Login (JWT + user) |
| `POST /api/auth/register/` | Register (JWT + user) |
| `GET /api/users/` | List users |
| `GET /api/users/<id>/` | User detail |
| `GET /api/workers/` | List workers (`?category=<id>`) |
| `GET /api/workers/nearby/?lat=&lng=&radius_km=` | Nearby workers |
| `GET /api/workers/<id>/` | Worker detail |
| `GET /api/categories/` | List categories |
| `GET /api/categories/<id>/` | Category detail |
| `GET /api/reviews/?worker_id=` | List reviews |
| `POST /api/reviews/` | Create review (auth) |
| `GET /api/reviews/<id>/` | Review detail |
| `PUT /api/reviews/<id>/` | Update review (owner) |
| `DELETE /api/reviews/<id>/` | Delete review (owner) |

All under `/api/` as requested.
