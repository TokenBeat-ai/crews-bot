# WF-SAMPLE-001 | Sample: Three-step plan

A sample workflow for trying Crews Bot with fictional materials. Running it once creates a sample task, a short plan, a review step and a next-day follow-up. It does not search the web, send invitations or use paid services.

## 1. Goal and entry

- **Goal:** turn a short brief into a three-step plan, let the user review it, and continue the same task on a later day.
- **Entry phrase:** "Try the sample task: Three-step plan."
- **Single method:** section 5 of this file. Prompts and dashboard buttons only point here.

## 2. Fixed inputs

Use this fictional brief unless the user provides their own:

> Organize a 30-minute team sharing session next week. Choose a topic, prepare three key points and invite colleagues. The date and participants are not decided yet.

- **Output location:** `runs/<task-id>/plan.md` inside the user's workspace. Use the location the user already confirmed if there is one.
- **Tools:** reading and writing local files. Nothing else is required.
- **Fixed rules:** mark every task and output as a sample (`is_example: true`). Keep unknown details as `TBD`; do not invent dates, names or facts.

## 3. Adjustable parameters

| Parameter | Default | Options |
|---|---|---|
| Brief | The fictional brief above | Any short brief the user provides |
| Output language | The user's language | Any language |
| Output location | `runs/<task-id>/plan.md` | Any folder the user can write to |

## 4. Confirmation checklist

Show this once, then wait for the user to confirm or edit:

1. Brief: the fictional team sharing session (or the user's own brief).
2. Output: `runs/<task-id>/plan.md`, in the user's language.
3. Execution: in this conversation, or in a separate task if the host supports it and the user agrees.

## 5. Steps

1. **Register the task.** Create one task in `workspace/tasks.json` with a new task ID, the title "Sample: Three-step plan", status `running`, `work_type: "Planning"`, `is_example: true`, the output path and the link to the conversation where the task runs (see [task links](../../general/getting-started.md#4-language-and-data)). Re-render the dashboard.
2. **Draft the plan.** Write exactly three steps. Each step has an action, an owner placeholder and a completion criterion. Mark unknown items as `TBD`.
3. **Ask for review.** Set the task to `review` with the next step "Review the plan and mark changes". Show the user the plan and its path.
4. **Apply feedback.** Update the same file. Record what changed at the bottom of the plan.
5. **Pause for the next day.** Set the task to `waiting` with the next step "Continue tomorrow: confirm the date and send the invitation draft". This is the hand-off a real task would have.
6. **Continue later.** When the user returns ("continue the sample task"), reopen the same task ID, read the plan, add a short invitation draft (not sent), verify the file, then set the task to `done` with `verified_at` and the evidence.

## 6. Execution arrangement

The coordinating agent registers and verifies the task. If the host can start a separate conversation and the user agrees, the drafting can run there; otherwise run it in the current conversation. See [host support](../../docs/hosts.md).

## 7. Acceptance and boundaries

- **Done when:** `plan.md` exists, has three steps with completion criteria, includes the review changes and the invitation draft, and the task record points to it.
- **Recovery:** if interrupted, continue the same task ID from the last saved step. Do not create a second sample task.
- **Boundaries:** no messages, invitations, purchases or web searches. Everything stays in the workspace.
