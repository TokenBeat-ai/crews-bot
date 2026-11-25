# Update and roll back

Managed installs (see [INSTALL.md](INSTALL.md)) are updated with `scripts/install_manager.py`. Requires Python 3.12 or newer.

```sh
python3 ~/crews-bot/releases/<current>/scripts/install_manager.py update --root ~/crews-bot --ref v2026.11.25.1
python3 ~/crews-bot/releases/<current>/scripts/install_manager.py rollback --root ~/crews-bot
```

Without `--ref`, `update` installs the latest commit on `main`.

## What happens

- **Update** downloads the requested version into `releases/<commit>/`, rejects unsafe archive entries, checks required files, records file hashes in `evidence/`, then switches `installation.json` so the new version is current and the old one is previous. If anything fails, nothing is switched.
- **Rollback** swaps current and previous. It only switches method files.
- **Your data is never touched.** `workspace/` is not read or written by updates. Your own workflows live there, so they survive every update.
- **Edited releases are protected.** If files in the current or previous release were modified, the command stops instead of overwriting them. Move your changes into `workspace/` first.
- Updating to a version that is already installed changes nothing.

## Data format changes

If a future version changes the format of `tasks.json` or `workflows.json`, the changelog will say so and describe the migration. Rollback does not convert data back; keep a copy of `workspace/` before updating across such a change.

## Installs without installation.json

If you copied or cloned the repository and used it directly, there is nothing to update in place. Create a managed install in a new folder, then point it at your existing data: copy your `tasks.json`, `workflows.json` and workflow files into the new `workspace/`. Keep the old folder until you have checked the result.
