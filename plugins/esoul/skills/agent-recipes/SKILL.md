---
name: agent-recipes
description: "Complete, working agent networks for ExternalSoul's agent builder, and what to build across the apps (Gmail, Telegram, spreadsheets, block notes, calendar, contacts, todo, files, sites) — inbox triage when an email arrives, a Telegram desk that answers from your notes, receipts into a spending sheet, meeting prep from the calendar, a knowledge base that grows from mail, a researcher with web search writing into notes, lead enrichment over every row of a spreadsheet, a report that builds its own slide deck, approval before anything is sent, a planner handing work to specialists, a daily/event watcher, image making, and networks that call networks. Use with the agent-builder skill when someone asks for a kind of agent and you need the right shape fast; adapt names, apps and instructions to their workspace."
---

# Agent recipes

Each recipe is a spec for `set_agent_network_<App>` (see the **agent-builder** skill for the tools,
the loop and `reference/spec.md` for every field). Before using one:

1. `agent_builder_catalogue_<App>` — replace app names with the person's real apps, event names with
   the ones their mail/calendar app actually emits, and pick models from the list.
2. Create any app the recipe writes to that does not exist yet (`create_app`): a spreadsheet with
   the columns the instructions name, a notes app, a slideshow. Agents write into existing apps.
3. Send the spec; fix every listed problem; `run_agent_network_` once with a realistic input;
   read the run; only then `start_agent_network_` (triggered recipes).

Instructions are written for the model — keep them concrete: which app, which columns, what to do
when unsure, how to finish.

---

## 1. Inbox triage — several agents, each with its own tools, on every new email

