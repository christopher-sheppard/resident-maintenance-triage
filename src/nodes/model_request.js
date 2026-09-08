const ctx = $input.first().json;
return [{ json: { ...ctx,
  model_mode: ctx.config.live_claude ? 'live_claude' : 'fixture',
  model_request: { model: ctx.config.model, max_tokens: 400, temperature: 0,
    system: __SYSTEM_PROMPT__,
    messages: [{ role: 'user', content: JSON.stringify({ maintenance_text: ctx.context.message }) }],
  },
} }];

