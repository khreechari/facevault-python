# Contributing

Thanks for taking the time to contribute! The `facevault` Python SDK is
load-bearing for integrators in production — so we ask for a bit of rigour to
keep it stable and safe.

## Repo layout

- `src/facevault/` — the installable package.
  - `_client.py` — synchronous `FaceVaultClient`.
  - `_async_client.py` — asynchronous `AsyncFaceVaultClient`.
  - `models.py` — typed dataclass models (`Session`, `SessionStatus`,
    `WebhookEvent`).
  - `webhook.py` — `verify_signature` and `parse_event` HMAC helpers.
  - `exceptions.py` — `AuthError`, `NotFoundError`, `RateLimitError`, etc.
  - `__init__.py` — public surface re-exports and `__version__`.
- `tests/` — pytest suite (pytest-asyncio + respx for HTTP mocking).
- `pyproject.toml` — Hatchling build, metadata, test config.
- `README.md` — integration guide and API reference.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest pytest-asyncio respx
pytest
```

All tests run against mocked HTTP (respx) — no live API key needed.

## Pull requests

- One topic per PR.
- **Keep the public client API stable.** `FaceVaultClient` /
  `AsyncFaceVaultClient` method signatures, model field names, and exception
  types are a contract — renaming or removing them breaks every integrator in
  the wild. Additive changes (new optional parameters, new model fields) are
  fine.
- **Don't add runtime dependencies** beyond what's already in `pyproject.toml`.
  The SDK's single runtime dep (`httpx`) is intentional — every additional
  dependency increases the blast radius for integrators.
- Add a `CHANGELOG.md` entry under `## [Unreleased]`. Bump nothing else —
  cutting a release (moving `[Unreleased]` to a version, tagging, and bumping
  `src/facevault/__init__.py`) is a maintainer step.
- The release workflow publishes the matching `CHANGELOG.md` section verbatim
  as the GitHub release body. Keep a blank line after each `###` heading and
  between bullets, and never wrap the section in a code fence.

## Code style

- Match the existing style: type hints throughout, 4-space indent, double
  quotes consistent with the surrounding module.
- Comments explain *why*, not *what*.
- Keep examples in the README minimal and dependency-light.

## Reporting a security issue

See [SECURITY.md](SECURITY.md). Please do not open public issues for
security-relevant bugs.

## License

By contributing you agree your contribution will be licensed under the
[MIT License](LICENSE) — the same as the rest of the project.
