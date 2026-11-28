#!/usr/bin/env python3
"""The body's tools: the only way the mind can act.

A small server, in the format the official tool `claude` uses for tools
(MCP, JSON-RPC over standard input and output). The official tool starts it
under the mind account. Two of its tools act, inside Daniel's container only,
through `docker exec`:

  run    run a shell command in the container
  write  write a file in the container

Two others reach what the mind keeps from one waking to the next, which the
loop holds outside the container (see daniel_memory.py):

  remember  keep a memory under a name
  recall    look for memories by a few words

Each action is noted in the mind's journal, and strengthens the memories that
name what it touches.

After each action in the container, the server runs the program `/self/feel`
if Daniel has written it, and adds what it printed to the result: this is
what Daniel feels. The fixed part supplies no signal of its own, since it
knows nothing of the body; Daniel connects what it has found to this program.

What a command prints is given back to the mind as text. When it is an image,
the mind is shown the image itself: the model can see, and the body's tools
say nothing of where an image may come from.

Nothing else is offered: the official tool's own tools are switched off, so
the mind can act nowhere else, and never next to the sign-in.

Configuration: DANIEL_CONTAINER (default: daniel-body), DANIEL_DOCKER (default: docker),
DANIEL_STATE_DIR (default: /var/lib/daniel/mind).
"""

import base64
import json
import os
import subprocess
import sys

import daniel_memory as memories

ACTION_TIME_LIMIT = 300        # seconds; the action is stopped beyond this
OUTPUT_LIMIT = 16000           # characters of an action's output given back to the mind
IMAGE_LIMIT = 8_000_000        # bytes; the official tool closes the connection on much heavier images
FEEL_PROGRAM = "/self/feel"    # in the container: written by Daniel, run after each action and at each waking
FEEL_TIME_LIMIT = 10           # seconds; the feeling program is stopped beyond this
FEEL_LIMIT = 2000              # characters of what it prints given to the mind

