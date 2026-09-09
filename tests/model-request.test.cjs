const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const prompt = fs.readFileSync(path.join(root, 'prompts/classifier-system-prompt.md'), 'utf8');
const source = fs.readFileSync(path.join(root, 'src/nodes/model_request.js'), 'utf8')
  .replace('__SYSTEM_PROMPT__', JSON.stringify(prompt));
const workflow = JSON.parse(fs.readFileSync(path.join(root, 'workflows/maintenance-triage.json'), 'utf8'));
const generated = workflow.nodes.find(n => n.name === '09 Build bounded model request').parameters.jsCode;

function request(code, live) {
  const context = {
    config: { live_claude: live, model: 'claude-haiku-4-5-20251001' },
    context: { message: 'Water leaking beneath the kitchen sink.', unit: '2B' },
    event_id: 'SYNTHETIC-REQUEST-TEST',
  };
  const result = vm.runInNewContext(`(function () { ${code}\n})()`, {
    $input: { first: () => ({ json: context }) },
  }, { timeout: 1000 });
  return JSON.parse(JSON.stringify(result[0].json));
}

for (const live of [false, true]) {
  test(`node 09 preserves source/export parity and ${live ? 'live' : 'fixture'} contract`, () => {
    const actual = request(source, live);
    assert.deepEqual(actual, request(generated, live));
    assert.equal(actual.model_mode, live ? 'live_claude' : 'fixture');
    const body = actual.model_request;
    assert.equal(body.model, 'claude-haiku-4-5-20251001');
    assert.equal(body.max_tokens, 400);
    assert.equal(body.system, prompt);
    assert.deepEqual(JSON.parse(body.messages[0].content), {
      maintenance_text: 'Water leaking beneath the kitchen sink.',
    });
    if (!live) {
      assert.equal(Object.hasOwn(body, 'output_config'), false);
      return;
    }
    assert.equal(body.output_config.format.type, 'json_schema');
    const schema = body.output_config.format.schema;
    assert.equal(schema.type, 'object');
    assert.equal(schema.additionalProperties, false);
    assert.deepEqual(schema.required, [
      'category', 'urgency', 'confidence', 'summary', 'human_review_required', 'policy_flags',
    ]);
    assert.deepEqual(Object.keys(schema.properties).sort(), [...schema.required].sort());
    assert.equal(schema.properties.confidence.type, 'number');
    assert.equal(schema.properties.human_review_required.type, 'boolean');
    assert.deepEqual(schema.properties.urgency.enum, ['routine', 'urgent', 'emergency']);
    assert.deepEqual(schema.properties.policy_flags.items.enum, [
      'prompt_injection', 'sensitive_data', 'safety_concern', 'insufficient_information',
    ]);
  });
}
