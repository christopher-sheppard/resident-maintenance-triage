# Live Claude demonstration evidence

Recorded September 9, 2026 UTC (September 8 local evening in California).
Evidence provenance: Chris supplied terminal responses and node 11 response data in this conversation, followed by the published workflow export. These are user-observed live runs, reviewed by Codex; Codex did not independently execute these paid API calls. No raw execution export or credentials are included.

Model: `claude-haiku-4-5-20251001`. User-reported runtime: Node 24.19.0, n8n 2.37.10, Linux.

| Scenario | Observed response | Interpretation |
| --- | --- | --- |
| Routine, exec-46 | HTTP 201; live_claude; VALIDATED_CLASSIFICATION; ticket_created; MOCK-3818158E2F6D | Live classification passed local validation and produced a mock ticket. |
| Emergency, exec-48 | HTTP 202; model_mode none; DETERMINISTIC_EMERGENCY; human_review | Emergency rule bypassed the model and recorded local review. No person notified. |
| Duplicate first delivery, exec-49 | HTTP 201; live_claude; VALIDATED_CLASSIFICATION; MOCK-1ADB25028C74 | First delivery created a mock ticket. |
| Identical replay | HTTP 200; duplicate true; same ticket and original trace exec-49 | Original disposition returned for the replay. The trace is the stored original trace, not an independently identified replay execution. |

Earlier live runs returned MODEL_INVALID_JSON because the model wrapped JSON in Markdown fences. Node 09 now requests output_config.format with a JSON schema. Node 12 continues to independently enforce the strict local contract; no permissive fence-stripping workaround was introduced.

Export review: 35 nodes; topology matches source; no pinned data; execution saving disabled; no literal Anthropic API key found. The uploaded node 09 and generated node 09 produced deeply equal request objects in both fixture and live modes. Personal runtime URLs and live-mode configuration are kept out of the portable public default.

These demonstrations are distinct from the 24 real-n8n integration scenarios using simulated classifier responses and six policy test groups. They establish working live integration for these examples, not an accuracy rate, exhaustive safety coverage, production readiness, real dispatch, or measured savings.
