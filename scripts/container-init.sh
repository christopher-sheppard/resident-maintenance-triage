#!/bin/sh
set -eu
# Scoped to this project's named n8n volume. No changes to other n8n instances.
if [ -f /home/node/.n8n/triage-initialized ]; then
  echo 'This lab is already initialized; keeping existing credentials and workflows.'
  exit 0
fi
n8n import:credentials --input=/local/credentials.json
n8n import:workflow --separate --input=/local/workflows
n8n publish:workflow --id=MaintenanceErrorsV1
n8n publish:workflow --id=MockTicketsV1
n8n publish:workflow --id=MaintenanceTriageV1
touch /home/node/.n8n/triage-initialized
chown -R 1000:1000 /home/node/.n8n
