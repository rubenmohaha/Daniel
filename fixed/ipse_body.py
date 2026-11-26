#!/usr/bin/env python3
"""The body's tools: the only way the mind can act.

A small server, in the format the official tool `claude` uses for tools
(MCP, JSON-RPC over standard input and output). The official tool starts it
under the mind account. It offers two tools, and both act inside Ipse's
container only, through `docker exec`:

  run    run a shell command in the container
  write  write a file in the container

Nothing else is offered: the official tool's own tools are switched off, so
the mind can act nowhere else, and never next to the sign-in.

Configuration: IPSE_CONTAINER (default: ipse-body), IPSE_DOCKER (default: docker).
"""

import json
import os
import subprocess
import sys

ACTION_TIME_LIMIT = 300        # seconds; the action is stopped beyond this
OUTPUT_LIMIT = 16000           # characters of an action's output given back to the mind

TOOLS = [
    {
        "name": "run",
        "description": f"Run a shell command (sh -c). Stopped after {ACTION_TIME_LIMIT} seconds.",
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
]


def shorten(text):
    if len(text) <= OUTPUT_LIMIT:
        return text
    half = OUTPUT_LIMIT // 2
    return (text[:half] + f"\n[... {len(text) - OUTPUT_LIMIT} characters omitted ...]\n"
            + text[-half:])


def act(name, arguments, container=None, docker=None):
    """Carry out one action inside the container. Return (text, is_error)."""
    container = container or os.environ.get("IPSE_CONTAINER", "ipse-body")
    docker = docker or os.environ.get("IPSE_DOCKER", "docker")
    if name == "run" and isinstance(arguments.get("command"), str) and arguments["command"].strip():
        command = [docker, "exec", "-i", container,
                   "timeout", "-k", "5", str(ACTION_TIME_LIMIT), "sh", "-c", arguments["command"]]
        stdin = ""
    elif (name == "write" and isinstance(arguments.get("path"), str) and arguments["path"]
          and isinstance(arguments.get("content"), str)):
        command = [docker, "exec", "-i", container, "sh", "-c",
                   'mkdir -p -- "$(dirname -- "$1")" && cat > "$1"', "sh", arguments["path"]]
        stdin = arguments["content"]
    else:
        return f"invalid call to {name}", True
    try:
        done = subprocess.run(command, input=stdin, capture_output=True, text=True,
                              errors="replace", timeout=ACTION_TIME_LIMIT + 30)
    except subprocess.TimeoutExpired:
        return f"[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]", True
    except OSError as error:
        return f"[the action could not be started: {error}]", True
    output = done.stdout + done.stderr
    if done.returncode == 124 and name == "run":
        output += f"\n[stopped after the time limit of {ACTION_TIME_LIMIT} seconds]"
    return shorten(output + f"\n[exit code {done.returncode}]"), done.returncode != 0


def handle(request):
    """Answer one JSON-RPC request. Return the response, or None for a notification."""
    method, ident = request.get("method"), request.get("id")
    if ident is None:
        return None
    if method == "initialize":
        version = (request.get("params") or {}).get("protocolVersion", "2025-06-18")
        result = {"protocolVersion": version, "capabilities": {"tools": {}},
                  "serverInfo": {"name": "ipse-body", "version": "1"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        params = request.get("params") or {}
        text, is_error = act(params.get("name"), params.get("arguments") or {})
        result = {"content": [{"type": "text", "text": text}], "isError": is_error}
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
