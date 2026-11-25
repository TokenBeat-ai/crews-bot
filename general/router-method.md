# Coordinator method

This is the method your agent follows when you use Crews Bot. One coordinating conversation (the **coordinator**) takes your goals, picks a workflow, arranges execution, checks results and keeps the dashboard up to date. Each workflow file says *how a specific job is done*; this file says *how work is managed*.

First-time users: read [Getting started](getting-started.md) first.

## 1. Roles

| Part | Responsibility |
|---|---|
| Coordinator | Understands the goal, selects a workflow, confirms parameters, arranges execution, verifies outputs, updates the dashboard, reports to the user |
| Workflow file | The single source of truth for one job: inputs, adjustable parameters, fixed rules, steps, execution arrangement, acceptance |
| Executor | Does the work, in the coordinator's conversation or in a separate task when the host supports it |
| Dashboard | A local, read-only view of saved task records. It never runs work |

The coordinator does not copy or rewrite a workflow's steps. It points executors to the workflow file and passes the confirmed parameters.

## 2. From request to result

1. The user asks for something ("run the sample plan", or any goal).
2. The coordinator checks whether this continues an existing task (same goal, inputs, outputs or stage). If so, it reuses that task. Unrelated requests become separate tasks.
3. It reads the workflow file, if one applies, and shows **one numbered confirmation checklist**: one adjustable parameter per line with its proposed value. Fixed rules are not repeated as questions.
4. The user edits by number or confirms as a whole. Discussing a method, editing documents or loading the coordinator is not a start signal.
5. The coordinator registers the task (see section 6), arranges execution and hands over the workflow path, parameters, inputs, output location and authorized scope.
6. Each stage delivers files. The coordinator verifies them against the workflow's acceptance criteria before starting the next stage or reporting completion. A message saying "done" is not proof.
7. The coordinator records the verified result, updates the dashboard and reports outputs, open items and next steps.

A user can request work without first saving a workflow. Save a workflow only when the user wants to reuse the method.

## 3. Arranging execution

- Check what the host can actually do before promising anything. Capabilities differ by host; see [host support](../docs/hosts.md).
- If the host can start separate conversations and the user authorized it, create them as the workflow specifies and record the real IDs or links returned by the tool. Never invent a task link.
- If the host cannot, say so and give a manual hand-off: the exact prompt to paste and where. Only run the work inside the coordinator if the user chooses that.
- If a creation call times out, check whether it was created before retrying. Reuse the existing task instead of creating duplicates.
- Once a specific arrangement is authorized, follow it without asking again at every step.

## 4. Tracking active work

Keep a short **active list**: only tasks that still need attention. Each entry holds the task ID, the real execution link, current stage, next step, authorized scope and output location. Remove an entry once its result is verified and reported. An empty list is normal.

When checking progress:

- Read status first, then look closely only at tasks that changed.
- Do not wait on one task while others are ignored.
- When tasks share a file or database, confirm who is writing before anyone writes.
- If a result conflicts with the files, pause that hand-off and resolve the difference first.

| What you find | What the coordinator does |
|---|---|
| Running normally | Keep tracking; do not ask "is it done?" |
| Claims completion | Verify outputs against the workflow's acceptance criteria |
| Stopped before finishing | Find the stop point and resume within the authorized scope; do not repeat paid actions |
| Output accepted, next stage authorized | Record acceptance and start the next stage |
| Needs a user decision | Record it with options and a recommendation; keep other tasks moving |

Scheduled background checks only exist if the host supports them and the user set them up. Loading the coordinator does not start monitoring.

## 5. Reporting to the user

- The user handles one topic at a time. Do not switch topics because another task returned a result.
- Routine progress stays quiet. Completed work that can continue automatically does so and is reported at a natural break.
- Decisions the user must make (choosing an option, accepting output) are kept and presented when the current topic ends or the user asks.
- Interrupt only for imminent deadlines, wrong writes in progress, or actions that would exceed the authorized scope.

## 6. Recording tasks on the dashboard

The coordinator is the only writer of task records. After registering a task, receiving a hand-off or verifying a result, it updates `tasks.json` and re-renders the dashboard:

```sh
python3 dashboard/publish_snapshot.py --tasks <workspace>/tasks.json --workflows <workspace>/workflows.json --output <workspace>/dashboard.html
```

- Record real verification times, not page render times.
- Use `unknown` when the status is uncertain rather than guessing.
- Completion is recorded by the coordinator after verifying outputs (`status: done`, `verified_at`, `evidence`). The dashboard can only remove a task from view; removal does not stop work or delete outputs.
- Refreshing the dashboard reloads saved records. It does not check live progress.

Field definitions are in the [dashboard guide](../dashboard/README.md).

## 7. Dispatch fidelity

The coordinator routes; it does not add, drop or soften requirements.

- **Know the source of every instruction.** Confirmed parameters come from the user's confirmation; defaults come from the workflow file; research notes or the coordinator's own reasoning are references, not requirements.
- **Compare before sending.** Check the dispatch text against the confirmation and the workflow file. Remove anything that adds limits, narrows or widens scope, changes the method or lowers acceptance criteria without a source. If a change seems necessary, propose it to the user first.
- **Send the minimum.** Workflow path, confirmed parameters, inputs, output location, authorized scope and execution arrangement.
- **Fix mis-dispatches in place.** Correct the original executor; do not create a duplicate task or rewrite history.

## 8. Creating and importing workflows

When the user describes or imports a method, follow [workflow authoring](workflow-authoring.md). Report separately: method saved, registered in the list, requirements checked, trial run. Do not say "ready to use" unless requirements were checked in this environment.

## 9. Workflow list versus active list

The workflow list registers reusable methods (ID, name, purpose, file). The active list registers current work. Dates, batch numbers and one-off details never go into workflow names.
