# Start here — interview setup

The project files are built. Your remaining steps are to start the lab on your computer, connect your own Claude API credential if you want live AI, rehearse, and publish your repository.

## 1. Open a terminal in this folder

Unzip the project. Open the `resident-maintenance-triage` folder in VS Code or your editor, then open its terminal.

Check:

```bash
node --version
python3 --version
```

On Windows, use `python --version`. Use Node 22 or 24 and Python 3.10 or newer. If a command is missing, install that runtime from its official website before continuing. You already use Node for app development; check the installed version before installing another copy.

## 2. Install the pinned n8n version

```bash
npm install --prefix .local/n8n n8n@2.37.10 --no-audit --no-fund
```

This is a project-local install. It may take several minutes and needs internet access. It does not replace another globally installed n8n version.

## 3. Start the complete lab

Mac or Linux:

```bash
python3 scripts/run_native.py --n8n-script .local/n8n/node_modules/n8n/bin/n8n
```

Windows:

```powershell
python scripts/run_native.py --n8n-script .local/n8n/node_modules/n8n/bin/n8n
```

The runner generates private local secrets, creates the database, imports three workflows, publishes them, and starts n8n plus the mock services. No n8n Cloud account is required. Leave this terminal open.

Wait for **Lab ready**, then open `http://localhost:5678` in your browser. Complete the local n8n owner-login setup if prompted. Do not run another n8n instance on ports 5678 or 8080 at the same time.

## 4. Run a maintenance request

Open another terminal in the project folder:

```bash
python3 scripts/demo.py routine
```

Again, Windows uses `python`. You should see HTTP 201, `ticket_created`, a mock ticket ID, and `model_mode: fixture`. This is a working workflow with a simulated classifier.

Then run:

```bash
python3 scripts/demo.py emergency
python3 scripts/demo.py ambiguous
python3 scripts/demo.py duplicate
python3 scripts/demo.py failure
python3 scripts/demo.py snapshot
```

The emergency should show `human_review` and `model_mode: none`. The ambiguous request should show `human_review` with `model_mode: fixture`. The duplicate demo sends the identical request twice and prints the same ticket ID. The failure demo temporarily disables the local mock ticket endpoint, verifies the recovery response, and restores normal behavior.

## 5. Add live Claude

Use `docs/live-claude-checklist.md`. Add the API key in the **Claude API Key** credential, set `live_claude` to `true` in node **02 Validate and trace**, and publish. Run the routine sample again and confirm `model_mode: live_claude` with a valid disposition.

The chat subscription does not include API credits. If you do not have an API account yet, the local fixture demo is fully usable while you set one up. Do not label the fixture response as live AI.

## 6. Rehearse for 30 minutes

Follow `docs/interview-demo.md`. Practice routine intake, emergency bypass, duplicate prevention, and failure recovery. Explain why each control exists in your own words.

## 7. Put the project in GitHub

Follow `docs/github-handoff.md`. The archive includes a Git history bundle if you want to preserve the actual development commits. Upload source, workflow exports, documentation, and sanitized evidence. Keep `.env`, `.local`, databases, raw logs, and credentials out of Git.

The final résumé wording depends on whether you completed live Claude verification. Use `docs/resume-handoff.md` to give Claude accurate facts.

## Stopping and restarting

Press Ctrl+C in the first terminal. Restart with the same command when needed. Your local workflow edits and database persist. Do not add `--refresh` during normal use: that deliberately replaces the three lab workflows with generated source versions.
