# Lộ trình Phát triển Tuần tự: Database & API — Task Flow Manager

> **Nguyên tắc cốt lõi**: Xây dựng tuần tự theo luồng nghiệp vụ thực tế. **Làm API đến đâu thì dựng bảng Database (Model + Migration) tương ứng đến đó**. Không tạo bảng tràn lan trước khi có API phục vụ.

---

## 🗺️ Bản đồ các Phase phát triển (Tuần tự từ 1 → 7)

```text
[Phase 1: Auth & User]  ✅ ĐÃ XONG
       │
       ▼
[Phase 2: Workspaces]   👉 BƯỚC TIẾP THEO (Tạo không gian làm việc & thành viên)
       │
       ▼
[Phase 3: Projects]     (Tạo dự án trực thuộc Workspace & gán PM/Members)
       │
       ▼
[Phase 4: Tasks & Kanban] (Linh hồn hệ thống: Thẻ công việc, Nhãn, Kéo thả Kanban, Lịch sử)
       │
       ▼
[Phase 5: Comments & Attachments] (Trao đổi, thảo luận, tệp đính kèm trong Task)
       │
       ▼
[Phase 6: Dashboard & Analytics] (Thống kê số liệu thực tế, My Tasks, Lịch Calendar)
       │
       ▼
[Phase 7: Notifications & Settings] (Thông báo chuông real-time, cấu hình Profile)
```

---

## Chi tiết từng Phase: Bảng DB & Danh sách API

---

### 🟢 Phase 1: Authentication & User Profile *(Đã hoàn thành ✅)*

Mục đích: Đăng ký, đăng nhập tài khoản qua Email/Password và Google OAuth 2.0, cấp Access/Refresh Token JWT xoay vòng (Token Rotation).

#### 1. Bảng Database đã dựng:
* **`users`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `email`: String(255), Unique, Indexed, Not Null
  * `name`: String(100), Not Null
  * `password_hash`: String(255), Nullable (khi đăng nhập qua Google)
  * `avatar_url`: Text, Nullable
  * `google_id`: String(255), Unique, Nullable
  * `is_active`: Boolean, Default = True
  * `created_at`: DateTime(timezone=True), Server Default = NOW()
  * `updated_at`: DateTime(timezone=True), Server Default = NOW()
* **`refresh_tokens`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `user_id`: BigInteger, Foreign Key -> `users.id`, Indexed, Not Null
  * `token_hash`: String(255), Not Null
  * `expires_at`: DateTime(timezone=True), Not Null
  * `revoked_at`: DateTime(timezone=True), Nullable
  * `created_at`: DateTime(timezone=True), Server Default = NOW()

#### 2. Danh sách API đã triển khai:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Đăng ký tài khoản mới bằng Email/Password | Public |
| `POST` | `/api/v1/auth/login` | Đăng nhập tài khoản, trả về cặp Token | Public |
| `POST` | `/api/v1/auth/google` | Đăng ký / Đăng nhập đồng bộ qua Google SSO | Public |
| `POST` | `/api/v1/auth/refresh` | Cấp Access Token mới và xoay vòng Refresh Token | Bearer Token |
| `POST` | `/api/v1/auth/logout` | Thu hồi Refresh Token hiện tại trong DB | Bearer Token |
| `GET` | `/api/v1/users/me` | Lấy thông tin hồ sơ của tài khoản đang đăng nhập | Bearer Token |

* **Màn hình Stitch tương ứng**: 
  * `Screen 01`: Đăng nhập (Login)
  * `Screen 02`: Đăng ký tài khoản (Register)

---

### 🚀 Phase 2: Workspaces & Workspace Members *(Bước tiếp theo cần làm)*

**Tại sao phải làm bước này tiếp theo?**
Trong mô hình SaaS, mọi Project và Task bắt buộc phải thuộc về một Workspace (`docs/business-rules.md`). Sau khi user đăng nhập lần đầu, họ cần có Workspace (tự tạo hoặc được mời vào) để bắt đầu tạo dự án.

#### 1. Bảng Database cần dựng mới:
* **`workspaces`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `name`: String(100), Not Null
  * `description`: Text, Nullable
  * `owner_id`: BigInteger, Foreign Key -> `users.id`, Not Null, Indexed
  * `created_at`: DateTime(timezone=True), Server Default = NOW()
  * `updated_at`: DateTime(timezone=True), Server Default = NOW()
