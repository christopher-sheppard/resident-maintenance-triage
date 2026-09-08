"""Create local credentials and workflow copies without placing secrets in exports."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--native', action='store_true', help='Use localhost service URLs for the native test runner')
args = parser.parse_args()
local = ROOT / '.local'
local.mkdir(exist_ok=True)
envfile = ROOT / '.env'
if not envfile.exists():
    envfile.write_text(f'LAB_API_KEY={secrets.token_hex(24)}\nN8N_ENCRYPTION_KEY={secrets.token_hex(32)}\nN8N_VERSION=2.37.10\n')
    envfile.chmod(0o600)
env = dict(line.strip().split('=', 1) for line in envfile.read_text().splitlines() if line.strip() and not line.startswith('#') and '=' in line)
if len(env.get('LAB_API_KEY', '')) < 24 or env.get('LAB_API_KEY') == 'GENERATE_LOCALLY':
    raise SystemExit('The existing .env has placeholder secrets. Rename it, then rerun configure.py.')
credentials = [
    {'id': 'LabHeaderAuthV1', 'name': 'Synthetic Lab Header', 'type': 'httpHeaderAuth',
     'data': {'name': 'X-Lab-Key', 'value': env['LAB_API_KEY']}},
    {'id': 'ClaudeHeaderAuthV1', 'name': 'Claude API Key', 'type': 'httpHeaderAuth',
     'data': {'name': 'x-api-key', 'value': 'NOT_CONFIGURED_USE_N8N_CREDENTIAL_EDITOR'}},
]
credfile = local / 'credentials.json'
# Preserve a configured Claude credential on repeat setup; import only when intentionally initializing.
if not credfile.exists():
    credfile.write_text(json.dumps(credentials, indent=2))
    credfile.chmod(0o600)
command = [sys.executable, str(ROOT / 'scripts/build_workflows.py'), '--output', str(local / 'workflows')]
if args.native:
    command += ['--lab-base', 'http://127.0.0.1:8080', '--ticket-url', 'http://127.0.0.1:5678/webhook/mock-maintenance-ticket']
subprocess.run(command, check=True)
print('Local configuration ready. Secrets are in ignored files; their values were not printed.')