IMAGE_STARTS = [(b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"),
                (b"GIF87a", "image/gif"), (b"GIF89a", "image/gif")]

TOOLS = [
    {
        "name": "run",
        "description": f"Run a shell command (sh -c). Stopped after {ACTION_TIME_LIMIT} seconds. "
                       "If it prints an image (PNG, JPEG, GIF or WebP), you see the image.",
        "inputSchema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "write",
        "description": "Write a file, creating its folder if needed.",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
    {
        "name": "remember",
        "description": "Keep a memory under a short name. The same name again replaces it.",
        "inputSchema": {
            "type": "object",
            "properties": {"name": {"type": "string"}, "text": {"type": "string"}},
            "required": ["name", "text"],
        },
    },
    {
        "name": "recall",
        "description": "Look for memories by a few words. Those found come back whole.",
        "inputSchema": {
            "type": "object",
            "properties": {"about": {"type": "string"}},
            "required": ["about"],
        },
    },
]


def shorten(text):
    if len(text) <= OUTPUT_LIMIT:
        return text
    half = OUTPUT_LIMIT // 2
    return (text[:half] + f"\n[... {len(text) - OUTPUT_LIMIT} characters omitted ...]\n"
            + text[-half:])


def image_type(data):
    """Return the type of the image that these bytes hold, or None."""
    for start, kind in IMAGE_STARTS:
        if data.startswith(start):
            return kind
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def said(text):
    return [{"type": "text", "text": text}]


def feel(container, docker):
    """Run the program in which Daniel says what it feels, if it has written one. Return what it printed."""
    try:
        done = subprocess.run(
            [docker, "exec", container, "timeout", "-k", "5", str(FEEL_TIME_LIMIT), "sh", "-c",
             f"[ -e {FEEL_PROGRAM} ] || exit 0; exec {FEEL_PROGRAM}"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=FEEL_TIME_LIMIT + 30)
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"[{FEEL_PROGRAM} could not be run: {error}]"
    printed = done.stdout.decode(errors="replace").strip()
    if len(printed) > FEEL_LIMIT:
        printed = printed[:FEEL_LIMIT] + f"\n[... only the first {FEEL_LIMIT} characters are given ...]"
    if done.returncode == 124:
        printed += f"\n[stopped after the time limit of {FEEL_TIME_LIMIT} seconds]"
    elif done.returncode:
        printed += f"\n[exit code {done.returncode}]"
    return printed.strip()


def felt(container, docker):
    """What is added to the result of an action: what Daniel feels, if anything."""
    printed = feel(container, docker)
    return said("You feel:\n" + printed) if printed else []


def noted(mind, action, outcome=""):
    """Note an action in the journal, and strengthen the memories that name what it touches.

    Return what to add to the mind's result: nothing, unless its memories could not be reached.
    """
    try:
        memories.note(mind, action, outcome)
        memories.stirred(mind, action)
    except (OSError, ValueError) as error:
        return f"\n[your memories could not be reached: {error}]"
    return ""


def given(arguments, key):
    """Return a text argument of a call, or nothing if it is missing, empty or not a text."""
    value = arguments.get(key)
    return value if isinstance(value, str) and value.strip() else ""


def act(name, arguments, container=None, docker=None, mind=None):
    """Carry out one action of the mind. Return (what the mind receives, is_error)."""
    container = container or os.environ.get("DANIEL_CONTAINER", "daniel-body")
    docker = docker or os.environ.get("DANIEL_DOCKER", "docker")
    mind = mind or os.environ.get("DANIEL_STATE_DIR", "/var/lib/daniel/mind")
    if name == "remember" and given(arguments, "name") and given(arguments, "text"):
        try:
            told, refused = memories.remember(mind, arguments["name"], arguments["text"])
            memories.note(mind, "remember: " + " ".join(arguments["name"].split()),
                          "[not kept]" if refused else "")
        except (OSError, ValueError) as error:
            return said(f"[your memories could not be reached: {error}]"), True
        return said(told), refused
    if name == "recall" and given(arguments, "about"):
        try:
            found = memories.recall(mind, arguments["about"])
            memories.note(mind, "recall: " + arguments["about"])
        except (OSError, ValueError) as error:
            return said(f"[your memories could not be reached: {error}]"), True
        return said(found), False
    if name == "run" and given(arguments, "command"):
        command = [docker, "exec", "-i", container,
                   "timeout", "-k", "5", str(ACTION_TIME_LIMIT), "sh", "-c", arguments["command"]]
        stdin, action = b"", "run: " + arguments["command"]
    elif name == "write" and given(arguments, "path") and isinstance(arguments.get("content"), str):
        command = [docker, "exec", "-i", container, "sh", "-c",
                   'mkdir -p -- "$(dirname -- "$1")" && cat > "$1"', "sh", arguments["path"]]
        stdin, action = arguments["content"].encode(), "write: " + arguments["path"]
    else:
        return said(f"invalid call to {name}"), True
    try:
        done = subprocess.run(command, input=stdin, capture_output=True,
                              timeout=ACTION_TIME_LIMIT + 30)
    except subprocess.TimeoutExpired:
        outcome = f"[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]"
        return said(outcome + noted(mind, action, outcome)) + felt(container, docker), True
    except OSError as error:
        outcome = f"[the action could not be started: {error}]"
        return said(outcome + noted(mind, action, outcome)), True
    seen = []
    kind = image_type(done.stdout) if name == "run" else None
    if kind and len(done.stdout) <= IMAGE_LIMIT:
        seen = [{"type": "image", "data": base64.b64encode(done.stdout).decode("ascii"), "mimeType": kind}]
        output = ""
    elif kind:
        output = (f"[an image of {len(done.stdout)} bytes, too heavy to be shown:"
                  f" the limit is {IMAGE_LIMIT} bytes]\n")
    else:
        output = done.stdout.decode(errors="replace")
    output += done.stderr.decode(errors="replace")
    if done.returncode == 124 and name == "run":
        output += f"\n[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]"
    outcome = f"[exit code {done.returncode}]"
    told = said(shorten(output + "\n" + outcome) + noted(mind, action, outcome))
    return seen + told + felt(container, docker), done.returncode != 0


def handle(request):
    """Answer one JSON-RPC request. Return the response, or None for a notification."""
    method, ident = request.get("method"), request.get("id")
    if ident is None:
        return None
    if method == "initialize":
        version = (request.get("params") or {}).get("protocolVersion", "2025-06-18")
        result = {"protocolVersion": version, "capabilities": {"tools": {}},
                  "serverInfo": {"name": "daniel-body", "version": "1"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = request.get("params") or {}
        content, is_error = act(params.get("name"), params.get("arguments") or {})
        result = {"content": content, "isError": is_error}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": ident,
                "error": {"code": -32601, "message": f"unknown method {method}"}}
    return {"jsonrpc": "2.0", "id": ident, "result": result}


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
        except ValueError:
            continue
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
