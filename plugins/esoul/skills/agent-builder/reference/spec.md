# The network spec — full reference

`set_agent_network_<App>({ spec })` takes this object. `describe_agent_network_<App>` returns the
same shape for an existing network, so read, edit and send it back to change one thing — also while
the network is listening or has runs open: it keeps listening and uses the new version from the next
event (runs already going finish on theirs). A spec without a trigger stops it listening.

```json
{
  "name": "string — the network's display name",
  "description": "string, optional",
  "default_model": "provider/model — used by every agent without its own model",
  "max_iter": "1–60 — hand-offs per run before it stops (default 10)",
  "nodes": [ { "id": "unique string", "type": "…", "…": "…" } ],
  "edges": [ { "from": "node id", "to": "node id", "when": "string, agent→agent only" } ]
}
```

Validation is the editor's own: any problem → nothing written, every problem listed with the node
it is on. Ids are yours (short, readable: `sorter`, `leads`, `new-mail`); they survive edits.

## Node kinds

### `agent`
A model with instructions.

| Field | |
|---|---|
| `name` | Shown in the app and in run steps. |
| `instructions` | **Required.** The system prompt. Say what to read, what to write where, when to finish, when to hand off. |
| `model` | Optional `provider/model`; else `default_model`. |
| `description` | Optional; the router reads it when choosing between hand-offs — say what this agent is for. |

The **first agent in `nodes`** is where every run starts. Its input is the run's `input`
(`run_agent_network_`) or the trigger's rendered `prompt`. A later agent receives what the previous
one produced.

### `app_tools`
All the tools of ONE app in this workspace (a spreadsheet, notes, calendar, contacts, Gmail,
slideshow, site, todo…). `app`: the app's name or id (from the catalogue's `apps`). The agent sees
them as `<verb>_<AppName>` — the same tools `get_app_tools` shows you for that app (calendar,
contacts and the old `email_viewer` inbox use the last six characters of the app's id instead of
its name: `add_event_hh9e0M`). Tools are bound by the app's identity: renaming the app later keeps
the binding. In instructions, name the tool the way `get_app_tools` spells it, or name the verb and
the app ("add the meeting to the Calendar") — never a spelling you have not seen.

### `workspace_tools`
Named tools that are not one app's: `tools: [names]` from the catalogue's `workspace_tools`, e.g.

| Tool | For |
|---|---|
| `ask_user` | Ask the person a question (optionally with button `options`); the run waits for the answer |
| `search_documents`, `list_documents`, `get_document_page`, `list_workspace_files` | Read the workspace's files (PDFs, docs) — indexed search |
| `search_workspace`, `what_changed` | Find things across the workspace; what happened recently |
| `drive_search`, `drive_list_folder`, `drive_import_file`, `drive_create_folder`, `move_file_to_drive` | Google Drive |
| `fetch_email_attachment`, `wait_for_indexing` | Pull an email's attachment into the workspace, wait until it can be read |
| `wait_for_reply`, `wait_for_app_state`, `sleep` | Durable waits: a reply to a thread, a condition on an app, a time |
| `generate_image` | Make an image into the workspace's files |
| `run_agent_network_<Other>` | Run ANOTHER network in this workspace as a tool (listed in the catalogue per network) |

`label` optional. Give each agent only the tools it needs.

### `web_search`
Searches the internet (and can read the pages). `limit` (results per query, default 6),
`sources` (`["web"]`, `["news"]`, `["images"]`), `name`/`description` optional.

### `image_agent`
An agent whose model makes or edits images (Gemini). `name`, `instructions`. Give it an image in
its input to edit one; otherwise it generates. Results land in the workspace's files.

