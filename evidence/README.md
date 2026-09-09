# Test evidence

These records describe separate verification events, not one combined benchmark.

| Record | Scope |
| --- | --- |
| [integration-results.json](integration-results.json) | Chris's machine: 24 passing real-n8n scenarios using fixture model responses, September 8, 2026 at 19:00 UTC. Not rerun during the later source update. |
| [update-verification.json](update-verification.json) | Source update: eight JavaScript tests, three generated-export checks, and offline request parity against the published node. No paid API calls or new integration run. |
| [live-claude-results.md](live-claude-results.md) | Chris's observed live classification, emergency bypass, and duplicate demonstrations, with outcome details and provenance. |

The original fixture build also passed 24 scenarios. Its [original evidence remains in Git history](https://github.com/christopher-sheppard/resident-maintenance-triage/tree/83958d791f50833028aeb0a17b94f29e5821ec36/evidence). The [pre-cleanup snapshot](https://github.com/christopher-sheppard/resident-maintenance-triage/tree/a7f7a8d/evidence) retains the historical preparation reports and checksum manifests.

Native Linux execution is the verified runtime path. Docker Compose is an optional configuration that has not been executed successfully in the recorded checks; no Docker verification is claimed. Neither fixture checks nor the small live demonstration set establish production readiness, model accuracy, or business savings.

The screenshot shows the workflow structure, not an execution trace. Raw executions, credentials, runtime files, and databases are excluded. The portable workflow defaults to fixture mode.
