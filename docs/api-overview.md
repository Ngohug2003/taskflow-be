# API Overview — Task Flow Manager

Base path:

```text
/api/v1
```

## Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
POST /auth/forgot-password
POST /auth/reset-password
GET  /users/me
```

## Workspaces

```text
GET    /workspaces
POST   /workspaces
GET    /workspaces/{id}
PATCH  /workspaces/{id}
DELETE /workspaces/{id}

GET    /workspaces/{id}/members
POST   /workspaces/{id}/members/invite
PATCH  /workspaces/{id}/members/{member_id}
DELETE /workspaces/{id}/members/{member_id}
```

## Projects

```text
GET    /projects
POST   /projects
GET    /projects/{id}
PATCH  /projects/{id}
DELETE /projects/{id}

GET    /projects/{id}/members
POST   /projects/{id}/members
DELETE /projects/{id}/members/{member_id}
```

## Tasks

```text
GET    /tasks
POST   /tasks
GET    /tasks/{id}
PATCH  /tasks/{id}
DELETE /tasks/{id}
POST   /tasks/{id}/move
```

Supported query parameters:

```text
page
limit
search
status
priority
assignee_id
project_id
label_id
due_date_from
due_date_to
sort
```

## Comments

```text
GET    /tasks/{task_id}/comments
POST   /tasks/{task_id}/comments
PATCH  /comments/{id}
DELETE /comments/{id}
```

## Notifications

```text
GET  /notifications
POST /notifications/{id}/read
POST /notifications/read-all
DELETE /notifications/{id}
```

## Dashboard

```text
GET /dashboard/summary
GET /dashboard/task-distribution
GET /dashboard/project-progress
GET /dashboard/recent-activity
```

## API Rules

- Use consistent HTTP status codes.
- Validate request bodies with Pydantic.
- Enforce authorization in backend services.
- Paginate list endpoints.
- Return typed, predictable response structures.
- Avoid exposing internal database implementation details unnecessarily.
