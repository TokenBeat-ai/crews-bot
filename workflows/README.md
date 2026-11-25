# Workflows

A workflow is a reusable method: inputs, steps, outputs and acceptance criteria written in one file. Running a workflow creates a task.

This release ships one sample workflow. Add your own by describing or importing them; see [workflow authoring](../general/workflow-authoring.md).

| ID | Name | Needs | Purpose |
|---|---|---|---|
| [WF-SAMPLE-001](sample-three-step-plan/README.md) | Sample: Three-step plan | An agent that can read and write local files | Try the full loop with fictional materials: plan, review, continue the next day |

[`catalog.json`](catalog.json) lists the workflows shipped with this package. Your own workflows are registered in your workspace, not here, so updates never overwrite them.
