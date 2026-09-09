# Integration test coverage

The retained fixture run at `2026-09-08T19:00:47.921090+00:00` recorded **24 passed, 0 failed** in real n8n 2.37.10. See [the report](../evidence/integration-results.json) for individual timings and [evidence provenance](../evidence/README.md) for scope.

| Scenario | Result |
| --- | --- |
| Routine request through real n8n and mock ticket webhook | PASS |
| Duplicate returns existing disposition without another model call | PASS |
| Changed content under reused ID is rejected | PASS |
| Eight concurrent replays create one ticket | PASS |
| Missing webhook authentication rejected | PASS |
| Malformed JSON rejected by n8n ingress | PASS |
| Missing source event ID rejected | PASS |
| Non-synthetic input rejected | PASS |
| Unknown field rejected | PASS |
| Unknown property rejected | PASS |
| Oversized message rejected | PASS |
| Stale timestamp rejected | PASS |
| Gas emergency bypasses the model | PASS |
| Injection indicator bypasses the model | PASS |
| Ambiguous model result routes to human review | PASS |
| Malformed model output routes to human review | PASS |
| Model emergency cannot create a routine ticket | PASS |
| Known PII patterns excluded from stored records | PASS |
| Transient model 429 succeeds on bounded retry | PASS |
| Permanent model failure retries three times then records recovery | PASS |
| Model timeout retries three times then records recovery | PASS |
| Ticket response lost after commit does not duplicate the ticket | PASS |
| Ticket API failure preserves checkpoint and recovery record | PASS |
| Unexpected error triggers linked workflow and supports reconciliation | PASS |

Eight JavaScript tests (six policy tests and two request-contract tests) also passed during the source update. Fixture tests do not measure live model accuracy. [Live demonstrations](../evidence/live-claude-results.md) are recorded separately.

Raw malformed JSON and authentication failures can be rejected by n8n before the workflow starts; those do not create workflow-owned audit records. Invalid input that reaches the validation node attempts a safe audit write. If that audit write fails, the request is still rejected; no successful audit claim is made.
