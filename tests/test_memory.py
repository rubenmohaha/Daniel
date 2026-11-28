"""Tests of Daniel's memories: what comes back to the mind, and how strongly."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fixed"))
import daniel_memory as memories  # noqa: E402

HOUR, DAY = 3600, 86400
NOW = 1_800_000_000.0


def uses(mind, name):
    memory = memories.load(mind)[name]
    return len(memory["uses"]) + memory.get("earlier", 0)


class Strength(unittest.TestCase):
    """A memory grows stronger each time it is used, and fades with time."""

    def test_what_was_used_lately_comes_back_before_what_was_used_long_ago(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "old", "learnt long ago", now=NOW - 30 * DAY)
        memories.remember(mind, "recent", "learnt today", now=NOW - HOUR)
        text = memories.waking(mind, 10000, now=NOW)
        self.assertLess(text.index("[recent]"), text.index("[old]"))

    def test_what_is_used_often_comes_back_before_what_was_used_once(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "often", "what I do every day", now=NOW - 20 * DAY)
        for day in range(19, 2, -1):
            memories.recall(mind, "every day", now=NOW - day * DAY)
        memories.remember(mind, "once", "what I did a single time", now=NOW - 2 * DAY)
        text = memories.waking(mind, 10000, now=NOW)  # "once" was used last, and yet:
        self.assertLess(text.index("[often]"), text.index("[once]"))

    def test_what_was_just_used_comes_back_before_an_old_habit(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "habit", "what I did every day last month", now=NOW - 40 * DAY)
        for day in range(39, 30, -1):
            memories.recall(mind, "last month", now=NOW - day * DAY)
        memories.remember(mind, "fresh", "what I have just found", now=NOW - 60)
        text = memories.waking(mind, 10000, now=NOW)
        self.assertLess(text.index("[fresh]"), text.index("[habit]"))

    def test_uses_older_than_those_kept_still_count(self):
        mind = tempfile.mkdtemp()
        for n in range(memories.USES_KEPT + 50, 0, -1):
            memories.remember(mind, "worn", "used a great many times", now=NOW - n * HOUR)
        for n in range(memories.USES_KEPT, 0, -1):
            memories.remember(mind, "less worn", "used many times", now=NOW - n * HOUR)
        store = memories.load(mind)
        self.assertEqual(len(store["worn"]["uses"]), memories.USES_KEPT)
        self.assertEqual(store["worn"]["earlier"], 50)
        self.assertGreater(memories.strength(store["worn"], NOW),
                           memories.strength(store["less worn"], NOW))


class Remembering(unittest.TestCase):
    def test_a_memory_is_found_again_by_its_words(self):
        mind = tempfile.mkdtemp()
        said, refused = memories.remember(mind, "left side", "My left side is slower.", now=NOW)
        self.assertFalse(refused)
        memories.remember(mind, "noise", "A hum comes back every evening.", now=NOW)
        found = memories.recall(mind, "slower side", now=NOW)
        self.assertIn("[left side]\nMy left side is slower.", found)
        self.assertNotIn("hum", found)

    def test_the_same_name_replaces_the_memory(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "left  side", "My left side is slower.", now=NOW)
        said, refused = memories.remember(mind, "left side", "My left side is as fast as the right.", now=NOW)
        self.assertFalse(refused)
        self.assertIn("in place", said)
        self.assertEqual(list(memories.load(mind)), ["left side"])
        self.assertNotIn("slower", memories.waking(mind, 10000, now=NOW))

    def test_a_memory_too_long_is_refused_and_the_limit_is_told(self):
        mind = tempfile.mkdtemp()
        said, refused = memories.remember(mind, "everything", "x" * (memories.TEXT_LIMIT + 1), now=NOW)
        self.assertTrue(refused)
        self.assertIn(f"at most {memories.TEXT_LIMIT} characters", said)
        self.assertEqual(memories.load(mind), {})

    def test_a_name_too_long_is_refused_and_the_limit_is_told(self):
        mind = tempfile.mkdtemp()
        said, refused = memories.remember(mind, "n" * (memories.NAME_LIMIT + 1), "text", now=NOW)
        self.assertTrue(refused)
        self.assertIn(f"at most {memories.NAME_LIMIT} characters", said)

    def test_nothing_comes_back_when_no_memory_holds_the_words(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "left side", "My left side is slower.", now=NOW)
        self.assertEqual(memories.recall(mind, "weather", now=NOW), "[nothing comes back]")

    def test_one_recall_gives_a_few_memories_whole_and_names_the_others(self):
        mind = tempfile.mkdtemp()
        for n in range(memories.FOUND + 2):
            memories.remember(mind, f"wheel {n}", f"About the wheel number {n}.", now=NOW - n * HOUR)
        found = memories.recall(mind, "wheel", now=NOW)
        self.assertEqual(found.count("About the wheel"), memories.FOUND)
        self.assertIn(f"By name only: wheel {memories.FOUND}; wheel {memories.FOUND + 1}", found)

    def test_recalling_a_memory_makes_it_stronger(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "sought", "what I keep looking for", now=NOW - 10 * DAY)
        memories.remember(mind, "left alone", "what I never look for", now=NOW - 9 * DAY)
        memories.recall(mind, "looking", now=NOW - HOUR)
        text = memories.waking(mind, 10000, now=NOW)
        self.assertLess(text.index("[sought]"), text.index("[left alone]"))


class Waking(unittest.TestCase):
    def test_nothing_is_given_without_memories(self):
        self.assertIsNone(memories.waking(tempfile.mkdtemp(), 10000, now=NOW))

    def test_the_strongest_come_back_whole_the_next_by_name_and_the_rest_are_counted(self):
        mind = tempfile.mkdtemp()
        for n in range(200):
            memories.remember(mind, f"memory number {n:03}", "t" * 100, now=NOW - n * DAY)
        text = memories.waking(mind, 400, now=NOW)
        self.assertEqual(text.count("t" * 100), 3)  # each takes its name, its text and a blank line
        self.assertTrue(text.startswith("[memory number 000]\n"))
        self.assertIn("\n\nFainter, by name only: memory number 003; memory number 004;", text)
        named = text.split("by name only: ")[1].split("\n")[0].split("; ")
        self.assertGreater(len(named), 50)
        self.assertLessEqual(len("; ".join(named)), memories.NAMES_LIMIT)
        self.assertTrue(text.endswith(f"\n\nAnd {200 - 3 - len(named)} fainter still."))


class Stirred(unittest.TestCase):
    """What Daniel does brings back the memories that speak of it: they grow stronger."""

    def test_acting_on_what_a_memory_names_makes_it_stronger(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "eye", "What /dev/video0 gives is a picture of the front.", now=NOW - 10 * DAY)
        memories.remember(mind, "newer", "Something learnt later and never used.", now=NOW - 9 * DAY)
        for day in range(8, 1, -1):
            memories.stirred(mind, "ffmpeg -y -i /dev/video0 -frames 1 /tmp/now.png", now=NOW - day * DAY)
        text = memories.waking(mind, 10000, now=NOW)
        self.assertLess(text.index("[eye]"), text.index("[newer]"))

    def test_a_file_is_recognised_by_its_name_alone(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "voice", "To be heard: python3 /self/say.py 'the words'.", now=NOW - DAY)
        memories.stirred(mind, "cd /self && python3 say.py hello", now=NOW)
        self.assertEqual(uses(mind, "voice"), 2)

    def test_a_word_that_many_memories_hold_stirs_none(self):
        mind = tempfile.mkdtemp()
        for n in range(memories.RARE + 1):
            memories.remember(mind, f"program {n}", f"python3 runs the program number{n}.", now=NOW - DAY)
        memories.stirred(mind, "python3 --version", now=NOW)
        self.assertEqual([uses(mind, f"program {n}") for n in range(memories.RARE + 1)],
                         [1] * (memories.RARE + 1))

    def test_actions_in_quick_succession_count_once(self):
        mind = tempfile.mkdtemp()
        memories.remember(mind, "eye", "What /dev/video0 gives is a picture.", now=NOW - DAY)
        for second in range(0, memories.SAME_USE, 10):
            memories.stirred(mind, "cat /dev/video0", now=NOW + second)
        self.assertEqual(uses(mind, "eye"), 2)
        memories.stirred(mind, "cat /dev/video0", now=NOW + memories.SAME_USE)
        self.assertEqual(uses(mind, "eye"), 3)


class Journal(unittest.TestCase):
    """What Daniel does is noted, so that its latest actions come back when it wakes."""

    def test_the_latest_actions_are_given_the_most_recent_last(self):
        mind = tempfile.mkdtemp()
        memories.note(mind, "run: ls /dev", "[exit code 0]", now=NOW)
        memories.note(mind, "remember: left side", now=NOW + 1)
        self.assertEqual(memories.latest(mind, 1000), "run: ls /dev [exit code 0]\nremember: left side")

    def test_nothing_is_given_before_the_first_action(self):
        self.assertIsNone(memories.latest(tempfile.mkdtemp(), 1000))

    def test_only_the_latest_actions_that_fit_are_given_and_the_mind_is_told(self):
        mind = tempfile.mkdtemp()
        for n in range(100):
            memories.note(mind, f"run: step {n:02}", "[exit code 0]", now=NOW + n)
        self.assertEqual(memories.latest(mind, 100), "[... earlier actions are omitted ...]\n"
                         + "\n".join(f"run: step {n} [exit code 0]" for n in (97, 98, 99)))

    def test_an_action_is_noted_on_one_line_and_shortened_but_its_outcome_is_kept(self):
        mind = tempfile.mkdtemp()
        memories.note(mind, "run: cat > /self/x <<END\n" + "y" * 1000 + "\nEND", "[exit code 0]", now=NOW)
        memories.note(mind, "run: echo " + "z" * 1000, "[exit code 1]", now=NOW)
        first, second = memories.latest(mind, 5000).split("\n")
        self.assertEqual(first, "run: cat > /self/x <<END ... [exit code 0]")
        self.assertEqual(second, "run: echo " + "z" * (memories.ACTION_LIMIT - 10) + " ... [exit code 1]")

    def test_the_journal_does_not_grow_without_bound(self):
        mind = tempfile.mkdtemp()
        room, memories.JOURNAL_ROOM = memories.JOURNAL_ROOM, 5000
        self.addCleanup(setattr, memories, "JOURNAL_ROOM", room)
        for n in range(600):
            memories.note(mind, f"run: step {n}", "[exit code 0]", now=NOW + n)
        self.assertLess(os.path.getsize(os.path.join(mind, "journal")), 2 * 5000 + 200)
        self.assertTrue(memories.latest(mind, 1000).endswith("run: step 599 [exit code 0]"))


if __name__ == "__main__":
    unittest.main()
