#!/usr/bin/env python3
"""Stand-in for the official tool, for tests only. It never contacts Anthropic.

It records its arguments and the message it receives, then returns the next
reply from the file named by FAKE_CLAUDE_REPLIES (one JSON string per line).
"""
import json, os, sys

record = os.environ["FAKE_CLAUDE_RECORD"]
with open(record, "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "stdin": sys.stdin.read(), "cwd": os.getcwd()}) + "\n")
with open(os.environ["FAKE_CLAUDE_REPLIES"]) as f:
    replies = f.read().splitlines()
calls = sum(1 for _ in open(record))
reply = json.loads(replies[min(calls, len(replies)) - 1])
if reply == "FAIL":
    print(json.dumps({"is_error": True, "result": "usage limit reached"}))
    sys.exit(1)
print(json.dumps({"type": "result", "is_error": False, "result": reply}))
