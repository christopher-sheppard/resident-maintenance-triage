# Implementation references

Official references checked during the September 8, 2026 build. The installed n8n 2.37.10 runtime and executed workflow tests are the compatibility evidence for this release.

- [Webhook node: authentication, test and production URLs, and response modes](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook)
- [HTTP Request node: credentials, timeouts, JSON bodies, and error behavior](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest)
- [Code node: JavaScript, built-ins, and limitations](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.code)
- [Error Trigger node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger)
- [Error workflow configuration](https://docs.n8n.io/build/flow-logic/handle-errors-gracefully)
- [n8n server CLI: import and publish workflows](https://docs.n8n.io/deploy/host-n8n/configure-n8n/use-the-command-line)
- [Workflow export and import](https://docs.n8n.io/build/manage-workflows/export-and-import)
- [npm installation and runtime requirements](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-npm)
- [Community Edition](https://docs.n8n.io/deploy/host-n8n/community-edition-features)
- [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create)
- [Claude Haiku 4.5 model reference](https://platform.claude.com/docs/en/models/haiku-4-5/overview)
- [GitHub repository creation](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)

Compatibility note: in the tested n8n version, the linked error workflow needed to be published. The local bootstrap publishes all three workflows; leaving the error handler unpublished caused the actual error-path test to fail until corrected.

