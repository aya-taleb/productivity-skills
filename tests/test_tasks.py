"""Unit tests for skills/tasks/scripts/tasks.py. Run: python3 -I -m unittest discover -s tests -v"""
import contextlib
import datetime as dt
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "tasks", "scripts"))
import tasks  # noqa: E402

TODAY = "2026-10-23"  # a Friday


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "tasks.md")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tasks.main(["--file", self.path, "--today", TODAY] + list(argv))
        return code, out.getvalue(), err.getvalue()

    def text(self):
        with open(self.path, encoding="utf-8") as fh:
            return fh.read()

    def write(self, text):
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(text)


class TestSave(Base):
    def test_save_into_founder_folder(self):
        src = os.path.join(self.dir, "draft.md")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write("# Week\n")
        code, out, _ = self.run_cli("save", "weekly/2026-W43.md", "--from", src)
        self.assertEqual(code, 0)
        dest = os.path.join(self.dir, "weekly", "2026-W43.md")
        with open(dest, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "# Week\n")
        code, _, err = self.run_cli("save", "weekly/2026-W43.md", "--from", src)
        self.assertEqual(code, 1)
        self.assertIn("--replace", err)
        code, _, _ = self.run_cli("save", "weekly/2026-W43.md", "--from", src, "--replace")
        self.assertEqual(code, 0)

    def test_save_refuses_paths_outside(self):
        src = os.path.join(self.dir, "draft.md")
        with open(src, "w", encoding="utf-8") as fh:
            fh.write("x")
        code, _, _ = self.run_cli("save", "../escape.md", "--from", src)
        self.assertEqual(code, 1)


class TestDates(unittest.TestCase):
    today = dt.date(2026, 10, 23)  # Friday

    def test_words(self):
        p = tasks.parse_date
        self.assertEqual(p("today", self.today), self.today)
        self.assertEqual(p("tomorrow", self.today), dt.date(2026, 10, 24))
        self.assertEqual(p("+3d", self.today), dt.date(2026, 10, 26))
        self.assertEqual(p("+2w", self.today), dt.date(2026, 11, 6))
        self.assertEqual(p("2026-11-01", self.today), dt.date(2026, 11, 1))
        self.assertIsNone(p("none", self.today))

    def test_weekday_is_next_one(self):
        self.assertEqual(tasks.parse_date("monday", self.today), dt.date(2026, 10, 26))
        self.assertEqual(tasks.parse_date("fri", self.today), dt.date(2026, 10, 30))

    def test_bad_date(self):
        with self.assertRaises(tasks.TaskError):
            tasks.parse_date("soonish", self.today)
        with self.assertRaises(tasks.TaskError):
            tasks.parse_date("2026-02-30", self.today)


class TestPaths(unittest.TestCase):
    def test_env_wins(self):
        p = tasks.tasks_path(env={"FOUNDER_HOME": "/x"}, cwd="/c", home="/h")
        self.assertEqual(p, "/x/tasks.md")

    def test_default_home(self):
        p = tasks.tasks_path(env={}, cwd="/nonexistent", home="/h")
        self.assertEqual(p, "/h/.founder/tasks.md")

    def test_local_founder_folder_only_with_markers(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "founder"))
            open(os.path.join(d, "founder", "market.md"), "w").close()
            self.assertEqual(tasks.tasks_path(env={}, cwd=d, home="/h"),
                             "/h/.founder/tasks.md")
            os.makedirs(os.path.join(d, "founder", "people"))
            self.assertEqual(tasks.tasks_path(env={}, cwd=d, home="/h"),
                             os.path.join(d, "founder", "tasks.md"))
        finally:
            shutil.rmtree(d)

    def test_found_from_inside_founder_or_below(self):
        d = tempfile.mkdtemp()
        try:
            f = os.path.join(d, "founder")
            os.makedirs(os.path.join(f, "businesses"))
            want = os.path.join(f, "tasks.md")
            self.assertEqual(tasks.tasks_path(env={}, cwd=f, home="/h"), want)
            os.makedirs(os.path.join(d, "src", "deep"))
            self.assertEqual(tasks.tasks_path(env={}, cwd=os.path.join(d, "src", "deep"),
                                              home="/h"), want)
        finally:
            shutil.rmtree(d)

    def test_home_founder_not_mistaken_for_local(self):
        d = tempfile.mkdtemp()
        try:
            hf = os.path.join(d, ".founder")
            os.makedirs(hf)
            open(os.path.join(hf, "tasks.md"), "w").close()
            self.assertEqual(tasks.tasks_path(env={}, cwd=hf, home=d), os.path.join(hf, "tasks.md"))
        finally:
            shutil.rmtree(d)

    def test_read_businesses(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "businesses"))
            with open(os.path.join(d, "businesses", "street-lunch.md"), "w") as fh:
                fh.write("# Curbside Lunch Club\n\npitch: lunch\n")
            with open(os.path.join(d, "businesses", "app.md"), "w") as fh:
                fh.write("name: Tiny Tale Studio\n")
            with open(os.path.join(d, "active"), "w") as fh:
                fh.write("app\n")
            info = tasks.read_businesses(d, cwd=d, home="/nonexistent")
            self.assertEqual([b["slug"] for b in info["businesses"]], ["app", "street-lunch"])
            self.assertEqual(info["businesses"][1]["name"], "Curbside Lunch Club")
            self.assertEqual(info["businesses"][0]["name"], "Tiny Tale Studio")
            self.assertEqual(info["active"], "app")
        finally:
            shutil.rmtree(d)

    def test_no_businesses_means_empty(self):
        d = tempfile.mkdtemp()
        try:
            info = tasks.read_businesses(d, cwd=d, home=d)
            self.assertEqual(info["businesses"], [])
            self.assertIsNone(info["active"])
        finally:
            shutil.rmtree(d)


