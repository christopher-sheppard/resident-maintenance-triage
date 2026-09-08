const input = $('03 Minimize and redact').first().json;
let outcome = 'classify', reason = 'READY_FOR_CLASSIFICATION';
if (input.emergency_signals.length) { outcome = 'human_review'; reason = 'DETERMINISTIC_EMERGENCY'; }
else if (input.injection_detected) { outcome = 'human_review'; reason = 'PROMPT_INJECTION_INDICATOR'; }
return [{ json: { ...input, outcome, reason, stage: 'safety_gate', model_mode: 'none' } }];

