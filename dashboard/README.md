# Dashboard

A local web page that shows saved task records and your workflows. It does not run models, monitor conversations or start work. Terminology: [terminology](../general/terminology.md).

## Run it

```sh
python3 dashboard/serve.py --tasks <workspace>/tasks.json --workflows <workspace>/workflows.json --dashboard <workspace>/dashboard.html
```

Open the printed address (default `http://127.0.0.1:18761/dashboard.html`). The server listens on `127.0.0.1` only. After changing `serve.py`, restart it; reloading the page only re-reads records.

To render without serving, use `render_dashboard.py` (same arguments, `--output` instead of `--dashboard`) or `publish_snapshot.py`, which keeps the previous page if validation fails.

## Behavior

- **One status per task.** Internal statuses map to what users see: `running` → In progress; `review`, `blocked`, `waiting` → Pending; `waiting` with `has_started: false` and no `started_at` → Not started; `done` → Completed; `unknown` → Needs verification; `cancelled` → Cancelled. Review, missing input or external waits go into the next step, not into extra statuses.
- **Refresh** re-reads saved records. It does not poll tasks or call a model.
- **Remove from dashboard** deletes the task record from view (a backup is written next to `tasks.json`). It does not stop work or delete outputs. The dashboard cannot mark tasks complete; the coordinator does that after verifying outputs.
- **Getting started** opens automatically for an empty workspace the first time. The choice is remembered per workspace in the browser.
- **Prepare to run** builds a prompt for an existing workflow. The user copies it and sends it; nothing runs until then.
- Links: `#create` (Getting started), `#run?workflow=<ID>` (prepare a workflow), `#workflows?focus=<ID>` (highlight a workflow). IDs are URL-encoded.

## tasks.json

```json
{
  "instruction_target_name": "optional: name of the conversation that receives copied prompts",
  "tasks": [
    {
      "id": "T20261125-01-Planning-Team-sharing",
      "title": "Sample: Three-step plan",
      "status": "review",
      "next": "Review the plan and mark changes",
      "verified_at": "2026-11-25T10:30:00+08:00",
      "evidence": "plan.md has three steps with completion criteria",
      "artifact": "runs/T20261125-01/plan.md",
      "is_example": true
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `id`, `title`, `status`, `next`, `verified_at`, `evidence` | yes | Identity, status, next step, last real verification time, evidence for the status |
| `artifact` | no | Output file; `.md` and `.txt` can be previewed |
| `task_url` / `execution_url` | no | Real link to where the task runs, as returned by the host |
| `execution_provider`, `thread_id` | no | For Codex: a `codex` provider with a real thread ID produces an Open task link |
| `work_type` | no | Groups tasks by type; defaults to Other work |
| `user_priority`, `due_at`, `blocks_count`, `waiting_since` | no | Sorting: user priority, due date, blocking impact, time waiting |
| `started_at`, `has_started` | no | Distinguishes Not started from Pending |
| `is_example` | no | Marks sample tasks |

## workflows.json

A list of workflow entries. Built-in workflows from `example.workflows.json` are added automatically; your entries are kept as they are.

| Field | Required | Meaning |
|---|---|---|
| `id`, `name`, `category`, `purpose`, `path` | yes | ID ends in a number (`WF-OPS-012`); `path` points to the control file |
| `source` | no | `created` or `imported` for your own workflows |
| `builtin` | no | `true` only for workflows shipped with the package |
| `is_example`, `purpose_type` | no | Sample workflow; `reference` or `test` |
| `availability`, `verified_at`, `missing_requirements` | no | `not_checked`, `needs_configuration` or `ready` (with the check time) |
| `tested_at`, `created_at` | no | Successful trial time; creation time |

A personal index can replace the list: `{"scope": "personal", "index_path": "...", "overrides": [...]}` reads workflows from a Markdown table and never filters them by the built-in list.

## Tests

```sh
python3 -m unittest discover -s dashboard/tests
```
