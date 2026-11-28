#!/usr/bin/env python3
"""The page on which a human follows Daniel, from the local network.

Two programs, so that what listens on the network cannot read the mind's folder:

- `daniel_view.py collect` runs under the mind account. Every few seconds it
  reads what the loop and the official tool have recorded, and writes one
  file, `state.json`, in a folder of its own. It opens no connection.
- `daniel_view.py serve` runs under an account of its own, which can read
  that file and nothing of the mind. It serves the page and the file, and
  accepts nothing.

The page only shows: it has no button, and nothing it receives is acted upon.
Nothing here names a sense or an organ: the places Daniel touches are shown
by the names Daniel writes.

What is read, in the mind's folder (see daniel_loop.py and daniel_memory.py):

  wakings          when the loop started, woke the mind, and what came of it
  journal          each action of the mind, with its outcome
  memories.json    the memories and their uses
  .claude/projects the exchanges stored by the official tool: the words of the
                   mind, the summary of its reasoning, the size of the thread,
                   the time of each call and of each result

Configuration, read from the environment (see daniel.env.example):

  DANIEL_STATE_DIR     the mind's folder                   (default: /var/lib/daniel/mind)
  DANIEL_VIEW_DIR      where the state is written          (default: /var/lib/daniel/view)
  DANIEL_VIEW_ADDRESS  address the page is served on       (default: all the addresses of the robot)
  DANIEL_VIEW_PORT     port the page is served on          (default: 8642)
"""

import calendar
import glob
import http.server
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time

import daniel_memory as memories
from daniel_loop import THREAD_LIMIT

HERE = os.path.dirname(os.path.abspath(__file__))

PERIOD = 2             # seconds between two readings
DAYS = 7               # days shown, today included
SPAN = 900             # seconds; today's measures are grouped by quarters of an hour
RECENT = 300           # seconds; the pace "right now" is that of the last five minutes
KEPT = (DAYS + 1) * 86400  # seconds; what is older is dropped from the collector's memory
THOUGHT_LIMIT = 600    # characters of one thought
ACTION_SHOWN = 160     # characters of one action
FELT_SHOWN = 200       # characters of what Daniel felt
LOOP_UNIT, BODY_UNIT = "daniel-loop", "daniel-body"

# A path as Daniel writes it in a command: it starts a word, and is not the end of an address.
PATH = re.compile(r"""(?:^|(?<=[\s'"=(<>|;&]))/(?!/)[\w.+-]+(?:/[\w.+-]+)*""")
WRITTEN = re.compile(r"""(?:>{1,2}|\btee(?:\s+-a)?)\s*['"]?(/(?!/)[\w.+-]+(?:/[\w.+-]+)*)""")
NOWHERE = {"/dev/null", "/dev/stdin", "/dev/stdout", "/dev/stderr"}
FAILED = re.compile(r"\s*\[(?:exit code (\d+)|stopped after [^\]]*|the action could not be started[^\]]*|not kept)\]$")


def active(unit):
    """What systemd says of a service: `active`, `inactive`, `failed`... or `unknown`."""
    try:
        done = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    return done.stdout.strip() or "unknown"


class Tail:
    """The lines added to a file since it was last read."""

    def __init__(self, path):
        self.path, self.position, self.rest, self.inode = path, 0, b"", None

    def lines(self):
        try:
            found = os.stat(self.path)
        except OSError:
            return []
        if found.st_ino != self.inode or found.st_size < self.position:  # replaced or cut down: read anew
            self.inode, self.position, self.rest = found.st_ino, 0, b""
        with open(self.path, "rb") as f:
            f.seek(self.position)
            data = f.read()
        self.position += len(data)
        *whole, self.rest = (self.rest + data).split(b"\n")
        return whole


def entries(tail):
    """The lines of a tail that hold a JSON object."""
    for line in tail.lines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            yield entry


def moment(written):
    """The time written by the official tool on an exchange, in seconds, or None."""
    try:
        whole = calendar.timegm(time.strptime(written[:19], "%Y-%m-%dT%H:%M:%S"))
        return whole + float("0" + written[19:].rstrip("Z") or 0)
    except (TypeError, ValueError):
        return None


def paths(text):
    return [found.group(0) for found in PATH.finditer(text) if found.group(0) not in NOWHERE]


def places(text):
    """The places a command touches, by their first two names, in the order met and once each."""
    found = []
    for path in paths(text):
        place = "/".join(path.split("/")[:3])
        if place not in found:
            found.append(place)
    return found


