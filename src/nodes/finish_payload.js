const ctx = $input.first().json;
return [{ json: {
  config: ctx.config,
  http_status: ctx.outcome === 'ticket_created' ? 201 : 202,
  finish: {
    event_id: ctx.event_id, trace_id: ctx.trace_id,
    outcome: ctx.outcome, reason: ctx.reason, stage: ctx.stage,
    model_mode: ctx.model_mode,
    latency_ms: Date.now() - ctx.started_at_ms,
    ...(ctx.ticket_id ? { ticket_id: ctx.ticket_id } : {}),
  },
} }];

