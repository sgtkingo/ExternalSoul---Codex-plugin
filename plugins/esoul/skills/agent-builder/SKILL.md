---
name: agent-builder
description: "Build, run and operate multi-agent networks in the person's ExternalSoul workspace over MCP — agents with instructions and models, the workspace's apps as their tools, web search, hand-offs between agents, a trigger that runs the network on every new email / calendar event / todo / Telegram message, fan-out over a spreadsheet, questions to the person, changing a network while it is live (no stop needed), and stopping it. Use whenever someone asks for \"an agent that…\", wants work to happen automatically when something arrives, wants to automate a workflow across their apps, or asks what their agents are doing, why one failed, or to stop one. Also use when someone wants to change how an agent works, fix what it got wrong, or improve instructions of a network that is already running."
---

# Agent networks in ExternalSoul

An **agent network** is an app in a workspace (type `agent_builder`). It holds a graph: **agents**
(a model with instructions) connected to **tools** (the workspace's own apps, workspace tools, web
search) and to each other by **hand-offs**; optionally a **trigger** that runs it whenever an event
happens in the workspace. A run executes in the background; every step lands on the workspace
timeline, and the person sees it live in the app (Build / Runs tabs). Agents use the same tools the
person does, so whatever an agent writes is an ordinary change to the person's apps.

Everything below goes through the app's own tools: `get_app_tools` lists them, `call_app_tool`
calls one. Their names end with the app's name — spaces become underscores (`set_agent_network_Mail_Triage`
for an app called "Mail Triage"). A few older apps (calendar, contacts, the old `email_viewer` inbox)
end theirs with the last six characters of the app's id instead (`add_event_hh9e0M`), so a rename
never breaks them. Take exact names from `get_app_tools`; never guess.

| Tool (suffix `_<App>`) | Does |
|---|---|
| `agent_builder_catalogue_` | What can be built: node kinds, models, workspace tool names, trigger events with their `{{variables}}`, this workspace's apps |
| `set_agent_network_` | Build or replace the whole network from a **spec** (below). Validated; nothing is written if anything is wrong, and every problem is listed. **Works while the network listens or runs** — no Stop |
| `describe_agent_network_` | The network as a spec + whether it is listening / has runs open + problems that would stop it |
| `run_agent_network_` | Run once with a task (`input`). Returns at once; the run works in the background |
| `start_agent_network_` | Start listening for the trigger: every matching event runs the network |
| `stop_agent_network_` | Stop: trigger off, every run the network started cancelled, their questions closed |
| `list_agent_runs_` / `read_agent_run_` | Recent runs; one run's status, result or error, pending question, last steps |
| `answer_agent_question_` | Answer the question a run is waiting on; the run resumes |

## The loop

1. **Find or make the app.** `list_workspaces` → the workspace. An existing network: find the
   `agent_builder` app there. A new one: `create_app` with `application_type: "agent_builder"` and
   a name that says what it does ("Mail Triage", "Lead Researcher"). Then `get_app_tools`.
2. **Read the catalogue** (`agent_builder_catalogue_`) — the exact app names, event names and
   variables, workspace tool names and models you may use.
3. **Make the apps the agents will use, first.** An agent writes into apps that exist; the spec
   only names them. `create_app` takes the application TYPE as the catalogue's `apps` show it
   (`spreadsheet`, `todo_app`, `calendar`, `block_note_editor`, `plugin_gmail`, `telegram_messenger`…).
   Mail is `plugin_gmail` (the Gmail app; trigger `gmail_synced`) — `email_viewer` is the older
   inbox, kept working but not the one to build on.
   Shape them for the job: a new spreadsheet starts with placeholder columns A, B, C — add the
   columns the instructions name (`add_column_<Sheet>`, a `status` type with `options` for a fixed
   set of values) and delete the placeholders. A mail or Telegram app does nothing until its account
   is connected: the person assigns the Google account (or connects the bot) once, in the app —
   say so and wait before starting a trigger on it.
4. **Write the spec** and `set_agent_network_`. If it answers "Not saved", fix every listed problem
   and send the whole spec again. Full field reference: `reference/spec.md`. Complete worked
   networks: the `agent-recipes` skill.
