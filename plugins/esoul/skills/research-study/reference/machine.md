# The research machine — from zero, once per machine

The study's work runs on the person's own GPU machine. Two pieces run there:
- the **My Computer agent**, which pairs the machine to their esoul account and to one My Computer app;
- the **research worker** (`esoul-research`), which claims the study's work, launches each run and each planning session, and reports back.

## 1. Before you start: what the machine needs

Ask the person to confirm each of these. Don't assume.

| Need | Check with | If missing |
|---|---|---|
| Linux with an NVIDIA GPU and a working driver | `nvidia-smi` | a CPU-only machine works for small models: add `--cpu` to `esoul-research install` |
| Python 3.10+ and pip | `python3 --version` | install Python |
| `tmux` | `tmux -V` | `sudo apt install tmux` (the worker never uses sudo itself) |
| The `claude` CLI, logged in | `claude --version` | install Claude Code and run `claude` once to sign in; planning sessions run through it |
| `git`, and read access to the repo | `git clone <url>` in a scratch dir | a private repo: `gh auth login` or a deploy key |

## 2. Pair the machine

1. There must be a My Computer app in the study's workspace (`create_app` with `application_type: "my_computer"`, named after the machine, e.g. "gpu-box").
2. Get the connect command:
   - `get_app_tools` on that app. If one of its tools returns a connect or pairing command, call it and give the person the command exactly as returned.
   - Otherwise ask them to open the My Computer app in esoul and press **Connect**. It shows one `curl … | bash -s -- install --code …` line. The code works once, for 15 minutes.
3. They paste it into a terminal on the GPU machine. It ends by saying the machine is paired and assigned to that app.

## 3. The research worker — installed by the connect command

On Linux the connect command installs the research worker too, right after the agent: it creates `~/research/venv`, runs `pip install -U 'esoul[research]'`, `esoul-research install` (trainer venv, recipe library, a 2-step self-test) and `esoul-research install-service`, and starts it. Its summary ends with one of:

- `research worker : running (esoul X)` — done.
- `research worker : NOT installed — …` or `installed, NOT running — …` — the line names the cause (Python older than 3.10, no `python3-venv`, a failed pip). Fix that one thing and paste the connect command again; a second paste restarts nothing that is running.

Pasting the connect command again later also upgrades the worker. An upgrade skips the GPU self-test and restarts only the worker; runs in progress carry on. `--no-research` at the end of the command (or `ESOUL_COMPUTER_RESEARCH=0`) leaves the worker out.

By hand, on a machine where the connect command could not do it:

```bash
pip install -U 'esoul[research]'
esoul-research install          # ends with READY or names what is wrong
esoul-research install-service  # a systemd user service that survives a reboot
esoul-research doctor           # read-only: prints every check again
```

## 4. Verify from here

`study_<name>` with `{op: "status"}`. Look for:
- `machines[]`: the machine's label, its GPUs, `live: true`, and `ready: true`;
- `next`: no longer "Connect a machine".

It can take a minute after `install-service` for the first report to arrive. If `live` stays false after 10 minutes, ask for the output of `esoul-research doctor` and `systemctl --user status esoul-research`.

## 5. What the person never needs to do

- Paste an access token anywhere. Pairing mints the machine's own credential, and the worker gets a study-scoped one only after the person approves a budget.
- Open a port. The machine calls out, and nothing calls in.
