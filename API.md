# API Documentation

## Overview

Talk AI API reference.

## Endpoints

### POST /api/chat

Send a message to the AI and receive a response.

**Request:**

```json
{
  "message": "string",
  "context": {}
}
```

**Response:**

```json
{
  "reply": "string",
  "tokens": 0
}
```

### GET /api/health

Health check endpoint.

**Response:**

```json
{
  "status": "ok"
}
```
