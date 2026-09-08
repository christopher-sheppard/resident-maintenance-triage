# Five-minute interview demonstration

## Before opening the screen share

Run the lab once, verify the model mode, and keep it running. Open the main workflow canvas and a second terminal. Close credential screens. Use the project name rather than employer branding.

## Minute 1 — explain the problem

“I built this to explore how maintenance intake could become a more reliable business workflow. It receives a request, checks the input, identifies cases that need human review, creates a mock ticket for approved cases, and records what happened. All the data and ticket-system integrations are synthetic.”

If using fixtures, add: “For repeatable failure testing, this demo uses a simulated model response. I also implemented a separate Claude API branch.” If you have verified real Claude, say exactly which call you tested.

## Minute 2 — show one ordinary request

Run `python3 scripts/demo.py routine`. Show the response, source event ID, trace ID, and mock ticket ID.

Explain: “The language model only gets the minimized maintenance text. Its JSON still has to pass type, category, urgency, flag, and confidence checks. The ticket payload is checkpointed before the write.”

Point to the model node, validation node, and ticket HTTP request on the canvas. Do not claim a real Zendesk ticket was created.

## Minute 3 — show the emergency branch

Run `python3 scripts/demo.py emergency`.

Explain: “This rule runs before the model. A configured gas indicator goes to human review without asking an LLM whether the situation is important. These are demo rules; an actual deployment would use the organization's approved emergency policy.”

Show `model_mode: none`. Explain that the review queue is implemented but alert delivery is a mock outbox.

## Minute 4 — explain duplicates and failure

Open the test result for eight concurrent replays. Explain: “Checking a table and inserting later can race. The state service atomically claims the event ID, so one execution owns it. A duplicate gets the existing status. The ticket API also recognizes the same ID, which matters if a write succeeds but its response gets lost.”

Show the failure-recovery evidence. Explain: “The project does not declare success when state is uncertain. It preserves the event ID and existing ticket so an operator can reconcile the failed step.”

## Minute 5 — explain the handoff

Show the repository's workflow exports, source rules, acceptance criteria, test report, and runbook.

“I used AI assistance to build and review this, and I verified the behavior with tests. The most useful part was making the failure paths explicit. My operations background makes me think about exceptions, ownership, duplicate work, and what the next person needs when something goes wrong.”

## Questions to practice

1. Why use a deterministic safety gate before Claude?
2. Why is lookup-then-insert weaker than an atomic claim?
3. What if the ticket was created but the HTTP response failed?
4. Does a confidence of 0.94 mean 94 percent accuracy? No; it is uncalibrated model output.
5. What does the Error Trigger do, and can it answer the original webhook? It starts separately; the main flow owns the original response.
6. What actually happens on human escalation here? Local records and a mock outbox; no real dispatcher is notified.
7. What still needs work for production? Reviewed policy, better PII handling, vendor integration testing, real monitoring, access controls, and durable recovery procedures.
8. What did you personally learn or change while using AI assistance? Explain a real decision from your own rehearsal and code review.

