# API Endpoints & Usage

This document lists all the FastAPI endpoints and their purpose. It also includes example requests and responses.


## URL Shortening

### POST `/api/shorten`

**Description:** Create a new short URL.

**Request Body:**
```json
{
  "original_url": "https://example.com",
  "custom_alias": "my-link"  // optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "original_url": "https://example.com",
  "short_code": "my-link",
  "custom_alias": true,
  "click_count": 0,
  "created_at": "2026-01-17T12:34:56Z"
}
```


## URL Redirect

### GET `/api/redirect/{short_code}`

**Description:** Returns the original URL for a given short code (JSON response).

**Response:**
```json
{
  "url": "https://example.com",
  "short_code": "my-link"
}
```

### GET `/{short_code}`

**Description:** Direct 302 redirect to the original URL.



## User Authentication

### POST `/api/signup`

**Description:** Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### POST `/api/login`

**Description:** User login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### POST `/api/logout`

**Description:** Clear user authentication cookie.

**Response:**
```json
{
  "message": "Logged out successfully"
}
```



## URL Management

### GET `/api/urls`

**Description:** Get all URLs created by the authenticated user.

### DELETE `/api/urls/{url_id}`

**Description:** Delete a URL owned by the user.



## Pages (Template Routes)

- `/api/home` — Homepage with URL shortening form
- `/api/dashboard` — Analytics dashboard
- `/api/login` — Login page
- `/api/signup` — Signup page



## Health & Readiness (Production)

### GET `/api/health`

**Description:** Liveness probe

### GET `/api/ready`

**Description:** Readiness probe

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-17T12:34:56Z"
}
```



## Using Shortened URLs

- **Frontend (Recommended):** `https://yourdomain.com/{short_code}`
- **Backend JSON:** `https://yourdomain.com/api/redirect/{short_code}`
- **Local Testing:** `http://localhost:8001/{short_code}` (direct 302 redirect)