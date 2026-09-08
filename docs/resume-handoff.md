# Accurate project facts for Claude résumé drafting

## Current verified state

- Independent synthetic proof lab with three n8n workflow definitions.
- Executed on n8n 2.37.10 with JavaScript Code nodes and HTTP integration.
- Python standard-library service and SQLite durable state.
- Atomic event claim, content-conflict handling, idempotent mock-ticket creation.
- Configured emergency/injection prechecks, input validation, pattern-based redaction, strict model-output validation, review routing.
- Bounded retries, saved classification checkpoint, durable audit/review/recovery records, local mock alert outbox, and linked error workflow.
- 24 integration scenarios passed against real n8n using fixture model responses; six rule-test groups passed.
- Real Claude Messages API branch implemented, but live use is not verified in the supplied evidence.
- No remote GitHub URL until Chris publishes the repository.

## Bullets supported now

- Built an n8n maintenance-intake proof lab with authenticated webhooks, JSON validation, deterministic review rules, structured-output checks, and mock ticket integration.
- Implemented atomic duplicate prevention and idempotent ticket writes with a Python/SQLite service; verified concurrent replays, timeout handling, partial writes, and recovery across 24 synthetic integration scenarios.
- Documented the workflow exports, acceptance criteria, architecture, operational runbook, test evidence, and known limitations for reproducible handoff.

Do not paste first-person project claims into an application before Chris has run the project and can explain the implementation. AI-assisted construction is legitimate; understanding and accurately describing the work are essential.

## After live Claude is verified

Only after the live checklist has evidence, add:

- Integrated Claude's Messages API for constrained maintenance classification, with independent schema validation and human-review routing for uncertain or flagged outputs.

Only after GitHub publication, add the actual repository URL and describe the project as published. Replace any test count if the final suite changes.

## Job-specific emphasis

| Target | Emphasize |
| --- | --- |
| Ingersoll Rand | Process decomposition, AI-assisted implementation, APIs, structured data, tests, Git, documented handoff |
| Foley | Transportation/business ownership alongside reliable automation, exception handling, human oversight, and integration work |
| Advance Local / Catalyst IQ | Practical workflow building, data cleanup, iteration, explicit failure behavior, documentation |

This project is property-maintenance themed. Do not relabel it as a trucking or procurement deployment. The operational concepts transfer; the business-domain story comes from Chris's real owner-operator experience.

## Prohibited embellishments

Do not claim production deployment, live Zendesk/Yardi/Jira/Power BI/Supabase usage, real notifications, resident data, employer affiliation, calibrated AI accuracy, measured labor savings, cost savings, enterprise scale, or years of professional n8n experience.

