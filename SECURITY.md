# Security policy

## Authentication and authorization boundaries

- This repository does not implement end-user accounts, sessions, cookies, OAuth callbacks, or JWTs.
- Local third-party API credentials must be supplied through process environment variables or an untracked `.env` file. Never put credentials in source code, issue titles, issue bodies, workflow inputs, logs, or artifacts.
- Diagnostic output reports only whether a credential is configured; it never returns the credential value.
- Privileged workflows have no public event trigger. They can only be started through GitHub's `workflow_dispatch` interface, which GitHub restricts to users with repository write access.
- Workflows use GitHub's short-lived `${{ github.token }}` and declare only the permissions required by each job. Long-lived personal access tokens are not supported.

## Credential response

If a credential may have been committed or printed, revoke it at the provider immediately, remove it from Git history, and review workflow logs and artifacts before issuing a replacement.

Please report suspected vulnerabilities privately to the repository owner. Do not include live credentials or sensitive patient data in a GitHub issue.
