"""Local rehearsal runner when Docker is unavailable. Requires installed n8n 2.37.10."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--n8n', default='n8n', help='Path to installed n8n executable')
parser.add_argument('--n8n-script', help='Run a Node.js n8n entrypoint directly (cross-platform)')
parser.add_argument('--test', action='store_true', help='Run the integration suite, then stop the lab')
parser.add_argument('--refresh', action='store_true', help='Reimport source workflows into this lab; preserves credentials')
args = parser.parse_args()
command_prefix = ['node', args.n8n_script] if args.n8n_script else [args.n8n]
subprocess.run([sys.executable, str(ROOT/'scripts/configure.py'), '--native'], check=True)
env = os.environ.copy()
env.update(dict(line.split('=',1) for line in (ROOT/'.env').read_text().splitlines() if '=' in line and not line.startswith('#')))
env.update({'N8N_USER_FOLDER':str(ROOT/'.local/native-state'),'N8N_DIAGNOSTICS_ENABLED':'false',
    'N8N_VERSION_NOTIFICATIONS_ENABLED':'false','N8N_PERSONALIZATION_ENABLED':'false','N8N_SECURE_COOKIE':'false',
    'N8N_HOST':'localhost','N8N_LISTEN_ADDRESS':'127.0.0.1','N8N_PORT':'5678','WEBHOOK_URL':'http://localhost:5678/',
    'NODE_FUNCTION_ALLOW_BUILTIN':'crypto','GENERIC_TIMEZONE':'America/New_York','TZ':'America/New_York',
    'LAB_DB':str(ROOT/'.local/native-lab.sqlite'),'LAB_HOST':'127.0.0.1','LAB_PORT':'8080',
    'EXECUTIONS_DATA_SAVE_ON_ERROR':'none','EXECUTIONS_DATA_SAVE_ON_SUCCESS':'none','EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS':'false'})
local = ROOT/'.local'
marker = local/'native-initialized'
with (local/'native-init.log').open('w') as log:
    if not marker.exists() or args.refresh:
        commands=[] if marker.exists() else [['import:credentials','--input='+str(local/'credentials.json')]]
        commands += [['import:workflow','--separate','--input='+str(local/'workflows')],
                     ['publish:workflow','--id=MaintenanceErrorsV1'],
                     ['publish:workflow','--id=MockTicketsV1'],['publish:workflow','--id=MaintenanceTriageV1']]
        for command in commands:
            result = subprocess.run(command_prefix+command, env=env, stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                raise SystemExit('n8n initialization failed. See .local/native-init.log (keep logs private).')
        marker.touch()
procs=[]
logs=[]
try:
    for name, cmd in [('lab',[sys.executable,str(ROOT/'lab/server.py')]),('n8n',command_prefix+['start'])]:
        log=(local/f'{name}.log').open('w');logs.append(log)
        procs.append(subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT))
    for _ in range(90):
        if any(p.poll() is not None for p in procs):
            raise SystemExit('A lab service exited; inspect .local/lab.log or .local/n8n.log.')
        try:
            urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=1)
            # Healthz can be ready before webhook registration. An auth rejection
            # proves each published route has actually been installed.
            for route in ('maintenance','mock-maintenance-ticket'):
                req=urllib.request.Request('http://127.0.0.1:5678/webhook/'+route,data=b'{}',headers={'Content-Type':'application/json'})
                try:
                    urllib.request.urlopen(req,timeout=1)
                    raise RuntimeError('Expected webhook authentication')
                except urllib.error.HTTPError as exc:
                    if exc.code not in (401,403):raise
            print('Lab ready: http://localhost:5678 . Use another terminal for scripts/demo.py. Ctrl+C stops it.',flush=True)
            break
        except Exception:
            time.sleep(1)
    else:
        raise SystemExit('Startup timed out. Inspect the private logs.')
    if args.test:
        result=subprocess.run([sys.executable,str(ROOT/'tests/integration.py')],env=env)
        if result.returncode:
            raise SystemExit(result.returncode)
    else:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    for p in procs:
        p.terminate()
    for p in procs:
        try:p.wait(timeout=10)
        except subprocess.TimeoutExpired:p.kill()
    for log in logs:log.close()
