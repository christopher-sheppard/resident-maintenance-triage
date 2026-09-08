const ctx = $('09 Build bounded model request').first().json;
const result = validateModel($input.first().json);
const route = routeModel(result, ctx.config.threshold);
return [{ json: { ...ctx, ...route, classification: result.classification || null, stage: 'model' } }];

