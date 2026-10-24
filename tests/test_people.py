"""Unit tests for skills/personal-crm/scripts/people.py."""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "personal-crm", "scripts"))
import people  # noqa: E402

TODAY = "2026-10-23"


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def person(self, slug, text):
        with open(os.path.join(self.dir, slug + ".md"), "w", encoding="utf-8") as fh:
            fh.write(text)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = people.main(["--dir", self.dir, "--today", TODAY] + list(argv))
        return code, out.getvalue(), err.getvalue()

    def read(self, slug):
        with open(os.path.join(self.dir, slug + ".md"), encoding="utf-8") as fh:
            return fh.read()


class TestCadence(unittest.TestCase):
    def test_words(self):
        self.assertEqual(people.cadence_days("monthly"), 30)
        self.assertEqual(people.cadence_days("Every 2 weeks"), 14)
        self.assertEqual(people.cadence_days("quarterly (she's busy)"), 91)
        self.assertEqual(people.cadence_days("every 10 days"), 10)
        self.assertEqual(people.cadence_days("every 3 weeks"), 21)
        self.assertEqual(people.cadence_days(""), 30)
        self.assertIsNone(people.cadence_days("paused"))

    def test_bad(self):
        with self.assertRaises(people.PeopleError):
            people.cadence_days("whenever")

    def test_slug(self):
        self.assertEqual(people.slugify("Dana Kim-Lee"), "dana-kim-lee")
        with self.assertRaises(people.PeopleError):
            people.slugify("!!!")


class TestFolder(unittest.TestCase):
    def test_walks_up(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "founder", "people"))
            want = os.path.join(d, "founder", "people")
            for cwd in (d, os.path.join(d, "founder"), want):
                self.assertEqual(people.people_dir(env={}, cwd=cwd, home="/h"), want)
            self.assertEqual(people.people_dir(env={}, cwd="/", home="/h"),
                             "/h/.founder/people")
            self.assertEqual(people.people_dir(env={"FOUNDER_HOME": "/x"}, cwd=d, home="/h"),
                             "/x/people")
        finally:
            shutil.rmtree(d)


class TestDue(Base):
    def setUp(self):
        super().setUp()
        self.person("dana-kim", "# Dana Kim\nhow we know each other: cohort\ncadence: monthly\n"
                    "last contact: 2026-09-10\ncares about: thesis\ncoming up: defense 2026-11-12\n\n"
                    "## Log\n- 2026-09-10 coffee\n")
        self.person("omar", "# Omar Haddad\ncadence: every 2 weeks\nlast contact: 2026-10-01\n")
        self.person("lee", "# Lee\ncadence: quarterly\nlast contact: 2026-09-01\n")
        self.person("paused", "# Pat\ncadence: paused\nlast contact: 2025-01-01\n")
        self.person("new", "# Newcomer\ncadence: monthly\nlast contact:\n")

    def test_due_order_and_limit(self):
        code, out, _ = self.run_cli("due", "--json", "--limit", "0")
        data = json.loads(out)
        names = [r["name"] for r in data["shown"]]
        # Omar: 22 days since, cadence 14 -> 8 over. Dana: 43 since, 30 -> 13 over.
        self.assertEqual(names, ["Dana Kim", "Omar Haddad", "Newcomer"])
        self.assertEqual(data["due_total"], 3)
        code, out, _ = self.run_cli("due", "--limit", "1")
        self.assertIn("3 due, showing 1", out)
        self.assertIn("Dana Kim", out)
        self.assertIn("coming up: defense 2026-11-12", out)

    def test_news_soon_goes_first(self):
        self.person("priya", "# Priya Nair\ncadence: every 2 weeks\nlast contact: 2026-10-08\n"
                    "coming up: talk at a meetup 2026-10-29\n")
        code, out, _ = self.run_cli("due", "--json", "--limit", "0")
        shown = json.loads(out)["shown"]
        self.assertEqual(shown[0]["name"], "Priya Nair")
        self.assertEqual(shown[0]["coming_up_in_days"], 6)
        # Dana's defense is 20 days out, so she is ranked by overdue days as before
        self.assertIsNone([r for r in shown if r["name"] == "Dana Kim"][0]["coming_up_in_days"])
        code, out, _ = self.run_cli("due")
        self.assertIn("(in 6 days)", out)

    def test_log_entries_count_as_contact(self):
        self.person("omar", "# Omar Haddad\ncadence: every 2 weeks\nlast contact: 2026-10-01\n\n"
                    "## Log\n- 2026-10-20 texted about the market\n")
        code, out, _ = self.run_cli("due", "--json", "--limit", "0")
        names = [r["name"] for r in json.loads(out)["shown"]]
        self.assertNotIn("Omar Haddad", names)

    def test_list(self):
        code, out, _ = self.run_cli("list")
        self.assertIn("Pat", out)
        self.assertIn("paused", out)
        self.assertIn("never logged", out)

    def test_empty_folder(self):
        shutil.rmtree(self.dir)
        os.makedirs(self.dir)
        code, out, _ = self.run_cli("due")
        self.assertIn("nobody is due", out)


class TestLogAdd(Base):
    def test_log_updates_last_contact_and_appends(self):
        self.person("dana-kim", "# Dana Kim\ncadence: monthly\nlast contact: 2026-09-10\n"
                    "cares about: thesis\n\n## Log\n- 2026-09-10 coffee\n\n## Later\nx\n")
        code, out, err = self.run_cli("log", "dana", "--note", "sent a note about her defense")
        self.assertEqual(code, 0, err)
        text = self.read("dana-kim")
        self.assertIn("last contact: 2026-10-23", text)
        self.assertIn("- 2026-09-10 coffee\n- 2026-10-23 sent a note about her defense\n", text)
        self.assertIn("## Later\nx", text)

    def test_backdated_log_keeps_newest(self):
        self.person("omar", "# Omar\nlast contact: 2026-10-20\n")
        self.run_cli("log", "omar", "--date", "2026-10-01", "--note", "call")
        text = self.read("omar")
        self.assertIn("last contact: 2026-10-20", text)
        self.assertIn("## Log\n- 2026-10-01 call", text)

    def test_log_future_refused(self):
        self.person("omar", "# Omar\n")
        code, _, err = self.run_cli("log", "omar", "--date", "2026-12-01")
        self.assertEqual(code, 1)
        self.assertIn("future", err)

    def test_log_unknown_and_ambiguous(self):
        self.person("dana-kim", "# Dana Kim\n")
        self.person("dana-lee", "# Dana Lee\n")
        code, _, err = self.run_cli("log", "zed")
        self.assertIn("no person", err)
        code, _, err = self.run_cli("log", "dana")
        self.assertIn("more than one", err)
        code, out, _ = self.run_cli("log", "dana", "lee")
        self.assertEqual(code, 0)

    def test_add(self):
        code, out, err = self.run_cli("add", "Rami", "Saleh", "--how", "met at demo day",
                                      "--cadence", "quarterly", "--last", "2026-10-15",
                                      "--note", "demo day chat")
        self.assertEqual(code, 0, err)
        text = self.read("rami-saleh")
        self.assertIn("# Rami Saleh", text)
        self.assertIn("cadence: quarterly", text)
        self.assertIn("- 2026-10-15 demo day chat", text)
        code, _, err = self.run_cli("add", "Rami", "Saleh")
        self.assertIn("already exists", err)

    def test_add_bad_cadence(self):
        code, _, err = self.run_cli("add", "X", "--cadence", "whenever")
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "x.md")))


if __name__ == "__main__":
    unittest.main()
