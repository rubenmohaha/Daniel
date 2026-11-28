#!/usr/bin/env python3
"""Run a command at a terminal of its own and answer its questions as a person would. For tests only.

Usage: at_a_terminal.py "QUESTION=ANSWER" ... -- COMMAND ...

Each ANSWER is typed, followed by Enter, once QUESTION has appeared, in the
order given. Everything the command shows is printed. The exit code is that of
the command, or 124 if a question has not appeared, or the command has not
ended, within the time allowed.
"""
import os
import pty
import select
import signal
import sys
import time

WAIT = 120  # seconds, for each question and for the end

split = sys.argv.index("--")
questions = [pair.split("=", 1) for pair in sys.argv[1:split]]
pid, terminal = pty.fork()
if pid == 0:
    os.execvp(sys.argv[split + 1], sys.argv[split + 1:])


def show_until(text):
    """Print what the command shows until `text` appears (None: until it ends). False if the time runs out."""
    shown, limit = b"", time.time() + WAIT
    while text is None or text.encode() not in shown:
        if time.time() > limit:
            return False
        if not select.select([terminal], [], [], 1)[0]:
            continue
        try:
            chunk = os.read(terminal, 65536)
        except OSError:  # the command has ended and its terminal is closed
            chunk = b""
        if not chunk:
            return text is None
        shown += chunk
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
    return True


def give_up(reason):
    print(f"\n[at_a_terminal: {reason}]", flush=True)
    os.kill(pid, signal.SIGKILL)
    sys.exit(124)


for question, answer in questions:
    if not show_until(question):
        give_up(f"the question {question!r} did not appear")
    time.sleep(0.5)
    os.write(terminal, answer.encode() + b"\r")
if not show_until(None):
    give_up("the command did not end")
sys.exit(os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1]))
