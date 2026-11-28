"""Tests of the loop and of the body's tools. Nothing contacts Anthropic.

The mind is replaced by a stand-in (fake_claude.py) that starts the body's
tool server as the official tool does. Docker is replaced by a stand-in
(fake_docker.py) that runs the commands on this machine, in a folder that
stands for /self. What the loop keeps of the mind goes to a throwaway folder. The tests of the class Container need Docker and start a
throwaway container instead.
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fixed"))
import daniel_body  # noqa: E402
import daniel_loop  # noqa: E402
import daniel_memory  # noqa: E402

HAVE_DOCKER = shutil.which("docker") and subprocess.run(
    ["docker", "info"], capture_output=True).returncode == 0
FAKE_DOCKER = os.path.join(HERE, "fake_docker.py")


def fake_body(tmp):
    """Make the folder that stands for /self when Docker is replaced. Return its path."""
    home = os.path.join(tmp, "self")
    os.makedirs(home, exist_ok=True)
    os.environ["FAKE_DOCKER_SELF"] = home
    os.environ["DANIEL_STATE_DIR"] = os.path.join(tmp, "mind")  # for the body's tools called directly
    return home


def text_of(content):
    return "".join(block["text"] for block in content if block["type"] == "text")


def config(tmp, **extra):
    env = {
        "DANIEL_MODEL": "test-model-version",
        "DANIEL_STATE_DIR": os.path.join(tmp, "mind"),
        "DANIEL_CLAUDE": os.path.join(HERE, "fake_claude.py"),
        "DANIEL_DOCKER": FAKE_DOCKER,
    }
    env.update(extra)
    fake_body(tmp)
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


def received(tmp):
    """The message given to the mind at each waking, in order."""
    return [call["stdin"] for call in calls(tmp)]


def put(folder, name, content, program=False):
    path = os.path.join(folder, name)
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, 0o755 if program else 0o644)


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
        self.assertEqual(servers["body"]["env"]["DANIEL_STATE_DIR"], os.path.join(tmp, "mind"))
        self.assertEqual(argv[argv.index("--allowedTools") + 1],
                         "mcp__body__run,mcp__body__write,mcp__body__remember,mcp__body__recall")
        self.assertEqual(argv[argv.index("--system-prompt") + 1], "INSTRUCTION")
        self.assertEqual(os.path.realpath(calls(tmp)[0]["cwd"]),
                         os.path.realpath(os.path.join(tmp, "mind", "workdir")))

    def test_the_official_tool_is_asked_to_summarise_the_thread_of_a_long_waking(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "hello")
        daniel_loop.one_waking(config(tmp), "INSTRUCTION", {})
        argv = calls(tmp)[0]["argv"]
        self.assertEqual(argv[argv.index("--autocompact") + 1], "200000")

    def test_last_words_are_given_back(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "first words", "second words")
        state = {}
        daniel_loop.one_waking(config(tmp), "I", state)
        daniel_loop.one_waking(config(tmp), "I", state)
        self.assertEqual(received(tmp), ["Begin.", "Your last words:\nfirst words"])
        self.assertEqual(state["last_words"], "second words")

    def test_unreachable_mind_raises_and_keeps_the_state(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, "FAIL")
        state = {"last_words": "kept"}
        with self.assertRaisesRegex(RuntimeError, "usage limit reached"):
            daniel_loop.one_waking(config(tmp), "I", state)
        self.assertEqual(state["last_words"], "kept")

    def test_a_waking_cut_at_its_time_limit_is_told_to_the_mind_at_the_next_one(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        put(os.environ["FAKE_DOCKER_SELF"], "wake", "#!/bin/sh\necho an event\n", program=True)
        fake_mind(tmp, "HANG", "ok")
        state = {"last_words": "words from an earlier waking"}
        limit = daniel_loop.SESSION_TIME_LIMIT
        daniel_loop.SESSION_TIME_LIMIT = 1
        try:
            daniel_loop.one_waking(cfg, "I", state)  # the mind does not stop: the waking is cut
        finally:
            daniel_loop.SESSION_TIME_LIMIT = limit
        os.remove(os.path.join(os.environ["FAKE_DOCKER_SELF"], "wake"))
        daniel_loop.one_waking(cfg, "I", state)
        after = received(tmp)[1]
        self.assertIn("cut after 1 seconds", after)
        # neither the words of an older waking nor an event already given are passed off as new
        self.assertNotIn("words from an earlier waking", after)
        self.assertNotIn("an event", after)

    def test_model_must_be_pinned(self):
        with self.assertRaises(SystemExit):
            daniel_loop.Config({})

    def test_state_survives_a_restart(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        daniel_loop.save_state(cfg, {"last_words": "é"})
        self.assertEqual(daniel_loop.load_state(cfg)["last_words"], "é")


class Memory(unittest.TestCase):
    """What the mind remembers, and what it has just done, come back at the next waking."""

    def test_what_the_mind_remembers_is_given_back_at_each_waking_after_its_last_words(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        fake_mind(tmp, {"calls": [{"name": "remember", "arguments": {
            "name": "left side", "text": "My left side is slower."}}], "final": "I rest."},
            "I rest again.", "ok")
        state = {}
        for _ in range(3):
            daniel_loop.one_waking(cfg, "I", state)
        self.assertEqual(calls(tmp)[0]["results"],
                         [{"content": [{"type": "text", "text": "kept"}], "isError": False}])
        back = ("Your latest actions:\nremember: left side\n\n"
                "Your memories, the strongest first:\n[left side]\nMy left side is slower.")
        self.assertEqual(received(tmp), ["Begin.", "Your last words:\nI rest.\n\n" + back,
                                         "Your last words:\nI rest again.\n\n" + back])

    def test_the_mind_finds_a_memory_again_by_its_words(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        daniel_memory.remember(cfg.state_dir, "left side", "My left side is slower.")
        daniel_memory.remember(cfg.state_dir, "noise", "A hum comes back every evening.")
        fake_mind(tmp, {"calls": [{"name": "recall", "arguments": {"about": "which side is slower?"}}],
                        "final": "ok"})
        daniel_loop.one_waking(cfg, "I", {})
        self.assertEqual(calls(tmp)[0]["results"], [{"content": [
            {"type": "text", "text": "[left side]\nMy left side is slower."}], "isError": False}])

    def test_what_the_mind_has_just_done_is_given_back_with_its_outcome(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        fake_mind(tmp, {"calls": [
            {"name": "run", "arguments": {"command": "echo hello; exit 3"}},
            {"name": "write", "arguments": {"path": "/self/notes", "content": "a note\n"}},
        ], "final": "done"}, "ok")
        state = {}
        daniel_loop.one_waking(cfg, "I", state)
        daniel_loop.one_waking(cfg, "I", state)
        self.assertEqual(received(tmp)[1], "Your last words:\ndone\n\nYour latest actions:\n"
                         "run: echo hello; exit 3 [exit code 3]\nwrite: /self/notes [exit code 0]")

    def test_the_latest_actions_come_back_even_when_the_waking_was_cut(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        daniel_memory.note(cfg.state_dir, "run: ls /dev", "[exit code 0]")
        fake_mind(tmp, "HANG", "ok")
        limit, daniel_loop.SESSION_TIME_LIMIT = daniel_loop.SESSION_TIME_LIMIT, 1
        self.addCleanup(setattr, daniel_loop, "SESSION_TIME_LIMIT", limit)
        state = {}
        daniel_loop.one_waking(cfg, "I", state)
        daniel_loop.one_waking(cfg, "I", state)
        self.assertIn("\n\nYour latest actions:\nrun: ls /dev [exit code 0]", received(tmp)[1])

    def test_doing_what_a_memory_names_makes_it_stronger(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        daniel_memory.remember(cfg.state_dir, "eye", "What /self/eye gives is a picture of the front.",
                               now=time.time() - 3600)
        fake_mind(tmp, {"calls": [{"name": "run", "arguments": {"command": "cat /self/eye"}}], "final": "ok"})
        daniel_loop.one_waking(cfg, "I", {})
        self.assertEqual(len(daniel_memory.load(cfg.state_dir)["eye"]["uses"]), 2)

    def test_memories_that_cannot_be_read_are_reported_to_the_mind(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        os.makedirs(cfg.state_dir)
        put(cfg.state_dir, "memories.json", "{ this is not what the loop wrote")
        fake_mind(tmp, {"calls": [
            {"name": "remember", "arguments": {"name": "left side", "text": "My left side is slower."}},
            {"name": "run", "arguments": {"command": "echo hello"}},
        ], "final": "ok"})
        daniel_loop.one_waking(cfg, "I", {})
        self.assertIn("Your memories, the strongest first:\n[could not be read: ", received(tmp)[0])
        kept, ran = calls(tmp)[0]["results"]
        self.assertTrue(kept["isError"])
        self.assertIn("[your memories could not be reached: ", kept["content"][0]["text"])
        self.assertFalse(ran["isError"])
        self.assertIn("hello\n\n[exit code 0]\n[your memories could not be reached: ", ran["content"][0]["text"])


class Waiting(unittest.TestCase):
    """Between two wakings, the loop runs the program that Daniel has written, if any."""

    def test_what_the_waking_program_prints_is_given_to_the_mind(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        put(os.environ["FAKE_DOCKER_SELF"], "wake", "#!/bin/sh\necho 'someone said: come here'\n"
            "echo 'and a warning' >&2\nexit 3\n", program=True)
        fake_mind(tmp, "ok")
        daniel_loop.one_waking(cfg, "I", {})
        self.assertEqual(received(tmp), [
            "Printed by /self/wake:\nsomeone said: come here\nand a warning\n[exit code 3]"])

    def test_what_was_printed_is_kept_until_the_mind_has_received_it(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        home = os.environ["FAKE_DOCKER_SELF"]
        put(home, "wake", '#!/bin/sh\ncd "$(dirname "$0")"\nn=$(($(cat count 2>/dev/null || echo 0) + 1))\n'
            'echo $n > count\necho "event $n"\n', program=True)
        fake_mind(tmp, "FAIL", "heard", "heard")
        with self.assertRaises(RuntimeError):       # the mind cannot be reached
            daniel_loop.one_waking(cfg, "I", {})
        state = daniel_loop.load_state(cfg)          # the loop is restarted meanwhile
        daniel_loop.one_waking(cfg, "I", state)
        with open(os.path.join(home, "count")) as f:
            self.assertEqual(f.read().strip(), "1")  # the program was not run a second time
        daniel_loop.one_waking(cfg, "I", state)
        event_1 = "Printed by /self/wake:\nevent 1\n[exit code 0]"
        self.assertEqual(received(tmp), [event_1, event_1, "Your last words:\nheard\n\n"
                                         "Printed by /self/wake:\nevent 2\n[exit code 0]"])

    def test_only_the_end_of_a_very_long_output_is_given(self):
        tmp = tempfile.mkdtemp()
        cfg = config(tmp)
        put(os.environ["FAKE_DOCKER_SELF"], "wake", "#!/bin/sh\necho THE START\n"
            "yes | head -c 200000\necho THE END\n", program=True)
        fake_mind(tmp, "ok")
        daniel_loop.one_waking(cfg, "I", {})
        message = received(tmp)[0]
        self.assertNotIn("THE START", message)
        self.assertIn("THE END\n[exit code 0]", message)
        self.assertIn("omitted", message)
        self.assertLess(len(message), 16200)

    def test_the_mind_is_not_woken_while_the_body_cannot_be_reached(self):
        for docker in ["false", "/nonexistent/docker"]:
            tmp = tempfile.mkdtemp()
            fake_mind(tmp, "ok")
            with self.assertRaisesRegex(RuntimeError, "container"):
                daniel_loop.one_waking(config(tmp, DANIEL_DOCKER=docker), "I", {})
            self.assertFalse(os.path.exists(os.path.join(tmp, "record")))


class Feeling(unittest.TestCase):
    """What Daniel's own program prints is what it feels: after each action, and when it wakes."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = fake_body(self.tmp)

    def act(self, tool="run", **arguments):
        return daniel_body.act(tool, arguments or {"command": "echo done"}, docker=FAKE_DOCKER)[0]

    def test_what_the_program_prints_follows_the_result_of_each_action(self):
        put(self.home, "feel", "#!/bin/sh\necho 'reserve: 12 of 100'\n", program=True)
        ran = self.act()
        self.assertEqual([block["text"] for block in ran], ["done\n\n[exit code 0]", "You feel:\nreserve: 12 of 100"])
        wrote = self.act("write", path="/self/notes", content="a note")
        self.assertEqual(wrote[-1]["text"], "You feel:\nreserve: 12 of 100")

    def test_nothing_is_felt_without_a_program_or_when_it_prints_nothing(self):
        self.assertEqual(len(self.act()), 1)
        put(self.home, "feel", "#!/bin/sh\nexit 0\n", program=True)
        self.assertEqual(len(self.act()), 1)

    def test_a_program_that_fails_is_reported_with_what_it_printed(self):
        put(self.home, "feel", "#!/bin/sh\necho 'no reading' >&2\nexit 3\n", program=True)
        self.assertEqual(self.act()[-1]["text"], "You feel:\nno reading\n[exit code 3]")

    def test_what_it_prints_beyond_the_limit_is_cut_and_the_mind_is_told(self):
        put(self.home, "feel", "#!/bin/sh\nhead -c 5000 /dev/zero | tr '\\0' F\n", program=True)
        felt = self.act()[-1]["text"]
        self.assertEqual(felt.count("F"), daniel_body.FEEL_LIMIT)
        self.assertIn(f"only the first {daniel_body.FEEL_LIMIT} characters", felt)

    def test_keeping_and_recalling_memories_are_not_followed_by_a_feeling(self):
        put(self.home, "feel", "#!/bin/sh\necho 'reserve: 12 of 100'\n", program=True)
        self.assertEqual(len(self.act("remember", name="left side", text="slower")), 1)
        self.assertEqual(len(self.act("recall", about="side")), 1)

    def test_what_daniel_feels_is_given_last_when_it_wakes(self):
        put(self.home, "feel", "#!/bin/sh\necho 'reserve: 12 of 100'\n", program=True)
        put(self.home, "wake", "#!/bin/sh\necho 'a sound'\n", program=True)
        fake_mind(self.tmp, "ok")
        daniel_loop.one_waking(config(self.tmp), "I", {})
        self.assertEqual(received(self.tmp), [
            "Printed by /self/wake:\na sound\n[exit code 0]\n\nYou feel:\nreserve: 12 of 100"])

    def test_the_mind_is_not_woken_without_its_body_even_when_an_output_awaits_it(self):
        fake_mind(self.tmp, "ok")
        state = {"last_words": "kept", "printed": "heard\n[exit code 0]"}
        with self.assertRaisesRegex(RuntimeError, "container"):
            daniel_loop.one_waking(config(self.tmp, DANIEL_DOCKER="false"), "I", state)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "record")))
        self.assertEqual(state, {"last_words": "kept", "printed": "heard\n[exit code 0]"})


