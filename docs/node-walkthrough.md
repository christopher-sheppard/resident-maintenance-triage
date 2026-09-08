# Walk the canvas from intake to response

| Node or decision | What to explain in the interview |
| --- | --- |
| 01 Authenticated maintenance intake | A POST webhook starts one execution. Header Auth rejects callers without the local lab credential. |
| 02 Validate and trace | Explicit fields, supported property, size, types, synthetic marker, and time window. A trace ID ties the request to the execution. This node also owns trusted configuration. |
| Input valid? | A rejected request receives an explicit response and does not call the model. Framework-level malformed JSON/auth failures may occur before these nodes. |
| 03 Minimize and redact | Keep only required fields. Mask known personal-data patterns. Compute a content fingerprint before discarding raw text. |
| 04–05 Atomic event claim | Ask durable storage to create one ownership record. A database constraint handles concurrent arrivals. The check prevents proceeding after storage failure. |
| Claim acquired? | New owner proceeds. A replay returns prior status; another active owner returns in-progress; changed content returns conflict. |
| 06–07 Deterministic safety gate | Configured emergency or injection indicators go to human review without a model call. |
| 09–10 Bounded model request | Trusted system instructions plus untrusted message data. Choose fixture or live Claude from configuration, never from the incoming request. |
| 11 Model call | An HTTP request uses a credential and a token budget. At most three attempts. The fixture timeout is shorter to make failure rehearsal quick. |
| 12 Validate model and route | Parse plain JSON; check six fields, values, confidence, flags, and completion status. A model answer is only a suggestion until these checks pass. |
| 13 Approved for ticket? | Human review for low confidence, unknown category, emergency urgency, review flags, invalid output, or policy flags. API failures go to recovery. |
| 14–15 Checkpoint | Save the approved classification before writing a ticket. Operators can inspect the exact approved payload after a downstream failure. |
| 16 Call mock ticket API | A real HTTP call reaches a second n8n webhook. That workflow delegates the atomic ticket insert to the local service. |
| 17 Inspect ticket result | Require a synthetic ticket ID and confirmation. A failed write never becomes a success acknowledgement. |
| 18–20 Commit outcome | Transactionally persist outcome, audit metadata, and any review, recovery, or mock alert records. |
| 21 Accurate acknowledgement | Tell the caller what was actually recorded. No promise that a repair or real dispatch occurred. |
| Respond unconfirmed / Stop and Error | If durable state cannot be confirmed, return 503 and activate the separately linked error workflow. |

## What the model returns

Exactly `category`, `urgency`, `confidence`, `summary`, `human_review_required`, and `policy_flags`.

The default confidence threshold is 0.75. It is a demo routing threshold, not a measured accuracy boundary. Model self-confidence is not calibrated. Emergency cues and schema validation remain separate controls.

## Why there is some code in a low-code tool

The workflow canvas communicates the process and controls the integrations. Short JavaScript functions make validation and policy rules precise and reviewable. The small Python service supplies state and test doubles. Each part has a clear job, and the exported workflow can be inspected without the helper source at runtime.

