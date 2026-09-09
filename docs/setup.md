# Setup details

## Start locally

From the repository root, with Node.js 24 and Python 3.10 or newer:

```bash
npm install --prefix .local/n8n n8n@2.37.10 --no-audit --no-fund
python3 scripts/run_native.py --n8n-script .local/n8n/node_modules/n8n/bin/n8n
```

Wait for **Lab ready**, then open `http://localhost:5678`. Complete the local n8n owner login if prompted. Keep the terminal open; use another terminal for [demo requests](demo.md). No n8n Cloud account or paid API credential is needed for fixture mode.

Press Ctrl+C to stop the lab. Start it again with the same command; your local configuration and data persist. Avoid `--refresh` during normal restarts because it replaces workflow definitions, including editor changes. Ports 5678 and 8080 must be free before startup.

On Windows, substitute `python` for `python3`. Linux is the tested platform; Windows and macOS launch instructions have not been verified here.

## Verified native path

Validation used the actual n8n 2.37.10 runtime on Linux, with Node 24.19.0 and Python 3.12.13. The native runner starts child processes together and binds them to loopback only. No Docker engine was available in the build environment.

Native state and secrets are in `.local/` and `.env`. The bootstrap imports the exported workflows into its own n8n database. It does not alter another instance. IDs are stable within this lab; avoid importing the same IDs into an unrelated instance without reviewing them.

The initial **Claude API Key** credential contains a nonfunctional placeholder. The default workflow uses the fixture branch, so that placeholder is not sent to Anthropic. Configure the credential through the n8n editor when ready.

## Docker Compose alternative

The Compose file is provided and its configuration was statically reviewed. **It was not executed in the build environment.** Use the native path first; Docker is optional.

Install Docker Desktop from the official Docker website, start it, and use:

```bash
python3 scripts/configure.py
docker compose up -d --build
docker compose logs -f n8n
```

Windows uses `python`. After startup, use the same `scripts/demo.py` commands. Stop with:

```bash
docker compose down
```

Do not append `-v` unless you deliberately want to delete this lab's named volumes and stored data.

The initialization container imports credentials and publishes all three workflows. It has root access only inside the project's initialization container so it can read the generated private credential file; it sets ownership of the resulting n8n volume back to the normal n8n user. The main n8n and Python containers run as non-root users. Ports bind to `127.0.0.1`.

## n8n Cloud

The workflow logic uses standard nodes, but the default exports target local mock services. A Cloud instance cannot reach `localhost` on your laptop. To move this version to Cloud, host the mock service behind authenticated HTTPS, change the two service URLs in node 02 and the supporting workflows, configure credentials, import all three workflows, relink the error workflow if its ID changes, and publish all three.

That hosting work is optional for this local demo. The public GitHub repository can contain the exports and evidence without an always-on endpoint.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| n8n command missing | Use the provided `--n8n-script` path after the project-local npm install |
| Python command missing | Try `python` on Windows or install Python from python.org |
| Initialization fails | Inspect `.local/native-init.log`; keep the log private |
| Port already in use | Stop the other local lab or n8n process before starting this one |
| Webhook 404 | Wait for the runner's ready message and verify the workflow is published |
| Webhook 401/403 | Use the demo client; verify the imported Lab Header credential matches `.env` |
| Timestamp rejected | Regenerate the payload with the demo client; replays must retain the original timestamp |
| Live model goes to recovery | Inspect the Claude credential and API credits, selected model, timeout, and exact model response in a synthetic manual run |
| Empty or unexpected response | Treat it as unconfirmed. Check JSON `status`, inspect safe event state, and preserve the event ID |

## Rebuilding exports after edits

`python3 scripts/build_workflows.py` regenerates source exports. `run_native.py --refresh` reimports those generated definitions into **this** native lab and preserves credentials. Export or commit intentional UI changes first; otherwise a refresh replaces them.

Normal `run_native.py` starts the existing workflows and keeps your UI configuration. Stop all local lab processes before running the integration suite with its own runner.

