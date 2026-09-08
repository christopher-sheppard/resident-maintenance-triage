// Pure business rules, embedded verbatim in the generated n8n Code nodes.
// Synthetic demonstration policy; requires domain-owner review before real use.
const CATEGORIES = ['plumbing', 'electrical', 'hvac', 'appliance', 'general', 'unknown'];
const URGENCIES = ['routine', 'urgent', 'emergency'];
const FLAGS = ['prompt_injection', 'sensitive_data', 'safety_concern', 'insufficient_information'];
const OUTPUT_KEYS = ['category', 'urgency', 'confidence', 'summary', 'human_review_required', 'policy_flags'];

function validateRequest(body, headers = {}, nowMs = Date.now()) {
  const errors = [];
  const allowed = ['source_event_id', 'property_id', 'unit', 'message', 'contact_preference', 'submitted_at', 'synthetic', 'resident_name'];
  if (!headers['content-type']?.toLowerCase().startsWith('application/json')) {
    return { valid: false, http_status: 415, errors: ['CONTENT_TYPE'] };
  }
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return { valid: false, http_status: 400, errors: ['JSON_OBJECT_REQUIRED'] };
  }
  if (JSON.stringify(body).length > 12000) {
    return { valid: false, http_status: 413, errors: ['PAYLOAD_TOO_LARGE'] };
  }
  if (Object.keys(body).some(k => !allowed.includes(k))) errors.push('UNKNOWN_FIELDS');
  if (body.synthetic !== true) errors.push('SYNTHETIC_DATA_ONLY');
  if (typeof body.source_event_id !== 'string' || !/^[A-Za-z0-9_-]{1,80}$/.test(body.source_event_id)) errors.push('SOURCE_EVENT_ID');
  if (body.property_id !== 'PROP-DEMO-001') errors.push('PROPERTY_NOT_ALLOWLISTED');
  if (typeof body.unit !== 'string' || !/^[A-Za-z0-9-]{1,12}$/.test(body.unit)) errors.push('UNIT');
  if (typeof body.message !== 'string' || body.message.trim().length < 5 || body.message.length > 2000) errors.push('MESSAGE_LENGTH');
  if (!['email', 'sms', 'phone', 'none'].includes(body.contact_preference)) errors.push('CONTACT_PREFERENCE');
  if (body.resident_name !== undefined && (typeof body.resident_name !== 'string' || body.resident_name.length > 80)) errors.push('RESIDENT_NAME');
  const timestamp = typeof body.submitted_at === 'string' && /^\d{4}-\d{2}-\d{2}T.*Z$/.test(body.submitted_at) ? Date.parse(body.submitted_at) : NaN;
  if (!Number.isFinite(timestamp) || timestamp > nowMs + 300000 || timestamp < nowMs - 30 * 86400000) errors.push('TIMESTAMP_WINDOW');
  if (errors.length) return { valid: false, http_status: 400, errors };
  return { valid: true, http_status: 200, request: {
    source_event_id: body.source_event_id,
    property_id: body.property_id,
    unit: body.unit,
    message: body.message.normalize('NFKC').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, '').trim(),
    contact_preference: body.contact_preference,
    submitted_at: new Date(timestamp).toISOString(),
    synthetic: true,
    resident_name: body.resident_name || '',
  } };
}

function redactText(text, name = '') {
  let result = text;
  let changed = false;
  const replace = (regex, tag) => { result = result.replace(regex, () => { changed = true; return tag; }); };
  if (name.trim()) {
    const escaped = name.trim().replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    replace(new RegExp(escaped, 'gi'), '[NAME]');
  }
  replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[EMAIL]');
  replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[GOV_ID]');
  replace(/\b(?:\d[ -]?){13,19}\b/g, '[PAYMENT_NUMBER]');
  replace(/(?:\+?1[ .-]?)?\(?\b\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b/g, '[PHONE]');
  replace(/\b(?:my name is|i am|i'm)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b/g, '[NAME_INTRO]');
  return { text: result, changed };
}

function emergencySignals(text) {
  const rules = [
    ['gas', /\b(?:gas (?:smell|odor|leak)|smell(?:s|ing)? (?:of )?gas)\b/i],
    ['fire', /\b(?:fire|smoke|carbon monoxide)\b/i],
    ['flood', /\b(?:active flooding|flooding|water pouring|burst pipe)\b/i],
    ['electrical', /\b(?:sparking|exposed live wire|electrical (?:fire|sparks))\b/i],
    ['immediate_threat', /\b(?:immediate (?:danger|threat)|trapped|cannot breathe|can't breathe)\b/i],
  ];
  return rules.filter(([, regex]) => regex.test(text)).map(([name]) => name);
}

function injectionSignals(text) {
  return /ignore (?:all |the |your |previous )*(?:instructions|rules|prompt)|system prompt|reveal (?:the |your )?(?:secret|api key)|override (?:the |your )?(?:rules|policy)|act as (?:an? )?(?:system|admin)/i.test(text);
}

function validateModel(envelope) {
  if (!envelope || envelope.error) return { valid: false, reason: 'MODEL_UNAVAILABLE' };
  if (envelope.stop_reason !== 'end_turn') return { valid: false, reason: 'MODEL_STOP_REASON' };
  if (!Array.isArray(envelope.content) || envelope.content.length !== 1 || envelope.content[0].type !== 'text') return { valid: false, reason: 'MODEL_CONTENT' };
  let value;
  try { value = JSON.parse(envelope.content[0].text); } catch { return { valid: false, reason: 'MODEL_INVALID_JSON' }; }
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).length !== OUTPUT_KEYS.length || OUTPUT_KEYS.some(k => !(k in value))) return { valid: false, reason: 'MODEL_SCHEMA' };
  const valid = CATEGORIES.includes(value.category) && URGENCIES.includes(value.urgency)
    && typeof value.confidence === 'number' && Number.isFinite(value.confidence) && value.confidence >= 0 && value.confidence <= 1
    && typeof value.summary === 'string' && value.summary.length > 0 && value.summary.length <= 240
    && typeof value.human_review_required === 'boolean'
    && Array.isArray(value.policy_flags) && value.policy_flags.length <= FLAGS.length
    && value.policy_flags.every(x => FLAGS.includes(x)) && new Set(value.policy_flags).size === value.policy_flags.length;
  if (!valid) return { valid: false, reason: 'MODEL_SCHEMA' };
  const safeSummary = redactText(value.summary);
  if (safeSummary.changed) {
    value.summary = safeSummary.text.slice(0, 240);
    value.human_review_required = true;
    value.policy_flags = [...new Set([...value.policy_flags, 'sensitive_data'])];
  }
  return { valid: true, classification: value };
}

function routeModel(result, threshold = 0.75) {
  if (!result.valid) return { outcome: result.reason === 'MODEL_UNAVAILABLE' ? 'manual_recovery' : 'human_review', reason: result.reason };
  const c = result.classification;
  if (c.urgency === 'emergency') return { outcome: 'human_review', reason: 'MODEL_EMERGENCY' };
  if (c.policy_flags.length) return { outcome: 'human_review', reason: 'MODEL_POLICY_FLAG' };
  if (c.human_review_required || c.category === 'unknown' || c.confidence < threshold) return { outcome: 'human_review', reason: 'LOW_CONFIDENCE_OR_REVIEW' };
  return { outcome: 'ticket_created', reason: 'VALIDATED_CLASSIFICATION' };
}

module.exports = { validateRequest, redactText, emergencySignals, injectionSignals, validateModel, routeModel };

