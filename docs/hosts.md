# Host support

Crews Bot is a set of methods, a local dashboard and an installer. The agent itself, its model and its tools come from your host application. Hosts differ in what they can do, so some steps are automatic in one host and manual in another.

## Support levels

| Host | Level |
|---|---|
| Codex | Fully supported. The methods were developed and tested here. |
| Cursor | In development |
| Claude Code | In development |
| Grok Build | In development |
| Hermes | In development |
| OpenClaw | In development |

Until support for a host is finished, any agent that can read and write local files can still follow the methods using the manual fallbacks below.

## Capabilities and manual fallbacks

| Capability | Used for | Codex | Other hosts | Manual fallback |
|---|---|---|---|---|
| Read and write local files | Everything | Yes | Yes | Required; no fallback |
| Run local commands | Installer, dashboard | Yes | Yes | Run the commands in INSTALL.md yourself |
| Start a separate task conversation | Running a task outside the coordinator | Yes | Manual | The coordinator gives you a prompt; open a new conversation, paste it, and tell the coordinator where it runs |
| Contact another conversation | Hand-offs between tasks | Yes | Manual | Copy the hand-off message the coordinator prepares into the other conversation; paste the reply back |
| Open the dashboard in a side panel | Viewing progress next to the chat | Yes | Manual | Open the printed `http://127.0.0.1:...` address in your browser |
| Scheduled checks | Periodic progress checks | If configured | Usually not | Ask the coordinator "check progress" when you return |
| Task links on the dashboard | Open task | Codex thread links | Not recorded | The card says no link is recorded; continue where the task runs |

The coordinator must state which fallback applies instead of claiming a capability the host does not have. See the [coordinator method](../general/router-method.md), section 3.
