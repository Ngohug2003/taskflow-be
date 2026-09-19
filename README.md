# Task Flow Manager — Backend (FastAPI)

Chạy hoàn toàn trong **Docker**. FE chạy local riêng.

## Cấu trúc BE

```
be/
├── app/
│   ├── commands/       # CLI / seeder
│   ├── constants/      # Config, database session
│   ├── controllers/    # Business logic
│   ├── middlewares/    # Auth dependency
│   ├── migrations/     # Alembic (env.py, versions/)
│   ├── models/         # SQLAlchemy ORM
│   ├── public/         # Static files
│   ├── repositories/   # Data access layer
│   ├── routes/         # FastAPI routers
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Payment, email, external APIs
│   ├── tasks/          # Background tasks
│   ├── utils/          # security, helpers
│   ├── zlogs/          # Log files
│   └── main.py
├── docker-compose.yml
├── docker-compose-migrate.yml
├── Dockerfile
├── deploy.sh
├── alembic.ini
├── requirements.txt
└── .env.example
```

## Yêu cầu

- Ubuntu server (hoặc WSL2)
- Docker + Docker Compose v2

## Khởi động

```bash
cd be/

# Lần đầu: tạo .env
cp .env.example .env

# Khởi động BE + DB
./deploy.sh up

# Chạy migration
./deploy.sh migrate
```

## URLs

| Service   | URL                          |
|-----------|------------------------------|
| API       | http://localhost:8000        |
| Swagger   | http://localhost:8000/docs   |
| ReDoc     | http://localhost:8000/redoc  |
| Health    | http://localhost:8000/health |
| DB port   | localhost:5432               |

## Lệnh thường dùng

```bash
./deploy.sh up                        # Khởi động
./deploy.sh down                      # Dừng
./deploy.sh logs                      # Log BE
./deploy.sh logs db                   # Log DB
./deploy.sh shell                     # Vào bash container BE
./deploy.sh migrate                   # Chạy migration
./deploy.sh migrate-make "ten_table"  # Tạo migration mới
./deploy.sh reset-db                  # Xoá sạch DB và migrate lại
./deploy.sh restart                   # Restart BE
```

## Kết nối từ FE/Admin (máy khác)

Nếu BE chạy trên server Ubuntu có IP `192.168.1.x`, set trong FE/Admin:

```env
# fe/.env.local
NEXT_PUBLIC_API_URL=http://192.168.1.x:8000/api/v1

# admin/.env
VITE_API_URL=http://192.168.1.x:8000/api/v1
```

## Thêm model mới

```bash
# 1. Tạo be/app/models/ten_model.py
# 2. Import vào be/app/models/__init__.py
# 3. Tạo + apply migration
./deploy.sh migrate-make "add_ten_model_table"
./deploy.sh migrate
```

## API Endpoints hiện có

```
GET  /health                  — Health check
POST /api/v1/auth/login       — Đăng nhập → JWT token
POST /api/v1/users            — Đăng ký user mới
GET  /api/v1/users/me         — Thông tin user hiện tại (cần token)
GET  /api/v1/users/{id}       — Lấy user theo ID
```