# Project instructions

This repository is a synthetic n8n portfolio lab. Preserve the default fixture mode and do not add real resident data, employer branding, credentials, or live external writes.

- n8n owns orchestration and policy; the Python service owns durable state and test doubles.
- JavaScript source lives in `src`. Regenerate workflow JSON with `python3 scripts/build_workflows.py` when source changes.
- Keep generated definitions deterministic and imports self-contained.
- Use `node --test tests/policy.test.cjs` for policy changes. Run the real n8n integration suite when changing routing, API interactions, state, retries, or recovery.
- Update evidence only from actual test runs. Label simulated-model results separately from live Claude results.
- Never commit `.env`, `.local`, credentials, databases, raw execution data, or secret-bearing logs.
- Do not claim production deployment, measured accuracy, savings, or live integrations absent evidence.
- Preserve the explicit 503 response before Stop and Error on state failures. The separate error workflow cannot answer the original webhook.

