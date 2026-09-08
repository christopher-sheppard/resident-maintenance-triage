"""Generate reviewable n8n exports from their versioned JavaScript source."""
import argparse
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--lab-base', default='http://lab:8080')
parser.add_argument('--ticket-url', default='http://n8n:5678/webhook/mock-maintenance-ticket')
parser.add_argument('--output', type=Path, default=ROOT / 'workflows')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
POLICY = (ROOT / 'src/policy.cjs').read_text().split('module.exports =')[0]
PROMPT = (ROOT / 'prompts/classifier-system-prompt.md').read_text()
LAB_CRED = {'httpHeaderAuth': {'id': 'LabHeaderAuthV1', 'name': 'Synthetic Lab Header'}}


def node(name, kind, params, x, y, version=1, **extra):
    return {'id': str(uuid.uuid5(uuid.NAMESPACE_URL, 'synthetic-triage/' + name)), 'name': name,
            'type': 'n8n-nodes-base.' + kind, 'typeVersion': version, 'position': [x, y], 'parameters': params, **extra}


def code(name, src, x, y, policy=False):
    source = (ROOT / 'src/nodes' / src).read_text() if src.endswith('.js') else src
    source = source.replace('__LAB_BASE__', args.lab_base).replace('__TICKET_URL__', args.ticket_url).replace('__SYSTEM_PROMPT__', json.dumps(PROMPT))
    return node(name, 'code', {'jsCode': (POLICY if policy else '') + '\n' + source}, x, y, 2)


def condition(name, expr, x, y):
    return node(name, 'if', {'conditions': {'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'strict', 'version': 2},
        'conditions': [{'id': str(uuid.uuid4()), 'leftValue': expr, 'rightValue': True, 'operator': {'type': 'boolean', 'operation': 'true', 'singleValue': True}}],
        'combinator': 'and'}, 'options': {}}, x, y, 2.2)


def http(name, url, body, x, y, credential=LAB_CRED, timeout=8000, retries=1, continue_error=True, headers=None):
    params = {'method': 'POST', 'url': url, 'authentication': 'genericCredentialType', 'genericAuthType': 'httpHeaderAuth',
        'sendBody': True, 'specifyBody': 'json', 'jsonBody': body,
        'options': {'timeout': timeout, 'redirect': {'redirect': {'followRedirects': False}}, 'response': {'response': {'responseFormat': 'json'}}}}
    if headers:
        params.update({'sendHeaders': True, 'headerParameters': {'parameters': headers}})
    extra = {'credentials': credential}
    if continue_error:
        extra['onError'] = 'continueRegularOutput'
    if retries > 1:
        extra.update({'retryOnFail': True, 'maxTries': retries, 'waitBetweenTries': 1000})
    return node(name, 'httpRequest', params, x, y, 4.2, **extra)


def webhook(name, path, x, y):
    return node(name, 'webhook', {'httpMethod': 'POST', 'path': path, 'authentication': 'headerAuth',
        'responseMode': 'responseNode', 'options': {}}, x, y, 2, credentials=LAB_CRED,
        webhookId=str(uuid.uuid5(uuid.NAMESPACE_URL, path)))


def respond(name, body, status, x, y):
    return node(name, 'respondToWebhook', {'respondWith': 'json', 'responseBody': body,
        'options': {'responseCode': status}}, x, y, 1.4)


def save(filename, wid, name, nodes, edges, error=True):
    connections = {}
    for source, target, branch in edges:
        outputs = connections.setdefault(source, {'main': []})['main']
        while len(outputs) <= branch:
            outputs.append([])
        outputs[branch].append({'node': target, 'type': 'main', 'index': 0})
    settings = {'executionOrder': 'v1', 'executionTimeout': 90, 'saveDataSuccessExecution': 'none',
                'saveDataErrorExecution': 'none', 'saveManualExecutions': False, 'saveExecutionProgress': False}
    if error:
        settings['errorWorkflow'] = 'MaintenanceErrorsV1'
    result = {'id': wid, 'name': name, 'active': False, 'nodes': nodes, 'connections': connections,
              'settings': settings, 'pinData': {}, 'tags': [], 'versionId': str(uuid.uuid5(uuid.NAMESPACE_URL, wid + '/v1'))}
    (args.output / filename).write_text(json.dumps(result, indent=2) + '\n')


