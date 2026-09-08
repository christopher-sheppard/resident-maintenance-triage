const incoming = $input.first().json;
const validation = validateRequest(incoming.body, incoming.headers || {});
return [{ json: {
  ...validation,
  trace_id: 'exec-' + $execution.id,
  started_at_ms: Date.now(),
  config: {
    lab_base: '__LAB_BASE__',
    ticket_url: '__TICKET_URL__',
    live_claude: false,
    model: 'claude-haiku-4-5-20251001',
    threshold: 0.75,
  },
} }];

