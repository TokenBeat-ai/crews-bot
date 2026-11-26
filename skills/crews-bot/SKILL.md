---
name: crews-bot
description: Start the Crews Bot coordinator, load saved workflows and tasks, and open its local dashboard. Use when the user asks to use Crews Bot or resume its work.
---

# Crews Bot

A bare invocation of this skill is a request to start: load the coordinator and saved workspace, open the dashboard, and show the available next actions. Do not ask the user to type a startup command or repeat their intent. Skill selection in an unsent composer is controlled by the host; these instructions apply when the invocation is sent. If the accompanying request only discusses or edits the skill, address that request without unnecessarily starting the coordinator.

Run `python3 <this skill directory>/scripts/start.py`. The adjacent `installation.json` remembers the registered installation; do not guess a default directory or reinstall on each invocation. If registration is missing, explain that `scripts/install_skill.py --root <existing installation>` from the repository completes installation; preserve existing data.

Read the returned `router` and, when present, `local_entry`. Load the returned workflow registry and task records. Treat old records as context, not authorization to resume all tasks. Read a workflow's original method when the user chooses it. Do not copy private methods into the public package.

Open the returned `url` in the host's side panel if available, otherwise provide the link. The launcher reuses the matching workspace's running server or starts it in the background. On errors, inspect the reported installation and log rather than switching to another workspace.

For a simple startup request, show existing active tasks and available workflows and wait for the user's choice. If the user already supplied a concrete authorized task, continue it without asking them to restate it. Use English by default when the invocation contains no language preference or surrounding conversation. Otherwise reply in the user’s language; never translate stored task or workflow names. Loading itself starts no business work. The host Agent executes tasks; the dashboard is not an Agent runtime.

On a later invocation, run the same launcher: read current saved state, do not recreate the workspace. For update requests, read the current release's UPGRADE.md; honor the user's transport choice and existing local adapter. Never overwrite workspace or unrelated skills. Separate task chats depend on the host's actual capabilities.
