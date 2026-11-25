# Install

Requirements: Python 3.12 or newer, and an agent host that can read and write local files ([host support](docs/hosts.md)). No other packages are needed. On Windows, use `py -3` instead of `python3`.

## Option A: managed install (recommended)

Installs a fixed version into its own folder, with your data kept separately so updates never touch it.

```sh
git clone https://github.com/TokenBeat-ai/crews-bot.git
python3 crews-bot/scripts/install_manager.py install --root ~/crews-bot
python3 ~/crews-bot/releases/*/scripts/open_dashboard.py --root ~/crews-bot
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

1. Tell your agent where Crews Bot is installed and ask it to read `general/getting-started.md`. That is enough to start.
2. Optional: copy `skills/crews-bot/` into your host's skills folder (for Codex, `~/.codex/skills/crews-bot/`). Then you can say "load Crews Bot", "open the Crews Bot dashboard" or "update Crews Bot".
3. In the dashboard, open **Getting started** and choose **Try a sample task: Three-step plan**. Copy the prompt and send it to your agent.

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