5. **Check it**: `describe_agent_network_` → `problems` must be empty.
6. **Try it once** with `run_agent_network_` and a realistic `input` — even for a triggered
   network (the input stands in for the trigger's prompt, so write it in the prompt's shape). Use
   a REAL item: take a thread id / row id / event from the app (`list_inbox_Gmail`, `read_sheet_…`),
   because an agent told to reply on thread "test-1" fails at the tool. Follow it with `list_agent_runs_` →
   `read_agent_run_` until the status is terminal (`ok`, `error`, `canceled`, `timeout`).
   Read the steps: did each agent call the tools you expected, did the hand-off happen, is the
   result right? Adjust the spec (instructions are the usual fix) and try again.
7. **Start it** (`start_agent_network_`) only when the person wants it to act on its own. A
   trigger fires only on events AFTER the start. To see it fire on mail, send the inbox an email
   from Gmail itself (another address, or the same account from gmail.com) — NOT with the Gmail
   app's `send_email_Gmail`: what the app sends it records as sent, and that never counts as new mail.
   A started network stays editable: change it with `set_agent_network_` while it listens — the
   trigger stays armed and the next event uses the new version.
8. **Report** what it will do, on what, with which model, what a run cost (a sorter on Haiku plus
   one specialist on DeepSeek flash is about $0.004 an email), and how to stop it.

**Edit it live.** `set_agent_network_` works while the network listens or runs — no Stop needed.
A listening network keeps listening and uses the new version from the next event; a run already
going finishes on the version it started with (the answer says how many). A new spec without a
trigger stops listening. To fix a network that got an email wrong: read the run, change the
instructions, save, then `run_agent_network_` on that same email to see the fix work.

## The spec in one screen

```json
{
  "name": "Mail Triage",
  "default_model": "anthropic/claude-haiku-4.5",
  "max_iter": 8,
  "nodes": [
    { "id": "new-mail", "type": "trigger", "event": "gmail_synced", "source_app": "Gmail",
      "run_mode": "per_item",
      "prompt": "New email.\nFrom: {{email.from}}\nSubject: {{email.subject}}\nThread id: {{email.threadId}}\n\n{{email.body}}" },
    { "id": "sorter", "type": "agent", "name": "Sorter",
      "instructions": "1. Decide the verdict, one word: reply, meeting or info. 2. Log it with add_row_Mail_Log, cells {\"From\", \"Subject\", \"Verdict\"} — all three, every time. 3. Finish with: Verdict, Row id (from add_row), From, Subject, Thread id, what they want. For info, finish with Done." },
    { "id": "replier", "type": "agent", "name": "Replier", "model": "anthropic/claude-sonnet-4.6",
      "instructions": "Draft a reply in the person's voice. Ask the person before sending anything that commits them." },
    { "id": "scheduler", "type": "agent", "name": "Scheduler",
      "instructions": "Find a free slot in the Calendar and propose it in a reply draft." },
    { "id": "log", "type": "app_tools", "app": "Mail Log" },
    { "id": "cal", "type": "app_tools", "app": "Calendar" },
    { "id": "mail", "type": "app_tools", "app": "Gmail" },
    { "id": "ask", "type": "workspace_tools", "tools": ["ask_user"] }
  ],
  "edges": [
    { "from": "new-mail", "to": "sorter" },
    { "from": "sorter", "to": "replier", "when": "the email needs a written reply" },
    { "from": "sorter", "to": "scheduler", "when": "the email asks to meet" },
    { "from": "scheduler", "to": "cal" },
    { "from": "scheduler", "to": "mail" },
    { "from": "sorter", "to": "log" },
    { "from": "replier", "to": "mail" },
    { "from": "replier", "to": "ask" }
  ]
}
```

- **The first agent in `nodes` is where every run starts.**
- **agent → agent** = a hand-off, with a `when` rule (required). What happens after an agent
  finishes depends on how many hand-offs leave it:
  - **none** — the run ends;
  - **exactly one** — it is ALWAYS taken, without asking the router: agents in a line run as a
    pipeline, one after the other, whatever `when` says;
  - **two or more** — the router reads their `when` rules and picks one, or ends the run when none
    fits. This is how a network makes a decision.

  So a conditional step ("hand off only if a reply is needed") needs a second hand-off (another
  specialist) or must live inside the agent's own instructions ("if no reply is needed, log it and
  finish").
