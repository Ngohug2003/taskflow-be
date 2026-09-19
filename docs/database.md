# Database Design — Task Flow Manager

Database: PostgreSQL

## Main Tables

### users

```text
id
name
email
password_hash
avatar_url
created_at
updated_at
```

### workspaces

```text
id
name
description
selected_color
privacy
owner_id
created_at
updated_at
```

### workspace_members

```text
id
workspace_id
user_id
role
joined_at
```

### projects

```text
id
workspace_id
name
description
status
manager_id
created_at
updated_at
```

### project_members

```text
id
project_id
user_id
joined_at
```

### tasks

```text
id
project_id
title
description
status
priority
assignee_id
reporter_id
due_date
completed_at
created_at
updated_at
```

### labels

```text
id
project_id
name
```

### task_labels

```text
task_id
label_id
```

### comments

```text
id
task_id
user_id
content
created_at
updated_at
```

### task_history

```text
id
task_id
user_id
event_type
old_value
new_value
created_at
```

### notifications

```text
id
user_id
type
title
message
read_at
created_at
```

### attachments

```text
id
task_id
uploaded_by
file_name
file_url
file_size
created_at
```

### refresh_tokens

```text
id
user_id
token_hash
expires_at
created_at
revoked_at
```

## Relationships

```text
User
 ├── WorkspaceMember
 ├── ProjectMember
 ├── Task (assignee)
 ├── Task (reporter)
 ├── Comment
 ├── TaskHistory
 └── Notification

Workspace
 ├── WorkspaceMember
 └── Project

Project
 ├── ProjectMember
 ├── Task
 └── Label

Task
 ├── TaskLabel
 ├── Comment
 ├── TaskHistory
 └── Attachment
```

## Recommended Indexes

Consider indexes for:

- users.email
- workspace_members.workspace_id
- workspace_members.user_id
- project_members.project_id
- project_members.user_id
- tasks.project_id
- tasks.assignee_id
- tasks.status
- tasks.priority
- tasks.due_date
- notifications.user_id
