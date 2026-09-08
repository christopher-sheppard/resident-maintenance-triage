# Design decisions and limits

## Implemented choices

- **n8n owns the process.** Validation, policy checks, branching, HTTP integration, retries, and responses are visible on the canvas.
- **SQLite provides atomic state.** A primary-key event claim inside `BEGIN IMMEDIATE` prevents the lookup-then-insert race of a simple spreadsheet or naive table lookup. This choice replaces the earlier Data Table sketch with testable concurrent behavior.
- **The model is a bounded service.** A trusted prompt requests six fields; code independently enforces the schema. There are no model-controlled tools, URLs, or credentials.
- **Two classifier modes.** Deterministic fixtures make failure tests reproducible and free of API cost. A real Messages API branch is available for live verification. The acknowledgement reports the chosen mode.
- **Idempotency is scoped.** It covers the local event store and mock ticket API. A real vendor's API may have different idempotency behavior and would need independent validation.
- **A checkpoint precedes ticket creation.** Approved classification is persisted before the external-style write, supporting inspection after failure.
- **Acceptance follows durable state.** The final transaction creates the event outcome and the required queue/audit/outbox records. A failed state operation returns 503, then invokes the linked error handler.
- **Raw execution persistence is disabled.** n8n's success, failure, and manual execution data are not saved by this lab. Manual editor views can still temporarily show synthetic payloads and authentication metadata. The execution list may retain metadata without full node data.

## What the tests do not prove

1. **Claude model quality:** the 24 integration scenarios used fixtures. No live API call, accuracy benchmark, precision/recall evaluation, or model-output distribution was measured.
2. **Complete emergency detection:** regex rules are examples, not a reviewed emergency policy. They can miss paraphrases and trigger on negations or harmless context. A real system needs domain-approved escalation rules and human coverage.
3. **Complete anonymization:** masking covers configured email, telephone, government-ID, payment-number, supplied-name, and limited name-introduction patterns. It will not detect every name, address, language, or identifier. Synthetic data only.
4. **Prompt-injection immunity:** the precheck covers selected patterns. Prompt separation, no model tools, strict output checks, and human-review routing limit impact; a regex is not a complete attack detector.
5. **Calibrated confidence:** 0.75 is an illustrative routing threshold. A model's self-reported confidence is not a probability of correctness.
6. **Production hosting:** no TLS, production rate limiter, independent monitoring, managed backups, multi-tenant isolation, disaster recovery, security review, or load certification is supplied. Services bind to loopback for local use.
7. **Real notification delivery:** alerts are durable local mock outbox rows only. Email, Teams, Slack, Jira, and on-call delivery are not implemented.
8. **Automatic end-to-end replay:** a total process crash can leave an event in processing. Recovery tooling only reconciles an already committed ticket. It does not automatically repeat classification or create a replacement ticket.
9. **Selective retries:** n8n's Retry On Fail is configured for three total attempts, separated by one second. It retries all node errors, including permanent 4xx errors, within that bound. Production should distinguish permanent errors from 429/5xx and respect vendor Retry-After headers.
10. **Unlimited payload size handling:** the workflow enforces a 2,000-character message cap and a 12,000-character serialized-object cap. Framework parsing happens first. This is not an edge-level byte limit or denial-of-service defense.
11. **Universal error responses:** expected state failures have an explicit 503 path. A brand-new unhandled bug in another node may still produce a framework-specific response. Clients must require a valid disposition body and preserve the source ID when uncertain.
12. **Platform portability evidence:** Linux native execution was tested. The Docker Compose file and Windows/macOS launch instructions were reviewed, not executed in this environment. n8n Cloud requires reachable authenticated mock-service URLs.
13. **Business outcomes:** no real user adoption, production uptime, cost savings, reduced labor, or reduced response time is claimed.

## Production discussion topics

Use a tenant-scoped database key, reviewed schema, transactional outbox, vendor-specific idempotency strategy, lease ownership and replay controls, role-based access, TLS/secret rotation, production monitoring and backup recovery. Establish review ownership and escalation SLAs with the people doing the work. Measure routing quality and business outcomes on approved data before rollout.

These are future requirements and interview discussion points, not completed project features.