- **agent → tool node** = that agent can use those tools. Tools are per agent — connect each
  agent to what it needs, nothing more.
- **trigger → first agent.** The trigger's `prompt` (with `{{variables}}`) is the run's input.
- Apps are named by their name as `list_workspaces` / the catalogue shows them (or their id).

## Choosing well

- **Few agents, one job each.** One agent that sorts and one that writes beats five that chat.
  Every hand-off is a model call and a chance to misroute; `max_iter` caps hand-offs per run.
- **Instructions are the program.** Say what to read, what to write where, when to stop, and when to
  hand off. Name the apps by name. Ask for short final answers — the last agent's final message is
  the run's result.
- **A hand-off carries only the previous agent's final message.** So the agent that decides must
  END with everything the next one needs, ids included — the row it wrote, the thread id, the
  message id — in a fixed shape ("Verdict: … / Row id: … / Thread id: …"). Put the ids in the
  trigger's prompt too (`{{email.threadId}}`, `{{email.id}}`), or nobody downstream can act on the thread.
- **Decide, then write, and name every cell.** "Add a row with sender, subject, verdict" before the
  verdict is decided gets a row without the verdict. Order the steps, and give the exact column
  names: `cells {"From", "Subject", "Verdict"}`. Downstream agents update that row by its id
  (`update_cell_<Sheet>` with `rowId` and `column`).
- **A reply is judged with its thread.** Tell the deciding agent to read the thread when the email is
  a reply ("Re:", or it refers to an earlier message), and to judge by what the NEW email says — the
  sender may be the owner writing to themself, which is still a request (the Gmail app labels such a
  message "your own"). Give every kind of request somewhere to go: a meeting agent that only books
  leaves "cancel" and "move" with no one to act on them.
- **Drafts, not sends, until the person says otherwise.** `create_email_draft_Gmail` on the same
  thread leaves the letter one press from sent; `send_email_Gmail` sends to real people at once.
- **Cheap models for sorting and routing** (`anthropic/claude-haiku-4.5`, `deepseek/deepseek-v4-flash`),
  strong models where quality shows (`anthropic/claude-sonnet-4.6` and up). Set the cheap one as
  `default_model`, override per agent.
- **Triggers cost per event.** `run_mode: "per_item"` runs once per item of a batch (one run per
  email, not one per sync). Use `filter` to skip noise before any model runs (see `reference/spec.md`).
- **Questions park runs.** An agent with `ask_user` waits — for days if nobody answers — and each
  waiting run counts as open. Tell the agent exactly when to ask; for routine cases tell it to decide.
- **Runs spend the person's credits.** Test with one run before starting a trigger on a busy inbox.

## Operating

- "Change it" / "it got this wrong" → **edit it live, never Stop first.** `describe_agent_network_`,
  change the one agent's instructions (or the trigger's prompt, filter, source), send the whole spec
  back with `set_agent_network_`. The trigger stays armed and the next event uses the new version;
  runs already going finish on theirs. Then `run_agent_network_` on the email that went wrong, and
  `read_agent_run_` to see the fix work. Stopping only to edit loses events that arrive meanwhile.

- "What is it doing?" → `describe_agent_network_` (status line) then `list_agent_runs_`.
- "Why did it fail?" → `read_agent_run_` → `error` and the last steps. Common causes:
  `Out of credits`; `Stopped at the iteration cap` (raise `max_iter` or tighten `when` rules);
  a tool the agent needed was not connected; a source app was removed (`describe_…` lists it).
- A run waiting on the person → `read_agent_run_` shows `pending_question`; answer with
  `answer_agent_question_` only with the person's words or explicit permission.
- "Stop it" → `stop_agent_network_`. It reports runs cancelled, whether the trigger was on, and
  questions closed. Nothing new starts until `start_agent_network_`.
- Undo: in the app's Runs tab a finished run can be **reverted** (its changes to the workspace are
  rolled back) — unless it changed something outside the workspace (sent mail, a calendar event on
  Google, a Gmail label), which cannot be taken back. That is a person's action in the app.

## Never

- Never start a trigger the person did not ask for, or on an inbox/calendar without saying which.
- Never answer a run's question with your own guess about the person's wishes.
- Never claim an agent did something without reading the run (`read_agent_run_`).
