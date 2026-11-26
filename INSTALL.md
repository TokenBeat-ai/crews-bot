# Install

Requirements: Python 3.12 or newer, and an agent host that can read and write local files ([host support](docs/hosts.md)). No other packages are needed. On Windows, use `py -3` instead of `python3`.

## Option A: managed install (recommended)

Installs a fixed version into its own folder, with your data kept separately so updates never touch it.

```sh
git clone https://github.com/TokenBeat-ai/crews-bot.git
python3 crews-bot/scripts/install_manager.py install --root ~/crews-bot
python3 crews-bot/scripts/install_skill.py --root ~/crews-bot
python3 ~/.codex/skills/crews-bot/scripts/start.py
```

Open the printed address, usually `http://127.0.0.1:18761/dashboard.html`. You can also download the repository as a ZIP instead of cloning.

The installation folder looks like this:

| Path | Contents |
|---|---|
| `releases/<commit>/` | Installed versions. Never edit these; updates check that they are unchanged |
| `workspace/` | Your data: `tasks.json`, `workflows.json`, `runs/` and the rendered dashboard |
| `evidence/` | File hashes for each installed version |
| `installation.json` | Which version is current and which is previous |

Install a specific version with `--ref`, for example `--ref v2026.11.25.1`. No GitHub account is needed for the public repository. To install from a private repository, set `GITHUB_TOKEN` (for example `GITHUB_TOKEN=$(gh auth token)`).

## Option B: try it from the repository

```sh
git clone https://github.com/TokenBeat-ai/crews-bot.git && cd crews-bot
mkdir -p workspace && cp dashboard/example.tasks.json workspace/tasks.json && echo '[]' > workspace/workflows.json
python3 dashboard/serve.py --tasks workspace/tasks.json --workflows workspace/workflows.json --dashboard workspace/dashboard.html
```

`workspace/` is ignored by Git. Use Option A when you want updates and rollback.

## Connect your agent

1. Register the installed package with `python3 crews-bot/scripts/install_skill.py --root ~/crews-bot`. Use your actual root for a non-default installation. This creates a separate `crews-bot` skill; other skills are untouched. The default destination respects `CODEX_HOME`; `--skills-dir` overrides it.
2. In a new Codex chat select **Crews Bot** (or invoke `$crews-bot`) and send the selection; no additional startup phrase is required. If discovery has not refreshed, restart the host and open a new chat. The skill opens the dashboard and reads saved workflows/tasks without automatically executing old tasks.
3. Next time, select the same skill. No path-pasting or reinstall is needed. Its launcher reuses the matching local dashboard or starts it again. `--port` at registration chooses the preferred port; occupied unrelated ports are skipped.

Registration currently targets Codex on macOS/Linux. Other hosts still use the file-based method until their skill discovery is verified. Option B is an unmanaged preview; use Option A for the registered skill.

Re-running registration for the same root refreshes packaged skill files. A locally edited skill or a different registered root is rejected rather than silently overwritten. Personal installation settings live only in the installed skill, never in the repository. Package updates continue to resolve `installation.json.current`; re-run registration when distributing a new skill version.

To uninstall only the entry, remove the managed `crews-bot` folder from the selected skills directory after checking for personal edits. Keep the installation/workspace to preserve tasks and workflows. This does not stop a running dashboard or remove other skills.

## Costs

Crews Bot is free. Your agent host, model usage and any external tools you connect are billed by their providers. The sample workflow uses no paid services beyond your agent's own model usage.

## Troubleshooting

| Problem | What to check |
|---|---|
| Download fails | Network access; for a private repository, `GITHUB_TOKEN` |
| `Run render_dashboard.py first` | Start `serve.py` with `--tasks` and `--workflows` so it can render the page |
| Port already in use | Add `--port 18762` |
| Dashboard shows an old state | Click Refresh dashboard; it re-reads saved records |

Updating and rolling back: see [UPGRADE.md](UPGRADE.md).