* **`workspace_members`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `workspace_id`: BigInteger, Foreign Key -> `workspaces.id` (ON DELETE CASCADE), Indexed, Not Null
  * `user_id`: BigInteger, Foreign Key -> `users.id` (ON DELETE CASCADE), Indexed, Not Null
  * `role`: Enum(`OWNER`, `ADMIN`, `MEMBER`), Default = `MEMBER`, Not Null
  * `joined_at`: DateTime(timezone=True), Server Default = NOW()
  * *Ràng buộc*: `UniqueConstraint(workspace_id, user_id)`

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/workspaces` | Lấy danh sách các Workspace mà user hiện tại đang tham gia | Member |
| `POST` | `/api/v1/workspaces` | Tạo Workspace mới (User tạo tự động gán là `OWNER` trong `workspace_members`) | Authenticated User |
| `GET` | `/api/v1/workspaces/{id}` | Lấy chi tiết Workspace (kèm tổng quan số dự án, thành viên) | Member của WS |
| `PATCH` | `/api/v1/workspaces/{id}` | Sửa tên, mô tả Workspace | `OWNER`, `ADMIN` |
| `DELETE` | `/api/v1/workspaces/{id}` | Xóa vĩnh viễn Workspace | Chỉ `OWNER` |
| `GET` | `/api/v1/workspaces/{id}/members` | Lấy danh sách thành viên trong Workspace (kèm role, email, avatar) | Member của WS |
| `POST` | `/api/v1/workspaces/{id}/members/invite` | Thêm/Mời thành viên vào Workspace qua email | `OWNER`, `ADMIN` |
| `PATCH` | `/api/v1/workspaces/{id}/members/{user_id}` | Cập nhật quyền thành viên (`ADMIN` $\leftrightarrow$ `MEMBER`) | `OWNER` |
| `DELETE` | `/api/v1/workspaces/{id}/members/{user_id}` | Xóa thành viên khỏi Workspace | `OWNER`, `ADMIN` |

* **Màn hình Stitch tương ứng**:
  * `Screen 04`: Danh sách Không gian làm việc
  * `Screen 05`: Chi tiết Không gian làm việc
  * `Screen 13`: Quản lý Thành viên (Tab Workspace)

---

### 📦 Phase 3: Projects & Project Members

**Mục đích**: Tổ chức công việc thành các dự án cụ thể (ví dụ: Marketing Q3, Website Redesign, Backend Core API) trong một Workspace.

#### 1. Bảng Database cần dựng mới:
* **`projects`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `workspace_id`: BigInteger, Foreign Key -> `workspaces.id` (ON DELETE CASCADE), Indexed, Not Null
  * `name`: String(150), Not Null
  * `description`: Text, Nullable
  * `status`: Enum(`PLANNING`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `ARCHIVED`), Default = `ACTIVE`, Indexed
  * `manager_id`: BigInteger, Foreign Key -> `users.id`, Nullable, Indexed
  * `start_date`: Date, Nullable
  * `due_date`: Date, Nullable
  * `created_at`: DateTime(timezone=True), Server Default = NOW()
  * `updated_at`: DateTime(timezone=True), Server Default = NOW()
* **`project_members`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `project_id`: BigInteger, Foreign Key -> `projects.id` (ON DELETE CASCADE), Indexed, Not Null
  * `user_id`: BigInteger, Foreign Key -> `users.id` (ON DELETE CASCADE), Indexed, Not Null
  * `joined_at`: DateTime(timezone=True), Server Default = NOW()
  * *Ràng buộc*: `UniqueConstraint(project_id, user_id)`

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/projects` | Lấy danh sách dự án (Lọc theo `workspace_id`, `status`, `search`, phân trang) | Workspace Member |
| `POST` | `/api/v1/projects` | Tạo dự án mới trong Workspace | `OWNER`, `ADMIN`, `MEMBER` |
| `GET` | `/api/v1/projects/{id}` | Chi tiết dự án (thông tin, người phụ trách, % tiến độ hoàn thành) | Project Member / WS Admin |
| `PATCH` | `/api/v1/projects/{id}` | Cập nhật thông tin dự án, trạng thái, ngày hạn chót | Manager / WS Admin |
| `DELETE` | `/api/v1/projects/{id}` | Xóa hoặc đưa dự án vào lưu trữ (Archived) | Manager / WS Owner |
| `GET` | `/api/v1/projects/{id}/members` | Danh sách thành viên được phân công trong dự án | Project Member |
| `POST` | `/api/v1/projects/{id}/members` | Gán thêm thành viên từ Workspace vào Dự án | Manager / WS Admin |
| `DELETE` | `/api/v1/projects/{id}/members/{user_id}` | Gỡ thành viên khỏi dự án | Manager / WS Admin |

