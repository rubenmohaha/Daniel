"""Tests of the loop and of the body's tools. Nothing contacts Anthropic.

The mind is replaced by a stand-in (fake_claude.py) that starts the body's
tool server as the official tool does. The tests marked "container" need
Docker and start a throwaway container.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fixed"))
import daniel_body  # noqa: E402
import daniel_loop  # noqa: E402

HAVE_DOCKER = shutil.which("docker") and subprocess.run(
    ["docker", "info"], capture_output=True).returncode == 0


def config(tmp, **extra):
    env = {
        "DANIEL_MODEL": "test-model-version",
        "DANIEL_STATE_DIR": os.path.join(tmp, "mind"),
        "DANIEL_CLAUDE": os.path.join(HERE, "fake_claude.py"),
    }
    env.update(extra)
    return daniel_loop.Config(env)


def fake_mind(tmp, *replies):
    path = os.path.join(tmp, "replies")
    with open(path, "w") as f:
        for reply in replies:
            f.write(json.dumps(reply) + "\n")
    os.environ["FAKE_CLAUDE_REPLIES"] = path
    os.environ["FAKE_CLAUDE_RECORD"] = os.path.join(tmp, "record")


def calls(tmp):
    with open(os.path.join(tmp, "record")) as f:
        return [json.loads(line) for line in f]


class Loop(unittest.TestCase):
    def test_the_official_tool_is_called_with_the_body_tools_only(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "hello")
        daniel_loop.one_waking(config(tmp), "INSTRUCTION", {})
        argv = calls(tmp)[0]["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "test-model-version")
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertIn("--strict-mcp-config", argv)
        servers = json.loads(argv[argv.index("--mcp-config") + 1])["mcpServers"]
        self.assertEqual(list(servers), ["body"])
        self.assertEqual(argv[argv.index("--allowedTools") + 1], "mcp__body__run,mcp__body__write")
        self.assertEqual(argv[argv.index("--system-prompt") + 1], "INSTRUCTION")
        self.assertEqual(calls(tmp)[0]["cwd"], os.path.join(tmp, "mind", "workdir"))

    def test_last_words_are_given_back(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "first words", "second words")
        state = {}
        daniel_loop.one_waking(config(tmp), "I", state)
        daniel_loop.one_waking(config(tmp), "I", state)
        self.assertEqual([c["stdin"] for c in calls(tmp)], ["Begin.", "first words"])
        self.assertEqual(state["last_words"], "second words")

    def test_unreachable_mind_raises_and_keeps_the_state(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "FAIL")
        state = {"last_words": "kept"}
        with self.assertRaisesRegex(RuntimeError, "usage limit reached"):
            daniel_loop.one_waking(config(tmp), "I", state)
        self.assertEqual(state["last_words"], "kept")

    def test_model_must_be_pinned(self):
        with self.assertRaises(SystemExit):
            daniel_loop.Config({})

    def test_state_survives_a_restart(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        daniel_loop.save_state(cfg, {"last_words": "é"})
        self.assertEqual(daniel_loop.load_state(cfg)["last_words"], "é")


class BodyServer(unittest.TestCase):
    def test_protocol(self):
        self.assertEqual(daniel_body.handle({"method": "notifications/initialized"}), None)
        init = daniel_body.handle({"id": 1, "method": "initialize",
                                 "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(init["result"]["protocolVersion"], "2025-06-18")
        tools = daniel_body.handle({"id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["run", "write"])
        self.assertIn("error", daniel_body.handle({"id": 3, "method": "resources/list"}))

    def test_invalid_calls_are_refused_without_acting(self):
        for name, arguments in [("run", {}), ("run", {"command": " "}), ("write", {"path": "x"}),
                                ("delete", {"path": "x"})]:
            text, is_error = daniel_body.act(name, arguments, docker="/nonexistent")
            self.assertTrue(is_error)
            self.assertIn("invalid call", text)


@unittest.skipUnless(HAVE_DOCKER, "Docker is not available")
class Container(unittest.TestCase):
    name = "daniel-test-body"

    @classmethod
    def setUpClass(cls):
        cls.self_dir = tempfile.mkdtemp()
        subprocess.run(["docker", "rm", "-f", cls.name], capture_output=True)
        subprocess.run(["docker", "run", "-d", "--name", cls.name, "--init",
                        "-v", f"{cls.self_dir}:/self", "-w", "/self",
                        "debian:stable-slim", "sleep", "infinity"],
                       check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["docker", "rm", "-f", cls.name], capture_output=True)

    def test_a_waking_acts_inside_the_container_through_the_body_tools(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, {"calls": [
            {"name": "run", "arguments": {"command": "hostname; id -u; echo err >&2; exit 3"}},
            {"name": "write", "arguments": {"path": "/self/notes/first.md",
                                            "content": "a line; with $pecial `chars`\n"}},
        ], "final": "I have written my first note."})
        state = {}
        daniel_loop.one_waking(config(tmp, DANIEL_CONTAINER=self.name), "I", state)
        record = calls(tmp)[0]
        self.assertEqual(record["tools"], ["run", "write"])
        ran, wrote = record["results"]
        self.assertTrue(ran["isError"])
        self.assertIn("\n0\n", ran["content"][0]["text"])
        self.assertIn("err", ran["content"][0]["text"])
        self.assertIn("[exit code 3]", ran["content"][0]["text"])
        self.assertFalse(wrote["isError"])
        with open(os.path.join(self.self_dir, "notes", "first.md")) as f:
            self.assertEqual(f.read(), "a line; with $pecial `chars`\n")
        self.assertEqual(state["last_words"], "I have written my first note.")

    def test_time_limit(self):
        limit = daniel_body.ACTION_TIME_LIMIT
        daniel_body.ACTION_TIME_LIMIT = 2
        try:
            text, is_error = daniel_body.act("run", {"command": "sleep 30"}, container=self.name)
        finally:
            daniel_body.ACTION_TIME_LIMIT = limit
        self.assertTrue(is_error)
        self.assertIn("time limit", text)
        still = subprocess.run(["docker", "exec", self.name, "sh", "-c",
                                "for f in /proc/[0-9]*/cmdline; do tr '\\0' ' ' < $f; echo; done"
                                " | grep -c '^sleep 30 $' || true"],
                               capture_output=True, text=True).stdout.strip()
        self.assertEqual(still, "0")  # the stopped command does not keep running

    def test_long_output_is_shortened(self):
        text, _ = daniel_body.act("run", {"command": "yes | head -c 100000"}, container=self.name)
        self.assertLess(len(text), daniel_body.OUTPUT_LIMIT + 100)
        self.assertIn("characters omitted", text)


if __name__ == "__main__":
    unittest.main()
