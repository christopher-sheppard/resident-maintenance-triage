const input = $input.first().json;
const request = input.request;
const crypto = require('crypto');
const fingerprint = crypto.createHash('sha256').update(JSON.stringify(request)).digest('hex');
const redacted = redactText(request.message, request.resident_name);
// Only the message goes to the model. IDs and contact preference stay in local context.
return [{ json: {
  trace_id: input.trace_id, started_at_ms: input.started_at_ms, config: input.config,
  event_id: request.source_event_id, fingerprint,
  context: { property_id: request.property_id, unit: request.unit, message: redacted.text,
    contact_preference: request.contact_preference, submitted_at: request.submitted_at, synthetic: true },
  privacy_redacted: redacted.changed,
  emergency_signals: emergencySignals(request.message),
  injection_detected: injectionSignals(request.message),
} }];