n = []
n.append(webhook('01 Authenticated maintenance intake', 'maintenance', 0, 0))
n.append(code('02 Validate and trace', 'validate.js', 240, 0, True))
n.append(condition('Input valid?', '={{ $json.valid }}', 480, 0))
n.append(code('03 Minimize and redact', 'privacy.js', 720, 0, True))
n.append(http('04 Atomic event claim', '={{ $json.config.lab_base + "/events/claim" }}', '={{ {event_id:$json.event_id,fingerprint:$json.fingerprint,trace_id:$json.trace_id,context:$json.context} }}', 960, 0, retries=3))
n.append(code('05 Check claim', "const r=$input.first().json;return [{json:{...r,state_ok:!r.error && typeof r.acquired==='boolean'}}];", 1200, 0))
n.append(condition('Claim storage available?', '={{ $json.state_ok }}', 1320, 160))
n.append(condition('Claim acquired?', '={{ $json.acquired }}', 1440, 0))
n.append(code('06 Deterministic safety gate', 'safety.js', 1680, 0))
n.append(condition('07 Safe to classify?', '={{ $json.outcome === "classify" }}', 1920, 0))
n.append(code('09 Build bounded model request', 'model_request.js', 1920, 400))
n.append(condition('10 Use live Claude?', '={{ $json.config.live_claude }}', 1680, 400))
n.append(http('11 Claude Messages API', 'https://api.anthropic.com/v1/messages', '={{ $json.model_request }}', 1440, 280,
    credential={'httpHeaderAuth': {'id': 'ClaudeHeaderAuthV1', 'name': 'Claude API Key'}}, timeout=12000, retries=3,
    headers=[{'name': 'anthropic-version', 'value': '2023-06-01'}]))
n.append(http('11 Fixture model - no live AI', '={{ $json.config.lab_base + "/model/messages" }}', '={{ $json.model_request }}', 1440, 520, timeout=2500, retries=3))
n.append(code('12 Validate model and route', 'model_validate.js', 1200, 400, True))
n.append(condition('13 Approved for ticket?', '={{ $json.outcome === "ticket_created" }}', 960, 400))
n.append(http('14 Save approved classification', '={{ $json.config.lab_base + "/events/checkpoint" }}', '={{ {event_id:$json.event_id,trace_id:$json.trace_id,classification:$json.classification} }}', 720, 400, retries=3))
n.append(code('15 Build ticket request', "const r=$input.first().json;return [{json:{...$('12 Validate model and route').first().json,state_ok:!r.error && r.stored===true}}];", 480, 400))
n.append(condition('Checkpoint storage available?', '={{ $json.state_ok }}', 360, 580))
n.append(http('16 Call mock ticket API', '={{ $json.config.ticket_url }}', '={{ {event_id:$json.event_id,trace_id:$json.trace_id,classification:$json.classification} }}', 240, 400, retries=3))
n.append(code('17 Inspect ticket result', "const ctx=$('15 Build ticket request').first().json;const r=$input.first().json;const ok=!r.error && r.synthetic===true && typeof r.ticket_id==='string' && /^MOCK-[A-F0-9]{12}$/.test(r.ticket_id);return [{json:{...ctx,outcome:ok?'ticket_created':'manual_recovery',reason:ok?'VALIDATED_CLASSIFICATION':'TICKET_UNAVAILABLE',stage:'ticket',...(ok?{ticket_id:r.ticket_id}:{})}}];", 0, 400))
n.append(code('18 Build durable outcome', 'finish_payload.js', 0, 800))
n.append(http('19 Commit audit and outcome', '={{ $json.config.lab_base + "/events/finish" }}', '={{ $json.finish }}', 240, 800, retries=3))
n.append(code('20 Verify durable outcome', "const r=$input.first().json;return [{json:{...r,state_ok:!r.error && ['ticket_created','human_review','manual_recovery'].includes(r.status)}}];", 480, 800))
n.append(condition('Outcome storage available?', '={{ $json.state_ok }}', 720, 800))
n.append(respond('21 Accurate acknowledgement', '={{ Object.fromEntries(Object.entries($json).filter(([k]) => k !== "state_ok")) }}', '={{ $("18 Build durable outcome").first().json.http_status }}', 960, 800))
n.append(respond('Respond unconfirmed - 503', '={{ {status:"unconfirmed",reason:"STATE_UNAVAILABLE",trace_id:$("02 Validate and trace").first().json.trace_id,synthetic:true,message:"No acceptance confirmed. Keep the same source_event_id for operator reconciliation."} }}', 503, 1200, 1000))
n.append(node('Raise safe operational error', 'stopAndError', {'errorType':'errorMessage','errorMessage':'STATE_UNAVAILABLE'}, 1440, 1000))
n.append(code('Invalid response', "const v=$('02 Validate and trace').first().json;return [{json:{config:v.config,http_status:v.http_status,response:{status:'rejected',reason:'INVALID_INPUT',errors:v.errors,trace_id:v.trace_id,synthetic:true},audit:{trace_id:v.trace_id,reason:'INVALID_INPUT',model_mode:'none',latency_ms:Date.now()-v.started_at_ms}}}];", 480, -400))
n.append(http('Audit rejected intake', '={{ $json.config.lab_base + "/audit" }}', '={{ $json.audit }}', 720, -400, retries=1))
n.append(respond('Respond rejected', '={{ $("Invalid response").first().json.response }}', '={{ $("Invalid response").first().json.http_status }}', 960, -400))
n.append(code('Duplicate or conflict response', "const r=$input.first().json;const c=$('03 Minimize and redact').first().json;return [{json:{config:c.config,http_status:r.http_status,response:{...(r.result||{status:'rejected',reason:r.reason,source_event_id:c.event_id}),duplicate:r.reason==='DUPLICATE',synthetic:true},audit:{trace_id:c.trace_id,event_id:c.event_id,reason:r.reason,model_mode:'none',latency_ms:Date.now()-c.started_at_ms}}}];", 1440, -400))
n.append(http('Audit replay decision', '={{ $json.config.lab_base + "/audit" }}', '={{ $json.audit }}', 1680, -400, retries=1))
n.append(respond('Respond replay decision', '={{ $("Duplicate or conflict response").first().json.response }}', '={{ $("Duplicate or conflict response").first().json.http_status }}', 1920, -400))
n.append(node('Read me first', 'stickyNote', {'content':'## Resident Maintenance Triage\nSynthetic proof lab. Default classifier is a fixture, not live Claude.\nSet live_claude in 02 only after configuring the Claude credential.\nSource files + test results are in the repository.\nReview and alert destinations are local mock records.', 'height':230,'width':550}, 0, -660))
edges=[]
def chain(*names):
    edges.extend((a,b,0) for a,b in zip(names,names[1:]))
