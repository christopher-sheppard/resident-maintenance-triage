# Run the demo

Start the lab using [setup](setup.md), then run these commands from a second terminal in the repository root. All requests are synthetic. The default classifier uses fixtures; live Claude is optional.

| Command | Expected behavior |
| --- | --- |
| `python3 scripts/demo.py routine` | A valid fixture classification creates a mock ticket, HTTP 201. |
| `python3 scripts/demo.py emergency` | A configured gas indicator records human review, HTTP 202, with `model_mode: none`. |
| `python3 scripts/demo.py ambiguous` | The fixture returns insufficient information; the workflow records review. |
| `python3 scripts/demo.py duplicate` | First delivery creates a ticket; replay returns HTTP 200, `duplicate: true`, and the same ticket ID. |
| `python3 scripts/demo.py snapshot` | Shows local record counts, counters, and recent event states. |

For live mode, follow [Claude setup and verification](live-claude-checklist.md). A live classification may request human review; it is not required to reproduce a fixture answer. Inspect `status`, `reason`, and `model_mode`, not only the HTTP code.

## Controlled failure

In a fixture lab with no other demo running:

```bash
python3 scripts/demo.py failure
```

This temporarily makes the mock ticket service unavailable. Bounded retries end in a durable recovery record; the client then restores normal ticket behavior. See the [operator runbook](runbook.md) for inspection and reconciliation.

A mock ticket is a local record, not a repair or dispatch. Review and alert records do not notify a real person. See [test evidence](../evidence/README.md) for recorded fixture and live outcomes.
