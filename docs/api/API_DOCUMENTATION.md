# Citizen Urban Planning Participation System - API Documentation

## Overview

RESTful API for the Citizen Urban Planning Participation System MVP.

**Base URL**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/api/docs`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "citizen"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "citizen",
  "is_active": true,
  "created_at": "2025-10-23T10:00:00",
  "updated_at": "2025-10-23T10:00:00"
}
```

#### POST /auth/login
Login and receive JWT token.

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information. **Requires authentication**.

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "citizen",
  "is_active": true,
  "created_at": "2025-10-23T10:00:00",
  "updated_at": "2025-10-23T10:00:00"
}
```

---

### Opinions

#### POST /opinions
Create a new opinion. **Requires authentication**.

**Request Body**:
```json
{
  "title": "Need more bike lanes on Main Street",
  "content": "Main Street needs dedicated bike lanes for safety...",
  "category_id": 1,
  "region": "Downtown",
  "latitude": 23.5880,
  "longitude": 120.5470,
  "is_public": true,
  "status": "draft",
  "tags": ["transportation", "safety", "bike"]
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Need more bike lanes on Main Street",
  "content": "Main Street needs dedicated bike lanes...",
  "category_id": 1,
  "status": "draft",
  "region": "Downtown",
  "latitude": 23.5880,
  "longitude": 120.5470,
  "view_count": 0,
  "is_public": true,
  "merged_to_id": null,
  "created_at": "2025-10-23T10:00:00",
  "updated_at": "2025-10-23T10:00:00",
  "media": [],
  "tags": ["transportation", "safety", "bike"],
  "vote_count": 0,
  "comment_count": 0
}
```

#### GET /opinions
Get paginated list of opinions.

**Query Parameters**:
- `page` (int, default: 1): Page number
- `page_size` (int, default: 20): Items per page
- `status` (string, optional): Filter by status (draft/pending/approved/rejected/resolved)
- `category_id` (int, optional): Filter by category

**Response** (200 OK):
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "john_doe",
      "user_full_name": "John Doe",
      "title": "Need more bike lanes on Main Street",
      "content": "...",
      "status": "approved",
      "vote_count": 15,
      "comment_count": 3,
      "tags": ["transportation", "safety"]
    }
  ]
}
```

#### GET /opinions/{id}
Get specific opinion by ID.

**Response** (200 OK): Same as create opinion response.

#### POST /opinions/{id}/comments
Add a comment to an opinion. **Requires authentication**.

**Request Body**:
```json
{
  "content": "Great idea! I support this proposal."
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "opinion_id": 1,
  "user_id": 2,
  "username": "jane_smith",
  "content": "Great idea! I support this proposal.",
  "is_deleted": false,
  "created_at": "2025-10-23T10:00:00"
}
```

#### POST /opinions/{id}/vote
Vote on an opinion. **Requires authentication**.

**Request Body**:
```json
{
  "vote_type": "like"
}
```

**Response** (200 OK):
```json
{
  "message": "Vote recorded successfully"
}
```

#### POST /opinions/{id}/collect
Add opinion to personal collection. **Requires authentication**.

**Response** (200 OK):
```json
{
  "message": "Opinion collected successfully"
}
```

#### DELETE /opinions/{id}/collect
Remove opinion from collection. **Requires authentication**.

**Response** (200 OK):
```json
{
  "message": "Opinion removed from collection"
}
```

---

### Notifications

#### GET /notifications
Get user's notifications. **Requires authentication**.

**Query Parameters**:
- `unread_only` (bool, default: false): Only show unread notifications

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "opinion_id": 5,
    "type": "comment",
    "title": "New comment on your opinion",
    "content": "Someone commented on your opinion",
    "is_read": false,
    "created_at": "2025-10-23T10:00:00"
  }
]
```

#### POST /notifications/{id}/read
Mark notification as read. **Requires authentication**.

**Response** (200 OK):
```json
{
  "message": "Notification marked as read"
}
```

---

### Moderation (Admin/Moderator Only)

All moderation endpoints require admin or moderator role.

#### POST /admin/opinions/{id}/approve
Approve an opinion.

**Response** (200 OK):
```json
{
  "message": "Opinion approved successfully"
}
```

#### POST /admin/opinions/{id}/reject
Reject an opinion.

**Request Body**:
```json
{
  "reason": "Does not meet community guidelines"
}
```

**Response** (200 OK):
```json
{
  "message": "Opinion rejected successfully"
}
```

#### POST /admin/opinions/{id}/merge
Merge opinion into another.

**Request Body**:
```json
{
  "target_id": 10
}
```

**Response** (200 OK):
```json
{
  "message": "Opinions merged successfully"
}
```

#### DELETE /admin/comments/{id}
Delete a comment.

**Response** (200 OK):
```json
{
  "message": "Comment deleted successfully"
}
```

#### PUT /admin/opinions/{id}/category
Update opinion category.

**Request Body**:
```json
{
  "category_id": 2
}
```

**Response** (200 OK):
```json
{
  "message": "Category updated successfully"
}
```

---

## Error Responses

All endpoints may return error responses:

**400 Bad Request**:
```json
{
  "detail": "Error description"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found"
}
```

---

## Data Models

### OpinionStatus
- `draft`: Draft, not submitted
- `pending`: Submitted, awaiting review
- `approved`: Approved by moderator
- `rejected`: Rejected by moderator
- `resolved`: Issue has been resolved

### UserRole
- `citizen`: Regular user
- `moderator`: Can moderate content
- `admin`: Full administrative access

### MediaType
- `image`: Image file
- `video`: Video file
- `audio`: Audio file

### NotificationType
- `comment`: New comment notification
- `status_change`: Opinion status changed
- `merged`: Opinion merged
- `approved`: Opinion approved
- `rejected`: Opinion rejected