class BodyServer(unittest.TestCase):
    def test_protocol(self):
        self.assertEqual(daniel_body.handle({"method": "notifications/initialized"}), None)
        init = daniel_body.handle({"id": 1, "method": "initialize",
                                 "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(init["result"]["protocolVersion"], "2025-06-18")
        tools = daniel_body.handle({"id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["run", "write", "remember", "recall"])
        self.assertIn("error", daniel_body.handle({"id": 3, "method": "resources/list"}))

    def test_invalid_calls_are_refused_without_acting(self):
        for name, arguments in [("run", {}), ("run", {"command": " "}), ("write", {"path": "x"}),
                                ("remember", {"name": "x"}), ("remember", {"name": " ", "text": "t"}),
                                ("recall", {}), ("recall", {"about": " "}), ("delete", {"path": "x"})]:
            content, is_error = daniel_body.act(name, arguments, docker="/nonexistent")
            self.assertTrue(is_error)
            self.assertIn("invalid call", text_of(content))


class Perception(unittest.TestCase):
    """What a command prints reaches the mind as text, or as an image when it is one."""

    def setUp(self):
        self.home = fake_body(tempfile.mkdtemp())

    def run_command(self, command):
        return daniel_body.act("run", {"command": command}, docker=FAKE_DOCKER)

    def test_an_image_printed_by_a_command_is_shown_to_the_mind(self):
        pictures = [
            ("image/png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\xff"),
            ("image/jpeg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01"),
            ("image/gif", b"GIF89a\x01\x00\x01\x00\x80\x00"),
            ("image/gif", b"GIF87a\x01\x00\x01\x00\x80\x00"),
            ("image/webp", b"RIFF\x1a\x00\x00\x00WEBPVP8L\x0d\x00"),
        ]
        for kind, data in pictures:
            with open(os.path.join(self.home, "picture"), "wb") as f:
                f.write(data)
            content, is_error = self.run_command("cat /self/picture; echo noted >&2")
            self.assertFalse(is_error)
            self.assertEqual(content[0], {"type": "image", "mimeType": kind,
                                          "data": base64.b64encode(data).decode()})
            self.assertEqual([block["type"] for block in content], ["image", "text"])
            self.assertIn("noted", content[1]["text"])
            self.assertIn("[exit code 0]", content[1]["text"])

    def test_text_that_only_names_an_image_format_stays_text(self):
        content, _ = self.run_command("echo PNG GIF89a RIFF WEBP")
        self.assertEqual([block["type"] for block in content], ["text"])
        self.assertIn("PNG GIF89a RIFF WEBP", content[0]["text"])

    def test_bytes_that_are_neither_text_nor_image_are_still_given_back(self):
        content, is_error = self.run_command("printf '\\377\\376 then text'")
        self.assertFalse(is_error)
        self.assertEqual([block["type"] for block in content], ["text"])
        self.assertIn(" then text", content[0]["text"])

    def test_an_image_too_heavy_to_be_shown_is_announced_with_the_limit(self):
        with open(os.path.join(self.home, "picture"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)  # 40 bytes
        limit = daniel_body.IMAGE_LIMIT
        daniel_body.IMAGE_LIMIT = 39
        try:
            content, _ = self.run_command("cat /self/picture")
        finally:
            daniel_body.IMAGE_LIMIT = limit
        self.assertEqual([block["type"] for block in content], ["text"])
        self.assertIn("40 bytes", content[0]["text"])
        self.assertIn("39 bytes", content[0]["text"])

    def test_the_tool_server_passes_the_image_on(self):
        with open(os.path.join(self.home, "picture"), "wb") as f:
            f.write(b"\xff\xd8\xff\xe0 a picture")
        os.environ["DANIEL_DOCKER"] = FAKE_DOCKER
        try:
            result = daniel_body.handle({"id": 7, "method": "tools/call", "params": {
                "name": "run", "arguments": {"command": "cat /self/picture"}}})["result"]
        finally:
            del os.environ["DANIEL_DOCKER"]
        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["type"], "image")
        self.assertEqual(result["content"][0]["mimeType"], "image/jpeg")


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

    def setUp(self):
        fake_body(tempfile.mkdtemp())  # what the body's tools note goes to a throwaway folder

    def tearDown(self):
        if os.path.exists(os.path.join(self.self_dir, "wake")):
            os.remove(os.path.join(self.self_dir, "wake"))

    def config(self, tmp):
        return config(tmp, DANIEL_CONTAINER=self.name, DANIEL_DOCKER="docker")

    def test_a_waking_acts_inside_the_container_through_the_body_tools(self):
        tmp = tempfile.mkdtemp()
        fake_mind(tmp, {"calls": [
            {"name": "run", "arguments": {"command": "hostname; id -u; echo err >&2; exit 3"}},
            {"name": "write", "arguments": {"path": "/self/notes/first.md",
                                            "content": "a line; with $pecial `chars`\n"}},
        ], "final": "I have written my first note."})
        state = {}
        daniel_loop.one_waking(self.config(tmp), "I", state)
        record = calls(tmp)[0]
        self.assertEqual(record["tools"], ["run", "write", "remember", "recall"])
        ran, wrote = record["results"]
        self.assertTrue(ran["isError"])
        self.assertIn("\n0\n", ran["content"][0]["text"])
        self.assertIn("err", ran["content"][0]["text"])
        self.assertIn("[exit code 3]", ran["content"][0]["text"])
        self.assertFalse(wrote["isError"])
        with open(os.path.join(self.self_dir, "notes", "first.md")) as f:
            self.assertEqual(f.read(), "a line; with $pecial `chars`\n")
        self.assertEqual(state["last_words"], "I have written my first note.")

    def test_the_waking_program_is_that_of_the_container(self):
        tmp = tempfile.mkdtemp()
        put(self.self_dir, "wake", "#!/bin/sh\necho \"heard in $(hostname)\"\n", program=True)
        container = subprocess.run(["docker", "exec", self.name, "hostname"],
                                   capture_output=True, text=True).stdout.strip()
        fake_mind(tmp, "ok")
        daniel_loop.one_waking(self.config(tmp), "I", {})
        self.assertEqual(received(tmp), [f"Printed by /self/wake:\nheard in {container}\n[exit code 0]"])

    def test_a_waking_program_that_cannot_be_run_is_reported_to_the_mind(self):
        tmp = tempfile.mkdtemp()
        put(self.self_dir, "wake", "#!/bin/sh\necho never printed\n")  # not marked as a program
        fake_mind(tmp, "ok")
        daniel_loop.one_waking(self.config(tmp), "I", {})
        message = received(tmp)[0]
        self.assertTrue(message.startswith("Printed by /self/wake:\n"))
        self.assertNotIn("never printed", message)
        self.assertIn("[exit code 126]", message)

    def test_the_wait_has_a_time_limit(self):
        tmp = tempfile.mkdtemp()
        put(self.self_dir, "wake", "#!/bin/sh\necho waiting\nsleep 60\n", program=True)
        fake_mind(tmp, "ok")
        limit = daniel_loop.WAIT_LIMIT
        daniel_loop.WAIT_LIMIT = 2
        try:
            daniel_loop.one_waking(self.config(tmp), "I", {})
        finally:
            daniel_loop.WAIT_LIMIT = limit
        message = received(tmp)[0]
        self.assertIn("waiting", message)
        self.assertIn("time limit of 2 seconds", message)
        self.assertIn("[exit code 124]", message)

    def test_an_image_made_in_the_container_is_shown_to_the_mind(self):
        content, is_error = daniel_body.act(
            "run", {"command": "printf '\\211PNG\\r\\n\\032\\n\\0\\0\\0\\rIHDR' | tee /self/picture >/dev/null"
                               " && cat /self/picture"}, container=self.name)
        self.assertFalse(is_error)
        self.assertEqual(content[0], {"type": "image", "mimeType": "image/png",
                                      "data": base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR").decode()})
        os.remove(os.path.join(self.self_dir, "picture"))

    def test_time_limit(self):
        limit = daniel_body.ACTION_TIME_LIMIT
        daniel_body.ACTION_TIME_LIMIT = 2
        try:
            content, is_error = daniel_body.act("run", {"command": "sleep 30"}, container=self.name)
        finally:
            daniel_body.ACTION_TIME_LIMIT = limit
        self.assertTrue(is_error)
        self.assertIn("time limit", text_of(content))
        still = subprocess.run(["docker", "exec", self.name, "sh", "-c",
                                "for f in /proc/[0-9]*/cmdline; do tr '\\0' ' ' < $f; echo; done"
                                " | grep -c '^sleep 30 $' || true"],
                               capture_output=True, text=True).stdout.strip()
        self.assertEqual(still, "0")  # the stopped command does not keep running

    def test_a_feeling_program_that_lasts_is_stopped_and_the_mind_is_told(self):
        put(self.self_dir, "feel", "#!/bin/sh\necho before\nsleep 30\n", program=True)
        self.addCleanup(os.remove, os.path.join(self.self_dir, "feel"))
        limit, daniel_body.FEEL_TIME_LIMIT = daniel_body.FEEL_TIME_LIMIT, 2
        self.addCleanup(setattr, daniel_body, "FEEL_TIME_LIMIT", limit)
        content, _ = daniel_body.act("run", {"command": "echo done"}, container=self.name)
        self.assertEqual(content[-1]["text"], "You feel:\nbefore\n[stopped after the time limit of 2 seconds]")

    def test_long_output_is_shortened(self):
        content, _ = daniel_body.act("run", {"command": "yes | head -c 100000"}, container=self.name)
        self.assertLess(len(text_of(content)), daniel_body.OUTPUT_LIMIT + 100)
        self.assertIn("characters omitted", text_of(content))


if __name__ == "__main__":
    unittest.main()
