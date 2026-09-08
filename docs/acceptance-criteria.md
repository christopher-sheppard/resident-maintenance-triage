# Acceptance criteria

This is an independent synthetic proof lab. It does not represent an employer's systems or policies.

- Authenticated POST intake accepts only the documented synthetic JSON contract.
- Invalid input returns a controlled 4xx with no ticket or model call.
- An atomic event claim prevents concurrent duplicates; changed content under the same ID returns 409.
- Configured emergency indicators bypass the model and persist a human-review item.
- The model receives minimized, redacted text; model output is independently validated.
- Low confidence, emergency classification, policy flags, malformed output, and model failures never reach normal ticket creation.
- The mock ticket API is idempotent, including response loss after a committed ticket write.
- Accepted outcomes are returned only after durable storage succeeds.
- Human-review and recovery queues are real records; notifications are explicitly a local mock outbox.
- The error workflow handles unexpected production-webhook failures without copying raw error text or stack traces.
- Repeatable fixtures cover the happy path and adverse paths. Live Claude evidence is reported separately.
- Workflow JSON, source, setup, requirements, diagrams, evidence, runbook, and interview notes are versioned.

