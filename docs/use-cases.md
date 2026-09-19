# Use Cases — Task Flow Manager

## UC-AUTH-001 — Register

**Actor:** Guest

**Precondition:** User is not authenticated.

**Flow:**
1. User enters name, email and password.
2. System validates input.
3. System checks email uniqueness.
4. System creates user.
5. System creates default workspace.
6. System authenticates user.

**Alternative:**
- Existing email → return validation error.
- Invalid password → return validation error.

## UC-AUTH-002 — Login

**Actor:** Guest

**Flow:**
1. User enters email/password.
2. System validates credentials.
3. System returns access and refresh tokens.
4. User enters authenticated application.

## UC-WS-001 — Create Workspace

**Actor:** User

**Flow:**
1. User selects Create Workspace.
2. User enters workspace information.
3. System validates input.
4. System creates workspace.
5. User becomes workspace owner.

## UC-WS-002 — Invite Member

**Actor:** Owner/Admin

**Flow:**
1. User opens workspace members.
2. User enters invite email.
3. System validates permission.
4. System creates invitation.
5. Invitee can join the workspace.

## UC-PROJ-001 — Create Project

**Actor:** Authorized workspace user

**Flow:**
1. User selects Create Project.
2. User enters project information.
3. System validates workspace access.
4. System creates project.
5. Project appears in project list.

## UC-TASK-001 — Create Task

**Actor:** Project Manager/Member

**Flow:**
1. User selects Create Task.
2. User enters task information.
3. System validates project membership.
4. System creates task.
5. System records CREATE_TASK history.

## UC-TASK-002 — Move Task

**Actor:** Authorized project member

**Flow:**
1. User drags task to another Kanban column.
2. Frontend sends move request.
3. Backend validates authorization.
4. Backend validates target status.
5. Backend updates task.
6. Backend records status history.
7. UI reflects the new state.

## UC-TASK-003 — Comment on Task

**Actor:** Project member

**Flow:**
1. User opens task detail.
2. User enters comment.
3. System validates content.
4. System creates comment.
5. System creates notification where applicable.

## UC-TASK-004 — Assign Task

**Actor:** Project Manager/Authorized user

**Flow:**
1. User opens task.
2. User selects assignee.
3. System checks project membership.
4. System updates assignee.
5. System records history.
6. Assignee receives notification.

## UC-DASH-001 — View Dashboard

**Actor:** Authenticated user

**Flow:**
1. User opens dashboard.
2. System loads task/project aggregates.
3. System displays summary cards.
4. System displays project progress.
5. System displays recent activity.
