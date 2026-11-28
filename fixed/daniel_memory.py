#!/usr/bin/env python3
"""Daniel's memories: what the mind keeps from one waking to the next.

The mind keeps nothing by itself. What it wants to keep, it gives a name and
keeps with the tool `remember`; it looks for it with the tool `recall`. The
memories are kept by the loop, next to the mind's last words, and are meant to
come back as a human's do:

- A memory grows stronger each time it is used, and fades with time. A use is
  keeping it, recalling it, or doing something that it names: each action is
  compared with the memories, and those that hold one of its words grow
  stronger, as long as few memories hold that word.
- When the mind wakes, the strongest memories come back by themselves, whole.
  The next ones come back by their name only. The others must be looked for.
- Nothing is erased: a faint memory is harder to reach, not lost.

The strength of a memory is the sum, over its uses, of the age of the use
raised to the power -DECAY. This is the base-level learning equation of the
ACT-R theory of human memory: one rule gives both the advantage of what is
recent and the advantage of what is frequent.

The latest actions of the mind are also noted in a journal, whose end is
given back at each waking: the mind knows what it was doing, even when its
last waking was cut.
"""

import json
import os
import re
import tempfile
import time

TEXT_LIMIT = 2000     # characters of one memory
NAME_LIMIT = 80       # characters of its name
USES_KEPT = 64        # the latest uses of a memory are kept one by one; earlier ones are counted
DECAY = 0.5           # a use that is t seconds old weighs t ** -DECAY
SAME_USE = 60         # seconds; actions closer than this stir a memory only once
RARE = 3              # a word of an action points to a memory only if at most this many hold it
FOUND = 5             # memories that one recall gives whole
NAMES_LIMIT = 2000    # characters of the names given, at waking, for the memories not given whole
ACTION_LIMIT = 300    # characters of an action noted in the journal
JOURNAL_ROOM = 200000 # bytes; the journal is cut down to its latest half beyond twice this

WORD = re.compile(r"[a-z0-9_./:+-]{4,}")


def load(mind):
    """Return the memories kept in the folder `mind`: {name: {"text", "uses", "earlier"}}."""
    try:
        with open(os.path.join(mind, "memories.json")) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def keep(mind, name, content):
    """Write a file of the folder `mind` in one step."""
    os.makedirs(mind, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=mind)
    with os.fdopen(handle, "w") as f:
        f.write(content)
    os.replace(temporary, os.path.join(mind, name))


def save(mind, store):
    keep(mind, "memories.json", json.dumps(store, ensure_ascii=False, indent=1))


def strength(memory, now):
    """How easily a memory comes back: each use counts, and counts less as it grows old."""
    uses = memory["uses"]
    total = sum(max(now - at, 1.0) ** -DECAY for at in uses)
    return total + memory.get("earlier", 0) * max(now - uses[0], 1.0) ** -DECAY


def use(memory, now):
    memory["uses"].append(now)
    extra = len(memory["uses"]) - USES_KEPT
    if extra > 0:
        del memory["uses"][:extra]
        memory["earlier"] = memory.get("earlier", 0) + extra


def whole(name, memory):
    return f"[{name}]\n{memory['text']}"


def remember(mind, name, text, now=None):
    """Keep a memory under a name. Return (what the mind is told, whether it was refused)."""
    now = time.time() if now is None else now
    name, text = " ".join(name.split()), text.strip()
    if not name or not text:
        return "[not kept: a memory needs a name and a text]", True
    if len(name) > NAME_LIMIT:
        return f"[not kept: a name has at most {NAME_LIMIT} characters; this one has {len(name)}]", True
    if len(text) > TEXT_LIMIT:
        return f"[not kept: a memory has at most {TEXT_LIMIT} characters; this one has {len(text)}]", True
    store = load(mind)
    known = name in store
    memory = store.setdefault(name, {"uses": []})
    memory["text"] = text
    use(memory, now)
    save(mind, store)
    return ("kept, in place of what this name held" if known else "kept"), False