class Actions:
    """The actions noted in the journal, and what can be counted from them."""

    def __init__(self):
        self.all, self.seen, self.written, self.reused = [], set(), set(), set()

    def feed(self, entry):
        at, did = entry.get("at"), entry.get("did")
        if not isinstance(at, (int, float)) or not isinstance(did, str) or ": " not in did:
            return
        if self.all and at <= self.all[-1]["at"]:
            return  # already read, before the journal was cut down
        tool, text = did.split(": ", 1)
        failed = FAILED.search(text)
        ok = not failed or failed.group(1) == "0"
        text = FAILED.sub("", text)
        new = None
        if tool in ("run", "write"):
            touched = places(text)
            new = any(place not in self.seen for place in touched) if touched else None
            self.seen.update(touched)
            targets = {text} if tool == "write" else set(WRITTEN.findall(text))
            if tool == "run":
                self.reused.update(path for path in paths(text) if path in self.written and path not in targets)
            self.written.update(targets - NOWHERE)
        self.all.append({"at": at, "tool": tool, "text": text, "ok": ok, "new": new, "reused": len(self.reused)})

    def forget(self, before):
        self.all = [action for action in self.all if action["at"] >= before] or self.all[-1:]


class Exchanges:
    """What the exchanges stored by the official tool say of the mind."""

    def __init__(self):
        self.thoughts, self.decisions, self.thread, self.feelings, self.signs = [], [], [], [], []
        self.pending, self.answered = {}, {}

    def feed(self, entry, source):
        if not isinstance(entry, dict) or not isinstance(entry.get("message"), dict):
            return
        at, content = moment(entry.get("timestamp")), entry["message"].get("content")
        if at is None:
            return
        if not self.signs or at - self.signs[-1] >= 30:
            self.signs.append(at)
        if entry.get("type") == "user":
            if isinstance(content, str):
                self.felt(at, content.rpartition("\n\n")[2] if "\n\n" in content else content)
            for part in content if isinstance(content, list) else []:
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    self.pending.pop(part.get("tool_use_id"), None)
                    self.answered[source] = at
                    inside = part.get("content")
                    for piece in inside if isinstance(inside, list) else []:
                        if isinstance(piece, dict) and piece.get("type") == "text":
                            self.felt(at, piece.get("text", ""))
        elif entry.get("type") == "assistant" and isinstance(content, list):
            usage = entry["message"].get("usage")
            if isinstance(usage, dict):
                size = sum(usage.get(key) or 0 for key in
                           ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
                if size:
                    self.thread.append((at, size))
            for part in content:
                if not isinstance(part, dict):
                    continue
                kind = part.get("type")
                text = part.get("thinking") if kind == "thinking" else part.get("text") if kind == "text" else None
                if isinstance(text, str) and text.strip():
                    self.thoughts.append({"at": at, "text": " ".join(text.split())[:THOUGHT_LIMIT],
                                          "kind": "reasoning" if kind == "thinking" else "words"})
                if kind == "tool_use":
                    if source in self.answered:
                        self.decisions.append((at, round(at - self.answered.pop(source), 1)))
                    given = part.get("input") if isinstance(part.get("input"), dict) else {}
                    shown = given.get("command") or given.get("path") or given.get("name") or given.get("about") or ""
                    self.pending[part.get("id")] = {
                        "at": at, "tool": str(part.get("name", "")).rsplit("__", 1)[-1],
                        "text": " ".join(str(shown).split())[:ACTION_SHOWN]}

    def felt(self, at, text):
        if isinstance(text, str) and text.startswith("You feel:\n"):
            self.feelings.append((at, " ".join(text[len("You feel:\n"):].split())[:FELT_SHOWN]))

    def doing(self, since):
        """The action of the mind that has no result yet, if it began after `since`."""
        latest = max(self.pending.values(), key=lambda action: action["at"], default=None)
        return latest if latest and latest["at"] >= since else None

    def forget(self, before):
        self.thoughts = self.thoughts[-40:]
        for name in ("decisions", "thread", "feelings"):
            setattr(self, name, [item for item in getattr(self, name) if item[0] >= before])
        self.signs = [at for at in self.signs if at >= before]
        self.pending = {ident: action for ident, action in self.pending.items() if action["at"] >= before}


def states(notes, signs, now, running):
    """What the mind was doing, as [start, end, state] in order: acting, waiting, or unreachable.

    `notes` are those of the loop. Where the loop started anew, or runs no more, it is
    shown only up to its last sign of life (`signs`, in order): nothing is known after it.
    """
    spans = []
    for index, note in enumerate(notes):
        start, what = note["at"], note["what"]
        following = notes[index + 1] if index + 1 < len(notes) else None
        if what == "woken":
            state = "unreachable" if following and following["what"] == "unreachable" else "acting"
        else:
            state = "unreachable" if what == "unreachable" else "waiting"
        end = following["at"] if following else now
        if (following and following["what"] == "started") or (not following and not running):
            end = max([start] + [at for at in signs if start <= at < end])
        if end > start:
            if spans and spans[-1][2] == state and spans[-1][1] == start:
                spans[-1][1] = end
            else:
                spans.append([start, end, state])
    return spans


def midnight(now, back=0):
    """The start of the day that began `back` days before today, on the robot's own clock."""
    year, month, day = time.localtime(now)[:3]
    return time.mktime((year, month, day - back, 0, 0, 0, 0, 0, -1))


def middle(values):
    return round(statistics.median(values), 1) if values else None


def share(part, whole):
    return round(100 * part / whole) if whole else None


class Machine:
    """How busy the machine that hosts Daniel is: processor, working memory, disk, each in percent."""

    def __init__(self):
        self.before = None

    def read(self):
        return {"cpu": self.processor(), "memory": self.memory(), "disk": self.disk()}

    def processor(self):
        try:
            with open("/proc/stat") as f:
                counts = [int(value) for value in f.readline().split()[1:]]
        except (OSError, ValueError):
            return None
        idle, total = counts[3] + (counts[4] if len(counts) > 4 else 0), sum(counts)
        before, self.before = self.before, (idle, total)
        if not before or total == before[1]:
            return None
        return round(100 * (1 - (idle - before[0]) / (total - before[1])))

    def memory(self):
        try:
            with open("/proc/meminfo") as f:
                found = dict(line.split(":", 1) for line in f)
            return round(100 * (1 - int(found["MemAvailable"].split()[0]) / int(found["MemTotal"].split()[0])))
        except (OSError, ValueError, KeyError, ZeroDivisionError):
            return None

    def disk(self):
        try:
            found = os.statvfs("/")
            return round(100 * (1 - found.f_bavail / found.f_blocks))
        except (OSError, ZeroDivisionError):
            return None


class Collector:
    """Reads the records of the mind as they grow, and says what the page shows."""

    def __init__(self, mind):
        self.mind = mind
        self.notes, self.notes_tail = [], Tail(os.path.join(mind, "wakings"))
        self.actions, self.journal_tail = Actions(), Tail(os.path.join(mind, "journal"))
        self.exchanges, self.tails = Exchanges(), {}
        self.machine = Machine()

    def read(self, now):
        for note in entries(self.notes_tail):
            at, what = note.get("at"), note.get("what")
            if isinstance(at, (int, float)) and isinstance(what, str) and (not self.notes or at > self.notes[-1]["at"]):
                self.notes.append({"at": at, "what": what, "why": str(note.get("why", ""))})
        for entry in entries(self.journal_tail):
            self.actions.feed(entry)
        pattern = os.path.join(self.mind, ".claude", "projects", "*", "*.jsonl")
        for path in sorted(glob.glob(pattern), key=lambda found: (os.path.getmtime(found), found)):
            if path in self.tails or os.path.getmtime(path) >= now - KEPT:
                for entry in entries(self.tails.setdefault(path, Tail(path))):
                    self.exchanges.feed(entry, path)
        self.notes = [note for note in self.notes if note["at"] >= now - KEPT] or self.notes[-1:]
        self.actions.forget(now - KEPT)
        self.exchanges.forget(now - KEPT)

    def state(self, now=None):
        now = time.time() if now is None else now
        self.read(now)
        loop, body = active(LOOP_UNIT), active(BODY_UNIT)
        done, told = self.actions.all, self.exchanges
        signs = sorted([action["at"] for action in done] + told.signs)
        spans = states(self.notes, signs, now, loop == "active")
        today = midnight(now)

        current = spans[-1] if spans and spans[-1][1] >= now else None
        last = self.notes[-1] if self.notes else None
        moment_now = {
            "state": current[2] if current else "stopped" if self.notes else "never",
            "since": current[0] if current else spans[-1][1] if spans else None,
            "why": last["why"] if last and current and current[2] == "unreachable" else "",
            "wakings_today": sum(1 for start, _, state in spans if state == "acting" and start >= today),
            "last_action_at": done[-1]["at"] if done else None,
        }

        days = []
        for back in range(DAYS - 1, -1, -1):
            start, end = midnight(now, back), midnight(now, back - 1)
            inside = [[max(a, start), min(b, end), state] for a, b, state in spans if a < end and b > start]
            mine = [action for action in done if start <= action["at"] < end]
            judged = [action for action in mine if action["tool"] in ("run", "write")]
            placed = [action for action in judged if action["new"] is not None]
            before = [action for action in done if action["at"] < end]
            days.append({
                "start": start, "end": end, "segments": inside,
                "acting": round(sum(b - a for a, b, state in inside if state == "acting")),
                "success": share(sum(action["ok"] for action in judged), len(judged)),
                "new": share(sum(action["new"] for action in placed), len(placed)),
                "reused": before[-1]["reused"] if before else None,
                "decision": middle([seconds for at, seconds in told.decisions if start <= at < end]),
            })

        def quarters(pairs, summary):
            groups = {}
            for at, value in pairs:
                if at >= today:
                    groups.setdefault(today + SPAN * int((at - today) // SPAN), []).append(value)
            return [[start, summary(values)] for start, values in sorted(groups.items())]

        mine = [action for action in done if action["at"] >= today]
        acting = current and current[2] == "acting"
        try:
            kept = memories.load(self.mind)
            strongest = sorted(((name, round(memories.strength(memory, now), 2)) for name, memory in kept.items()),
                               key=lambda pair: pair[1], reverse=True)
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError):
            kept, strongest = {}, []

        busy = {}
        for action in done:
            if action["at"] >= now - 3600 and action["tool"] in ("run", "write"):
                for place in places(action["text"]):
                    busy[place] = busy.get(place, 0) + 1

        return {
            "at": now, "offset": time.localtime(now).tm_gmtoff, "loop": loop, "body": body,
            "now": moment_now,
            "days": [{key: day[key] for key in ("start", "end", "segments", "acting")} for day in days],
            "today": {
                "rate": quarters([(action["at"], 1) for action in mine], lambda ones: round(len(ones) * 60 / SPAN, 1)),
                "decision": quarters(told.decisions, middle),
                "thread": quarters(told.thread, max),
                "feelings": [[at, text] for at, text in told.feelings if at >= today],
                "failures": [[action["at"], action["text"][:ACTION_SHOWN]] for action in mine if not action["ok"]],
                "rate_now": round(sum(1 for action in done if action["at"] > now - RECENT) * 60 / RECENT, 1),
                "actions": len(mine), "failed": sum(1 for action in mine if not action["ok"]),
                "decision_median": middle([seconds for at, seconds in told.decisions if at >= today]),
                "thread_now": told.thread[-1][1] if acting and told.thread else None,
                "thread_limit": THREAD_LIMIT,
            },
            "thoughts": told.thoughts[-3:],
            "doing": told.doing(current[0]) if acting else None,
            "actions": [{"at": action["at"], "tool": action["tool"], "text": action["text"][:ACTION_SHOWN],
                         "ok": action["ok"]} for action in reversed(done[-4:])],
            "busy": sorted(busy.items(), key=lambda pair: (-pair[1], pair[0]))[:4],
            "memories": {"count": len(kept), "strongest": strongest[:3]},
            "capacity": {name: [day[name] for day in days] for name in ("reused", "success", "new", "decision")},
            "machine": self.machine.read(),
        }


def write(folder, state):
    """Write the state in one step, readable by the account that serves the page."""
    os.makedirs(folder, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=folder)
    with os.fdopen(handle, "w") as f:
        json.dump(state, f, ensure_ascii=False)
    os.chmod(temporary, 0o644)
    os.replace(temporary, os.path.join(folder, "state.json"))


def collect(mind, folder):
    collector = Collector(mind)
    while True:
        try:
            write(folder, collector.state())
        except Exception as error:  # a record that cannot be read must not stop the page for good
            print(f"the state could not be collected: {error!r}", file=sys.stderr, flush=True)
        time.sleep(PERIOD)


def server(address, port, page, folder):
    """The server of the page: it gives the page and the state, and nothing else."""

    class Page(http.server.BaseHTTPRequestHandler):
        timeout = 15
        server_version, sys_version = "daniel-view", ""

        def do_GET(self):
            if self.path == "/":
                self.give(page, "text/html; charset=utf-8", 404)
            elif self.path == "/state.json":
                self.give(os.path.join(folder, "state.json"), "application/json", 503)
            else:
                self.send_error(404)

        def give(self, path, kind, missing):
            try:
                with open(path, "rb") as f:
                    body = f.read()
            except OSError:
                return self.send_error(missing)
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                             "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *arguments):
            pass

    return http.server.ThreadingHTTPServer((address, port), Page)


def main():
    env = os.environ
    mind = env.get("DANIEL_STATE_DIR", "/var/lib/daniel/mind")
    folder = env.get("DANIEL_VIEW_DIR", "/var/lib/daniel/view")
    if sys.argv[1:] == ["collect"]:
        collect(mind, folder)
    elif sys.argv[1:] == ["serve"]:
        server(env.get("DANIEL_VIEW_ADDRESS", ""), int(env.get("DANIEL_VIEW_PORT", "8642")),
               os.path.join(HERE, "daniel-view.html"), folder).serve_forever()
    else:
        raise SystemExit("usage: daniel_view.py collect | serve")


if __name__ == "__main__":
    main()
