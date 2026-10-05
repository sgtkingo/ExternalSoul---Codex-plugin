# Sandbox mechanics — how the code sandbox actually behaves

> Read this when running anything in the `e2b_sandbox` app that takes longer than a minute,
> installing packages, moving files across the workspace boundary, or diagnosing "my render died
> halfway". `SKILL.md` says what to build; this is how the machine behaves underneath it.
> Everything here is driven as `call_app_tool(workspace_id, sandbox_app_id, tool_name, args)`.

## THE MACHINE (get the mental model right first)

- **One Jupyter kernel**, shared by every `run_code` call. Variables, imports, `os.environ` and
  `sys.path` persist from call to call — you are continuing one session, not running isolated
  scripts.
- **Tabs are CELLS, not files.** Tab code lives in app state; editing a tab writes NOTHING to the
  sandbox disk. The filesystem only changes when code runs.
- **The sandbox is a THROWAWAY VM.** `/home/user`, pip installs and kernel state all vanish
  whenever it is replaced (see LIFECYCLE) — the workspace is the only durable store. Anything you
  care about: save it the MOMENT it exists, never deferred to the end. That does NOT mean one call
  per file — `save_files_to_workspace([{filePath}, …])` saves each poll's newly-finished files in
  ONE call (and returns each `durationSeconds`), which keeps the "save as you go" durability without
  the per-file round-trip tax.
- `os.environ` carries `ESOUL_TOKEN` + `ESOUL_BASE_URL` — a short-lived scoped API session,
  refreshed on each run entry, so code inside the sandbox can call the ExternalSoul API directly.

## GETTING SET UP

- `get_app_tools` on the sandbox app to learn its exact per-app tool names (suffixed `_<base>`).
  Never guess them.
- **Check the environment before assuming it**: run one cell importing what you need. Assume
  little beyond `requests`, `numpy`, `matplotlib` — manim is NOT preinstalled (~26s to add).
- **You have root.** Debian 12, passwordless `sudo`, working apt (verified 2026-08-10). System
  packages are installable, LaTeX included:
  `sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-extra dvisvgm`
  → ~56s, 255MB, and `MathTex` renders. "There is no LaTeX" describes the cold image, not a limit.
  Note the kernel runs `/usr/local/bin/python3.13`, which is NOT the same interpreter as a bare
  `pip` in a shell command — install with `sys.executable -m pip` or `!pip` inside a cell, or you
  will install into one Python and import from another.
- Install with `!pip install X` inside a `run_code` cell. Each cell has ~60 SECONDS total, so
  install ONE heavy package per cell (manim, torch and friends each get their own). Installs
  persist across calls but die with the sandbox.

## THE 60-SECOND RULE (why cells die)

Every `run_code` call has roughly one minute end to end. A cell that blocks longer does not merely
error: on timeout the platform may EVICT the sandbox, create a FRESH one and RE-RUN your cell
there. So **a heavy cell can execute TWICE**, and everything on the old box (files, installs,
variables) is gone. Two consequences:

- Keep every interactive cell well under a minute. Chunk work; precompute; print progress.
- Anything longer runs **DETACHED** — a background process the cell only LAUNCHES:

```python
subprocess.Popen(['bash','-lc','setsid nohup /home/user/r.sh > /home/user/r.log 2>&1 < /dev/null &'],
                 start_new_session=True)
```

In `r.sh`: `set -euo pipefail` (else a failed job still writes its success marker — a green light
over a red run); append each finished output's name to a PROGRESS file; SKIP anything already on
disk so a relaunch RESUMES instead of redoing; write final artifacts directly under `/home/user`.

Then poll with `list_files` — it reads the disk and needs no kernel, so it works while the job
runs. Between polls you can run other short cells; the kernel is free.

## LIFECYCLE — the sandbox will restart on you; plan for it

- Lifetime is ~30 minutes, ABSOLUTE, from the last `run_code` entry. Polling `list_files` extends
  NOTHING; only real `run_code` calls reset the clock.
- A sandbox saturated by heavy work answers the platform slowly and can get silently replaced by
  an EMPTY one — this is the mechanism behind "/home/user wiped every 15–30 minutes".
- After any restart sign (imports gone, files gone, unfamiliar sandbox id): reinstall, let
  auto-sync re-copy inputs, re-run only what is MISSING from the workspace — which is why you
  saved as you went.
- There is no kill or restart tool. `start_sandbox` refuses while a sandbox is alive; a fresh box
  comes from letting the old one expire.
- **A recycle loses the TOOLCHAIN, not just files** — manim and LaTeX vanish too, and the failure
  surfaces as `FAIL <scene>` with a log reading `No module named manim`, which looks EXACTLY like
  a code bug. Defend against the misdiagnosis:
  - Save `setup.sh` (the pip + apt install script) to the WORKSPACE, not just `/home/user`, so a
    recycle can't take it.
  - **Assert the toolchain before every render batch**: one cell that does `import manim, av` and
    `shutil.which("latex")` and PRINTS the result. A green line here means a later `FAIL` is a
    real code bug; its absence means reinstall, not debug.
  - Re-save the SOURCE tarball after every edit round, not once. Saving the scene files pre-fixes
    and then hitting a recycle means re-applying every patch by hand.

## FILES IN — workspace → sandbox

