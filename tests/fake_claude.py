#!/usr/bin/env python3
"""Stand-in for the official tool, for tests only. It never contacts Anthropic.

It records its arguments and the message it receives. Each line of the file
named by FAKE_CLAUDE_REPLIES describes one waking, as JSON: either the text of
the mind's last words, "FAIL" to simulate an unreachable mind, "HANG" to
simulate a mind that does not stop, or an object
{"calls": [{"name": ..., "arguments": {...}}], "final": "..."}. For an object,
the stand-in starts the tool server named in --mcp-config, as the official
tool does, calls the tools in order, records their results, and ends with the
final text.

When FAKE_CLAUDE_REFUSES names an option, a call that carries it is refused as
the official tool refuses an option it does not know, and noted apart.

It also stands in for the sign-in, as far as the installation script uses it:
`auth status` says whether a code has been received, and `auth login` asks for
a code. Like the official tool, it asks on its own terminal, whatever it is
given as input, and is not stopped when that terminal is not handed to it: it
then waits for a code that never comes. This was observed with the official
tool (version 2.1.332) started by sudo on Ubuntu 24.04.
"""
import json, os, signal, subprocess, sys, time

argv = sys.argv[1:]
if argv[:1] == ["auth"]:
    signed_in = os.path.expanduser("~/.fake-claude-signed-in")
    if argv[1] == "login":
        signal.signal(signal.SIGTTIN, signal.SIG_IGN)
        signal.signal(signal.SIGTTOU, signal.SIG_IGN)
        terminal = os.open("/dev/tty", os.O_RDWR)
        os.write(terminal, b"Paste code here if prompted > ")
        code, limit = b"", time.time() + 60
        while not code.endswith(b"\n"):
            if time.time() > limit:
                sys.exit(1)
            try:
                code += os.read(terminal, 1024)
            except OSError:  # the terminal is not handed to this program
                time.sleep(0.2)
        with open(signed_in, "wb") as f:
            f.write(code.strip())
    else:
        print(json.dumps({"loggedIn": os.path.exists(signed_in)}, indent=2))
    sys.exit(0)
record = os.environ["FAKE_CLAUDE_RECORD"]
refused = os.environ.get("FAKE_CLAUDE_REFUSES")  # an option that this version of the tool does not know
if refused and refused in argv:
    with open(record + ".refused", "a") as f:
        f.write(json.dumps(argv) + "\n")
    sys.exit(f"error: unknown option '{refused}'")
entry = {"argv": argv, "stdin": sys.stdin.read(), "cwd": os.getcwd(), "results": []}
with open(os.environ["FAKE_CLAUDE_REPLIES"]) as f:
    replies = f.read().splitlines()
calls = (sum(1 for _ in open(record)) if os.path.exists(record) else 0) + 1
reply = json.loads(replies[min(calls, len(replies)) - 1])

if isinstance(reply, dict):
    server = json.loads(argv[argv.index("--mcp-config") + 1])["mcpServers"]["body"]
    proc = subprocess.Popen([server["command"], *server["args"]], text=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            env={**os.environ, **server.get("env", {})})
    def rpc(ident, method, params=None):
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "id": ident, "method": method,
                                     "params": params or {}}) + "\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())
    rpc(1, "initialize", {"protocolVersion": "2025-06-18"})
    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    entry["tools"] = [t["name"] for t in rpc(2, "tools/list")["result"]["tools"]]
    for n, call in enumerate(reply["calls"]):
        entry["results"].append(rpc(10 + n, "tools/call", call)["result"])
    proc.stdin.close(); proc.wait()
    reply = reply["final"]

with open(record, "a") as f:
    f.write(json.dumps(entry) + "\n")
if reply == "HANG":
    time.sleep(3600)
if reply == "FAIL":
    print(json.dumps({"is_error": True, "result": "usage limit reached"}))
    sys.exit(1)
print(json.dumps({"type": "result", "is_error": False, "result": reply}))