class TestAddList(Base):
    def test_init_creates_template(self):
        code, out, _ = self.run_cli("init")
        self.assertEqual(code, 0)
        self.assertIn("## Active", self.text())
        self.assertIn("## Done", self.text())
        code, out, _ = self.run_cli("init")
        self.assertIn("already there", out)

    def test_add_creates_file_and_tags(self):
        code, out, _ = self.run_cli("add", "Call", "the", "printer", "--biz", "Street-Lunch",
                                    "--due", "monday", "--note", "ask about menus")
        self.assertEqual(code, 0, out)
        self.assertIn("added [1] Call the printer", out)
        line = [l for l in self.text().splitlines() if l.startswith("- [ ]")][0]
        self.assertEqual(line, "- [ ] **Call the printer** #street-lunch due:2026-10-26 "
                               "added:2026-10-23 - ask about menus")

    def test_add_waiting_gets_since(self):
        self.run_cli("add", "Logo from Sam", "--biz", "app", "--section", "waiting")
        t = self.text()
        self.assertIn("since:2026-10-23", t)
        self.assertLess(t.index("## Waiting on"), t.index("Logo from Sam"))
        self.assertLess(t.index("Logo from Sam"), t.index("## Someday"))

    def test_bad_tag(self):
        code, _, err = self.run_cli("add", "x", "--biz", "two words")
        self.assertEqual(code, 1)
        self.assertIn("business tags", err)

    def test_cannot_add_to_done(self):
        code, _, err = self.run_cli("add", "x", "--section", "done")
        self.assertEqual(code, 1)

    def test_list_filters(self):
        self.run_cli("add", "A", "--biz", "app", "--due", "2026-10-20")
        self.run_cli("add", "B", "--biz", "lunch", "--due", "2026-10-25")
        self.run_cli("add", "C")
        code, out, _ = self.run_cli("list", "--biz", "app")
        self.assertIn("A", out)
        self.assertNotIn("] B", out)
        code, out, _ = self.run_cli("list", "--overdue")
        self.assertIn("OVERDUE 2026-10-20", out)
        self.assertNotIn("] B", out)
        code, out, _ = self.run_cli("list", "--due-by", "+3d")
        self.assertIn("] A", out)
        self.assertIn("] B", out)
        self.assertNotIn("] C", out)
        code, out, _ = self.run_cli("list", "--untagged")
        self.assertIn("] C", out)
        self.assertNotIn("] A", out)

    def test_list_json(self):
        self.run_cli("add", "A", "--biz", "app", "--due", "2026-10-20")
        code, out, _ = self.run_cli("list", "--json")
        data = json.loads(out)
        self.assertEqual(data[0]["title"], "A")
        self.assertEqual(data[0]["tags"], ["app"])
        self.assertTrue(data[0]["overdue"])

    def test_list_without_file(self):
        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 1)
        self.assertIn("no tasks.md yet", out)

    def test_hand_written_lines_still_parse(self):
        self.write("# Tasks\n\nsome intro note\n\n## Active\n"
                   "- [ ] **Old style task** - for Sam, due Friday\n"
                   "- [ ] plain text task #app\n  - a sub bullet\n\n"
                   "## Waiting on\n\n## Someday\n\n## Done\n"
                   "- [x] ~~Shipped it~~ (2026-10-01)\n")
        code, out, _ = self.run_cli("list", "--all")
        self.assertIn("Old style task", out)
        self.assertIn("plain text task", out)
        self.assertIn("Shipped it", out)


