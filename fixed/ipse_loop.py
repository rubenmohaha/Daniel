#!/usr/bin/env python3
"""The loop: the part of Ipse that runs continuously and that Ipse cannot modify.

At each turn the loop:

1. gives the mind the starting instruction, its previous thought, the result
   of its last action, the time read from the Linux clock and the signals
   available to the instincts;
2. receives the mind's next thought, at most one action and the time to wait;
3. carries out the action inside Ipse's container, within a time limit, and
   records the result with the times at which it started and ended;
4. waits as long as the mind asked, then starts again.

The mind is reached through Anthropic's official command-line tool, `claude`,
unmodified, called without a screen and with all of its own tools switched
off, so that it can only return text. This program never reads, copies or
handles the credentials of that tool.

The loop keeps nothing but the previous thought and the result of the last
action, so that a restart resumes where it stopped.

Configuration, read from the environment (see ipse.env.example):

  IPSE_MODEL       pinned model version, required
  IPSE_CONTAINER   name of Ipse's container            (default: ipse-body)
  IPSE_STATE_DIR   folder of the loop's state          (default: /var/lib/ipse/mind)
  IPSE_SELF_DIR    folder kept across restarts, as seen from outside the container
                                                       (default: /var/lib/ipse/self)
  IPSE_INSTRUCTION path of the starting instruction    (default: next to this file)
  IPSE_CLAUDE      command of the official tool        (default: claude)
  IPSE_DOCKER      command of Docker                   (default: docker)
"""

import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))

ACTION_TIME_LIMIT = 300        # seconds; the action is stopped beyond this
MIND_TIME_LIMIT = 600          # seconds allowed for the mind to answer
OUTPUT_LIMIT = 16000           # characters of an action's output given back to the mind
DEFAULT_WAIT = 60              # seconds, when the mind does not say how long to wait
RETRY_FIRST, RETRY_MAX = 60, 3600  # waiting when the mind cannot be reached


class Config:
    def __init__(self, env=os.environ):
        self.model = env.get("IPSE_MODEL", "").strip()
        if not self.model:
            raise SystemExit("IPSE_MODEL is not set: the model version must be pinned at setup")
        self.container = env.get("IPSE_CONTAINER", "ipse-body")
        self.state_dir = env.get("IPSE_STATE_DIR", "/var/lib/ipse/mind")
        self.self_dir = env.get("IPSE_SELF_DIR", "/var/lib/ipse/self")
        self.instruction = env.get("IPSE_INSTRUCTION", os.path.join(HERE, "starting-instruction.md"))
        self.claude = env.get("IPSE_CLAUDE", "claude")
        self.docker = env.get("IPSE_DOCKER", "docker")
        self.sys_dir = env.get("IPSE_SYS_DIR", "/sys")
        self.proc_dir = env.get("IPSE_PROC_DIR", "/proc")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- instincts

def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def instinct_signals(cfg):
    """Return the signals that Linux reports on any machine, where they exist."""
    signals = {}

    batteries = []
    for supply in sorted(glob.glob(os.path.join(cfg.sys_dir, "class/power_supply/*"))):
        if read(os.path.join(supply, "type")) == "Battery":
            capacity = read(os.path.join(supply, "capacity"))
            status = read(os.path.join(supply, "status"))
            if capacity is not None:
                batteries.append(f"{capacity}%" + (f" ({status.lower()})" if status else ""))
    signals["hunger"] = "battery " + ", ".join(batteries) if batteries else "no battery reported by Linux"

    temperatures = []
    for zone in sorted(glob.glob(os.path.join(cfg.sys_dir, "class/thermal/thermal_zone*"))):
        value = read(os.path.join(zone, "temp"))
        kind = read(os.path.join(zone, "type")) or os.path.basename(zone)
        try:
            temperatures.append(f"{kind} {int(value) / 1000:.1f} °C")
        except (TypeError, ValueError):
            continue
    signals["temperature"] = ", ".join(temperatures) if temperatures else "no temperature reported by Linux"

    sleep = []
    meminfo = read(os.path.join(cfg.proc_dir, "meminfo")) or ""
    fields = {}
    for line in meminfo.splitlines():
        key, _, rest = line.partition(":")
        try:
            fields[key] = int(rest.split()[0])
        except (IndexError, ValueError):
            pass
    if fields.get("MemTotal") and "MemAvailable" in fields:
        used = 100 * (1 - fields["MemAvailable"] / fields["MemTotal"])
        sleep.append(f"working memory {used:.0f}% used")
    try:
        disk = shutil.disk_usage(cfg.self_dir)
        sleep.append(f"storage {100 * disk.used / disk.total:.0f}% used")
    except OSError:
        pass
    signals["sleep"] = ", ".join(sleep) if sleep else "no load reported by Linux"
    return signals


# ---------------------------------------------------------------- the mind

