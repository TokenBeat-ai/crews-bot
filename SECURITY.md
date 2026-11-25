# Security

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's **Report a vulnerability** (private security advisory) on this repository. We aim to acknowledge reports within five working days.

## Scope

- The dashboard server listens on `127.0.0.1` only and requires a per-session token for write actions.
- The installer downloads fixed commits, rejects unsafe archive entries and never modifies your workspace.
- Crews Bot stores no credentials. Keep API keys in your host's credential settings or environment variables, never in workflow files or `tasks.json`.

Your agent host, models and connected tools have their own security policies.
