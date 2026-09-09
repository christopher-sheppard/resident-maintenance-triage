const ctx = $input.first().json;
return [{ json: { ...ctx,
  model_mode: ctx.config.live_claude ? 'live_claude' : 'fixture',
  model_request: { model: ctx.config.model, max_tokens: 400, temperature: 0,
    system: __SYSTEM_PROMPT__,
    messages: [{ role: 'user', content: JSON.stringify({ maintenance_text: ctx.context.message }) }],
    // Constrain live output at the provider. Node 12 still validates every response.
    ...(ctx.config.live_claude ? {
      output_config: {
        format: {
          type: 'json_schema',
          schema: {
            type: 'object',
            additionalProperties: false,
            properties: {
              category: { type: 'string', enum: ['plumbing', 'electrical', 'hvac', 'appliance', 'general', 'unknown'] },
              urgency: { type: 'string', enum: ['routine', 'urgent', 'emergency'] },
              confidence: { type: 'number', description: 'A routing signal between 0 and 1, not a calibrated probability.' },
              summary: { type: 'string', description: 'A factual maintenance summary, 1 to 240 characters, without personal data.' },
              human_review_required: { type: 'boolean' },
              policy_flags: {
                type: 'array',
                items: { type: 'string', enum: ['prompt_injection', 'sensitive_data', 'safety_concern', 'insufficient_information'] },
                description: 'Use each applicable flag at most once; use an empty array if none apply.'
              }
            },
            required: ['category', 'urgency', 'confidence', 'summary', 'human_review_required', 'policy_flags']
          }
        }
      }
    } : {}),
  },
} }];
