---
name: crews-bot
description: Load the Crews Bot coordinator, open the dashboard, or update an installed Crews Bot package. Use only when the user is working with Crews Bot.
---

# Crews Bot

Use the installation root the user gives you; otherwise use `~/crews-bot`. The root contains `installation.json`. If there are several installations or the target is unclear, ask before switching.

- **Load:** read `installation.json` in the installation root, find the `current` release folder and the `workspace` folder. Follow `general/getting-started.md` and `general/router-method.md` from the current release. Do not copy their rules here.
- **Open the dashboard:** run `python3 <current release>/scripts/open_dashboard.py --root <installation root>` and open the printed address (side panel if the host supports it, otherwise the browser).
- **Update:** follow `UPGRADE.md` from the current release and run `scripts/install_manager.py update` for the installation the user named. Never modify the workspace.

Loading does not start any work. Separate task conversations depend on the host; see `docs/hosts.md`.
