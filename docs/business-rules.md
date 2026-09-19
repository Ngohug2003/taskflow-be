# Business Rules — Task Flow Manager

## Authentication

- BR-AUTH-001: Email must be unique.
- BR-AUTH-002: Password must be stored as a secure hash.
- BR-AUTH-003: Protected API endpoints require valid authentication.
- BR-AUTH-004: Authorization is checked by the backend.

## Workspace

- BR-WS-001: A workspace has one owner.
- BR-WS-002: A user can belong to multiple workspaces.
- BR-WS-003: Workspace membership is required before accessing protected workspace data.
- BR-WS-004: Only authorized roles can invite/remove members.
- BR-WS-005: Only the owner can delete the workspace.

## Project

- BR-PROJ-001: Every project belongs to exactly one workspace.
- BR-PROJ-002: A project member must belong to the associated workspace.
- BR-PROJ-003: Archived projects should not accept normal task operations unless explicitly supported.
- BR-PROJ-004: Project managers can manage project configuration.

## Task

- BR-TASK-001: Every task belongs to exactly one project.
- BR-TASK-002: Task title is required.
- BR-TASK-003: Task status is required.
- BR-TASK-004: Only project members can be assigned to a task.
- BR-TASK-005: A task may have multiple labels.
- BR-TASK-006: A task may have multiple comments.
- BR-TASK-007: A task may have multiple attachments.
- BR-TASK-008: Important task changes must be recorded in task history.

## Status

Valid statuses:

- BACKLOG
- TODO
- IN_PROGRESS
- IN_REVIEW
- DONE

- BR-STATUS-001: A task can move between valid statuses.
- BR-STATUS-002: When status becomes DONE, set `completed_at`.
- BR-STATUS-003: When a DONE task moves to another status, clear `completed_at`.

## Deadline

- BR-DUE-001: A task with a past deadline and status other than DONE is overdue.
- BR-DUE-002: Overdue is a derived state and should not require a separate database status.
- BR-DUE-003: The UI should clearly identify overdue tasks.

## Priority

Valid priorities:

- LOW
- MEDIUM
- HIGH
- URGENT

## History

Important history events include:

- CREATE_TASK
- UPDATE_TASK
- CHANGE_STATUS
- CHANGE_PRIORITY
- ASSIGN_USER
- CHANGE_DEADLINE
- ADD_LABEL
- REMOVE_LABEL
- ADD_COMMENT

History should include actor, event type, timestamp and relevant change information.

## Pagination

- BR-PAGE-001: Default page is 1.
- BR-PAGE-002: Default limit is 20.
- BR-PAGE-003: Maximum limit is 100.
- BR-PAGE-004: Large collections must be paginated.