A sorter logs every email and decides; specialists act. Three hand-offs leave the sorter, so the
router chooses (or ends the run when none fits — info and promo stop at the log). This exact
network ran live on a real Gmail inbox (the docs' Mail Desk): about $0.004 an email.

Apps: Gmail (`plugin_gmail`, named "Gmail" here), a spreadsheet "Mail Log" with columns
From (email), Subject, Verdict (status: reply, meeting, task, info, promo), Action; Calendar; Todo.

```json
{
  "name": "Mail Desk",
  "default_model": "deepseek/deepseek-v4-flash",
  "max_iter": 6,
  "nodes": [
    {
      "id": "new-mail",
      "type": "trigger",
      "event": "gmail_synced",
      "source_app": "Gmail",
      "run_mode": "per_item",
      "prompt": "New email.\nFrom: {{email.from}}\nSubject: {{email.subject}}\nThread id: {{email.threadId}}\nMessage id: {{email.id}}\n\n{{email.body}}"
    },
    {
      "id": "sorter",
      "type": "agent",
      "name": "Sorter",
      "model": "anthropic/claude-haiku-4.5",
      "description": "Reads each new email, logs it, and decides whose work it is.",
      "instructions": "You sort one new email. Judge it by what the NEW email says; the sender may be the account's owner writing to themself, and that is still a request to act on.\n1. If it is a reply (the subject starts with Re:, or it refers to an earlier message), read the thread with read_thread_Gmail for context — what was asked or booked before.\n2. Decide the verdict, one word: reply (a person asks something you can answer in writing), meeting (they want to meet or call at a time, OR to move, confirm or cancel a meeting already agreed), task (they ask for something to be done later), info (nothing to do), promo (newsletters, marketing, automated mail).\n3. Log it with add_row_Mail_Log, cells {\"From\": sender address, \"Subject\": subject, \"Verdict\": the verdict word}. All three cells, every time.\n4. Finish with a short message in this shape, so the next agent has everything:\nVerdict: <verdict>\nRow id: <the rowId add_row returned>\nFrom: <sender>\nSubject: <subject>\nThread id: <thread id>\nMessage id: <message id>\nWhat they want: <one or two sentences — for a meeting say whether it is new, moved or cancelled, and the day and time>\nFor info and promo, end with Done: nobody else needs to act."
    },
    {
      "id": "replier",
      "type": "agent",
      "name": "Replier",
      "description": "Drafts a reply in Gmail for mail that asks a question.",
      "instructions": "You draft the reply to one email. Read the thread with read_thread_Gmail if you need more than the summary. Write a short, warm, specific answer and save it with create_email_draft_Gmail as a reply on the same thread (never send). Then set the Action cell of the Mail Log row (the Row id you were given) with update_cell_Mail_Log to 'Reply drafted'. Finish with one line saying what you drafted."
    },
    {
      "id": "scheduler",
      "type": "agent",
      "name": "Scheduler",
      "description": "Books, moves or cancels meetings in the calendar and drafts the reply.",
      "instructions": "You handle one email about a meeting. Read the thread with read_thread_Gmail first.\n- A NEW meeting: add it to the Calendar (title: the sender's name and the topic; one hour unless they said otherwise; if the time is busy, pick the nearest free hour). Action: 'Booked <day time>'.\n- A MOVED meeting: read the Calendar's events, find the meeting this thread booked (same person and topic, the day it was set for), and change its time. Action: 'Moved to <day time>'.\n- A CANCELLED meeting: find it the same way and delete it. Action: 'Cancelled <day time>'. If you cannot find it, change nothing and set Action to 'Cancel: meeting not found'.\nThen draft a short reply with create_email_draft_Gmail on the same thread saying what you did (never send), and set the Action cell of the Mail Log row (the Row id you were given) with update_cell_Mail_Log. Finish with one line."
    },
    {
      "id": "tasker",
      "type": "agent",
      "name": "Tasker",
      "description": "Turns a request into a todo.",
      "instructions": "You turn a request into work. Add one todo item to the Todo app that says exactly what to do and for whom, with the deadline if they gave one. Set the Action cell of the Mail Log row (the Row id you were given) with update_cell_Mail_Log to 'Todo added'. Finish with one line."
    },
    {
      "id": "log",
      "type": "app_tools",
      "app": "Mail Log"
    },
    {
      "id": "gmail",
      "type": "app_tools",
      "app": "Gmail"
    },
    {
      "id": "calendar",
      "type": "app_tools",
      "app": "Calendar"
    },
    {
      "id": "todo",
      "type": "app_tools",
      "app": "Todo"
    }
  ],
  "edges": [
    {
      "from": "new-mail",
      "to": "sorter"
    },
    {
      "from": "sorter",
      "to": "replier",
      "when": "Verdict is reply"
    },
    {
      "from": "sorter",
      "to": "scheduler",
      "when": "Verdict is meeting (new, moved or cancelled)"
    },
    {
      "from": "sorter",
      "to": "tasker",
      "when": "Verdict is task"
    },
    {
      "from": "sorter",
      "to": "log"
    },
    {
      "from": "sorter",
      "to": "gmail"
    },
    {
      "from": "replier",
      "to": "gmail"
    },
    {
      "from": "replier",
      "to": "log"
    },
    {
      "from": "scheduler",
      "to": "gmail"
    },
    {
      "from": "scheduler",
      "to": "calendar"
    },
    {
      "from": "scheduler",
      "to": "log"
    },
    {
      "from": "tasker",
      "to": "todo"
    },
    {
      "from": "tasker",
      "to": "log"
    }
  ]
}
```

Why it is shaped this way: meetings are booked, moved AND cancelled — a Scheduler that only books
leaves a cancellation with no one to act on it (the first live run did exactly that). A hand-off carries
only the sorter's final message, so the sorter ends
with the row id and thread id the specialists act on; it decides BEFORE it writes, and names every
cell, or the verdict comes out empty. Test: `run_agent_network_` with an input in the prompt's shape
built from a REAL email (`list_inbox_Gmail` gives its thread id). Then start it; to watch it fire,
email the inbox from anywhere but the Gmail app (another address, or gmail.com) — what the app
sends it records as sent, and that never counts as new mail.
Add `"filter": "{{email.fromEmail}} not in noreply@…, notifications@…"` to the trigger to skip noise.

## 2. Researcher that writes a brief into notes

Apps: a notes app (`block_note_editor`) "Briefs".

```json
{
  "name": "Researcher",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "research", "type": "agent", "name": "Researcher",
      "instructions": "Research the topic in the task with web search (several focused queries). Write a page in the Briefs notes app titled with the topic: a five-line summary, key facts with sources as links, open questions. Finish with the page title." },
    { "id": "web", "type": "web_search", "limit": 6 },
    { "id": "notes", "type": "app_tools", "app": "Briefs" }
  ],
  "edges": [ { "from": "research", "to": "web" }, { "from": "research", "to": "notes" } ]
}
```

Run: `run_agent_network_` with `input: "Heat pumps for Czech family houses in 2026"`.

## 3. Enrich every row of a spreadsheet (fan-out)

Two networks. The per-row one first, then the one that fans out.

Apps: spreadsheet "Leads" with columns Company, Website, Summary, Size, Done.

Network **"Lead Row"**:
```json
{
  "name": "Lead Row",
  "default_model": "deepseek/deepseek-v4-flash",
  "nodes": [
    { "id": "enrich", "type": "agent", "name": "Enricher",
      "instructions": "The input is one row of the Leads sheet (the company name and all its columns). Find the company's website, a one-sentence summary and the rough headcount with web search. Update THAT row (find it by Company) with Website, Summary, Size, and Done = yes. Finish with the company name." },
    { "id": "web", "type": "web_search", "limit": 4 },
    { "id": "leads", "type": "app_tools", "app": "Leads" }
  ],
  "edges": [ { "from": "enrich", "to": "web" }, { "from": "enrich", "to": "leads" } ]
}
```

Network **"Lead Fan-out"**:
```json
{
  "name": "Lead Fan-out",
  "default_model": "anthropic/claude-haiku-4.5",
  "nodes": [
    { "id": "start", "type": "agent", "name": "Dispatcher",
      "instructions": "Confirm the Leads sheet has rows to enrich and finish with how many." },
    { "id": "each", "type": "sub_agent_mapper", "sub_agent_network": "Lead Row", "sheet": "Leads", "column": "Company" },
    { "id": "leads", "type": "app_tools", "app": "Leads" }
  ],
  "edges": [ { "from": "start", "to": "leads" }, { "from": "start", "to": "each" } ]
}
```

Run the fan-out once; each row gets its own sub-run (visible in the Runs tab). Test "Lead Row"
alone first with one row as input.

## 4. A report that builds its own deck

`open_app` makes a fresh slideshow per run.

```json
{
  "name": "Weekly Report",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "analyst", "type": "agent", "name": "Analyst",
      "instructions": "Read the Sales sheet. Work out this week's totals, the three biggest changes and one risk. Hand the numbers on as a short list." },
    { "id": "designer", "type": "agent", "name": "Deck writer",
      "instructions": "Make a five-slide deck in the new slideshow: title, totals, three changes (one slide), the risk, next steps. Short text, big numbers. Finish with the deck's name." },
    { "id": "sales", "type": "app_tools", "app": "Sales" },
    { "id": "deck", "type": "open_app", "app_type": "slideshow", "name": "Weekly report" }
  ],
  "edges": [
    { "from": "analyst", "to": "sales" },
    { "from": "analyst", "to": "designer", "when": "the numbers are ready" },
    { "from": "designer", "to": "deck" }
  ]
}
```

One hand-off → always taken: a two-step pipeline.

## 5. Nothing goes out without the person's yes

The writer drafts, asks, and sends only on approval.

```json
{
  "name": "Careful Sender",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "writer", "type": "agent", "name": "Writer",
      "instructions": "Write the email the task asks for. Then ask the person with ask_user, showing the full email, with options [\"Send\", \"Change\", \"Cancel\"]. On Send: send it from Gmail. On Change: ask what to change, rewrite, ask again. On Cancel: finish without sending." },
    { "id": "ask", "type": "workspace_tools", "tools": ["ask_user"] },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" }
  ],
  "edges": [ { "from": "writer", "to": "ask" }, { "from": "writer", "to": "gmail" } ]
}
```

The run waits on the question: the person answers in the app (the bell), or you relay their answer
with `answer_agent_question_<App>` — only their words.

## 6. A planner and specialists

The planner decides who works next; specialists hand back to the planner, which ends the run when
the goal is met (two or more hand-offs → the router may end).

```json
{
  "name": "Event Planner",
  "default_model": "anthropic/claude-haiku-4.5",
  "max_iter": 10,
  "nodes": [
    { "id": "plan", "type": "agent", "name": "Planner", "model": "anthropic/claude-sonnet-4.6",
      "instructions": "Turn the task into steps: venue research, invitations list, schedule. After each specialist reports, decide what is still missing. When everything is done, finish with a summary." },
    { "id": "venues", "type": "agent", "name": "Venue scout", "description": "Finds venues.",
      "instructions": "Find three venues that fit with web search; add them to the Plan notes page under Venues." },
    { "id": "guests", "type": "agent", "name": "Guest list", "description": "Builds the invitation list.",
      "instructions": "Build the invitation list from the Contacts app into the Guests sheet (Name, Email)." },
    { "id": "sched", "type": "agent", "name": "Scheduler", "description": "Books time.",
      "instructions": "Put the event and two prep meetings in the Calendar." },
    { "id": "web", "type": "web_search" },
    { "id": "notes", "type": "app_tools", "app": "Plan" },
    { "id": "contacts", "type": "app_tools", "app": "Contacts" },
    { "id": "sheet", "type": "app_tools", "app": "Guests" },
    { "id": "cal", "type": "app_tools", "app": "Calendar" }
  ],
  "edges": [
    { "from": "plan", "to": "venues", "when": "venues are still missing" },
    { "from": "plan", "to": "guests", "when": "the guest list is still missing" },
    { "from": "plan", "to": "sched", "when": "the schedule is still missing" },
    { "from": "venues", "to": "plan", "when": "always, to report" },
    { "from": "guests", "to": "plan", "when": "always, to report" },
    { "from": "sched", "to": "plan", "when": "always, to report" },
    { "from": "venues", "to": "web" }, { "from": "venues", "to": "notes" },
    { "from": "guests", "to": "contacts" }, { "from": "guests", "to": "sheet" },
    { "from": "sched", "to": "cal" }
  ]
}
```

`max_iter` bounds the back-and-forth; a run that hits it ends as an error saying so.

## 7. React to something in the workspace

Any event in the catalogue can start a network — a todo added, a contact added, a calendar event
created, a new Telegram message, a notes page created:

```json
{
  "name": "Todo Helper",
  "default_model": "deepseek/deepseek-v4-flash",
  "nodes": [
    { "id": "added", "type": "trigger", "event": "todo_add_item", "source_app": "Todo",
      "prompt": "A todo was added to {{event.listName}}: {{event.text}}" },
    { "id": "helper", "type": "agent", "name": "Helper",
      "instructions": "If the todo needs information from the web, research it and put a short note in the Notes app linked from the todo. Otherwise finish with 'nothing to add'." },
    { "id": "web", "type": "web_search" },
    { "id": "notes", "type": "app_tools", "app": "Notes" }
  ],
  "edges": [ { "from": "added", "to": "helper" }, { "from": "helper", "to": "web" }, { "from": "helper", "to": "notes" } ]
}
```

## 8. Images

```json
{
  "name": "Product Shots",
  "nodes": [
    { "id": "brief", "type": "agent", "name": "Art director",
      "instructions": "Turn the product description into one precise image prompt: subject, setting, light, lens, mood." },
    { "id": "paint", "type": "image_agent", "name": "Painter",
      "instructions": "Make the image the prompt describes. Describe what you made in one line." }
  ],
  "edges": [ { "from": "brief", "to": "paint", "when": "the prompt is written" } ]
}
```

## 9. Waiting — durable, days if needed

Give an agent `wait_for_reply` (a reply to a thread it sent), `wait_for_app_state` (a condition on an
app, e.g. a sheet cell becoming "approved"), or `sleep` (until a time). The run parks without cost
and resumes when the condition holds.

```json
{ "id": "wait", "type": "workspace_tools", "tools": ["wait_for_reply", "sleep"] }
```

Instruction pattern: "After sending, wait for a reply for up to 3 days with wait_for_reply; if none,
send one short follow-up; if still none, mark the row 'no reply' and finish."

## 10. Networks that use networks

A network is a tool for another: in the catalogue's `workspace_tools`, each other network appears as
`run_agent_network_<Name>`.

```json
{ "id": "delegate", "type": "workspace_tools", "tools": ["run_agent_network_Researcher"] }
```

Use it when a reusable skill (research, enrichment) should be one call inside a bigger flow. For
"once per row", use a `sub_agent_mapper` instead (recipe 3).

---

# Across the apps

Every app in a workspace is both a tool an agent can use and, through its events, a reason for a
network to run. The useful networks connect them: something arrives in one app, an agent reads
the others, and writes the result where the person will look. Five more complete recipes, then a
list of shapes worth offering.

## 11. A Telegram desk that answers from your notes

Customers write to the business's Telegram bot; the answer comes from the notes the owner keeps,
and anything that needs a person becomes a todo. Apps: Telegram (bot connected), block notes
"Handbook" (prices, hours, policies), Todo.

```json
{
  "name": "Telegram Desk",
  "default_model": "anthropic/claude-haiku-4.5",
  "nodes": [
    { "id": "msg", "type": "trigger", "event": "telegram_messages_synced", "source_app": "Telegram",
      "run_mode": "per_item",
      "prompt": "Telegram message from {{message.from.name}} in chat {{message.chatId}}:\n{{message.text}}" },
    { "id": "desk", "type": "agent", "name": "Desk",
      "instructions": "Answer the message from the Handbook notes only (search_notes, read_page). Reply in the same chat with send_telegram_message, in the customer's language, two or three sentences. If the Handbook does not answer it, or they want to book, pay or complain, reply that a person will get back to them today and add a todo with the chat id and the question." },
    { "id": "tg", "type": "app_tools", "app": "Telegram" },
    { "id": "kb", "type": "app_tools", "app": "Handbook" },
    { "id": "todo", "type": "app_tools", "app": "Todo" }
  ],
  "edges": [
    { "from": "msg", "to": "desk" },
    { "from": "desk", "to": "tg" }, { "from": "desk", "to": "kb" }, { "from": "desk", "to": "todo" }
  ]
}
```

A bot's messages are its own; with a personal Telegram account connected, sending speaks as the
owner — use `propose_telegram_reply` there and let the person approve.

## 12. Receipts into a spending sheet

Every email with an invoice or receipt: save the PDF, read it, add a row. Apps: Gmail, spreadsheet
"Spending" (Date, Vendor, Amount, Currency, Category, File).

```json
{
  "name": "Receipts",
  "default_model": "anthropic/claude-haiku-4.5",
  "nodes": [
    { "id": "mail", "type": "trigger", "event": "gmail_synced", "source_app": "Gmail", "run_mode": "per_item",
      "filter": "{{email.attachments[0].filename}} != ",
      "prompt": "Email from {{email.from}}, subject {{email.subject}}, message {{email.id}}, first attachment {{email.attachments[0].filename}}" },
    { "id": "clerk", "type": "agent", "name": "Clerk",
      "instructions": "If this is not an invoice or receipt, finish with 'not a receipt'. Otherwise save its attachments into the workspace, wait for the file to be indexed, read the total, currency, vendor and date, and add one row to Spending with the file's name in File. Pick Category from: software, travel, food, office, other." },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" },
    { "id": "sheet", "type": "app_tools", "app": "Spending" },
    { "id": "files", "type": "workspace_tools", "tools": ["wait_for_indexing", "search_documents", "get_document_page"] }
  ],
  "edges": [
    { "from": "mail", "to": "clerk" },
    { "from": "clerk", "to": "gmail" }, { "from": "clerk", "to": "sheet" }, { "from": "clerk", "to": "files" }
  ]
}
```

## 13. Meeting prep from the calendar

When a meeting is created, research the people in it and put a one-page brief in the notes.

```json
{
  "name": "Meeting Prep",
  "default_model": "anthropic/claude-sonnet-4.6",
  "nodes": [
    { "id": "evt", "type": "trigger", "event": "calendar_create_event", "source_app": "Calendar",
      "prompt": "New meeting: {{event.title}} at {{event.startTime}}, {{event.location}}\n{{event.description}}" },
    { "id": "prep", "type": "agent", "name": "Prep",
      "instructions": "Work out who the meeting is with (title, description, Contacts). Search the web and the person's mail (search_mail) for the last exchanges. Write a page in the Meetings notes titled with the meeting's date and title: who they are, what was last said, three questions to ask. Finish with the page title." },
    { "id": "web", "type": "web_search", "limit": 4 },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" },
    { "id": "contacts", "type": "app_tools", "app": "Contacts" },
    { "id": "notes", "type": "app_tools", "app": "Meetings" }
  ],
  "edges": [
    { "from": "evt", "to": "prep" },
    { "from": "prep", "to": "web" }, { "from": "prep", "to": "gmail" }, { "from": "prep", "to": "contacts" }, { "from": "prep", "to": "notes" }
  ]
}
```

## 14. A knowledge base that grows from the inbox

Newsletters and reports worth keeping become notes, linked to what is already there.

```json
{
  "name": "Reading Desk",
  "default_model": "deepseek/deepseek-v4-flash",
  "nodes": [
    { "id": "mail", "type": "trigger", "event": "gmail_synced", "source_app": "Gmail", "run_mode": "per_item",
      "filter": "CATEGORY_UPDATES in {{email.labelIds}}",
      "prompt": "Email {{email.id}} from {{email.from}}: {{email.subject}}" },
    { "id": "reader", "type": "agent", "name": "Reader",
      "instructions": "Read the email. If it holds nothing worth keeping (a promotion, a receipt, a notification), finish with 'skipped'. Otherwise add what is new to the Library notes with integrate_idea — one idea per call, the source's name and date in the text — so it lands next to related pages, and archive the email (modify_labels, remove INBOX)." },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" },
    { "id": "lib", "type": "app_tools", "app": "Library" }
  ],
  "edges": [ { "from": "mail", "to": "reader" }, { "from": "reader", "to": "gmail" }, { "from": "reader", "to": "lib" } ]
}
```

## 15. Booking requests answered

A visitor asks for a slot on the public calendar page; confirm it by email and log the lead.

```json
{
  "name": "Bookings",
  "default_model": "anthropic/claude-haiku-4.5",
  "nodes": [
    { "id": "req", "type": "trigger", "event": "calendar_request_event", "source_app": "Calendar",
      "prompt": "{{request.submitterName}} <{{request.submitterEmail}}> asks for {{request.startTime}}: {{request.message}}" },
    { "id": "host", "type": "agent", "name": "Host",
      "instructions": "Check the Calendar is still free at that time. If it is, add the event and send a short confirmation from Gmail; if not, reply with the two nearest free slots. Add or update the person in the Leads sheet (Name, Email, Asked, Status)." },
    { "id": "cal", "type": "app_tools", "app": "Calendar" },
    { "id": "gmail", "type": "app_tools", "app": "Gmail" },
    { "id": "leads", "type": "app_tools", "app": "Leads" }
  ],
  "edges": [ { "from": "req", "to": "host" }, { "from": "host", "to": "cal" }, { "from": "host", "to": "gmail" }, { "from": "host", "to": "leads" } ]
}
```

## More shapes worth offering

| When… | An agent… | Apps |
|---|---|---|
| a Telegram message asks for something | adds a todo, books a slot, or answers from the notes | Telegram, Todo, Calendar, notes |
| a mail thread goes quiet for a week | nudges once, then marks the sheet row "cold" | Gmail (`wait_for_reply`), spreadsheet |
| a contact is added | researches them and fills their company, role and a note | Contacts, web search, notes |
| a notes page is created in "Ideas" | links it to related pages and adds next steps as todos | block notes (graph tools), Todo |
| a site form or order comes in | answers the customer, updates stock, logs the order | site, Gmail, inventory, spreadsheet |
| every row of a sheet (fan-out) | writes each person a personal draft, enriches, scores | spreadsheet, Gmail drafts, web search |
| a file lands in the workspace | reads it (search_documents) and files a summary | files, notes |
| once, on request | builds a deck, a report page, a film script from the workspace | slideshow (`open_app`), notes, sheets |
| a campaign reply needs a decision | asks the person with options, then acts | Gmail campaign tools, `ask_user` |

The pattern is always the same three questions: what event starts it (or does the person start it),
which apps does each agent need to read and write, and where does the person look for the result.
