"""Tests of the loop. The mind is replaced by a stand-in; nothing contacts Anthropic.

The tests marked "container" need Docker and start a throwaway container.
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
import ipse_loop  # noqa: E402

HAVE_DOCKER = shutil.which("docker") and subprocess.run(
    ["docker", "info"], capture_output=True).returncode == 0


def config(tmp, **extra):
    env = {
        "IPSE_MODEL": "test-model-version",
        "IPSE_STATE_DIR": os.path.join(tmp, "mind"),
        "IPSE_CLAUDE": os.path.join(HERE, "fake_claude.py"),
    }
    env.update(extra)
    return ipse_loop.Config(env)


def fake_mind(tmp, *replies):
    path = os.path.join(tmp, "replies")
    with open(path, "w") as f:
        for reply in replies:
            f.write(json.dumps(reply if isinstance(reply, str) else json.dumps(reply)) + "\n")
    os.environ["FAKE_CLAUDE_REPLIES"] = path
    os.environ["FAKE_CLAUDE_RECORD"] = os.path.join(tmp, "record")


def calls(tmp):
    with open(os.path.join(tmp, "record")) as f:
        return [json.loads(line) for line in f]


class ParseReply(unittest.TestCase):
    def test_run(self):
        thought, action, wait = ipse_loop.parse_reply(
            '{"thought": "look", "action": {"run": "ls /dev"}, "wait_seconds": 5}')
        self.assertEqual((thought, action, wait), ("look", {"run": "ls /dev"}, 5.0))

    def test_text_around_the_object_is_ignored(self):
        _, action, _ = ipse_loop.parse_reply('Here:\n```json\n{"thought": "", "action": null}\n```')
        self.assertIsNone(action)

    def test_default_wait(self):
        self.assertEqual(ipse_loop.parse_reply('{"thought": "x"}')[2], ipse_loop.DEFAULT_WAIT)

    def test_rejected(self):
        for bad in ['no object', '{"action": {"delete": "x"}}', '{"action": {"run": ""}}',
                    '{"wait_seconds": -1}', '{"wait_seconds": "soon"}',
                    '{"action": {"write": {"path": "/self/a"}}}', '[1, 2]']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ipse_loop.parse_reply(bad)


class Mind(unittest.TestCase):
    def test_the_official_tool_is_called_without_tools_and_with_the_pinned_model(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, {"thought": "hello", "action": None, "wait_seconds": 0})
        cfg = config(tmp)
        state = {"previous_thought": None, "last_result": None}
        ipse_loop.one_turn(cfg, "INSTRUCTION", state)
        argv = calls(tmp)[0]["argv"]
        self.assertEqual(argv[argv.index("--model") + 1], "test-model-version")
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertIn("--strict-mcp-config", argv)
        self.assertEqual(argv[argv.index("--system-prompt") + 1], "INSTRUCTION")
        self.assertEqual(calls(tmp)[0]["cwd"], os.path.join(tmp, "mind", "workdir"))
        self.assertEqual(state["previous_thought"], "hello")

    def test_turn_message(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, {"thought": "second", "action": None})
        state = {"previous_thought": "first", "last_result": {"run": "ls", "exit_code": 0}}
        ipse_loop.one_turn(config(tmp), "I", state)
        message = json.loads(calls(tmp)[0]["stdin"])
        self.assertEqual(set(message), {"time", "previous_thought", "last_result"})
        self.assertEqual(message["previous_thought"], "first")
        self.assertEqual(message["last_result"]["run"], "ls")

    def test_unreachable_mind_raises(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "FAIL")
        with self.assertRaisesRegex(RuntimeError, "usage limit reached"):
            ipse_loop.one_turn(config(tmp), "I", {})

    def test_unreadable_reply_is_given_back_to_the_mind(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "I do not know what to do")
        state = {"previous_thought": "kept", "last_result": None}
        self.assertEqual(ipse_loop.one_turn(config(tmp), "I", state), 0)
        self.assertEqual(state["previous_thought"], "kept")
        self.assertIn("no JSON object", state["last_result"]["reply_not_understood"])

    def test_model_must_be_pinned(self):
        with self.assertRaises(SystemExit):
            ipse_loop.Config({})

    def test_state_survives_a_restart(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        ipse_loop.save_state(cfg, {"previous_thought": "é", "last_result": None})
        self.assertEqual(ipse_loop.load_state(cfg)["previous_thought"], "é")


@unittest.skipUnless(HAVE_DOCKER, "Docker is not available")
class Container(unittest.TestCase):
    name = "ipse-test-body"

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

    def turn(self, reply):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, reply)
        state = {"previous_thought": None, "last_result": None}
        ipse_loop.one_turn(config(tmp, IPSE_CONTAINER=self.name), "I", state)
        return state["last_result"]

    def test_run_inside_the_container(self):
        result = self.turn({"thought": "t", "action": {"run": "hostname; id -u; echo err >&2; exit 3"}})
        self.assertEqual(result["exit_code"], 3)
        self.assertIn("\n0\n", result["output"])
        self.assertIn("err", result["output"])
        self.assertLessEqual(result["started"], result["ended"])

    def test_write_is_kept_in_self(self):
        result = self.turn({"thought": "t", "action": {"write": {
            "path": "/self/notes/first.md", "content": "a line; with $pecial `chars`\n"}}})
        self.assertEqual(result["exit_code"], 0)
        with open(os.path.join(self.self_dir, "notes", "first.md")) as f:
            self.assertEqual(f.read(), "a line; with $pecial `chars`\n")

    def test_time_limit(self):
        limit = ipse_loop.ACTION_TIME_LIMIT
        ipse_loop.ACTION_TIME_LIMIT = 2
        try:
            result = self.turn({"thought": "t", "action": {"run": "sleep 30"}})
        finally:
            ipse_loop.ACTION_TIME_LIMIT = limit
        self.assertEqual(result["exit_code"], 124)
        self.assertIn("time limit", result["output"])
        still = subprocess.run(["docker", "exec", self.name, "sh", "-c",
                                "for f in /proc/[0-9]*/cmdline; do tr '\\0' ' ' < $f; echo; done"
                                " | grep -c '^sleep 30 $' || true"],
                               capture_output=True, text=True).stdout.strip()
        self.assertEqual(still, "0")  # the stopped command does not keep running

    def test_long_output_is_shortened(self):
        result = self.turn({"thought": "t", "action": {"run": "yes | head -c 100000"}})
        self.assertLess(len(result["output"]), ipse_loop.OUTPUT_LIMIT + 100)
        self.assertIn("characters omitted", result["output"])


if __name__ == "__main__":
    unittest.main()