chain('01 Authenticated maintenance intake','02 Validate and trace','Input valid?','03 Minimize and redact','04 Atomic event claim','05 Check claim','Claim storage available?','Claim acquired?','06 Deterministic safety gate','07 Safe to classify?','09 Build bounded model request','10 Use live Claude?','11 Claude Messages API','12 Validate model and route','13 Approved for ticket?','14 Save approved classification','15 Build ticket request','Checkpoint storage available?','16 Call mock ticket API','17 Inspect ticket result','18 Build durable outcome','19 Commit audit and outcome','20 Verify durable outcome','Outcome storage available?','21 Accurate acknowledgement')
edges += [('Input valid?','Invalid response',1),('Claim acquired?','Duplicate or conflict response',1),
          ('07 Safe to classify?','18 Build durable outcome',1),('10 Use live Claude?','11 Fixture model - no live AI',1),
          ('11 Fixture model - no live AI','12 Validate model and route',0),('13 Approved for ticket?','18 Build durable outcome',1)]
edges += [(name,'Respond unconfirmed - 503',1) for name in ['Claim storage available?','Checkpoint storage available?','Outcome storage available?']]
chain('Respond unconfirmed - 503','Raise safe operational error')
chain('Invalid response','Audit rejected intake','Respond rejected')
chain('Duplicate or conflict response','Audit replay decision','Respond replay decision')
save('maintenance-triage.json','MaintenanceTriageV1','Resident Maintenance Triage | Synthetic Lab',n,edges)

mock=[webhook('Mock ticket intake','mock-maintenance-ticket',0,0),
      http('Idempotent mock ticket store',args.lab_base+'/tickets','={{ $json.body }}',280,0,retries=1,continue_error=False),
      respond('Mock ticket response','={{ $json }}',200,560,0)]
save('mock-ticket-api.json','MockTicketsV1','Mock Maintenance Ticket API',mock,[('Mock ticket intake','Idempotent mock ticket store',0),('Idempotent mock ticket store','Mock ticket response',0)],error=False)

err=[node('Unexpected error trigger','errorTrigger',{},0,0),
     code('Sanitize error metadata',"const e=$input.first().json;return [{json:{trace_id:'exec-'+(e.execution?.id||'unknown'),workflow_id:String(e.workflow?.id||'unknown').slice(0,100)}}];",280,0),
     http('Record recovery and mock alert',args.lab_base+'/errors','={{ $json }}',560,0,retries=3,continue_error=False)]
save('maintenance-error-handler.json','MaintenanceErrorsV1','Maintenance Unexpected Error Handler',err,[('Unexpected error trigger','Sanitize error metadata',0),('Sanitize error metadata','Record recovery and mock alert',0)],error=False)
print(f'Generated three workflows in {args.output}')