class TestDoneEdit(Base):
    def setUp(self):
        super().setUp()
        self.run_cli("add", "Send invoice to Dana", "--biz", "consulting", "--due", "today")
        self.run_cli("add", "Draft menu", "--biz", "lunch")
        self.run_cli("add", "Draft pitch", "--biz", "app")

    def test_done_by_title_moves_and_keeps_subbullets(self):
        t = self.text().replace("**Send invoice to Dana** #consulting due:2026-10-23 added:2026-10-23",
                                "**Send invoice to Dana** #consulting due:2026-10-23 added:2026-10-23\n"
                                "  - net 30")
        self.write(t)
        code, out, _ = self.run_cli("done", "invoice")
        self.assertEqual(code, 0, out)
        text = self.text()
        done_part = text.split("## Done", 1)[1]
        self.assertIn("- [x] ~~Send invoice to Dana~~ #consulting", done_part)
        self.assertIn("done:2026-10-23", done_part)
        self.assertIn("  - net 30", done_part)
        self.assertNotIn("Send invoice", text.split("## Done", 1)[0])

    def test_done_ambiguous(self):
        code, _, err = self.run_cli("done", "draft")
        self.assertEqual(code, 1)
        self.assertIn("more than one", err)
        code, out, _ = self.run_cli("done", "3")
        self.assertIn("Draft pitch", out)

    def test_done_twice(self):
        self.run_cli("done", "invoice")
        code, out, _ = self.run_cli("done", "invoice")
        self.assertIn("already done", out)

    def test_done_since(self):
        self.run_cli("done", "invoice")
        code, out, _ = self.run_cli("list", "--done-since", "2026-10-20")
        self.assertIn("Send invoice", out)

    def test_edit_due_tag_note_section(self):
        code, out, _ = self.run_cli("edit", "menu", "--due", "+1w", "--note", "ask Rami")
        self.assertEqual(code, 0, out)
        self.assertIn("**Draft menu** #lunch added:2026-10-23 due:2026-10-30 - ask Rami", self.text())
        self.run_cli("edit", "menu", "--note", "ask Rami first")
        self.assertIn("- ask Rami first", self.text())
        self.assertNotIn("- ask Rami - ", self.text())
        self.run_cli("edit", "menu", "--due", "none")
        self.assertNotIn("due:2026-10-30", self.text())
        self.run_cli("edit", "pitch", "--biz", "school", "--drop-biz", "app")
        self.assertIn("**Draft pitch** #school", self.text())
        self.run_cli("edit", "pitch", "--section", "someday")
        someday = self.text().split("## Someday", 1)[1].split("## Done", 1)[0]
        self.assertIn("Draft pitch", someday)

    def test_edit_nothing(self):
        code, _, err = self.run_cli("edit", "menu")
        self.assertEqual(code, 1)


class TestRollover(Base):
    def test_archives_old_done_and_lists_overdue(self):
        self.write("# Tasks\n\n## Active\n"
                   "- [ ] **Late thing** #app due:2026-10-10 added:2026-09-01\n\n"
                   "## Waiting on\n\n## Someday\n\n## Done\n"
                   "- [x] ~~Old win~~ #app done:2026-10-01\n"
                   "- [x] ~~New win~~ #app done:2026-10-22\n")
        code, out, _ = self.run_cli("rollover")
        self.assertEqual(code, 0)
        self.assertIn("archived 1", out)
        self.assertIn("Late thing", out)
        self.assertIn("13 days late", out)
        self.assertIn("30+ days", out)
        self.assertNotIn("Old win", self.text())
        self.assertIn("New win", self.text())
        with open(os.path.join(self.dir, "tasks-archive.md"), encoding="utf-8") as fh:
            self.assertIn("Old win", fh.read())

    def test_dry_run_changes_nothing(self):
        body = ("# Tasks\n\n## Active\n\n## Waiting on\n\n## Someday\n\n## Done\n"
                "- [x] ~~Old win~~ #app done:2026-10-01\n")
        self.write(body)
        self.run_cli("rollover", "--dry-run")
        self.assertEqual(self.text(), body)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "tasks-archive.md")))

    def test_missing_section_is_added(self):
        self.write("# Tasks\n\n## Active\n- [ ] **A** #app\n")
        self.run_cli("done", "A")
        self.assertIn("## Done", self.text())
        self.assertIn("~~A~~", self.text())


if __name__ == "__main__":
    unittest.main()
