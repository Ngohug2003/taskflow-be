# Business Analysis Document — Task Flow Manager

**Version:** 1.0  
**Project Type:** Web Application  
**Target:** Junior Full Stack Portfolio

## 1. Overview

Task Flow Manager is a SaaS project and task management platform for individuals and small teams.

The system allows users to:
- create workspaces
- create projects
- manage members
- create and assign tasks
- manage tasks through a Kanban board
- manage priority, labels and deadlines
- collaborate through comments
- track task history
- receive notifications
- view project and task statistics

## 2. Scope

### In Scope

Authentication:
- Register
- Login
- Logout
- Refresh token
- Forgot/reset password

Workspace:
- Create/update/delete workspace
- Invite members
- Manage members
- Assign workspace roles

Project:
- Create/update/archive/delete project
- Manage project members
- Project dashboard

Task:
- Create/update/delete task
- Assign member
- Status
- Priority
- Deadline
- Labels
- Description
- Checklist
- Comments
- Attachments
- Task history

Kanban:
- Backlog
- Todo
- In Progress
- In Review
- Done
- Drag and drop
- Reordering

Dashboard:
- Total tasks
- Completed tasks
- In-progress tasks
- Overdue tasks
- Task distribution
- Project progress
- Recent activity

Notifications:
- Assignment
- Mention
- Comment
- Status changes
- Deadline reminders

## 3. Actors

| Actor | Description |
|---|---|
| Guest | Unauthenticated user |
| User | Authenticated user |
| Workspace Owner | Workspace owner |
| Workspace Admin | Workspace administrator |
| Project Manager | Project manager |
| Member | Project/workspace member |

A user may have different roles in different workspaces/projects.

## 4. Permission Summary

### Workspace

| Action | Owner | Admin | Member |
|---|---:|---:|---:|
| View | Yes | Yes | Yes |
| Edit | Yes | Yes | No |
| Delete | Yes | No | No |
| Invite member | Yes | Yes | No |
| Remove member | Yes | Yes | No |
| Change role | Yes | Yes | No |

### Project

| Action | Manager | Member |
|---|---:|---:|
| View | Yes | Yes |
| Edit | Yes | No |
| Delete | Yes | No |
| Create task | Yes | Yes |
| Edit task | Yes | Yes* |
| Delete task | Yes | No |
| Assign task | Yes | No |

`*` Subject to task permissions.

## 5. Main Business Processes

### Registration

```text
Register
→ Validate email/password
→ Check duplicate email
→ Hash password
→ Create user
→ Create default workspace
→ Authenticate
```

### Workspace

```text
Login
→ Dashboard
→ Create workspace
→ Invite members
→ Create project
```

### Project

```text
Workspace
→ Create project
→ Add members
→ Create task
→ Assign member
→ Manage task
```

### Task lifecycle

```text
BACKLOG
→ TODO
→ IN_PROGRESS
→ IN_REVIEW
→ DONE
```

A task may move backwards when required.

## 6. Core Entities

- User
- Workspace
- WorkspaceMember
- Project
- ProjectMember
- Task
- Label
- TaskLabel
- Comment
- TaskHistory
- Notification
- Attachment
- RefreshToken

## 7. Functional Requirements

### Authentication

- FR-AUTH-001: User can register.
- FR-AUTH-002: User can login.
- FR-AUTH-003: User can logout.
- FR-AUTH-004: User can refresh an expired access token.
- FR-AUTH-005: User can reset password.
- FR-AUTH-006: User can view current profile.

### Workspace

- FR-WS-001: User can create a workspace.
- FR-WS-002: User can update a workspace if authorized.
- FR-WS-003: Owner can delete a workspace.
- FR-WS-004: Authorized users can invite members.
- FR-WS-005: Authorized users can manage member roles.

### Project

- FR-PROJ-001: Authorized users can create projects.
- FR-PROJ-002: Users can view projects they have access to.
- FR-PROJ-003: Project managers can update projects.
- FR-PROJ-004: Project managers can archive projects.
- FR-PROJ-005: Project managers can manage project members.

### Task

- FR-TASK-001: Authorized users can create tasks.
- FR-TASK-002: Users can view tasks available to them.
- FR-TASK-003: Authorized users can update tasks.
- FR-TASK-004: Authorized users can delete tasks.
- FR-TASK-005: Project managers can assign tasks.
- FR-TASK-006: Users can change task status according to permissions.
- FR-TASK-007: Users can set priority and deadline.
- FR-TASK-008: Users can add labels.
- FR-TASK-009: Users can comment on tasks.
- FR-TASK-010: System records important task changes.

### Dashboard

- FR-DASH-001: User can view task summary.
- FR-DASH-002: User can view project progress.
- FR-DASH-003: User can view recent activity.
- FR-DASH-004: User can filter relevant task information.

### Notifications

- FR-NOTI-001: User receives assignment notifications.
- FR-NOTI-002: User receives mention notifications.
- FR-NOTI-003: User receives comment notifications.
- FR-NOTI-004: User receives deadline reminders.
- FR-NOTI-005: User can mark notifications as read.

## 8. Non-functional Requirements

Performance:
- Paginate large collections.
- Default page size is 20.
- Maximum page size is 100.
- Typical API requests should target sub-500ms response time in normal development conditions.

Security:
- Passwords must be hashed.
- JWT authentication is required for protected resources.
- Backend must enforce authorization.
- Request payloads must be validated.
- Sensitive tokens must not be exposed unnecessarily.

Maintainability:
- Use modular frontend and backend architecture.
- Use migrations for database changes.
- Use Git for version control.
- Use Docker for reproducible development.

## 9. MVP

### Phase 1
Authentication

### Phase 2
Workspace and members

### Phase 3
Projects

### Phase 4
Tasks

### Phase 5
Kanban

### Phase 6
Comments, history and notifications

### Phase 7
Dashboard

### Phase 8
Testing, Docker and CI/CD