### `open_app`
Creates a NEW app for each run and gives the connected agent its tools — for a run that produces
a document of its own (a deck, a sheet, a notes page). `app_type` (e.g. `slideshow`, `spreadsheet`,
`block_note_editor`), `name` (the app's name; `{{…}}` not supported — each run gets its own).
To write into an EXISTING app, use `app_tools` instead.

### `sub_agent_mapper`
Fan-out: runs ANOTHER network once per row of a spreadsheet, in parallel (a few at a time).

| Field | |
|---|---|
| `sub_agent_network` | **Required.** Name or id of the network to run per row (an `agent_builder` app in this workspace). It must not be this network. |
| `sheet` | The spreadsheet's name or id. |
| `tab` | Optional tab name (first tab otherwise). |
| `column` | **Required with `sheet`.** One sub-run per non-empty cell in this column. |

Each sub-run's input is that cell's value plus every column of the row by name. Build the per-row
network first (usually: one agent with `web_search` and the sheet's `app_tools`, told to fill that
row's other columns), then the network that contains the mapper. Connect an agent → mapper with a
hand-off edge (`when` optional for a mapper). Write a "done" column in the sub-network so re-runs can
skip finished rows.

### `trigger`
Runs the network when something happens in the workspace. One trigger per network; connect it to
the first agent.

| Field | |
|---|---|
| `event` | **Required.** An event name from the catalogue's `trigger_events` (`event`). |
| `source_app` | Optional: only events from this app (name or id). Without it, any app of that type. |
| `prompt` | The run's input, with `{{variables}}` from the event (the catalogue lists each event's `variables`, e.g. `{{email.from}}`, `{{email.subject}}`, `{{email.snippet}}`, `{{email.body}}`, `{{email.threadId}}`). |
| `run_mode` | `per_event` (default) or `per_item` — for BATCH events (a mail sync delivers several emails at once) `per_item` runs once per item, with the item's variables. Use `per_item` for mail. |
| `filter` | Optional — skip items before any model runs. |

Common events (always confirm names in the catalogue — they differ by app):

| App | Event | Batch | Variables |
|---|---|---|---|
| Gmail (`plugin_gmail`) | `gmail_synced` — new email | yes, item `email` | `{{email.from}}`, `{{email.fromEmail}}`, `{{email.subject}}`, `{{email.snippet}}`, `{{email.body}}`, `{{email.threadId}}`, `{{email.id}}`, `{{email.labelIds}}`, `{{email.attachments[0].filename}}` |
| Inbox (`email_viewer`, the older mail app — build on Gmail) | `email_messages_synced` — new email | yes, item `email` | as above |
| Telegram | `telegram_messages_synced` — new message | yes, item `message` | `{{message.text}}`, `{{message.chatId}}`, `{{message.chat.title}}`, `{{message.from.name}}`, `{{message.from.username}}` |
| Calendar | `calendar_create_event` — event created | | `{{event.title}}`, `{{event.startTime}}`, `{{event.endTime}}`, `{{event.location}}`, `{{event.description}}` |
| Calendar | `calendar_external_events_synced` — Google event synced | yes, item `event` | as above |
| Calendar | `calendar_request_event` — a visitor asked for a slot | | `{{request.startTime}}`, `{{request.submitterName}}`, `{{request.submitterEmail}}`, `{{request.message}}` |
| Todo | `todo_add_item` — item added | | `{{event.text}}`, `{{event.listName}}` |
| Contacts | `contact_added_by_agent` / `contact_arrived_from_google` | | `{{contact.displayName}}`, `{{contact.email}}`, `{{contact.organization}}` |
| Block notes | `blocknote_create_tab` — page created | | `{{event.tabName}}`, `{{event.pageId}}` |

Many more apps emit events (site forms and orders, inventory movements, the cloud browser, training runs, the research graph, the Forge) — the catalogue lists them all with their variables.

**Filter grammar.** Clauses separated by commas are all required (AND). Each clause is
`<left> <op> <right>` with `==`, `!=`, `in`, `not in`. Field references MUST be in braces —
`{{email.from}}`, never bare `email.from` (a bare name is compared as literal text). `in` / `not in`
take a comma list, or an array field:

```
{{email.fromEmail}} != me@example.com, INBOX in {{email.labelIds}}
{{email.fromEmail}} not in noreply@x.com, alerts@y.com
```

A trigger only fires on events AFTER it was started. Mail sent from the Gmail app itself is recorded
as sent and is never new mail, and neither are drafts, spam, bounces or auto-replies. To see a mail
trigger fire, send the inbox an email from anywhere else — another address, or gmail.com.

## Edges

| From → to | Means |
|---|---|
| trigger → agent | The trigger starts runs at this agent (must be the first agent). |
| agent → agent | A hand-off. `when` required — the router's rule. |
| agent → sub_agent_mapper | Fan out after this agent. |
| agent → app_tools / workspace_tools / web_search / open_app | This agent gets those tools. |

After an agent finishes: no hand-offs → the run ends; exactly one → it is always taken (a
pipeline); two or more → the router picks by `when`, or ends the run. Tools never connect to
anything; nothing connects into a trigger.

## Models

`provider/model`, from the catalogue's `models`. Currently: `anthropic/claude-haiku-4.5`,
`anthropic/claude-sonnet-4.6`, `anthropic/claude-sonnet-5`, `anthropic/claude-opus-5`,
`openai/gpt-5.4`, `openai/gpt-4o`, `google/gemini-2.5-flash`, `google/gemini-2.5-pro`,
`deepseek/deepseek-v4-flash`, `deepseek/deepseek-v4-pro`. Cheap and fast for sorting, routing,
per-row work: Haiku, DeepSeek flash, Gemini flash. Careful writing and judgement: Sonnet, Opus, GPT-5.4.

## Escape hatch

Any node may carry `data: { … }` — raw builder fields merged last — for a setting the spec does not
name (for example a web_search `scrapeMode`). Read `describe_agent_network_` first to see the shape.
