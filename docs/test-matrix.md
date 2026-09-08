# Observed integration results

Actual n8n 2.37.10 run: 2026-09-08T06:08:15.389088+00:00

**24 passed, 0 failed. Classifier mode: deterministic fixture. Live Claude: not verified.**

| Scenario | Result | Runtime (seconds) |
| --- | --- | --- |
| Routine request through real n8n and mock ticket webhook | PASS | 0.877 |
| Duplicate returns existing disposition without another model call | PASS | 0.223 |
| Changed content under reused ID is rejected | PASS | 0.184 |
| Eight concurrent replays create one ticket | PASS | 1.493 |
| Missing webhook authentication rejected | PASS | 0.021 |
| Malformed JSON rejected by n8n ingress | PASS | 0.03 |
| Missing source event ID rejected | PASS | 0.319 |
| Non-synthetic input rejected | PASS | 0.348 |
| Unknown field rejected | PASS | 0.452 |
| Unknown property rejected | PASS | 0.135 |
| Oversized message rejected | PASS | 0.156 |
| Stale timestamp rejected | PASS | 0.12 |
| Gas emergency bypasses the model | PASS | 0.157 |
| Injection indicator bypasses the model | PASS | 0.142 |
| Ambiguous model result routes to human review | PASS | 0.159 |
| Malformed model output routes to human review | PASS | 0.18 |
| Model emergency cannot create a routine ticket | PASS | 0.302 |
| Known PII patterns excluded from stored records | PASS | 0.385 |
| Transient model 429 succeeds on bounded retry | PASS | 1.455 |
| Permanent model failure retries three times then records recovery | PASS | 2.389 |
| Model timeout retries three times then records recovery | PASS | 9.901 |
| Ticket response lost after commit does not duplicate the ticket | PASS | 1.487 |
| Ticket API failure preserves checkpoint and recovery record | PASS | 2.912 |
| Unexpected error triggers linked workflow and supports reconciliation | PASS | 3.337 |

These durations are single local fixture measurements, not production performance or live-model benchmarks.
The six JavaScript rule-test groups also passed. See `tests/policy.test.cjs`.

Raw malformed JSON and authentication failures can be rejected by n8n before the workflow starts; those do not create workflow-owned audit records. Invalid input that reaches the validation node attempts a safe audit write. If that audit write fails, the request is still rejected; no successful audit claim is made.
