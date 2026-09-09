# GitHub handoff

## Repository status

This source snapshot contains the reviewed public files, not a Git checkout. The original development history remains in the project owner’s separately supplied `project-history.bundle`. No remote publication is claimed.

Suggested repository name: `resident-maintenance-triage`.

## Preserve the actual development history

The original starter kit includes `project-history.bundle`; this public-source-only snapshot intentionally excludes Git history. Review that original history for private material before publication. In the directory containing the separately supplied bundle:

```bash
git clone project-history.bundle resident-maintenance-triage-git
cd resident-maintenance-triage-git
git remote remove origin
```

Create a new empty repository under your GitHub account. Do not initialize it with a competing README or license if you plan to push this existing history. Use the exact repository URL GitHub provides:

```bash
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

`YOUR_REPOSITORY_URL` is a placeholder, not a runnable value. Authentication should use your normal GitHub sign-in or credential manager. Never embed an access token in the remote URL.

The commits identify the AI coding assistant as their author. Preserve that attribution; add your own commits for configuration changes, tests you run, documentation refinements, and the rehearsal. Do not fabricate dates or a longer development history.

## Simpler upload path

You can also upload the project source files through GitHub's website. That will not preserve the included development history. Upload the provided source folder before running it, or carefully exclude `.env`, `.local`, credential exports, databases, raw logs, and `node_modules` afterward.

## Public release checks

- README accurately states whether live Claude was verified.
- All workflow credentials are references or placeholders, with no raw API key/header values.
- No pinned execution data or employer material is present.
- Synthetic test results and runbook are included.
- Any screenshots are from your actual run and show no credentials.
- Choose a license deliberately if you want to grant reuse rights. No license is imposed by this starter.
- Open the repository in a signed-out browser before adding its URL to a résumé.

## Export after a real change

Use n8n's workflow menu to download JSON. Save the three exports to `workflows/`, review the diff, and remove accidental pinned data or sensitive header values. If you change logic in the UI, update the corresponding `src` and generator files as well, or clearly document the UI export as the source of truth. Otherwise regeneration would overwrite the UI change.

