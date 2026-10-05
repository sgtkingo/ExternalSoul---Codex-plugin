# The study's ops — the map

Call every op through `study_<name>` as `{op, args}`. `{op: "help"}` returns each op's exact arguments, so read it before any op you haven't used. The ops fall into four groups.

## Decisions — the person's, and only after they said yes

| op | what it does |
|---|---|
| `approve_plan` | THE approval: grants the budget, then freezes the objective, in one step. `{grant: {maxRounds, maxRuns, maxGpuHours, maxTokenUsd}}` |
| `set_budget` | Grant or extend a budget without approving a plan. The preview is `{maxRounds: 0, maxRuns: 0, maxGpuHours: 0, maxTokenUsd: 8}`. The FIRST grant starts the study and is refused (`no_computer`) until a computer reports live and ready |
| `confirm_brief` | Freeze the objective alone (normally `approve_plan` does it) |
| `decide_hint` | Accept or reject a hint the study appraised: `{hintId, decision: "accepted"｜"rejected"}` |
| `decide_paper` | Adopt or decline a digested paper's proposal |
| `request_tick` | Start a planning session now, instead of waiting for the clock |
| `set_models` | Choose which Claude model plans and which runs |

## The person's words and material

| op | what it does |
|---|---|
| `set_brief` | The brief's prose, until approval. After approval the brief is frozen, so use `add_hint` |
| `declare_source` | The subject (`repository` with `repo: {url, ref?}`, or `ollama_model`) and every dataset: `url` (a link to download), `drive_folder`, `workspace_folder`, `box_folder` (a path on the machine). One call per dataset, as many as needed |
| `add_hint` | An idea, a correction, or an answer to the study's question (`answersAsk`). A hint from the person is accepted at once |
| `withdraw_experiments` | Stop runs: `{experimentIds}` or `{round}`, plus a `reason` |
| `bind_app` | Which app holds runs / hypotheses / the notebook, or any role in the person's own words: `{role, app?, type?, how}` |
| `attach_paper` | Add a PDF (`upload_file` it first) for the study to digest |
| `write_report` | Write the report page into the workspace |
| `set_data_note` · `set_source_note` · `set_source_path` · `remove_source` · `resolve_drive_folder` · `import_drive_labels` · `list_folders` | Data housekeeping, for image studies mostly |

## Reading

| op | what it answers |
|---|---|
| `status` | **Start here.** Phase, success line, best result, budget used, what needs the person, apps, machines, and `next`: the one act to take now |
| `overview` | Everything the planning session sees. Large |
| `read_synthesis` | What the study currently believes, with its claims ledger |
| `graph` · `read_experiment` · `read_cards` | The runs: structure, one run in full, run cards |
| `read_knob` | Every value of every parameter tried, and what it did |
| `read_hypotheses` · `read_hints` · `read_ticks` · `read_chapters` | Ledgers in full |
| `list_findings` | What the sessions noticed; `kind: "dataset_characterisation"` is Phase 0's reading of the repo |
| `read_recipes` | The recipe's parameters (ranges = the person's constraints) and metrics |
| `read_report` · `list_papers` · `read_paper` · `read_data` · `search_study` · `help` | as named |

## The study's own work — leave it to the sessions on the machine

The planning sessions on the machine do these, under the study's rules. Do **not** call them yourself unless the person explicitly asks to steer by hand. A plan made here skips the reading, measuring and pairing the sessions do.

`declare_hypothesis` · `declare_experiment` · `enqueue_experiment` · `register_recipes` · `seal_suite` · `post_finding` · `appraise_hint` · `record_tick` · `write_synthesis` · `write_chapter` · `request_recipe` · `resolve_recipe_request` · `retire_recipe` · `digest_paper` · `probe_source` · `ack_data`