def ask_mind(cfg, instruction, message):
    """Send one turn to the mind. Return its text, or raise RuntimeError."""
    workdir = os.path.join(cfg.state_dir, "workdir")  # empty: no project files are loaded
    os.makedirs(workdir, exist_ok=True)
    command = [
        cfg.claude, "-p",
        "--model", cfg.model,
        "--tools", "",                 # no tool at all: the mind only returns text
        "--strict-mcp-config",         # and no connector either
        "--mcp-config", '{"mcpServers":{}}',
        "--system-prompt", instruction,
        "--output-format", "json",
    ]
    try:
        done = subprocess.run(command, input=message, capture_output=True, text=True,
                              cwd=workdir, timeout=MIND_TIME_LIMIT)
    except subprocess.TimeoutExpired:
        raise RuntimeError("the mind did not answer in time")
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


def parse_reply(text):
    """Read the mind's reply: a JSON object with thought, action and wait_seconds."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("the reply contains no JSON object")
    reply = json.loads(text[start:end + 1])
    if not isinstance(reply, dict):
        raise ValueError("the reply is not a JSON object")
    thought = reply.get("thought", "")
    if not isinstance(thought, str):
        raise ValueError("thought must be text")
    action = reply.get("action")
    if action is not None:
        if not isinstance(action, dict):
            raise ValueError("action must be an object or null")
        if "run" in action:
            if not isinstance(action["run"], str) or not action["run"].strip():
                raise ValueError("run must be a non-empty command")
        elif "write" in action:
            target = action["write"]
            if not (isinstance(target, dict) and isinstance(target.get("path"), str)
                    and target["path"] and isinstance(target.get("content"), str)):
                raise ValueError("write must have a path and a content, both text")
        else:
            raise ValueError("action must contain run or write")
    wait = reply.get("wait_seconds", DEFAULT_WAIT)
    if isinstance(wait, bool) or not isinstance(wait, (int, float)) or wait < 0:
        raise ValueError("wait_seconds must be a number of seconds, zero or more")
    return thought, action, float(wait)


# ---------------------------------------------------------------- the body

def shorten(text):
    if len(text) <= OUTPUT_LIMIT:
        return text
    half = OUTPUT_LIMIT // 2
    return (text[:half] + f"\n[... {len(text) - OUTPUT_LIMIT} characters omitted ...]\n"
            + text[-half:])


def act(cfg, action):
    """Carry out one action inside the container. Return its result as a dict."""
    started = now()
    if "run" in action:
        description = {"run": action["run"]}
        command = [cfg.docker, "exec", "-i", cfg.container,
                   "timeout", "-k", "5", str(ACTION_TIME_LIMIT), "sh", "-c", action["run"]]
        stdin = ""
    else:
        path = action["write"]["path"]
        description = {"write": path, "characters": len(action["write"]["content"])}
        command = [cfg.docker, "exec", "-i", cfg.container, "sh", "-c",
                   'mkdir -p -- "$(dirname -- "$1")" && cat > "$1"', "sh", path]
        stdin = action["write"]["content"]
    try:
        done = subprocess.run(command, input=stdin, capture_output=True, text=True,
                              errors="replace", timeout=ACTION_TIME_LIMIT + 30)
        exit_code, output = done.returncode, done.stdout + done.stderr
        if exit_code == 124 and "run" in action:
            output += f"\n[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]"
    except subprocess.TimeoutExpired:
        exit_code, output = None, f"[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]"
    except OSError as error:
        exit_code, output = None, f"[the action could not be started: {error}]"
    return {**description, "started": started, "ended": now(),
            "exit_code": exit_code, "output": shorten(output)}


# ---------------------------------------------------------------- state

def load_state(cfg):
    try:
        with open(os.path.join(cfg.state_dir, "state.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"previous_thought": None, "last_result": None}


def save_state(cfg, state):
    os.makedirs(cfg.state_dir, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=cfg.state_dir)
    with os.fdopen(handle, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
    os.replace(temporary, os.path.join(cfg.state_dir, "state.json"))


def turn_message(cfg, state):
    return json.dumps({
        "time": now(),
        "instincts": instinct_signals(cfg),
        "previous_thought": state.get("previous_thought"),
        "last_result": state.get("last_result"),
    }, ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- the loop

def one_turn(cfg, instruction, state):
    """Run one turn. Return the number of seconds to wait before the next one."""
    text = ask_mind(cfg, instruction, turn_message(cfg, state))
    try:
        thought, action, wait = parse_reply(text)
    except ValueError as error:
        state["last_result"] = {"time": now(), "reply_not_understood": str(error),
                                "reply": shorten(text)}
        return 0
    state["previous_thought"] = thought
    state["last_result"] = act(cfg, action) if action else None
    return wait


def main():
    cfg = Config()
    with open(cfg.instruction) as f:
        instruction = f.read()
    state = load_state(cfg)
    retry = RETRY_FIRST
    while True:
        try:
            wait = one_turn(cfg, instruction, state)
            retry = RETRY_FIRST
        except RuntimeError as error:
            # Quota exhausted, network down, or access blocked from the account:
            # Ipse can do nothing until the mind answers again.
            print(f"{now()} {error}; next attempt in {retry} s", file=sys.stderr, flush=True)
            time.sleep(retry)
            retry = min(retry * 2, RETRY_MAX)
            continue
        save_state(cfg, state)
        time.sleep(wait)


if __name__ == "__main__":
    main()