* **Màn hình Stitch tương ứng**:
  * `Screen 06`: Danh sách Dự án
  * `Screen 07`: Tổng quan Dự án

---

### 📋 Phase 4: Tasks, Labels, Task History & Kanban Board *(Linh hồn của ứng dụng)*

**Mục đích**: Quản lý thẻ công việc chi tiết, 5 cột Kanban kéo thả, gắn nhãn màu, tính toán hạn chót/quá hạn và tự động ghi nhật ký thay đổi.

#### 1. Bảng Database cần dựng mới:
* **`tasks`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `project_id`: BigInteger, Foreign Key -> `projects.id` (ON DELETE CASCADE), Indexed, Not Null
  * `title`: String(255), Not Null
  * `description`: Text, Nullable
  * `status`: Enum(`BACKLOG`, `TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`), Default = `TODO`, Indexed, Not Null
  * `priority`: Enum(`LOW`, `MEDIUM`, `HIGH`, `URGENT`), Default = `MEDIUM`, Indexed, Not Null
  * `assignee_id`: BigInteger, Foreign Key -> `users.id`, Nullable, Indexed (Người nhận việc)
  * `reporter_id`: BigInteger, Foreign Key -> `users.id`, Not Null, Indexed (Người tạo việc)
  * `position`: Float / Integer, Default = 0 (Thứ tự sắp xếp trong cột Kanban)
  * `due_date`: DateTime(timezone=True), Nullable, Indexed
  * `completed_at`: DateTime(timezone=True), Nullable (Tự động set khi status -> `DONE`, tự xóa khi lùi status)
  * `created_at`: DateTime(timezone=True), Server Default = NOW()
  * `updated_at`: DateTime(timezone=True), Server Default = NOW()
* **`labels`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `project_id`: BigInteger, Foreign Key -> `projects.id` (ON DELETE CASCADE), Indexed, Not Null
  * `name`: String(50), Not Null
  * `color_hex`: String(7), Default = `#2563EB`
* **`task_labels`**:
  * `task_id`: BigInteger, Foreign Key -> `tasks.id` (ON DELETE CASCADE), Not Null
  * `label_id`: BigInteger, Foreign Key -> `labels.id` (ON DELETE CASCADE), Not Null
  * *Primary Key*: `(task_id, label_id)`
