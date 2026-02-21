# FaceVault Python SDK

Python client for the [FaceVault](https://facevault.id) identity verification API. Supports sync and async usage, webhook verification, and typed models.

## Installation

```bash
pip install facevault
```

## Quick start

### Sync

```python
from facevault import FaceVaultClient

client = FaceVaultClient("fv_live_your_api_key")

# Create a verification session
session = client.create_session(external_user_id="user-123")
print(session.webapp_url)  # Send this URL to your user

# Check session status
status = client.get_session(session.session_id)
print(status.status)  # "pending", "completed", "failed"

client.close()
```

### Async

```python
from facevault import AsyncFaceVaultClient

async def verify_user():
    async with AsyncFaceVaultClient("fv_live_your_api_key") as client:
        session = await client.create_session(external_user_id="user-123")
        print(session.webapp_url)
```

## Webhook verification

```python
from facevault import verify_signature, parse_event

# Verify the webhook signature
body = request.body
signature = request.headers["X-Signature"]

if verify_signature(body, signature, secret="your_webhook_secret"):
    event = parse_event(body)
    print(event.event)            # "session.completed"
    print(event.session_id)
    print(event.face_match_passed)
```

## Error handling

```python
from facevault import FaceVaultClient, AuthError, NotFoundError, RateLimitError

client = FaceVaultClient("fv_live_your_api_key")

try:
    session = client.get_session("nonexistent")
except AuthError:
    print("Invalid API key")
except NotFoundError:
    print("Session not found")
except RateLimitError:
    print("Too many requests")
```

## Documentation

Full API docs at [facevault.id/docs](https://facevault.id/docs).

## License

MIT
