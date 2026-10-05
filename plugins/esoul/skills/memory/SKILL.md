---
name: memory
description: "ExternalSoul's lifelong memory — how to remember things for the user across sessions, projects and years. Use it WHENEVER the user refers to the past (\"remember that list of leads we made?\", \"what did I tweet about this years ago?\", \"the note I wrote two days after that spreadsheet\", \"what's my budget again?\", \"what did we do last week?\", \"who changed the sales sheet?\"), whenever they state or correct a fact that will matter later (\"actually the budget is 8,000 now\", \"remember I prefer…\"), before telling them something does not exist, and when they ask to be taken to something they made. Covers recall, remember, timeline and who_did_what on the hosted endpoint, how to read their answers honestly, time-chained questions, and what never to do (invent, guess dates, or make a separate \"Memory\" notes app)."
---

# Memory — lifelong recall in ExternalSoul

The user may be vague and may misremember. They may come back years later. Your job is to
find the thing, say plainly what esoul knows about it **today**, and never invent it. The
account already records the past for you. **Work done in apps is filed automatically** as
episodes (about 20 minutes after a session goes quiet), and every note, sheet, mail, post,
chat and file is searchable by the date it happened. You only write when the user tells you
something worth keeping.

## 1. What you are working with

| Fact | Consequence |
|---|---|
| `recall` searches three stores in one call: **episodes** (past work sessions: title, summary, who, where, artifacts), **facts** (things the user asked to keep, newest version first) and **content** (all workspace content, dated) | one call answers "remember that…". Don't pre-search with `search_workspace`, and don't list workspaces first |
| Time phrases are parsed and **widened** ("about 3 years ago", "last spring", "March 2025", "2 days after 2025-06-03") | pass the user's phrase **verbatim** as `when`. Never convert it to dates yourself; a wrong guess narrows the window and hides the answer |
| A kind word plus a time with no other subject **browses** ("notes from then", "emails that week") and lists every such item in the window, across all projects | this is how chains work (§2.3) |
| Every artifact comes back with its status **now**: `alive`, `app_deleted`, `workspace_in_trash`, `project_in_trash`, `gone`, plus `now` (where it is) and `current_name` if it was renamed | say "you made it on 2025-03-02; it was renamed to X", or "it is in Recently deleted". Never say it's there if it isn't |
| Results carry `link` (opens it exactly there in their browser), `workspace_id` / `app_id` / `entry_key` | give the link when they want to go there; read the real content with `read_app_entry` (one page or sheet) or `read_app_state` (whole app) |
| `selected_by: "similarity only…"` means no model judged relevance | **you** judge. Drop anything merely on a similar topic, and say so if nothing fits |
| `memory_coverage.dated_content` / `kind_coverage` say how far back each source reaches | if they ask about a time before that, say "esoul has no posts from before 2024-05", which is not "you never tweeted that" |
| `remember` keeps facts versioned: a correction supersedes the old line and keeps it as history | never delete or rewrite a fact. Remember the correction and recall returns the current one first |
| `recall`, `remember` and `timeline` exist only on the owner's own endpoint (`/mcp/me`); `remember` needs read+write | on a storefront or read-only grant, fall back to `search_workspace` and say remembering is unavailable |

The tools on the hosted endpoint:

- **`recall {query?, when?, since?, until?, limit?}`**: anything from the past. `query` = the
  user's own words; `when` = their time phrase, verbatim.
- **`remember {text, subject?}`**: one fact per call, in a full sentence that stands alone.
  Use `subject` to file it with an existing fact that `recall` returned.
- **`timeline {when?}`**: what happened in a period, in order (work sessions, projects and
  workspaces created, renamed or deleted, facts remembered). Defaults to the last two weeks.
- **`who_did_what {workspace?, when?}`**: people, agents, MCP clients, voice and scripts, with
  the apps each one changed. `workspace` is a name or id, owned or shared; the default window
  is this week.
