# Evidence provenance

These records describe different verification events, not one combined benchmark.

| Evidence | Scope | Status |
| --- | --- | --- |
| `original-build-integration-results.json` | Original real-n8n fixture run, 2026-09-08T06:08:15.389088+00:00 | 24 passed, 0 failed |
| `integration-results.json` | Existing machine fixture report, 2026-09-08T19:00:47.921090+00:00 | 24 passed, 0 failed; preserved, not rerun during this update |
| `original-build-verification-summary.json` and `verification-summary.json` | Historical original-build snapshot and hashes | Not a checksum manifest for the updated source |
| `live-claude-results.md` | User-observed routine, emergency and duplicate demonstrations reviewed by Codex | Separate live evidence; not an accuracy evaluation |
| `update-verification.json` | This source update: six policy tests, two request-contract tests, export consistency and offline saved-node parity | Eight tests passed; no paid API calls or live fault tests |

The update handoff reports that the same fix passed 24 fixture integration scenarios in a separate Codex lab. A separate run log for that updated-fix run was not supplied; it is not presented as a newly executed local test.

The live demonstration record was corroborated against selected saved outcomes for exec-46, exec-48 and exec-49. This update did not rerun paid classification. Raw executions, credentials, private runtime files and uploaded editor exports are excluded. The portable workflow remains in fixture mode.

Historical fixture reports and their original hashes are retained unchanged. This update's received-payload hashes are recorded separately in `update-verification.json`.

## Verification scope for this update

The required source checks use the existing native Node/Python path. Docker is an optional alternative described in [setup details](../docs/setup.md#docker-compose-alternative), not a mandatory gate for this source update. The automatic workspace verifier selected Compose from the presence of `compose.yaml`; that selection does not replace the project-specific verification instructions.

Keep these results separate:

- Previously recorded native real-n8n fixture integration: 24 scenarios passed; not rerun during this source-only update.
- User-observed live Claude demonstrations: mock ticket creation, emergency bypass and duplicate replay, with the supplied provenance.
- Current source checks: eight JavaScript tests and three export checks passed.
- Docker verification: blocked by Docker API socket permissions before any build, container tests or readiness check; see `docker-verification-blocked.json`. Neither Docker nor full workspace verification is claimed as passed.

No refresh, workflow import, permission change or fault test against the private live instance was performed.
