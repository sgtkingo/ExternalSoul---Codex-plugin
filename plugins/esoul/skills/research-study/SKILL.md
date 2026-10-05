---
name: research-study
description: "Run an autonomous ML research study on ExternalSoul from Codex — the person's own GitHub repo (or a local model, or labelled images) becomes the recipe, experiments run on their own GPU machine, every run is graded against a matched control, and the results land in apps they read and present from (a runs sheet, a hypotheses board, a notebook). Use when someone wants to \"find the best config/hyperparameters\", \"run ablations\", \"research/optimise my training\", \"autoresearch\", \"run experiments on my repo\", \"set up a research study\", \"train and compare models on my GPU\", or asks how their study is going. Starts with an interview: it asks what they need before it creates anything."
---

# Research study — the person's repo, their words, their apps

A study is a `research_graph` app. It is the referee: it holds the objective, the budget, every experiment and its verdict, and it refuses anything that breaks the rules the person set. The work runs on the person's own GPU machine: a research worker there runs each experiment and a Claude session there plans each round. The person reads the results in ordinary esoul apps they chose (a sheet, a kanban, notes), and watches in the esoul web app. **Everything else happens here, through these tools.**

You talk to the study through ONE tool: `study_<name>` on the research_graph app (found with `get_app_tools`). Call it as `call_app_tool` with `arguments: {op, args}`. `{op: "help"}` lists every op and its arguments. `reference/ops.md` is the short map.

## 0. Before anything: interview

Ask before you create anything. A study built on a guess spends GPU on the wrong question. Ask in small groups (two or three questions at a time), in plain words, and offer a sensible default the person can accept with "yes". Stop asking once you can fill every line of the brief (§2).

1. **The code.** "Which repository? A GitHub link (and a branch if not main), or a path on your machine." Then: "Is it private?", "Which command trains, and which evaluates — or should the study find out by reading the repo?", "Which evaluation set is held out, never trained or tuned on?"
2. **The objective.** "Which number should go up (or down)? On which evaluation?" Pin the metric's exact name, as his code prints or saves it.
3. **The constraints.** Ask for three kinds, and keep them apart:
   - design limits ("at most 8 latent steps", "batch ≤ 64"). These become parameter ranges the study cannot exceed.
   - metric floors ("CoT accuracy must not drop below 0.40"). These become guardrails: a run that breaks one never counts, whatever else it did.
   - spend ("40 GPU-hours", "$20 of planning", "by Friday").
4. **Success.** "When is it done? Which number, what value?" Get a threshold on a named metric ("≥ 0.55 GSM8K accuracy"), not "as good as possible".
5. **Data.** "Which datasets does it use? Which one is held out? Is any of it already on the machine (a path), or does the repo download it itself?" Also ask "Anything the study must know about using them?" That becomes the data note, which the planning session reads first.
6. **Papers and documents.** "Any papers, notes or specs it should read?" Each one becomes a PDF attached to the study.
7. **Ideas.** "Anything you already suspect matters, or want tried first?" Each one becomes a hint the study must weigh.
8. **Apps.** "Where do you want to read the results?" Default, which the person can take with "yes": a new sheet for every run, a kanban for the hypotheses, and a notes notebook for the synthesis. If they name an existing app, use it by that name.
9. **The machine.** "Which machine runs it — which GPU? Is it already connected to esoul (a My Computer app)?"

Then **play the brief back**: the four parts in their own words, plus the apps and the machine. Ask "Is this right?" Only after a yes, go on.

## 1. The workspace and the study

- `list_workspaces`. Use the workspace they name, or `create_workspace` ("Research — <topic>").
- `create_app` with `application_type: "research_graph"`, named after the study ("latent-reasoning"). Every later call is `study_<that name>`.
- Tell them the one place to look: the study in the esoul web app. It shows the graph live, and it is where they watch.

## 2. The machine (once per machine)

