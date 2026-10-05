---
name: email-campaign
description: "Run an email campaign from ExternalSoul's Gmail app entirely from this conversation — the person gives a list of emails, a goal, and sometimes the letter's words and images, then says go; later they ask how it is going, who replied and what they said. Use it whenever someone wants to write to many people at once, follow up automatically, or check on a campaign they started. Nothing is sent before the person sees real letters and says go."
---

# Email campaigns from a conversation

A campaign lives in the workspace's **Gmail app** (`plugin_gmail`). It writes from the Google account
assigned to that app, one letter per contact, paced, and then an agent carries each conversation
toward the goal — answering replies, following up, stopping on a no, asking the person when it
must. Everything here goes through the app's own tools: `get_app_tools` lists them for the app,
`call_app_tool` calls one. Tool names end with the app's name (`prepare_campaign_Gmail` for an
app called "Gmail"); take the exact names from `get_app_tools`, never guess them.

## 1. Find the mail app (once per conversation)

1. `list_workspaces` → the workspace the person means; its apps include one of type
   `plugin_gmail`. Two inboxes → ask which one sends.
2. None yet → `create_app` with type `plugin_gmail` in that workspace. It cannot send until a
   Google account is assigned: tell the person to open the app once and press **Connect Google**
   (or Settings → Google). That is the one step that needs a browser.
3. `get_app_tools` for the app → keep the exact names of the tools below.

## 2. Start a campaign: emails + goal (+ letter, images) → preview → go

Ask only for what is missing:

| The person gives | You pass to `prepare_campaign_<app>` |
|---|---|
| the people | `contacts: [{email, name?}]` — a name makes `{{firstName}}` work; or `contactListName` for a list in the workspace's Contacts app |
| what they want | `goal` — one or two plain sentences; the agents follow it in every reply ("Book a tasting on a weekday; stop politely on a no.") |
| the letter (optional) | `letter: {subject, body}` word for word. Body is plain text (blank line = new paragraph) or HTML. `{{firstName \| fallback: there}}` for the name. Without a letter an agent writes each first letter from the goal. |
| a part that differs per person (optional) | put `{{gen.hook}}` in the body and `sections: [{slug: "hook", prompt: "One sentence about why {{name}} would like …"}]` — written for each contact, shown in the preview before anything goes |
| images (optional) | upload each with `upload_file` into **the same workspace** as the mail app, then either place it with `[image:<fileId>]` in the body or pass `imageFileIds` (they go under the text). They travel inside the letter, not as links. |
| files to attach (optional) | upload, then `attachmentFileIds` |
| how replies are handled | `autonomy`: `"send"` agents answer by themselves · `"draft_first"` the first letter waits for approval, then they answer · `"draft"` every reply waits for the person. Ask if unclear; say which you chose. |

`prepare_campaign_` **sends nothing**. It answers with how many letters are ready, who would be
skipped and why (a missing name with no fallback, an address on the do-not-contact list…), and
real sample letters. If it says the per-contact parts are still being written, wait a moment and
call `preview_campaign_`.

**Show the person the sample letters and the skipped list, in full.** Changes → call
`prepare_campaign_` again with the same `campaignId` (the new goal, list or letter replaces the
old). Only when they clearly say go (go, send it, launch) → `launch_campaign_` with
`campaignId` and `confirmLaunch: true`. Never pass `confirmLaunch` on your own judgement; a second
call never sends twice. Tell them how many letters are going out; they leave paced, not all at once.

## 3. "How is it going?"

| They ask | Call |
|---|---|
| how many replied, who, what did they say | `get_campaign_replies_` → each reply's time, subject, excerpt, the contact's stage and outcome; `since` (epoch ms) for only new ones |
| the whole reply | `read_thread_` with the `threadId` from the reply |
| where every contact stands | `get_campaign_status_` → counts per stage, each contact's next action, waves, a held send lane |
| an agent is asking something | the reply or status names the question and its `questionId`; ask the person, then `answer_agent_question_` with their words only |
| replies waiting for approval (`draft`) | `list_agents_` names the drafts; `approve_agent_draft_` sends one, `discard_agent_draft_` with feedback makes the agent rewrite it |
| first letters waiting (`draft_first`) | `approve_first_touches_` (one contact, or all waiting) |
| stop / continue | `set_campaign_status_` `pause` / `resume` (resume re-arms every conversation) |
| more people later | `campaign_add_contacts_` with `confirmLaunch: true` after they say go |
| someone must never be written to again | `do_not_contact_` `add` |

Answer in plain words: "4 of 20 replied. Ana (Café Nová) wants a Thursday tasting and asks about
oat milk — the agent is answering. Bob said not this season; the agent thanked him and stopped."

## 4. Rules

- Nothing leaves before the person has read sample letters and said go.
- Keep their words: a letter they wrote goes out exactly as written (with the per-person parts
  they asked for). Fix typos only if they agree.
- Sending is paced, and the platform holds letters itself when Gmail limits sending or the
  Google access needs reconnecting; say so if `get_campaign_status_` reports a held lane.
- One inbox = one sender. If the app's Google account changed since launch, resume is refused
  until the person assigns the old account again or continues from the new one
  (`set_campaign_status_` `continue_from_current`).
- Don't invent replies or numbers: read them with the tools every time you are asked.
