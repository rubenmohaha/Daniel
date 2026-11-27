#!/usr/bin/env python3
"""Stand-in for Docker, for tests only: there is no container.

`docker exec [options] CONTAINER COMMAND...` runs the command on this machine
instead. The folder `/self` of the container becomes the folder named by
FAKE_DOCKER_SELF, and the time limit set with `timeout -k 5 SECONDS` is
dropped, since that command does not exist on every system.
"""
import os
import subprocess
import sys

argv = sys.argv[1:]
if argv[:1] != ["exec"]:
    sys.exit(125)
argv = argv[1:]
while argv and argv[0].startswith("-"):
    argv.pop(0)
command = argv[1:]  # argv[0] is the name of the container
if command[:1] == ["timeout"]:
    command = command[4:]
command = [word.replace("/self", os.environ["FAKE_DOCKER_SELF"]) for word in command]
sys.exit(subprocess.run(command).returncode)