`reference/machine.md` has the whole procedure. In short:
- The machine needs a **My Computer** app in the same workspace, paired to it. If there is none, `create_app` with `application_type: "my_computer"`.
- **Pairing:** `get_app_tools` on the My Computer app. If one of its tools returns a connect command, call it and give the person the command. Otherwise ask them to open the My Computer app, press **Connect**, and paste the command it shows into a terminal on the GPU machine. This is the one moment the web app is needed for setup.
- **The research worker comes with it:** on Linux the connect command also installs the research worker into `~/research/venv` and starts it as a service. It ends with a `research worker : running` line. It needs `tmux` and a logged-in `claude` CLI; if the line says NOT installed or NOT running, `reference/machine.md` §3 has the manual commands.
- **Verify, never assume:** `study_<name>` `{op: "status"}` → `machines[].live` and `ready` must both be true. Until they are, nothing can run, and the first `set_budget` is refused with `no_computer`. Say so, and name the failing check from `machines[].readyDetail`.

## 3. Declare the subject and write the brief

- The repository: `{op: "declare_source", args: {sourceId: "repo_<slug>", kind: "repository", label: "<repo name>", repo: {url, ref?}}}`. For a model on the machine use `kind: "ollama_model"`. For labelled images, see `help` for `declare_source`.
- The brief: `{op: "set_brief", args: {prose}}`. The prose holds the four parts under their headings, **in the person's words** (§0):

  ```
  Objective: …
  Constraints: …
  Success: …
  Apps: every run in the sheet `…`; hypotheses on a kanban; synthesis in the notes `…`
  ```

  The machine's first session turns this into the structured objective, parameter ranges and guardrails, because only it can see which metrics the code actually reports.
- **Data:**
  - `{op: "set_data_note", args: {text}}` holds how to use the data, in their words.
  - Add as many datasets as he names, one `declare_source` each:
    - a link to download: `kind: "url", url`;
    - a Google Drive folder: `resolve_drive_folder {path}`, then `kind: "drive_folder", driveFolderId`;
    - a workspace folder: `list_folders`, then `kind: "workspace_folder", folderId`;
    - a path on the machine: `kind: "box_folder", boxPath`.
  - Each takes a `sourceId` you mint (`url_<slug>`, `drive_<slug>`, `box_<slug>`) and a `label`.
  - Its own note goes in `{op: "set_source_note", args: {sourceId, note}}`.
  - Data the repo downloads itself needs only a line in the data note.
- **Papers:** `upload_file` each PDF, then `{op: "attach_paper", args: {fileId, note}}`.
- **Ideas** from §0.7: one `{op: "add_hint", args: {hintId: "h-<slug>", text}}` each. A hint from the person is accepted at once.

## 4. Start, then the one approval

- **Ask first, with his numbers:** "Start the study with 3 rounds, 20 runs, 4 GPU-hours and $30 of planning (the caps you gave)? The first session reads the repo, writes the recipe, smoke-tests it and proposes the objective. Nothing trains until you confirm it."
  - On yes: `{op: "set_budget", args: {maxRounds, maxRuns, maxGpuHours, maxTokenUsd}}` with exactly those caps.
  - If he wants to see a plan before committing any budget, start the preview instead: `{op: "set_budget", args: {maxRounds: 0, maxRuns: 0, maxGpuHours: 0, maxTokenUsd: 8}}`.
- **Wait for the proposal.** Read `{op: "status"}`. Its `next` says what the study is waiting for. Don't poll in a tight loop: check every few minutes, and tell the person to watch the study in the web app meanwhile. The proposal is ready when `next` says "Approve the plan".
- **Present it plainly** and ask for a yes. Read:
  - `{op: "overview"}` for the proposed objective, guardrails and success, and the `grant` ask with its numbers;
  - `{op: "list_findings", args: {kind: "dataset_characterisation"}}` for what the session found in the repo: the command, the knobs with their ranges, the smoke run's numbers, and the estimated hours per run;
  - `{op: "read_recipes"}` for the recipe's parameters.

  Say it in the person's terms. For example: "It will run `train.py` at commit 3f2a9c1, turning latent_steps 1–8 and lr; each run is about 2 GPU-hours; round 0 is 3 seeds of your default config to measure the noise; it asks for 3 rounds, 12 runs, 40 GPU-hours, $20 of planning."
