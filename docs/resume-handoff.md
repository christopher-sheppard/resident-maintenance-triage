# Verified project facts

## Current verified state

- Independent synthetic proof lab with three n8n workflow definitions.
- Executed on n8n 2.37.10 with JavaScript Code nodes and HTTP integration.
- Python standard-library service and SQLite durable state.
- Atomic event claim, content-conflict handling, idempotent mock-ticket creation.
- Configured emergency/injection prechecks, input validation, pattern-based redaction, strict model-output validation, review routing.
- Bounded retries, saved classification checkpoint, durable audit/review/recovery records, local mock alert outbox, and linked error workflow.
- 24 integration scenarios passed against real n8n using fixture model responses; six rule-test groups passed.
- Live Claude Messages API classification verified by Chris through mock ticket creation; emergency bypass and duplicate replay also demonstrated. See `evidence/live-claude-results.md` for the user-supplied evidence and limits.
- No remote GitHub URL until Chris publishes the repository.

## Bullets supported now

- Built an n8n maintenance-intake proof lab with authenticated webhooks, JSON validation, deterministic review rules, structured-output checks, and mock ticket integration.
- Implemented atomic duplicate prevention and idempotent ticket writes with a Python/SQLite service; verified concurrent replays, timeout handling, partial writes, and recovery across 24 synthetic integration scenarios.
- Documented the workflow exports, acceptance criteria, architecture, operational runbook, test evidence, and known limitations for reproducible handoff.

This is an AI-assisted portfolio project. The evidence supports only the observed behaviors and stated limitations.

## Live integration bullet supported by the recorded demonstrations

The user-observed live runs support:

- Integrated Claude's Messages API for constrained maintenance classification, with independent schema validation and human-review routing for uncertain or flagged outputs.

Only after GitHub publication, add the actual repository URL and describe the project as published. Replace any test count if the final suite changes.

## Scope

This is a synthetic property-maintenance portfolio lab, not an employer deployment.

## Prohibited embellishments

Do not claim production deployment, live Zendesk/Yardi/Jira/Power BI/Supabase usage, real notifications, resident data, employer affiliation, calibrated AI accuracy, measured labor savings, cost savings, enterprise scale, or years of professional n8n experience.