- **`search_workspace {query}`**, **`read_app_entry {workspace_id, app_id, entry_key}`**,
  **`read_app_state {workspace_id, app_id}`**: to open what recall pointed at, or as a fallback
  where recall is absent.

## 2. Recipes

### 2.1 "Remember that list of 500 leads we made?"

1. `recall({query: "list of 500 leads we made"})`. Add `when` only if they gave a time.
2. Read the top episode or content hit. Check each artifact's `status` / `now` / `current_name`.
3. Answer with the date, what it was, where it is now and the `link`. If they want the data,
   `read_app_entry` or `read_app_state` with the returned ids. Don't paraphrase a sheet you
   haven't read.
4. Nothing plausible? Say so. Offer other words, a wider time, or no time. Never present a
   near-miss as the answer.

### 2.2 "What did I tweet about this, like three years ago?"

`recall({query: "tweet about <topic>", when: "about three years ago"})`. The kind word
("tweet", "post", "email", "note", "meeting") narrows the search. If `kind_coverage` says esoul
has no posts that old, tell them that. It is not evidence the tweet never existed.

### 2.3 Chains: "the note I wrote two days after making that spreadsheet about X"

1. Recall the **anchor**: `recall({query: "spreadsheet about X"})`. Take its `created` (on an
   episode artifact) or `app_created` / `date` (on a content hit).
2. Recall the target relative to that date, with the kind and nothing else:
   `recall({query: "note", when: "2 days after 2025-06-03"})`. This lists every note from then,
   across all projects and workspaces, oldest first.
3. Pick the one that fits and say how you got there ("the sheet was created on 3 June; this
   note is from 5 June").

### 2.4 Facts, preferences and corrections

- "Remember I'm vegetarian", "our budget is 6,000", "Jana owns the supplier list":
  `remember({text: "The marketing budget for Q3 is 6,000 EUR."})`.
- "Actually it's 8,000 now": recall first, to find the subject it lives under, then
  `remember({text: "The Q3 marketing budget is now 8,000 EUR (was 6,000).", subject: "<that subject>"})`.
  The old line stays as history.
- "What's my budget again?": `recall({query: "budget"})`. Answer from `current`. Mention the
  `history` only if the change matters.
- Remember unprompted when the user states something durable that later sessions will need:
  a decision and its reason, a standing preference, who someone is, where something lives. Don't
  store what the repository, the conversation or the app already records.

### 2.5 "What did we do last week?" / "Who did what in Sales this week?"

- The account as a whole: `timeline({when: "last week"})`.
- One workspace, especially a shared one:
  `who_did_what({workspace: "Sales", when: "this week"})`. If it returns `candidates` (the
  name is ambiguous), ask which one or pass the id.

### 2.6 "Where is that note? Take me there."

`recall` (or `search_workspace` for exact wording) → hand the user the result's `link`. It
opens the project, workspace, app and page in their browser. You cannot move their screen
from here.

## 3. Rules that make it trustworthy

1. **Recall before answering.** Any reference to the past, and before saying "I don't have
   that" or "that doesn't exist".
2. **The user's words in, the tool's dates out.** Pass phrases verbatim. Quote the dates recall
   returns; never guess them.
3. **Status today, stated plainly.** Deleted, in Recently deleted, renamed or purged: say which.
4. **Never invent.** A similar-topic hit is not the answer. "Nothing matched" is a correct
   answer.
5. **One memory.** Facts go to `remember`. Never create a notes app called "Memory", and don't
   append facts to random pages. That splits the user's memory in two, and recall won't treat
   those pages as facts.
6. **Absence of coverage is not absence of events.** Check `memory_coverage.dated_content` before saying
   something never happened.

## Invocation in Codex

Load this skill for the former Claude `/esoul:memory` workflow. Use the user's
topic, or the current project when no topic was given. Read relevant recalled
artifacts and report dates, current status, links and missing information.
There is no `$ARGUMENTS` substitution or Claude slash-command dependency.
