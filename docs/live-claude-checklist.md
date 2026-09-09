# Verify the live Claude branch

**Updated status:** Chris verified live routine classification, emergency bypass, and duplicate replay; see [the recorded results](../evidence/live-claude-results.md). The 24 integration scenarios use a fixture service and remain separate evidence. Neither set establishes Claude accuracy.

## Connect

1. Use an Anthropic Platform/Console account with API credits. Claude chat subscriptions and API billing are separate.
2. Create an API key and paste it only into the n8n **Claude API Key** Header Auth credential. Header name: `x-api-key`.
3. Open the main workflow and node **02 Validate and trace**. Change `live_claude: false` to `true`.
4. The configured model is `claude-haiku-4-5-20251001`; verify it is still available in your account before changing models. The token cap is 400 output tokens and the live node timeout is 12 seconds per attempt.
5. Publish the main workflow. Keep the second mock-ticket workflow and the error workflow published as well.

## Demonstrate

1. Send a fresh routine sample. Require a valid `status` and `model_mode: live_claude`. If it routes to review, inspect the reason; a live model is allowed to request review.
2. Send a synthetic emergency. Require `human_review` and `model_mode: none`. This path must never call the model.
3. Send an ambiguous sample. Inspect the actual classification and whether review occurred. Do not force an expected answer by silently editing the evidence.
4. Run at least a few paraphrases manually. Save actual observations and any prompt changes.
5. For an actual successful call, record the date, model ID, synthetic case ID, n8n version, observed output, and outcome in `evidence/live-claude-results.md`. Record failures too.

## Keep the evidence accurate

- The acknowledgement's mode describes the configured branch. Successful model output plus a valid disposition is the evidence of a working call; a `manual_recovery` response alone is not proof of a successful Claude response.
- Capture a sanitized canvas screenshot and a successful/failure response screenshot for the repository. Do not show the credential editor, headers, personal data, or unredacted logs.
- Re-export the workflow after a tested change. Confirm the new export has no raw credentials or pinned data.
- If you used a provider key in the editor, do not rerun the initial credential import from a placeholder file.
- The fixture integration suite assumes fixture mode. Switch back for that suite or use a separate lab copy. Do not pretend fixture expectations validate live model quality.

## Current sources

- [n8n HTTP Request credentials and options](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create)
- [Claude Haiku 4.5 model details](https://platform.claude.com/docs/en/models/haiku-4-5/overview)
- [Claude chat plans and API billing are separate](https://support.claude.com/en/articles/9876003-i-have-a-paid-claude-subscription-pro-max-team-or-enterprise-plans-why-do-i-have-to-pay-separately-to-use-the-claude-api-and-console)

