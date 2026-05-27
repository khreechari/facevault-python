# Security Policy

## Reporting a vulnerability

If you believe you have found a security issue in the FaceVault Python SDK
or the FaceVault services it depends on (the verification API, webhook
delivery), please **do not open a public GitHub issue**.

Instead, email **security@facevault.id** with:

- A description of the issue and its impact.
- Reproduction steps or a proof-of-concept.
- Affected version (the release tag or commit SHA you are using).
- Whether you have already disclosed the issue elsewhere.

We will acknowledge receipt within **3 business days** and aim to ship a fix
within **30 days** for high-severity issues. We will credit you in the release
notes unless you ask to remain anonymous.

## Scope

In scope:

- The `facevault` Python SDK code — especially the `verify_signature` /
  `parse_event` webhook HMAC-SHA256 verification helpers, the sync and async
  HTTP clients, and any credential or token handling.
- The FaceVault API endpoints the SDK calls (`/api/v1/sessions`,
  `/api/v1/sessions/{id}`, and related).

Out of scope:

- The integrator's own backend — how you authenticate users before creating a
  session, or how you store API keys. The SDK never transmits your API key
  beyond the authorised endpoint.
- Operator/integrator misconfiguration (e.g. logging raw request bodies that
  contain webhook secrets, or storing API keys insecurely).
- DoS / volumetric attacks — the API endpoints are rate-limited at the edge.
- Theoretical issues without a demonstrated impact path.

## Supply chain

- All GitHub Actions used in CI and the release workflow are SHA-pinned;
  comments record the human-readable version next to each SHA so bumps stay
  reviewable. `dependabot.yml` watches the pins for updates.
- Release assets include an unsigned `SHA256SUMS.txt`. We are evaluating
  sigstore signing for a future release.
- The SDK has a single runtime dependency (`httpx`); any supply-chain issue
  in `httpx` should be reported upstream to the httpx project as well.
