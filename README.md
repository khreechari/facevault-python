# FaceVault Python SDK

[![PyPI version](https://img.shields.io/pypi/v/facevault)](https://pypi.org/project/facevault/)
[![Python versions](https://img.shields.io/pypi/pyversions/facevault)](https://pypi.org/project/facevault/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-46%20passed-brightgreen)]()

Python client for the [FaceVault](https://facevault.id) identity verification API — privacy-first KYC with liveness detection, face matching, and document verification.

## Features

- **Sync & async clients** — use `FaceVaultClient` or `AsyncFaceVaultClient`
- **Webhook verification** — HMAC-SHA256 signature validation
- **Typed models** — dataclasses for sessions, status, and webhook events
- **Secure by default** — HTTPS enforced, API keys validated, secrets redacted from logs
- **Lightweight** — only depends on [httpx](https://www.python-httpx.org/)

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

# With proof of address required
session = client.create_session(external_user_id="user-123", require_poa=True)

# Check session status
status = client.get_session(session.session_id)
print(status.status)           # "in_progress", "passed", "failed", "review"
print(status.trust_score)      # 0-100 trust score
print(status.trust_decision)   # "accept", "review", "reject"

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
    print(event.event)             # "verification.completed"
    print(event.session_id)
    print(event.face_match_passed)
    print(event.trust_score)       # 0-100
    print(event.trust_decision)    # "accept", "review", "reject"
    print(event.sanctions_hit)     # True/False
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

## Security

The SDK enforces security best practices out of the box:

- **HTTPS only** — `http://` URLs are rejected at init to prevent credentials leaking over plaintext
- **Key validation** — empty or whitespace-only API keys raise `ValueError` immediately
- **Secret redaction** — `Session.__repr__` masks `session_token` and URL tokens, safe for logging
- **Client redaction** — `FaceVaultClient.__repr__` masks the API key
- **Path traversal protection** — `get_session()` validates session IDs

## What's new in 1.0.0

- `require_poa` parameter on `create_session()` — per-session proof of address override
- `trust_score` and `trust_decision` on `SessionStatus` — unified 0-100 trust score
- `require_poa`, `poa`, `anti_spoofing`, `credential` on `SessionStatus`
- `trust_score`, `trust_decision`, `sanctions_hit`, `poa` on `WebhookEvent`
- `challenge_nonce` on `Session` — capture integrity nonce

## Documentation

- [Getting started guide](https://facevault.id/docs)
- [API reference](https://facevault.id/docs)
- [Blog: Announcing the Python SDK](https://facevault.id/blog/python-sdk)

## License

[MIT](LICENSE)