- **AUTO-SYNC**: before each `run_code` (and on `list_files`), every workspace file not yet copied
  to THIS sandbox is downloaded to `/home/user/<name>` — flat, exact name, no subfolders. Your
  code can open `/home/user/<name>` for any workspace file without asking.
- `copy_file_to_sandbox({fileId|fileName, destPath?})` is the explicit arm: the only way to
  control the destination path, and the only file tool that WAKES a dead sandbox (then re-seeds
  everything, which it reports).
- Deleting a synced file in the sandbox is futile — the next run re-downloads it. And two
  workspace files with the SAME NAME race into one path (one silently shadows the other): keep
  workspace filenames unique.

## FILES OUT — sandbox → workspace

- `save_to_workspace({filePath, saveAs?, overwrite?})` — `filePath` must be under `/home/user`;
  per-file cap ~25MB; a name collision auto-renames (or set `overwrite:true` to replace the
  same-named file, retry-safe). The result ends with `[fileId: ...]` — THAT id is what attachment,
  messaging and file tools take — plus `[durationSeconds: N]` for media. Saving is the only
  durability there is.
- `save_files_to_workspace({files:[{filePath, saveAs?}, …], overwrite?})` — the BATCH form: one
  call, results in caller order, each with its `[fileId]` + `[durationSeconds]`. Prefer it whenever
  more than one file is ready.
- `list_workspace_files()` / `delete_workspace_files({fileIds})` — the ids you have, and cleanup of
  stale saves (workspace-scoped; removes them from the file panel live). Between `overwrite:true`
  and delete, filenames stay load-bearing across re-renders.
- **THE RE-DOWNLOAD TRAP**: a file you saved becomes a workspace file, and the NEXT run's
  auto-sync downloads it BACK over `/home/user/<name>` — clobbering that path before your code
  runs. Never keep writing to a path you already saved from: name outputs per iteration
  (`out_v2.mp4`) or move the local copy aside after saving.

## SEEING YOUR OWN OUTPUT (vision over MCP since 2026-08-10)

**An image written under `/home/user` during a run comes back to you as an actual image** — the
storefront returns it as a typed MCP image block, so you SEE it. Plot something,
`plt.savefig('/home/user/check.png')`, and LOOK: this is the verification loop.

The mechanics that shape it:

- **At most 3 images per tool result, downscaled to ≤1280px.** Many frames → ONE contact-sheet
  PNG, never nine separate files (`SKILL.md` step 5 has the snippet).
- The capture is **NOT recursive**: a file written in a subdirectory (`media/videos/...`) is
  invisible. `shutil.copy` artifacts up to `/home/user`.
- **VIDEOS never come back directly** on any surface. Sample frames into a sheet.
- An image that failed to render/attach shows as `imagesDropped` in the result — say so and fall
  back to the printed-assertion battery; never claim a look you did not get.
- Already-saved workspace images can be re-viewed WITHOUT running code: the storefront's
  `view_image(workspace_id, file)` (find them via `list_files(images_only: true)`).
- Whatever you want the USER to keep must reach the workspace: `save_to_workspace` it and say its
  name.

Eyes AND numbers: the look catches what no assertion anticipates; `verify_frames.py` measures
what a glance cannot (exact frame-fill %, a silent narration beat). Use both on anything that
ships.

## READING RESULTS HONESTLY

- A cell's returned text is stdout plus the final expression. `print()` what you need to see; a
  bare variable on the last line also comes back.
- stderr arriving as literal `[object Object]` is a REAL error with a mangled traceback: re-run
  the code wrapped in try/except with `import traceback; traceback.print_exc()` — the traceback
  then arrives via stdout.
- The app state's "Running: yes" can be a stale flag after a transport failure. Believe the DISK
  (`list_files`, your PROGRESS file), not the flag.

## TOOLS AT A GLANCE (names suffixed `_<base>`)

- `create_tab` / `set_code` / `read_tab_code` / `apply_patch_to_tab({edits:[{find,replace}]})` —
  manage cells; patching beats resending whole code.
- `run_code({tabId?})` — execute the tab's code in the shared kernel.
- `list_files({path?})` — the REAL disk listing (and it triggers auto-sync). `list_sandbox_files`
  is NOT the disk: it is the copy ledger — what has been copied in, with fileIds.
- `copy_file_to_sandbox` / `save_to_workspace` / `save_output_to_workspace` — files across the
  boundary; `save_output_to_workspace` saves a produced image by index when you never wrote it to
  disk.
- `start_sandbox` — only when dead; refuses while alive.
- `mount_drive` / `download_drive_file` — Google Drive under `/home/user/drive`.

## THINGS THAT GO WRONG, AND WHAT THEY MEAN

- **A cell died near the minute mark with no error worth reading** — client timeout. Detach the
  work; check whether it ran twice.
- **Everything vanished (imports, files, id changed)** — the sandbox restarted. Reinstall +
  re-copy; what you saved to the workspace survived.
- **An artifact reverted to an older version at run start** — auto-sync re-downloaded a same-name
  workspace file over it. Rename per iteration.
- **A file you wrote never came back as an image** — it is in a subdirectory. Copy it to
  `/home/user`.
- **`[object Object]` in stderr** — wrap in try/except + `traceback.print_exc()` and re-run.
- **pip install times out** — one heavy package per cell, or install detached.
- **`start_sandbox` refuses** — one is alive; just use it, `run_code` wakes it.
- **The same file seems to shadow another** — duplicate workspace filenames. Rename one.