* **`task_history`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `task_id`: BigInteger, Foreign Key -> `tasks.id` (ON DELETE CASCADE), Indexed, Not Null
  * `user_id`: BigInteger, Foreign Key -> `users.id`, Not Null
  * `event_type`: String(50), Not Null (`STATUS_CHANGE`, `PRIORITY_CHANGE`, `ASSIGNEE_CHANGE`, etc.)
  * `old_value`: Text, Nullable
  * `new_value`: Text, Nullable
  * `created_at`: DateTime(timezone=True), Server Default = NOW()

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tasks` | Lọc danh sách task (query: `project_id`, `status`, `priority`, `assignee_id`, `search`, `page`, `limit`) | Project Member |
| `POST` | `/api/v1/tasks` | Tạo task mới (validate: Assignee phải thuộc thành viên dự án) | Project Member |
| `GET` | `/api/v1/tasks/{id}` | Lấy chi tiết task (kèm nhãn, thông tin người giao, người nhận việc, lịch sử) | Project Member |
| `PATCH` | `/api/v1/tasks/{id}` | Cập nhật task (tự động ghi `task_history`, cập nhật `completed_at`) | Assignee / Reporter / Manager |
| `DELETE` | `/api/v1/tasks/{id}` | Xóa task | Reporter / Manager / WS Admin |
| `POST` | `/api/v1/tasks/{id}/move` | API kéo thả Kanban: đổi status & cập nhật vị trí thẻ trong cột | Project Member |
| `GET` | `/api/v1/projects/{project_id}/labels` | Danh sách các nhãn phân loại của dự án | Project Member |
| `POST` | `/api/v1/projects/{project_id}/labels` | Tạo nhãn mới cho dự án | Project Member |

* **Màn hình Stitch tương ứng**:
  * `Screen 08`: Bảng Kanban Dự án
  * `Screen 09`: Chi tiết công việc (Ngăn kéo trượt Task Drawer)
  * `Screen 10`: Hộp thoại Tạo công việc mới

---

### 💬 Phase 5: Comments & Attachments

**Mục đích**: Hỗ trợ trao đổi, thảo luận trực tiếp dưới thẻ task và tải lên các tài liệu đính kèm liên quan.

#### 1. Bảng Database cần dựng mới:
* **`comments`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `task_id`: BigInteger, Foreign Key -> `tasks.id` (ON DELETE CASCADE), Indexed, Not Null
  * `user_id`: BigInteger, Foreign Key -> `users.id`, Not Null
  * `content`: Text, Not Null
  * `created_at`: DateTime(timezone=True), Server Default = NOW()
  * `updated_at`: DateTime(timezone=True), Server Default = NOW()
* **`attachments`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `task_id`: BigInteger, Foreign Key -> `tasks.id` (ON DELETE CASCADE), Indexed, Not Null
  * `uploaded_by`: BigInteger, Foreign Key -> `users.id`, Not Null
  * `file_name`: String(255), Not Null
  * `file_url`: Text, Not Null
  * `file_size`: Integer, Not Null (bytes)
  * `content_type`: String(100), Nullable
  * `created_at`: DateTime(timezone=True), Server Default = NOW()

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tasks/{task_id}/comments` | Lấy danh sách bình luận trong task | Project Member |
| `POST` | `/api/v1/tasks/{task_id}/comments` | Đăng bình luận mới vào task | Project Member |
| `PATCH` | `/api/v1/comments/{id}` | Chỉnh sửa nội dung bình luận | Chỉ tác giả bình luận |
| `DELETE` | `/api/v1/comments/{id}` | Xóa bình luận | Tác giả hoặc Manager |
| `POST` | `/api/v1/tasks/{task_id}/attachments` | Upload file đính kèm vào task | Project Member |
| `DELETE` | `/api/v1/attachments/{id}` | Xóa file đính kèm | Người upload hoặc Manager |

* **Màn hình Stitch tương ứng**:
  * Tích hợp trực tiếp vào `Screen 09` (Task Detail Drawer)

---

### 📊 Phase 6: Dashboard Metrics & Cá nhân hóa (My Tasks & Calendar)

**Mục đích**: Tổng hợp dữ liệu từ các bảng `projects`, `tasks`, `task_history` thành các chỉ số phân tích trực quan cho người dùng.