def recall(mind, about, now=None):
    """Look for the memories that hold the words of `about`. Those given whole grow stronger."""
    now = time.time() if now is None else now
    sought = set(re.findall(r"\w{3,}", about.lower()))
    store = load(mind)
    found = []
    for name, memory in store.items():
        held = (name + "\n" + memory["text"]).lower()
        hits = sum(1 for word in sought if word in held)
        if hits:
            found.append((hits, strength(memory, now), name))
    if not found:
        return "[nothing comes back]"
    names = [name for _, _, name in sorted(found, reverse=True)]
    for name in names[:FOUND]:
        use(store[name], now)
    save(mind, store)
    text = "\n\n".join(whole(name, store[name]) for name in names[:FOUND])
    if names[FOUND:]:
        text += "\n\nBy name only: " + "; ".join(names[FOUND:FOUND + 20])
    return text


def words(text):
    """The words by which an action and a memory can meet: names of files, of programs, of things."""
    found = set()
    for word in WORD.findall(text.lower()):
        for part in (word.strip(".:/+-"), word.rsplit("/", 1)[-1].strip(".:+-")):
            if len(part) >= 4:
                found.add(part)
    return found


def stirred(mind, action, now=None):
    """Strengthen the memories that an action brings back: those that hold one of its rarer words."""
    now = time.time() if now is None else now
    named = words(action)
    store = load(mind)
    holders = {}
    for name, memory in store.items():
        for word in named & words(name + " " + memory["text"]):
            holders.setdefault(word, []).append(name)
    brought_back = {name for names in holders.values() if len(names) <= RARE for name in names}
    fresh = [store[name] for name in brought_back if now - store[name]["uses"][-1] >= SAME_USE]
    for memory in fresh:
        use(memory, now)
    if fresh:
        save(mind, store)


def waking(mind, limit, now=None):
    """What comes back by itself when the mind wakes, within `limit` characters. None without memories."""
    now = time.time() if now is None else now
    store = load(mind)
    if not store:
        return None
    ranked = sorted(store, key=lambda name: strength(store[name], now), reverse=True)
    given, fainter = [], []
    for name in ranked:
        entry = whole(name, store[name])
        if not fainter and len(entry) + 2 <= limit:
            given.append(entry)
            limit -= len(entry) + 2
        else:
            fainter.append(name)
    named = []
    while fainter and len("; ".join(named + fainter[:1])) <= NAMES_LIMIT:
        named.append(fainter.pop(0))
    parts = given + (["Fainter, by name only: " + "; ".join(named)] if named else [])
    return "\n\n".join(parts + ([f"And {len(fainter)} fainter still."] if fainter else []))


def note(mind, action, outcome="", now=None):
    """Note an action in the journal: on one line, shortened, followed by its outcome."""
    now = time.time() if now is None else now
    line = action.split("\n", 1)[0][:ACTION_LIMIT]
    line += " ..." if line != action else ""
    path = os.path.join(mind, "journal")
    os.makedirs(mind, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps({"at": now, "did": f"{line} {outcome}".strip()}, ensure_ascii=False) + "\n")
    if os.path.getsize(path) > 2 * JOURNAL_ROOM:
        with open(path) as f:
            lines = f.readlines()
        keep(mind, "journal", "".join(lines[len(lines) // 2:]))


def latest(mind, limit):
    """The latest actions noted, the most recent last, within `limit` characters. None without any."""
    path = os.path.join(mind, "journal")
    try:
        with open(path, "rb") as f:
            start = max(0, os.path.getsize(path) - 8 * (limit + ACTION_LIMIT))  # enough to fill the limit
            f.seek(start)
            lines = f.read().decode(errors="replace").splitlines()
    except FileNotFoundError:
        return None
    given = []
    for line in reversed(lines[1:] if start else lines):  # the first line read may be cut
        did = json.loads(line)["did"]
        if len("\n".join([did] + given)) > limit:
            given.insert(0, "[... earlier actions are omitted ...]")
            break
        given.insert(0, did)
    return "\n".join(given) or None
