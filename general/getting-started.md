# Getting started

Instructions for the agent helping a user for the first time.

## 1. Install and open

1. Check the installation path, version, file permissions and which capabilities this host actually has (see [host support](../docs/hosts.md)). Preserve any existing data.
2. Follow [INSTALL.md](../INSTALL.md) to install and start the dashboard (if the user already has a copy of the repository, use Option B in that folder). Run the dashboard server in the background, then open the page yourself: in the host's side panel if it has one (Codex does), otherwise give the user the address. Do not ask the user to run commands. Installing and opening the dashboard does not start any work.
3. If the user has a specific goal, help with it directly. Otherwise, open **Getting started** in the dashboard.

## 2. The three getting-started options

- **Try a sample task: Three-step plan.** Follow [the sample workflow](../workflows/sample-three-step-plan/README.md). It uses fictional materials and covers the full loop: register a task, draft, review, pause, continue later and verify.
- **Describe a workflow.** Follow [workflow authoring](workflow-authoring.md) to turn the user's description into a saved, registered method.
- **Import workflow.** Same guide; start from the user's existing file.

**Not now** returns to Tasks.

## 3. Running a saved workflow

The user chooses **Prepare to run** on a workflow, edits the prefilled prompt if needed, copies it and sends it to the agent conversation used to open the dashboard. Copying does not start a task. Before creating a task, check for an existing related one.

## 4. Language and data

- Reply and deliver in the user's language. The English interface does not require English output.
- Never translate or rename the user's tasks, workflows, categories or files.
- Record real task links, statuses, next steps and outputs. In Codex, set `execution_provider: "codex"` and `thread_id` to the ID of the conversation where the task runs (for the current conversation, Codex provides it to commands as the `CODEX_THREAD_ID` environment variable); the dashboard then shows **Open task**. In other hosts, set `task_url` only if the host returns a real link. Never invent one.
- Give every task a short `work_type` (for example Planning, Research, Writing) so the dashboard can group it.
- Refresh reloads saved records; it does not monitor live work. If the configuration is broken, keep the last snapshot and report the error.

Then continue with the [coordinator method](router-method.md).
