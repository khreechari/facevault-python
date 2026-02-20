# FaceVault Python SDK

Official Python SDK for [FaceVault.id](https://facevault.id) — privacy-first KYC & identity verification.

Add KYC to your Telegram bot in 5 lines of code.

## Installation

```bash
pip install facevault
```

## Quick Start

```python
from facevault import FaceVaultClient

fv = FaceVaultClient(api_key="fv_live_...")

# Create a verification session
session = fv.create_session(external_user_id="user_123")
print(session.webapp_url)
# → https://app.facevault.id/?sid=abc...&st=def...

# Poll for results (or use webhooks)
status = fv.get_session(session.session_id)
print(status.status)  # "passed" | "failed" | "in_progress"
```

## Telegram Bot Example (python-telegram-bot)

```python
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from facevault import FaceVaultClient

fv = FaceVaultClient(api_key="fv_live_...")

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = fv.create_session(external_user_id=str(update.effective_user.id))
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Verify Identity", web_app=WebAppInfo(url=session.webapp_url))
    ]])
    await update.message.reply_text("Tap below to verify your identity:", reply_markup=keyboard)

app = Application.builder().token("BOT_TOKEN").build()
app.add_handler(CommandHandler("verify", verify))
app.run_polling()
```

## Async Client (for aiogram, aiohttp, etc.)

```python
from facevault import AsyncFaceVaultClient

async def main():
    async with AsyncFaceVaultClient(api_key="fv_live_...") as fv:
        session = await fv.create_session(external_user_id="user_123")
        print(session.webapp_url)
```

## Webhook Verification

FaceVault signs webhook payloads with HMAC-SHA256. Verify them:

```python
from facevault import verify_signature, parse_event

# In your webhook handler:
body = request.body  # raw request body
signature = request.headers["X-Signature"]

if verify_signature(body, signature, "your_webhook_secret"):
    event = parse_event(body)
    print(f"Session {event.session_id}: {event.status}")
    print(f"Face match: {event.face_match_passed}")
else:
    print("Invalid signature!")
```

## API Reference

### `FaceVaultClient(api_key, *, base_url, webapp_base, timeout)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | required | Your FaceVault API key |
| `base_url` | `str` | `https://api.facevault.id` | API base URL |
| `webapp_base` | `str` | `https://app.facevault.id` | Webapp URL for session links |
| `timeout` | `float` | `15` | Request timeout in seconds |

### Methods

#### `create_session(external_user_id) -> Session`

Create a new verification session.

Returns a `Session` with:
- `session_id: str`
- `session_token: str`
- `steps: list[str]`
- `webapp_url: str` — URL to open in Telegram Mini App or browser

#### `get_session(session_id) -> SessionStatus`

Get session status and results.

Returns a `SessionStatus` with:
- `session_id: str`
- `status: str` — `"in_progress"`, `"passed"`, or `"failed"`
- `steps: dict[str, bool]`
- `face_match_passed: bool | None`
- `error: str`
- `created_at, completed_at`

### Webhook Helpers

#### `verify_signature(body, signature, secret) -> bool`

Verify HMAC-SHA256 signature of a webhook payload.

#### `parse_event(body) -> WebhookEvent`

Parse webhook JSON into a typed `WebhookEvent` dataclass with fields:
`event`, `session_id`, `status`, `external_user_id`, `face_match_passed`,
`face_match_score`, `anti_spoofing_score`, `anti_spoofing_passed`,
`confirmed_data`, `completed_at`, `document_check`.

### Exceptions

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `AuthError` | 401 | Invalid or missing API key |
| `NotFoundError` | 404 | Session not found |
| `RateLimitError` | 429 | Rate limit exceeded |
| `FaceVaultError` | other | Any other API error |

## License

MIT
