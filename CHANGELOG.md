# Changelog

All notable changes to `facevault` (Python SDK).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2026-05-29

### Docs

- Fix the misleading "What's new in 1.0.0" heading in the README — it now
  reflects the v1.0.1 changes (raw-body HMAC fix + `X-FaceVault-Signature`
  header). The PyPI project page displays the published sdist's README,
  so v1.0.1 visitors landed on an out-of-date "what's new" section.

### Changed

- Package keywords: add `telegram` and `mini-app` to surface the SDK to
  Telegram Mini App / bot developers, the dominant audience.

## [1.0.1] - 2026-05-28

### Fixed

- **Webhook signature verification now HMACs the raw request body** instead of
  re-serializing the parsed JSON. The old approach couldn't reproduce the
  server's exact signed bytes for payloads containing non-ASCII characters
  (names, addresses) or whole-number floats, so valid webhooks could be
  rejected with a bad-signature error. Verification is now byte-exact — pass the
  body exactly as received.

### Changed

- README and examples now document the webhook header as
  `X-FaceVault-Signature` (the API has always sent this header; v1.0.0 docs
  incorrectly showed `X-Signature`).

### Docs

- Roadmap note: credentials API methods are planned for the v2 SDK line
  (held alongside FacePass/FaceKey).

## [1.0.0] - 2026-03-11

### Added

- Sync client (`FaceVaultClient`) and async client (`AsyncFaceVaultClient`)
  backed by [httpx](https://www.python-httpx.org/); single runtime dependency.
- `create_session()` — create a KYC verification session; returns a `Session`
  with `webapp_url` to forward to the end user.
- `get_session()` — poll session status; returns a `SessionStatus` with
  `status`, `trust_score` (0–100), and `trust_decision`
  (`accept` / `review` / `reject`).
- Webhook HMAC helpers: `verify_signature` (HMAC-SHA256 constant-time check
  against the `X-FaceVault-Signature` header) and `parse_event` (deserialise
  the payload into a typed `WebhookEvent`).
- Typed dataclass models: `Session`, `SessionStatus`, `WebhookEvent`.
- Typed exceptions: `AuthError`, `NotFoundError`, `RateLimitError`,
  `FaceVaultError`.
- README with quick-start examples, webhook verification guide, and error
  handling reference.
- Project docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- CI (`ci.yml`) running on every push and pull request across Python 3.9–3.12.
  Release workflow (`release.yml`) that, on tag push, builds the distribution,
  publishes `dist/*` + `SHA256SUMS.txt` as release assets, and uses the
  matching CHANGELOG section as the release body.
