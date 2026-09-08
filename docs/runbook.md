# Operator runbook

## Before a demo

1. Start the lab and wait for the ready message.
2. Run `python3 scripts/demo.py routine` and `python3 scripts/demo.py emergency`.
3. Confirm the routine result records a mock ticket and the emergency result records review with `model_mode: none`.
4. Check `python3 scripts/demo.py snapshot`. Local alerts have `delivery: mock_outbox`; there is no real on-call notification.
5. Decide whether the demo uses fixture or live Claude, and say which before showing the result.

## Interpret an outcome

| State | Operator action |
| --- | --- |
| `ticket_created` | Inspect the mock ticket ID. No real ticketing system or repair has been triggered. |
| `human_review` | Inspect the corresponding review record and reason; decide how a real organization would assign an owner. |
| `manual_recovery` | Inspect the checkpoint and any existing ticket before further action. |
| `in_progress` | An execution already owns the ID. Wait and inspect; do not change the ID to force another ticket. |
| `unconfirmed` / unexpected body | Do not assume success. Preserve the event ID and inspect state. |
| `ID_CONTENT_CONFLICT` | Same ID arrived with different content. Resolve the source issue instead of silently overwriting it. |

## Inspect state without exposing credentials

The quick snapshot command prints counts and recent event states. For detailed synthetic records, run this in a Python shell from the project directory:

```python
import sys
sys.path.insert(0, 'scripts')
from client import call
code, snapshot = call('/admin/snapshot')
event_id = 'PASTE_THE_SYNTHETIC_EVENT_ID'
for table in ('events', 'tickets', 'reviews', 'dead_letters', 'alerts'):
    print(table, [r for r in snapshot['tables'][table] if r.get('event_id') == event_id])
```

The client adds the local secret internally. Do not share `.env`, `.local/credentials.json`, raw n8n logs, or the database.

## Recover after a partial ticket write

1. Stop the failing condition. In the fixture lab, return faults to normal with the client call below.
2. Inspect the event ID, saved classification, ticket table, and error record.
3. If a ticket exists and the event is in manual recovery, reconcile that existing ticket:

```python
call('/admin/faults', {'model': 'normal', 'ticket': 'normal', 'finish': 'normal'})
code, result = call('/admin/recover-ticket', {'event_id': event_id})
print(code, result)
```

This operation does not call Claude or create a ticket. It records the existing ticket as the final outcome and resolves the local recovery/review records. Replaying the original event then returns the recovered disposition.

If no ticket exists, the command refuses to reconcile. Leave the event in manual recovery for review. An automated resume that creates a new ticket after all attempts failed is deliberately not implemented in v1.

## Rehearse a controlled failure

Do this only in the local synthetic lab, without a simultaneous demo:

```python
call('/admin/faults', {'ticket': 'unavailable'})
```

Send a fresh routine request with the demo command. Expect three ticket attempts followed by a durable recovery outcome. Restore normal behavior:

```python
call('/admin/faults', {'ticket': 'normal'})
```

The integration suite tests the other fault modes and always attempts to restore normal settings in its cleanup block. After an interrupted test run, explicitly reset all three settings using the first recovery command above.

## Limits of recovery

Claims are not automatically stolen or expired. If the n8n process dies mid-execution, an event may remain `processing`; inspect it manually. This favors avoiding duplicate writes over automatic progress. A complete database outage also prevents the linked error handler from saving its records. The local process logs are then the fallback evidence. An independent monitoring channel would be needed in production.

