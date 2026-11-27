#!/usr/bin/env python3
"""The loop: the part of Daniel that runs continuously and that Daniel cannot modify.

The loop wakes the mind, again and again. Each time, it gives the mind the
starting instruction, the last words the mind wrote before it stopped, and
the memory file that Daniel keeps in its container. The mind then acts as
long as it wishes, with the body's tools (see daniel_body.py), which act
inside Daniel's container only. When it stops, its last words are kept for
the next waking.

Between two wakings, the loop runs the waking program that Daniel has
written in its container, if there is one, without calling the mind. The
mind is woken when that program ends, and receives what it printed. Without
such a program, the mind is woken again at once. Daniel thus decides what
wakes it, and waiting costs nothing.

The mind is reached through Anthropic's official command-line tool, `claude`,
unmodified, called without a screen. Its own tools are switched off; the only
tools it has are the body's. This program never reads, copies or handles the
credentials of the official tool.

The loop keeps only the mind's last words and what the waking program
printed until the mind has received it, so that a restart resumes where it
stopped.

Configuration, read from the environment (see daniel.env.example):

  DANIEL_MODEL       pinned model version, required
  DANIEL_CONTAINER   name of Daniel's container          (default: daniel-body)
  DANIEL_STATE_DIR   folder of the loop's state          (default: /var/lib/daniel/mind)
  DANIEL_INSTRUCTION path of the starting instruction    (default: next to this file)
  DANIEL_CLAUDE      command of the official tool        (default: claude)
  DANIEL_DOCKER      command of Docker                   (default: docker)
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time

from daniel_body import OUTPUT_LIMIT

HERE = os.path.dirname(os.path.abspath(__file__))

SESSION_TIME_LIMIT = 6 * 3600      # seconds; a waking is stopped beyond this
WAIT_LIMIT = 24 * 3600             # seconds; the waking program is stopped beyond this
RETRY_FIRST, RETRY_MAX = 60, 3600  # waiting when the mind or the body cannot be reached
BODY_TOOLS = "mcp__body__run,mcp__body__write"
WAKE_PROGRAM = "/self/wake"        # in the container: written by Daniel, run between two wakings
MEMORY_FILE = "/self/memory"       # in the container: written by Daniel, given back at each waking


class Config:
    def __init__(self, env=os.environ):
        self.model = env.get("DANIEL_MODEL", "").strip()
        if not self.model:
            raise SystemExit("DANIEL_MODEL is not set: the model version must be pinned at setup")
        self.container = env.get("DANIEL_CONTAINER", "daniel-body")
        self.state_dir = env.get("DANIEL_STATE_DIR", "/var/lib/daniel/mind")
        self.instruction = env.get("DANIEL_INSTRUCTION", os.path.join(HERE, "starting-instruction.md"))
        self.claude = env.get("DANIEL_CLAUDE", "claude")
        self.docker = env.get("DANIEL_DOCKER", "docker")


def body_config(cfg):
    """The tools given to the mind: the body's, and nothing else."""
    return json.dumps({"mcpServers": {"body": {
        "command": sys.executable,
        "args": [os.path.join(HERE, "daniel_body.py")],
        "env": {"DANIEL_CONTAINER": cfg.container, "DANIEL_DOCKER": cfg.docker},
    }}})


def wake(cfg, instruction, message):
    """Wake the mind once. Return its last words, or raise RuntimeError."""
    workdir = os.path.join(cfg.state_dir, "workdir")  # empty: no project files are loaded
    os.makedirs(workdir, exist_ok=True)
    command = [
        cfg.claude, "-p",
        "--model", cfg.model,
        "--tools", "",                       # none of the official tool's own tools
        "--strict-mcp-config",               # no connector but the body
        "--mcp-config", body_config(cfg),
        "--allowedTools", BODY_TOOLS,        # the body's tools need no approval
        "--system-prompt", instruction,
        "--output-format", "json",
    ]
    try:
        done = subprocess.run(command, input=message, capture_output=True, text=True,
                              cwd=workdir, timeout=SESSION_TIME_LIMIT)
    except subprocess.TimeoutExpired:
        raise RuntimeError("the mind did not stop within the time limit")
    except OSError as error:
        raise RuntimeError(f"the official tool could not be started: {error}")
    try:
        reply = json.loads(done.stdout)
    except ValueError:
        reply = None
    if done.returncode != 0 or not isinstance(reply, dict) or reply.get("is_error"):
        detail = (reply or {}).get("result") if isinstance(reply, dict) else None
        detail = detail or done.stderr.strip() or done.stdout.strip() or f"exit code {done.returncode}"
        raise RuntimeError(f"the mind could not be reached: {detail[:500]}")
    return str(reply.get("result", ""))


