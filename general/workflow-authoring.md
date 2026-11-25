# Workflow authoring

How the coordinator creates, imports or updates a workflow. A workflow is one file that fully describes a reusable job. Creating a workflow does not start any work.

## 1. When to use this

1. Read this guide and the current workflow list. Decide whether the request is a new method, a change to an existing one, or simply running an existing one. Reuse existing methods; a new batch or a new conversation is not a new workflow.
2. Understand the goal, inputs, current way of working, data and output locations, tools and completion criteria. Use what the user already said; ask only for what is missing.
3. Propose a concrete method using the template below: defaults, options, confirmation checklist, file locations and execution arrangement. Save it once the user approves.
4. Save one control file. Use the location the user specifies, otherwise `workflows/<short-name>/README.md` in the user's workspace. Check for duplicates and assign the next unused ID in the form `WF-<DOMAIN>-NNN`. Never renumber existing IDs.
5. Register the workflow in the dashboard's workflow configuration with `source: created` or `source: imported`, `builtin: false` and `created_at`. Only sample workflows set `is_example: true`.
6. Report what was saved and registered, what was checked, what is missing, and links to `#workflows?focus=<ID>` and `#run?workflow=<ID>` on the real dashboard address.

## 2. What every control file contains

| Section | Content |
|---|---|
| Identity and goal | Stable ID, name, goal, scope, branches, last updated, confirmation status |
| Fixed inputs and dependencies | Input and output locations, data, tools and templates; missing items marked clearly |
| Adjustable parameters | Meaning, default, short options; only those that apply |
| Confirmation checklist | Numbered, one adjustable item per line with its proposed value |
| Fixed rules | Followed every time; kept separate from adjustable parameters |
| Steps | The single method: inputs, actions, files read and written, outputs |
| Execution arrangement | Coordinator and executor roles, number of tasks, hand-off materials, stage start conditions |
| Acceptance and recovery | Evidence of completion, open items, resuming from interruptions, avoiding duplicate writes |
| Boundaries | Which actions need which authorization: spending, sending, publishing, writing |

Mark missing defaults as `TBD`; never invent them. Users can change several items at once or confirm everything together.

## 3. Confirmation and dispatch

- Show the checklist in the coordinator conversation before doing any work. Read-only lookups needed to build it are fine.
- Confirm the method and execution arrangement once; confirm adjustable parameters per batch. Do not ask again for what is already confirmed.
- Where a step needs a human decision (choosing an option, accepting output), state what is decided, when, and what happens next.
- Task titles use `TYYYYMMDD-NN-<category>-<task>`. Check existing tasks for the next unused number. A task continued on a later day keeps its original ID.

## 4. Import and creation receipts

- If requirements were checked and passed: "Workflow imported. Requirements checked: …" and offer a trial.
- Otherwise: "Workflow imported. Complete the following before running: …".
- `availability` is `ready` (with `verified_at`) only after checking in this environment; otherwise `not_checked` or `needs_configuration`. A successful trial is recorded separately as `tested_at`.
- Importing does not start a task.

## 5. Control file template

Replace the brackets and delete what does not apply. This is a structure, not an authorized instruction. See [the sample workflow](../workflows/sample-three-step-plan/README.md) for a filled-in example.

```markdown
# [ID] | [Workflow name]

Updated: [date]. Confirmation status: [pending / confirmed on date].

## 1. Goal and entry

Goal: [what is produced].
Entry phrase: [what the user can say].
Single method: section 5 of this file.

## 2. Fixed inputs and dependencies

- Inputs: [locations]
- Output location: [folder or file]
- Tools and materials: [available items; missing items]
- Fixed rules: [rules followed every time]

## 3. Adjustable parameters

| Parameter | Default | Options |
|---|---|---|
| [parameter] | [default or TBD] | [options] |

## 4. Confirmation checklist

1. [Parameter one]: [proposed value]; options [options].
2. [Parameter two]: [proposed value].
3. Execution: [where and how the work runs; authorizations needed].

The user edits by number or confirms everything. Work starts only after confirmation.

## 5. Steps

1. [Read inputs; check existing outputs]
2. [Do the work; decision points]
3. [Save results; check for other writers]
4. [Verify and hand off]

## 6. Execution arrangement

[Roles, number of tasks, order, hand-off files, start conditions]

## 7. Acceptance, recovery and boundaries

- Done when: [checkable outputs and evidence]
- Recovery: [resume from the last completed step without duplicate writes or costs]
- Boundaries: [authorizations for writing, spending, sending]
- Report: [outputs, file links, open items, next step]
```

## 6. Maintenance

Change an existing workflow by editing only the affected section of its file. Do not create parallel prompts. Saving a method, registering it and running a batch are three separate events.
