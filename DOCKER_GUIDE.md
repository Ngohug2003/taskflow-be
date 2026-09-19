# Hướng dẫn quản trị dự án bằng lệnh Docker (Manual Commands)

Tài liệu này tổng hợp các lệnh Docker trực tiếp để vận hành API, quản lý Database và Migrations.

## 1. Quản lý ứng dụng (API & Database)

| Thao tác | Lệnh | Mô tả |
|----------|------|-------|
| **Khởi động** | `docker compose up -d --build` | Build và chạy API + DB dưới nền. |
| **Dừng** | `docker compose down` | Dừng và gỡ bỏ các container. |
| **Dừng (giữ container)** | `docker compose stop` | Chỉ dừng các dịch vụ, không gỡ bỏ. |
| **Xem log API** | `docker compose logs -f be` | Xem log trực tiếp từ ứng dụng API. |
| **Xem log DB** | `docker compose logs -f db` | Xem log từ cơ sở dữ liệu. |
| **Kiểm tra trạng thái** | `docker compose ps` | Xem các container đang chạy hay dừng. |

## 2. Quản lý Cơ sở dữ liệu (Alembic Migrations)

Mọi lệnh migration đều được thực hiện thông qua container của ứng dụng API (`be`).

### 2.1. Cập nhật cấu trúc Database (Upgrade)
Dùng để tạo các bảng hoặc cập nhật thay đổi mới nhất vào DB:
```bash
docker compose exec be alembic upgrade head
```

### 2.2. Tạo file Migration mới
Khi bạn thay đổi code trong thư mục `app/models`, chạy lệnh này để Alembic tự tạo file quản lý thay đổi:
```bash
docker compose exec be alembic revision --autogenerate -m "mo_ta_thay_doi"
```
*Lưu ý: Sau khi tạo xong, bạn vẫn phải chạy lệnh **Upgrade** (mục 2.1) để áp dụng vào database.*

### 2.3. Quay lại phiên bản trước (Downgrade)
Nếu muốn hủy bỏ lần cập nhật cấu trúc gần nhất:
```bash
docker compose exec be alembic downgrade -1
```

## 3. Các lệnh hữu ích khác

*   **Truy cập terminal bên trong container**:
    ```bash
    docker compose exec be bash
    ```
*   **Xóa sạch Database và Volume (Làm lại từ đầu)**:
    ```bash
    docker compose down -v
    ```
*   **Kết nối DB từ DBeaver**:
    *   **Host**: `localhost`
    *   **Port**: `5432`
    *   **User/Pass/DB**: Lấy thông tin từ file `.env`