#### 1. Bảng Database:
* **Không cần tạo bảng mới**: Các API này truy vấn trực tiếp và tổng hợp (aggregate queries: `COUNT`, `SUM`, `GROUP BY`) trên dữ liệu `tasks` và `projects` đã có.

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/dashboard/summary` | Trả về các chỉ số: Tổng task, Task hoàn thành, Task quá hạn, Dự án đang chạy | Authenticated User |
| `GET` | `/api/v1/dashboard/task-distribution` | Phân bổ task theo trạng thái (`TODO`, `IN_PROGRESS`, `DONE`) và mức ưu tiên | Authenticated User |
| `GET` | `/api/v1/dashboard/project-progress` | Danh sách tiến độ % của các dự án người dùng tham gia | Authenticated User |
| `GET` | `/api/v1/dashboard/recent-activity` | Danh sách 10 hoạt động gần đây nhất từ `task_history` | Authenticated User |
| `GET` | `/api/v1/tasks/my-tasks` | Gom toàn bộ task được giao cho user hiện tại trên tất cả dự án | Authenticated User |
| `GET` | `/api/v1/tasks/calendar` | Lấy danh sách task theo khoảng thời gian (`start_date`, `end_date`) để vẽ lên lịch | Authenticated User |

* **Màn hình Stitch tương ứng**:
  * `Screen 03`: Tổng quan Dashboard
  * `Screen 11`: Việc của tôi (My Tasks)
  * `Screen 12`: Lịch công việc (Calendar)

---

### 🔔 Phase 7: Notifications & Cài đặt hệ thống (Settings)

**Mục đích**: Gửi thông báo đến người dùng khi có sự kiện (được giao việc mới, có người bình luận, task sắp đến hạn) và quản lý thiết lập tài khoản.

#### 1. Bảng Database cần dựng mới:
* **`notifications`**:
  * `id`: BigInteger, Primary Key, Auto-increment
  * `user_id`: BigInteger, Foreign Key -> `users.id` (ON DELETE CASCADE), Indexed, Not Null
  * `type`: Enum(`ASSIGNED`, `COMMENT`, `MENTION`, `DUE_SOON`, `STATUS_CHANGED`), Not Null
  * `title`: String(200), Not Null
  * `message`: Text, Not Null
  * `link_url`: String(255), Nullable (URL điều hướng khi bấm vào thông báo)
  * `read_at`: DateTime(timezone=True), Nullable
  * `created_at`: DateTime(timezone=True), Server Default = NOW()

#### 2. Danh sách API cần xây dựng:
| Phương thức | Endpoint | Chức năng | Phân quyền |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/notifications` | Lấy danh sách thông báo của user (phân trang, lọc chưa đọc/đã đọc) | Authenticated User |
| `POST` | `/api/v1/notifications/{id}/read` | Đánh dấu 1 thông báo là đã đọc | Chủ thông báo |
| `POST` | `/api/v1/notifications/read-all` | Đánh dấu tất cả thông báo là đã đọc | Authenticated User |
| `DELETE` | `/api/v1/notifications/{id}` | Xóa 1 thông báo | Chủ thông báo |
| `PATCH` | `/api/v1/users/me/profile` | Cập nhật thông tin cá nhân (Tên, Avatar) | Authenticated User |
| `PATCH` | `/api/v1/users/me/password` | Đổi mật khẩu tài khoản | Authenticated User |

* **Màn hình Stitch tương ứng**:
  * `Screen 14`: Dropdown Thông báo nhanh ở Header
  * `Screen 15`: Trung tâm Thông báo
  * `Screen 16`: Cài đặt hệ thống (Settings)

---

## 🎯 Bảng tóm tắt tiến độ & Hành động tiếp theo

| Phase | Nghiệp vụ | Bảng DB | Số lượng API | Trạng thái |
| :---: | :--- | :--- | :---: | :---: |
| **Phase 1** | Authentication & Users | `users`, `refresh_tokens` | 6 APIs | ✅ Hoàn thành |
| **Phase 2** | **Workspaces & Members** | `workspaces`, `workspace_members` | **9 APIs** | 🚀 **TIẾP THEO** |
| **Phase 3** | Projects & Members | `projects`, `project_members` | 8 APIs | ⏳ Chờ |
| **Phase 4** | Tasks & Kanban Board | `tasks`, `labels`, `task_labels`, `task_history` | 8 APIs | ⏳ Chờ |
| **Phase 5** | Comments & Attachments | `comments`, `attachments` | 6 APIs | ⏳ Chờ |
| **Phase 6** | Dashboard & My Tasks | *(Dùng dữ liệu Phase 3 + 4)* | 6 APIs | ⏳ Chờ |
| **Phase 7** | Notifications & Settings | `notifications` | 6 APIs | ⏳ Chờ |

👉 **Hành động đề xuất ngay bây giờ**:
Bắt đầu **Phase 2: Workspaces & Workspace Members**:
1. Tạo SQLAlchemy Models: `Workspace` và `WorkspaceMember` trong `taskflow-be/app/models/workspace.py`.
2. Tạo Alembic migration tự động tạo 2 bảng `workspaces` và `workspace_members` trong PostgreSQL.
3. Xây dựng Repository, Service và Router cho các API Workspace CRUD (`GET /workspaces`, `POST /workspaces`, v.v.).
