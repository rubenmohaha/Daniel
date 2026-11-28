"""Tests for the page on which a human follows Daniel: what is collected, and what is served."""

import http.client
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fixed"))

import daniel_memory  # noqa: E402
import daniel_view as view  # noqa: E402

NOON = time.mktime((2026, 11, 28, 12, 0, 0, 0, 0, -1))  # noon on the robot's own clock


def stamp(at):
    """A time as the official tool writes it in the exchanges it stores."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(at)) + ".000Z"


def said(at, *parts, usage=None):
    return {"type": "assistant", "timestamp": stamp(at),
            "message": {"content": list(parts), **({"usage": usage} if usage else {})}}


def result(at, ident, *texts):
    return {"type": "user", "timestamp": stamp(at), "message": {"content": [
        {"type": "tool_result", "tool_use_id": ident,
         "content": [{"type": "text", "text": text} for text in texts]}]}}


def run(ident, command):
    return {"type": "tool_use", "id": ident, "name": "mcp__body__run", "input": {"command": command}}


def lines(path, entries):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


class Timeline(unittest.TestCase):
    def test_the_mind_acts_from_a_waking_to_its_end_and_waits_in_between(self):
        notes = [{"at": 100, "what": "woken"}, {"at": 160, "what": "stopped"}, {"at": 400, "what": "woken"}]
        self.assertEqual(view.states(notes, [], now=500, running=True),
                         [[100, 160, "acting"], [160, 400, "waiting"], [400, 500, "acting"]])

    def test_a_waking_that_did_not_reach_the_mind_counts_as_unreachable(self):
        notes = [{"at": 100, "what": "woken"}, {"at": 103, "what": "unreachable"},
                 {"at": 163, "what": "woken"}, {"at": 166, "what": "unreachable"}, {"at": 300, "what": "woken"}]
        self.assertEqual(view.states(notes, [], now=350, running=True),
                         [[100, 300, "unreachable"], [300, 350, "acting"]])

    def test_a_waking_that_was_cut_is_followed_by_a_wait(self):
        notes = [{"at": 100, "what": "woken"}, {"at": 200, "what": "cut"}]
        self.assertEqual(view.states(notes, [], now=260, running=True),
                         [[100, 200, "acting"], [200, 260, "waiting"]])

    def test_before_a_new_start_the_loop_is_known_only_up_to_its_last_sign_of_life(self):
        notes = [{"at": 100, "what": "woken"}, {"at": 900, "what": "started"}, {"at": 950, "what": "woken"}]
        self.assertEqual(view.states(notes, [150, 240], now=1000, running=True),
                         [[100, 240, "acting"], [900, 950, "waiting"], [950, 1000, "acting"]])

    def test_a_loop_that_no_longer_runs_is_shown_up_to_its_last_sign_of_life(self):
        notes = [{"at": 100, "what": "woken"}]
        self.assertEqual(view.states(notes, [130], now=1000, running=False), [[100, 130, "acting"]])

    def test_nothing_is_shown_before_the_first_note(self):
        self.assertEqual(view.states([], [50], now=1000, running=True), [])


class WhatTheJournalSays(unittest.TestCase):
    def test_an_action_is_read_with_its_tool_and_whether_it_succeeded(self):
        actions = view.Actions()
        actions.feed({"at": 10, "did": "run: ls /sys/class [exit code 0]"})
        actions.feed({"at": 20, "did": "run: cat /nothing [exit code 1]"})
        actions.feed({"at": 30, "did": "run: sleep 999 [stopped after the time limit of 300 seconds]"})
        actions.feed({"at": 40, "did": "remember: what-i-am"})
        actions.feed({"at": 50, "did": "write: /self/try.py [exit code 0]"})
        self.assertEqual([(a["tool"], a["text"], a["ok"]) for a in actions.all], [
            ("run", "ls /sys/class", True), ("run", "cat /nothing", False), ("run", "sleep 999", False),
            ("remember", "what-i-am", True), ("write", "/self/try.py", True)])

    def test_the_places_an_action_touches_are_named_as_daniel_writes_them(self):
        self.assertEqual(view.places("cat /sys/class/input/event2/device/name | head; ls /proc; python3 /self/try.py"),
                         ["/sys/class", "/proc", "/self/try.py"])
        self.assertEqual(view.places("echo 3/4 and a//b and http://example.org/x"), [])

    def test_a_program_counts_as_reused_once_it_is_run_after_being_written(self):
        actions = view.Actions()
        actions.feed({"at": 10, "did": "write: /self/try.py [exit code 0]"})
        actions.feed({"at": 20, "did": "run: cat > /opt/tools/say.py <<'EOF' ... [exit code 0]"})
        self.assertEqual(actions.all[-1]["reused"], 0)
        actions.feed({"at": 30, "did": "run: python3 /self/try.py --times 3 [exit code 0]"})
        actions.feed({"at": 40, "did": "run: python3 /opt/tools/say.py hello [exit code 0]"})
        actions.feed({"at": 50, "did": "run: python3 /self/try.py [exit code 0]"})
        self.assertEqual([a["reused"] for a in actions.all], [0, 0, 1, 2, 2])

    def test_an_action_is_new_when_it_touches_a_place_never_touched_before(self):
        actions = view.Actions()
        for at, did in [(10, "run: ls /proc/meminfo"), (20, "run: ls /dev/input"),
                        (30, "run: cat /proc/meminfo /dev/input/event0"), (40, "run: date")]:
            actions.feed({"at": at, "did": did + " [exit code 0]"})
        self.assertEqual([a["new"] for a in actions.all], [True, True, False, None])


class WhatTheExchangesSay(unittest.TestCase):
    def setUp(self):
        self.exchanges = view.Exchanges()

    def feed(self, *entries):
        for entry in entries:
            self.exchanges.feed(entry, "one")

    def test_the_summary_of_its_reasoning_and_its_words_are_its_thoughts(self):
        self.feed(said(100, {"type": "thinking", "thinking": "I'm looking at what is here.", "signature": "x"}),
                  said(101, {"type": "thinking", "thinking": "", "signature": "x"}),
                  said(102, {"type": "text", "text": "I can see my screen."}))
        self.assertEqual([(t["at"], t["text"], t["kind"]) for t in self.exchanges.thoughts],
                         [(100, "I'm looking at what is here.", "reasoning"), (102, "I can see my screen.", "words")])

    def test_the_time_to_decide_runs_from_a_result_to_the_next_action(self):
        self.feed(said(100, run("a", "ls")), result(104, "a", "x\n[exit code 0]"),
                  said(106, {"type": "thinking", "thinking": "Next.", "signature": "x"}),
                  said(111, run("b", "ls /proc")))
        self.assertEqual(self.exchanges.decisions, [(111, 7)])

    def test_the_size_of_the_thread_is_what_each_call_sends_back(self):
        usage = {"input_tokens": 12, "cache_read_input_tokens": 40000, "cache_creation_input_tokens": 900,
                 "output_tokens": 55}
        self.feed(said(100, run("a", "ls"), usage=usage))
        self.assertEqual(self.exchanges.thread, [(100, 40912)])

    def test_what_daniel_felt_is_found_after_an_action_and_at_a_waking(self):
        self.feed({"type": "user", "timestamp": stamp(90),
                   "message": {"content": "Your last words:\nhello\n\nYou feel:\nenergy low: 12 %"}},
                  said(100, run("a", "ls")), result(104, "a", "x\n[exit code 0]", "You feel:\nmotor 3 is hot"))
        self.assertEqual(self.exchanges.feelings, [(90, "energy low: 12 %"), (104, "motor 3 is hot")])

    def test_the_action_under_way_is_the_one_that_has_no_result_yet(self):
        self.feed(said(100, run("a", "ls")), result(104, "a", "x"), said(110, run("b", "sleep 200")))
        self.assertEqual(self.exchanges.doing(since=0), {"at": 110, "tool": "run", "text": "sleep 200"})
        self.assertIsNone(self.exchanges.doing(since=120))  # left by a waking that has ended
        self.feed(result(130, "b", "done"))
        self.assertIsNone(self.exchanges.doing(since=0))

    def test_what_is_not_an_exchange_is_passed_over(self):
        self.feed({"type": "queue-operation"}, {"type": "assistant", "message": {"content": "text"}},
                  {"type": "assistant", "timestamp": "not a time", "message": {"content": [{"type": "text", "text": "x"}]}},
                  [1, 2], "x")
        self.assertEqual(self.exchanges.thoughts, [])


class Collected(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.mind = os.path.join(self.tmp, "mind")
        os.makedirs(self.mind)
        patch = mock.patch.object(view, "active", return_value="active")
        patch.start()
        self.addCleanup(patch.stop)

    def state(self, now=NOON):
        return view.Collector(self.mind).state(now)

    def test_without_any_record_the_state_is_empty_and_says_that_daniel_never_woke(self):
        state = self.state()
        self.assertEqual(state["now"]["state"], "never")
        self.assertEqual(len(state["days"]), 7)
        self.assertEqual(state["thoughts"], [])
        self.assertEqual(state["memories"], {"count": 0, "strongest": []})

    def test_the_state_of_the_moment_and_of_the_day(self):
        lines(os.path.join(self.mind, "wakings"), [
            {"at": NOON - 7200, "what": "started"}, {"at": NOON - 7000, "what": "woken"},
            {"at": NOON - 6400, "what": "stopped"}, {"at": NOON - 600, "what": "woken"}])
        lines(os.path.join(self.mind, "journal"), [
            {"at": NOON - 6900, "did": "run: ls /sys/class [exit code 0]"},
            {"at": NOON - 500, "did": "run: cat /nothing [exit code 1]"},
            {"at": NOON - 40, "did": "write: /self/try.py [exit code 0]"}])
        lines(os.path.join(self.mind, ".claude", "projects", "workdir", "one.jsonl"), [
            said(NOON - 500, {"type": "thinking", "thinking": "I'm reading a file.", "signature": "x"}),
            said(NOON - 499, run("a", "cat /nothing"), usage={"input_tokens": 9000}),
            result(NOON - 497, "a", "[exit code 1]", "You feel:\nsomething is wrong"),
            said(NOON - 490, run("b", "sleep 600"))])
        daniel_memory.remember(self.mind, "what-i-am", "A robot.", now=NOON - 9000)
        daniel_memory.remember(self.mind, "my-programs", "try.py", now=NOON - 100)
        state = self.state()
        now = state["now"]
        self.assertEqual((now["state"], now["since"], now["wakings_today"]), ("acting", NOON - 600, 2))
        self.assertEqual(now["last_action_at"], NOON - 40)
        self.assertEqual(state["doing"], {"at": NOON - 490, "tool": "run", "text": "sleep 600"})
        self.assertEqual(state["thoughts"][-1]["text"], "I'm reading a file.")
        today = state["days"][-1]
        self.assertEqual(today["segments"], [[NOON - 7200, NOON - 7000, "waiting"], [NOON - 7000, NOON - 6400, "acting"],
                                             [NOON - 6400, NOON - 600, "waiting"], [NOON - 600, NOON, "acting"]])
        self.assertEqual(today["acting"], 1200)
        self.assertEqual((state["today"]["actions"], state["today"]["failed"]), (3, 1))
        self.assertEqual(state["today"]["rate_now"], 0.2)  # one action in the last five minutes
        self.assertEqual(state["today"]["failures"], [[NOON - 500, "cat /nothing"]])
        self.assertEqual(state["today"]["feelings"], [[NOON - 497, "something is wrong"]])
        self.assertEqual(state["today"]["decision_median"], 7)
        self.assertEqual(state["today"]["thread_now"], 9000)
        self.assertEqual([name for name, _ in state["memories"]["strongest"]], ["my-programs", "what-i-am"])
        self.assertEqual(state["memories"]["count"], 2)
        self.assertEqual([action["text"] for action in state["actions"]],
                         ["/self/try.py", "cat /nothing", "ls /sys/class"])
        self.assertEqual(state["capacity"]["success"][-1], 67)
        self.assertEqual(state["loop"], "active")

    def test_what_is_added_later_is_read_once(self):
        journal = os.path.join(self.mind, "journal")
        lines(journal, [{"at": NOON - 50, "did": "run: ls [exit code 0]"}])
        collector = view.Collector(self.mind)
        self.assertEqual(collector.state(NOON)["today"]["actions"], 1)
        lines(journal, [{"at": NOON - 20, "did": "run: ls [exit code 0]"}])
        self.assertEqual(collector.state(NOON)["today"]["actions"], 2)
        self.assertEqual(collector.state(NOON)["today"]["actions"], 2)

    def test_a_journal_cut_down_to_its_latest_half_is_not_counted_twice(self):
        journal = os.path.join(self.mind, "journal")
        lines(journal, [{"at": NOON - 50 + n, "did": "run: ls [exit code 0]"} for n in range(4)])
        collector = view.Collector(self.mind)
        self.assertEqual(collector.state(NOON)["today"]["actions"], 4)
        with open(journal) as f:
            kept = f.readlines()[2:]
        daniel_memory.keep(self.mind, "journal", "".join(kept))  # as the loop cuts it down
        lines(journal, [{"at": NOON - 10, "did": "run: ls [exit code 0]"}])
        self.assertEqual(collector.state(NOON)["today"]["actions"], 5)

    def test_lines_that_cannot_be_read_are_passed_over(self):
        with open(os.path.join(self.mind, "journal"), "w") as f:
            f.write('not json\n{"at": "soon", "did": 3}\n' + json.dumps({"at": NOON - 5, "did": "run: ls [exit code 0]"}) + "\n")
        with open(os.path.join(self.mind, "wakings"), "w") as f:
            f.write("{}\n[]\n" + json.dumps({"at": NOON - 9, "what": "woken"}) + "\n")
        with open(os.path.join(self.mind, "memories.json"), "w") as f:
            f.write("{ cut")
        state = self.state()
        self.assertEqual(state["today"]["actions"], 1)
        self.assertEqual(state["now"]["state"], "acting")
        self.assertEqual(state["memories"]["count"], 0)

    def test_the_state_is_written_where_the_page_reads_it_and_can_be_read_by_all(self):
        folder = os.path.join(self.tmp, "view")
        view.write(folder, {"at": 1})
        path = os.path.join(folder, "state.json")
        with open(path) as f:
            self.assertEqual(json.load(f), {"at": 1})
        self.assertEqual(os.stat(path).st_mode & 0o777, 0o644)


class Served(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        with open(os.path.join(self.tmp, "page.html"), "w") as f:
            f.write("<!doctype html><title>Daniel</title>")
        self.server = view.server("127.0.0.1", 0, os.path.join(self.tmp, "page.html"), self.tmp)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def ask(self, path, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=5)
        connection.request(method, path)
        answer = connection.getresponse()
        return answer.status, answer.getheader("Content-Type"), answer.read()

    def test_the_page_is_served(self):
        status, kind, body = self.ask("/")
        self.assertEqual((status, kind), (200, "text/html; charset=utf-8"))
        self.assertIn(b"<title>Daniel</title>", body)

    def test_the_state_is_served_as_the_collector_wrote_it(self):
        view.write(self.tmp, {"at": 5})
        status, kind, body = self.ask("/state.json")
        self.assertEqual((status, kind, json.loads(body)), (200, "application/json", {"at": 5}))

    def test_a_state_not_yet_written_is_announced_as_such(self):
        self.assertEqual(self.ask("/state.json")[0], 503)

    def test_nothing_else_is_served(self):
        with open(os.path.join(self.tmp, "secret"), "w") as f:
            f.write("x")
        for path in ("/secret", "/../secret", "/state.json/../secret", "/page.html", "/?file=secret"):
            self.assertEqual(self.ask(path)[0], 404, path)

    def test_nothing_can_be_sent_to_it(self):
        for method in ("POST", "PUT", "DELETE"):
            self.assertIn(self.ask("/", method)[0], (405, 501), method)


class ThePage(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(HERE, "..", "fixed", "daniel-view.html"), encoding="utf-8") as f:
            self.page = f.read()

    def test_the_page_fetches_nothing_from_outside_the_robot(self):
        self.assertNotRegex(self.page, r"""(?:src|href|url\()\s*=?\s*["'(]?\s*(?:https?:)?//""")

    def test_what_daniel_wrote_is_never_inserted_as_markup(self):
        for word in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
            self.assertNotIn(word, self.page)


if __name__ == "__main__":
    unittest.main()