- **On a yes:** `{op: "approve_plan", args: {grant: {maxRounds, maxRuns, maxGpuHours, maxTokenUsd}}}` with exactly the numbers they agreed to. **On changes**, before approval: `set_brief` again with corrected prose, then `{op: "request_tick"}` to re-plan.

## 5. While it runs

- "How is it going?" → `{op: "status"}`. Relay `success`, `best`, `verdicts`, `budget` and `needsYou`. Point at the apps for the detail.
- The study asks something (`needsYou.asks`) → put the question to the person, then answer it with `{op: "add_hint", args: {hintId, text, answersAsk: <the ask's key from overview.asks[].key>, answer}}`.
- A new idea → `add_hint`. Stop a direction → `{op: "withdraw_experiments", args: {experimentIds | round, reason}}`. A paper → `upload_file` the PDF, then `{op: "attach_paper", args: {fileId, note}}`.
- Deeper reads: `read_synthesis`, `read_knob` (every value tried and what it did), `graph`, `read_experiment`, `search_study`.
- Change where results go → `{op: "bind_app", args: {role: "runs" | "hypotheses" | "notebook" | "<their word>", app?, type?, how: "<their sentence>"}}`.

## 6. Presenting

- The bound apps are already the presentation: the runs sheet (one column per knob and per metric, plus a verdict), the hypotheses board, and the notebook's synthesis and round pages. They stay current on their own, and the person's own columns and pages beside them are never touched.
- A written report: `{op: "write_report"}`, then send them the page. `read_report` gives you the text.

## Rules that hold whatever the person asks

- **Only the person approves spending.** `approve_plan`, `set_budget`, `confirm_brief`, `decide_hint`, `decide_paper`, `request_tick` and `set_models` act on their behalf. Call them only after they said yes, in this conversation, to exactly what you will send. The study refuses these ops from anyone but the account owner's authenticated MCP client.
- **Success is what `status.success` says, nothing else.** A run counts only when it met the threshold **and** beat its matched control. Never report "it worked" from one good number.
- **Never invent a result.** Every number you give has a run id beside it (`best.id`, a verdict, a claim's evidence).
- **Their code is theirs.** The study never edits it to make a run pass. A change it needs goes on its own branch, and it tells them.

## When something is refused

Every refusal from `study_<name>` carries a `guidance` block:
- `stage`: where the study is;
- `why`: why this op doesn't fit now;
- `next`: the one act that moves it forward;
- `canDoNow`: the ops that fit this stage;
- `didYouMean`, for a misspelled op.

Follow it rather than retrying. The table covers the refusals that need something from the person or the machine.

| Answer | Meaning | Do |
|---|---|---|
| `human_only` | A decision op arrived from something other than the owner's authenticated MCP client | Ask the person. If they are the owner and still see this, the platform predates the MCP approval path — they approve in the web app |
| `status.next` "Connect a machine" / machine not live | No research worker reports to this study | §2; `esoul-research doctor` on the machine |
| `skill_unavailable` / `skills_unpublished` | The platform's repository procedure is not published | Tell the owner of the platform; nothing to do from here |
| `daemon_too_old` | The worker on the machine is older than the study needs | `pip install -U 'esoul[research]'` and restart the service |
| a finding says the smoke failed | The recipe could not run or read the score | Read the finding's error, fix the repo or explain in a hint, then `request_tick` |
| clone refused | A private repo, no access on the machine | `gh auth login` or a deploy key on the machine, then `request_tick` |

## Codex client compatibility

Codex controls the study through hosted MCP tools. ExternalSoul's research worker
still uses a logged-in `claude` CLI on the paired machine for planning. Those
backend commands and model IDs are API dependencies; do not replace them with
invented Codex commands. Inspect current app tools before claiming an approval
operation is supported for this client.