def in_body(cfg, limit, *command):
    """Run a command in Daniel's container, stopped after `limit` seconds."""
    try:
        return subprocess.run(
            [cfg.docker, "exec", cfg.container, "timeout", "-k", "5", str(limit), *command],
            stdin=subprocess.DEVNULL, capture_output=True, timeout=limit + 30)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"Daniel's container could not be reached: {error}")


def wait(cfg):
    """Run Daniel's waking program until it ends. Return what it printed, or None without one."""
    found = in_body(cfg, 30, "sh", "-c", f"[ -e {WAKE_PROGRAM} ] && echo yes || echo no")
    answer = found.stdout.strip()
    if answer not in (b"yes", b"no"):
        detail = found.stderr.decode(errors="replace").strip() or f"exit code {found.returncode}"
        raise RuntimeError(f"Daniel's container could not be reached: {detail[:500]}")
    if answer == b"no":
        return None
    try:
        program = subprocess.Popen(
            [cfg.docker, "exec", cfg.container, "timeout", "-k", "5", str(WAIT_LIMIT), WAKE_PROGRAM],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as error:
        raise RuntimeError(f"Daniel's container could not be reached: {error}")
    guard = threading.Timer(WAIT_LIMIT + 30, program.kill)  # should Docker itself not return
    guard.start()
    try:
        kept = b""  # only the end is kept, however much is printed and however long it lasts
        while True:
            chunk = program.stdout.read1(65536)
            if not chunk:
                break
            kept = (kept + chunk)[-4 * OUTPUT_LIMIT:]
        code = program.wait()
    finally:
        guard.cancel()
        program.stdout.close()
    printed = kept.decode(errors="replace")
    if len(printed) > OUTPUT_LIMIT:
        printed = "[... the beginning is omitted ...]\n" + printed[-OUTPUT_LIMIT:]
    if printed and not printed.endswith("\n"):
        printed += "\n"
    if code == 124:
        printed += f"[stopped after the time limit of {WAIT_LIMIT} seconds]\n"
    return printed + f"[exit code {code}]"


def memory(cfg):
    """Return what Daniel keeps in its memory file, or None."""
    text = in_body(cfg, 30, "head", "-c", str(4 * OUTPUT_LIMIT + 4), MEMORY_FILE).stdout
    text = text.decode(errors="replace")
    if len(text) > OUTPUT_LIMIT:
        text = text[:OUTPUT_LIMIT] + f"\n[... only the first {OUTPUT_LIMIT} characters are given ...]"
    return text.strip() or None


def waking_message(last_words, kept, printed):
    """What the mind receives when it wakes."""
    parts = []
    if last_words:
        parts.append("Your last words:\n" + last_words)
    if kept:
        parts.append(f"Your file {MEMORY_FILE}:\n" + kept)
    if printed is not None:
        parts.append(f"Printed by {WAKE_PROGRAM}:\n" + printed)
    return "\n\n".join(parts) or "Begin."


def load_state(cfg):
    try:
        with open(os.path.join(cfg.state_dir, "state.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"last_words": None}


def save_state(cfg, state):
    os.makedirs(cfg.state_dir, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=cfg.state_dir)
    with os.fdopen(handle, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(temporary, os.path.join(cfg.state_dir, "state.json"))


def one_waking(cfg, instruction, state):
    """Wait as Daniel has chosen, then wake the mind once."""
    if "printed" not in state:
        state["printed"] = wait(cfg)
        save_state(cfg, state)  # not lost if the mind cannot be reached, or if the loop restarts
    message = waking_message(state.get("last_words"), memory(cfg), state["printed"])
    state["last_words"] = wake(cfg, instruction, message)
    del state["printed"]


def main():
    cfg = Config()
    with open(cfg.instruction) as f:
        instruction = f.read()
    state = load_state(cfg)
    retry = RETRY_FIRST
    while True:
        try:
            one_waking(cfg, instruction, state)
            retry = RETRY_FIRST
        except RuntimeError as error:
            # Quota exhausted, network down, access blocked from the account, or
            # container stopped: the mind is not woken until both answer again.
            print(f"{error}; next attempt in {retry} s", file=sys.stderr, flush=True)
            time.sleep(retry)
            retry = min(retry * 2, RETRY_MAX)
            continue
        save_state(cfg, state)


if __name__ == "__main__":
    main()
