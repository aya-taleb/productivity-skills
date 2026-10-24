#!/usr/bin/env python3
"""A small tool for one plain tasks.md file, tagged by business.

The file is ordinary Markdown that a person can edit by hand. This tool only
changes the lines it needs to, so hand edits and extra notes survive.

Task line format:
    - [ ] **Title** #business due:2026-10-30 added:2026-10-23 - optional note
      - optional sub-bullets (kept with the task when it moves)
Done tasks look like:
    - [x] ~~Title~~ #business done:2026-10-24

Sections, in order: Active, Waiting on, Someday, Done.

Commands:
    init                        create tasks.md if it is missing
    add TITLE [options]         add a task
    list [filters]              show tasks with an id you can use in done/edit
    done MATCH                  mark a task done and move it to Done
    edit MATCH [options]        change due date, business, section or note
    rollover                    archive old Done items, list overdue tasks
    where                       print which tasks.md file is in use
    context                     print the founder folder, businesses and tags (JSON)
    save REL --from FILE        copy FILE to <founder folder>/REL, e.g. weekly/2026-W43.md
                                (other skills use it so every save lands in the same
                                folder). Refuses to overwrite without --replace.

MATCH is the id shown by `list`, or a piece of the title.

Where the file lives (first match wins):
    --file PATH
    $FOUNDER_HOME/tasks.md
    a project founder/ at or above the current folder that already holds tasks.md,
        decisions.md, people/, weekly/, daily/ or businesses/ (per-project setups, tests)
    ~/.founder/tasks.md

Standard library only. Python 3.8+.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

SECTIONS = ["Active", "Waiting on", "Someday", "Done"]
SECTION_KEYS = {"active": "Active", "waiting": "Waiting on", "waiting on": "Waiting on",
                "someday": "Someday", "done": "Done"}
TEMPLATE = "# Tasks\n\n## Active\n\n## Waiting on\n\n## Someday\n\n## Done\n"
TASK_RE = re.compile(r"^- \[( |x|X)\] (.*)$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
TAG_RE = re.compile(r"(?<!\S)#([a-z0-9][a-z0-9_-]*)", re.I)
FIELD_RE = re.compile(r"(?<!\S)(due|since|added|done):(\d{4}-\d{2}-\d{2})(?!\S)")
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class TaskError(Exception):
    pass


# ---------------------------------------------------------------- paths

LOCAL_MARKERS = ("tasks.md", "decisions.md", "people", "weekly", "daily", "businesses")


def local_founder(cwd):
    """A project founder/ folder at or above cwd that already holds productivity files.

    Checks cwd itself (if it is a founder folder), then cwd/founder, then each parent, so the
    tool finds the same folder even when run from inside founder/ or a subfolder.
    """
    d = os.path.abspath(cwd)
    while True:
        for cand in ((d,) if os.path.basename(d) == "founder" else ()) + (os.path.join(d, "founder"),):
            if any(os.path.exists(os.path.join(cand, m)) for m in LOCAL_MARKERS):
                return cand
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def founder_dir(env=None, cwd=None, home=None):
    """The folder that holds tasks.md, decisions.md, weekly/, people/, daily/.

    Order: $FOUNDER_HOME, then a project founder/ folder at or above the current folder that
    already holds one of the productivity files (so a founder/ folder made by other skills is
    not taken over), then ~/.founder/.
    """
    env = os.environ if env is None else env
    cwd = os.getcwd() if cwd is None else cwd
    home = os.path.expanduser("~") if home is None else home
    if env.get("FOUNDER_HOME"):
        return os.path.expanduser(env["FOUNDER_HOME"])
    home_founder = os.path.join(home, ".founder")
    local = local_founder(cwd)
    if local and os.path.abspath(local) != os.path.abspath(home_founder):
        return local
    return home_founder


def read_businesses(folder, cwd=None, home=None):
    """List businesses from founder-context files. Never invents any.

    Reads <folder>/businesses/*.md, falling back to ~/.founder/businesses/.
    Also reports the active slug and a project-local founder/context.md if present.
    """
    cwd = os.getcwd() if cwd is None else cwd
    home = os.path.expanduser("~") if home is None else home
    out = []
    bdir = os.path.join(folder, "businesses")
    if not os.path.isdir(bdir):
        bdir = os.path.join(home, ".founder", "businesses")
    if os.path.isdir(bdir):
        for name in sorted(os.listdir(bdir)):
            if not name.endswith(".md"):
                continue
            slug = name[:-3]
            title = slug
            with open(os.path.join(bdir, name), encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"^\s*(?:#\s+|[-*]?\s*\**name\**:\s*)(.+?)\s*$", line, re.I)
                    if m:
                        title = m.group(1).strip("* ")
                        break
            out.append({"slug": slug, "name": title})
    active = None
    apath = os.path.join(os.path.dirname(bdir), "active")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            active = fh.read().strip() or None
    local_ctx = os.path.join(cwd, "founder", "context.md")
    return {"businesses": out, "active": active, "businesses_dir": bdir,
            "project_context": local_ctx if os.path.exists(local_ctx) else None}


def tasks_path(explicit=None, **kw):
    if explicit:
        return explicit
    return os.path.join(founder_dir(**kw), "tasks.md")


# ---------------------------------------------------------------- dates

def parse_date(text, today):
    """Turn a date word into a date. Returns None for 'none'."""
    if text is None:
        return None
    t = text.strip().lower()
    if t in ("", "none", "no", "-"):
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", t):
        try:
            return dt.date.fromisoformat(t)
        except ValueError:
            raise TaskError("not a real date: %s" % text)
    if t == "today":
        return today
    if t == "tomorrow":
        return today + dt.timedelta(days=1)
    m = re.match(r"^\+(\d+)([dw])$", t)
    if m:
        n = int(m.group(1)) * (7 if m.group(2) == "w" else 1)
        return today + dt.timedelta(days=n)
    for i, name in enumerate(WEEKDAYS):
        if t in (name, name[:3]):
            ahead = (i - today.weekday()) % 7 or 7  # next one, never today
            return today + dt.timedelta(days=ahead)
    raise TaskError("can't read the date %r. Use YYYY-MM-DD, today, tomorrow, "
                    "a weekday, +3d or +2w." % text)


# ---------------------------------------------------------------- parsing

class Task(object):
    def __init__(self, start, end, section, checked, body):
        self.start = start      # index of the task line
        self.end = end          # index after its last sub-line
        self.section = section
        self.checked = checked
        self.body = body
        self.id = 0

    @property
    def fields(self):
        return dict(FIELD_RE.findall(self.body))

    @property
    def tags(self):
        return [t.lower() for t in TAG_RE.findall(self.body)]

    @property
    def title(self):
        m = re.match(r"^\*\*(.+?)\*\*", self.body) or re.match(r"^~~(.+?)~~", self.body)
        if m:
            return m.group(1).strip()
        text = self.body.split(" - ", 1)[0]
        text = TAG_RE.sub("", FIELD_RE.sub("", text))
        return " ".join(text.split()).strip("~* ")

    @property
    def note(self):
        rest = re.sub(r"^(\*\*.+?\*\*|~~.+?~~)", "", self.body)
        if " - " in rest:
            return rest.split(" - ", 1)[1].strip()
        return ""

    def date(self, key):
        v = self.fields.get(key)
        return dt.date.fromisoformat(v) if v else None

    def is_done(self):
        return self.checked or self.section == "Done"

    def to_dict(self, today):
        due = self.date("due")
        return {
            "id": self.id, "title": self.title, "section": self.section,
            "done": self.is_done(), "tags": self.tags, "due": self.fields.get("due"),
            "since": self.fields.get("since"), "added": self.fields.get("added"),
            "done_date": self.fields.get("done"), "note": self.note,
            "overdue": bool(due and due < today and not self.is_done()),
        }


class TaskFile(object):
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                self.lines = fh.read().splitlines()
        else:
            self.lines = TEMPLATE.splitlines()
        self.parse()

    def parse(self):
        self.tasks = []
        self.section_at = {}
        section = None
        i = 0
        while i < len(self.lines):
            line = self.lines[i]
            sm = SECTION_RE.match(line)
            if sm:
                name = SECTION_KEYS.get(sm.group(1).strip().lower(), sm.group(1).strip())
                section = name
                self.section_at[name] = i
                i += 1
                continue
            tm = TASK_RE.match(line)
            if tm:
                j = i + 1
                while j < len(self.lines) and self.lines[j][:1] in (" ", "\t") \
                        and self.lines[j].strip():
                    j += 1
                self.tasks.append(Task(i, j, section or "Active",
                                       tm.group(1).lower() == "x", tm.group(2)))
                i = j
                continue
            i += 1
        for n, t in enumerate(self.tasks, 1):
            t.id = n

    def save(self):
        folder = os.path.dirname(self.path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        text = "\n".join(self.lines).rstrip("\n") + "\n"
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, self.path)

    # -- helpers

    def ensure_section(self, name):
        if name in self.section_at:
            return
        # insert before the next known section that exists, else at the end
        order = SECTIONS.index(name) if name in SECTIONS else len(SECTIONS)
        at = len(self.lines)
        for later in SECTIONS[order + 1:]:
            if later in self.section_at:
                at = self.section_at[later]
                break
        block = ["## " + name, ""]
        if at > 0 and self.lines[at - 1].strip():
            block.insert(0, "")
        self.lines[at:at] = block
        self.parse()

    def insert_at_section_end(self, name, block):
        self.ensure_section(name)
        start = self.section_at[name]
        end = len(self.lines)
        for other, idx in self.section_at.items():
            if idx > start and idx < end:
                end = idx
        # put after the last non-blank line of the section
        at = end
        while at - 1 > start and not self.lines[at - 1].strip():
            at -= 1
        self.lines[at:at] = block
        self.parse()

    def find(self, match):
        match = str(match).strip()
        if match.isdigit():
            n = int(match)
            for t in self.tasks:
                if t.id == n:
                    return t
            raise TaskError("no task with id %d" % n)
        low = match.lower()
        hits = [t for t in self.tasks if low in t.title.lower() and not t.is_done()]
        if not hits:
            hits = [t for t in self.tasks if low in t.title.lower()]
        if not hits:
            raise TaskError("no task matches %r" % match)
        if len(hits) > 1:
            exact = [t for t in hits if t.title.lower() == low]
            if len(exact) == 1:
                return exact[0]
            names = "; ".join("[%d] %s" % (t.id, t.title) for t in hits)
            raise TaskError("more than one task matches %r: %s. Use the id." % (match, names))
        return hits[0]

    def move(self, task, section, new_first_line):
        block = [new_first_line] + self.lines[task.start + 1:task.end]
        del self.lines[task.start:task.end]
        self.parse()
        self.insert_at_section_end(section, block)


def set_field(body, key, value):
    pattern = re.compile(r"(?<!\S)%s:\d{4}-\d{2}-\d{2}(?!\S)" % key)
    if value is None:
        body = pattern.sub("", body)
        return re.sub(r"  +", " ", body).strip()
    if pattern.search(body):
        return pattern.sub("%s:%s" % (key, value), body)
    head, sep, note = body.partition(" - ")
    head = head.rstrip() + " %s:%s" % (key, value)
    return head + (sep + note if sep else "")


def add_tags(body, tags):
    """Add tags right after the title and any tags already there."""
    have = [t.lower() for t in TAG_RE.findall(body)]
    new = [t.lstrip("#").lower() for t in tags]
    new = [t for t in new if t and t not in have]
    if not new:
        return body
    m = re.match(r"^((?:\*\*.+?\*\*|~~.+?~~)(?:\s+#[a-z0-9_-]+)*)(.*)$", body, re.I | re.S)
    if not m:
        head, sep, note = body.partition(" - ")
        return head.rstrip() + " " + " ".join("#" + t for t in new) + (sep + note if sep else "")
    return m.group(1) + " " + " ".join("#" + t for t in new) + m.group(2)


def clean_tag(tag):
    tag = tag.lstrip("#").strip().lower()
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", tag):
        raise TaskError("business tags use lowercase letters, numbers and dashes: %r" % tag)
    return tag


# ---------------------------------------------------------------- commands

def cmd_add(tf, args, today):
    title = " ".join(args.title).strip()
    if not title:
        raise TaskError("a task needs a title")
    title = title.replace("**", "")
    section = SECTION_KEYS.get(args.section.lower(), None)
    if section is None or section == "Done":
        raise TaskError("section must be active, waiting or someday")
    body = "**%s**" % title
    for tag in args.biz or []:
        body += " #" + clean_tag(tag)
    due = parse_date(args.due, today)
    if due:
        body += " due:" + due.isoformat()
    if section == "Waiting on":
        body += " since:" + (parse_date(args.since, today) or today).isoformat()
    body += " added:" + today.isoformat()
    if args.note:
        body += " - " + args.note.strip()
    tf.insert_at_section_end(section, ["- [ ] " + body])
    tf.save()
    t = [x for x in tf.tasks if x.body == body][-1]
    return "added [%d] %s%s  -> %s" % (t.id, title, (" (due %s)" % fmt_day(due)) if due else "",
                                       tf.path)


def fmt_day(d):
    return "%s %s" % (d.strftime("%a"), d.isoformat())


def select(tf, args, today):
    out = []
    due_by = parse_date(args.due_by, today) if args.due_by else None
    done_since = parse_date(args.done_since, today) if args.done_since else None
    sections = None
    if args.section:
        sections = {SECTION_KEYS.get(s.strip().lower(), s) for s in args.section.split(",")}
    for t in tf.tasks:
        if done_since:
            d = t.date("done")
            if not (t.is_done() and d and d >= done_since):
                continue
        elif sections:
            if t.section not in sections:
                continue
        elif not args.all and t.is_done():
            continue
        if args.biz and clean_tag(args.biz) not in t.tags:
            continue
        if args.untagged and t.tags:
            continue
        due = t.date("due")
        if args.overdue and not (due and due < today and not t.is_done()):
            continue
        if due_by and not (due and due <= due_by):
            continue
        out.append(t)
    return out


def cmd_list(tf, args, today):
    tasks = select(tf, args, today)
    if args.json:
        return json.dumps([t.to_dict(today) for t in tasks], indent=2)
    if not tasks:
        return "no tasks match"
    rows = []
    current = None
    for t in tasks:
        if t.section != current:
            current = t.section
            rows.append("%s:" % current)
        d = t.to_dict(today)
        bits = []
        if d["due"]:
            bits.append(("OVERDUE " if d["overdue"] else "due ") + d["due"])
        if d["since"] and t.section == "Waiting on":
            waited = (today - t.date("since")).days
            bits.append("waiting %d days" % waited)
        if d["done_date"]:
            bits.append("done " + d["done_date"])
        tags = " ".join("#" + x for x in d["tags"]) or "(no business)"
        rows.append("  [%d] %s  %s  %s" % (t.id, d["title"], tags, ", ".join(bits)))
    return "\n".join(rows).rstrip()


def cmd_done(tf, args, today):
    t = tf.find(" ".join(args.match))
    if t.is_done():
        return "already done: [%d] %s" % (t.id, t.title)
    when = parse_date(args.date, today) or today
    rest = re.sub(r"^\*\*(.+?)\*\*", "", t.body)
    body = "~~%s~~%s" % (t.title, rest)
    body = set_field(body, "done", when.isoformat())
    title = t.title
    tf.move(t, "Done", "- [x] " + body)
    tf.save()
    return "done: %s (%s)" % (title, when.isoformat())


def cmd_edit(tf, args, today):
    t = tf.find(" ".join(args.match))
    body = t.body
    changed = []
    if args.due is not None:
        d = parse_date(args.due, today)
        body = set_field(body, "due", d.isoformat() if d else None)
        changed.append("due " + (d.isoformat() if d else "removed"))
    if args.biz:
        body = add_tags(body, [clean_tag(b) for b in args.biz])
        changed.append("business " + ", ".join(args.biz))
    if args.drop_biz:
        tag = clean_tag(args.drop_biz)
        body = re.sub(r"(?<!\S)#%s(?![a-z0-9_-])" % re.escape(tag), "", body, flags=re.I)
        body = re.sub(r"  +", " ", body).strip()
        changed.append("removed #" + tag)
    if args.note is not None:
        m = re.match(r"^(\*\*.+?\*\*|~~.+?~~)(.*)$", body)
        title_part, rest = (m.group(1), m.group(2)) if m else ("", body)
        meta = rest.split(" - ", 1)[0].rstrip()
        body = title_part + meta + (" - " + args.note.strip() if args.note.strip() else "")
        changed.append("note")
    section = None
    if args.section:
        section = SECTION_KEYS.get(args.section.lower())
        if section is None or section == "Done":
            raise TaskError("section must be active, waiting or someday (use done to finish)")
        if section == "Waiting on" and "since" not in dict(FIELD_RE.findall(body)):
            body = set_field(body, "since", today.isoformat())
        changed.append("moved to " + section)
    if not changed:
        raise TaskError("nothing to change. Use --due, --biz, --drop-biz, --note or --section")
    mark = "x" if t.checked else " "
    line = "- [%s] %s" % (mark, body)
    if section and section != t.section:
        tf.move(t, section, line)
    else:
        tf.lines[t.start] = line
        tf.parse()
    tf.save()
    return "changed [%d] %s: %s" % (t.id, t.title, "; ".join(changed))


def cmd_rollover(tf, args, today):
    keep = dt.timedelta(days=args.keep_days)
    archive_path = args.archive or os.path.join(os.path.dirname(tf.path) or ".",
                                                "tasks-archive.md")
    old = [t for t in tf.tasks if t.is_done() and t.date("done")
           and today - t.date("done") > keep]
    report = []
    if old:
        blocks = []
        for t in sorted(old, key=lambda x: x.start, reverse=True):
            blocks.insert(0, tf.lines[t.start:t.end])
            del tf.lines[t.start:t.end]
        tf.parse()
        if not args.dry_run:
            exists = os.path.exists(archive_path)
            with open(archive_path, "a", encoding="utf-8") as fh:
                if not exists:
                    fh.write("# Done tasks archive\n")
                fh.write("\n## Archived %s\n" % today.isoformat())
                for b in blocks:
                    fh.write("\n".join(b) + "\n")
            tf.save()
        report.append("archived %d done task(s) older than %d days to %s"
                      % (len(old), args.keep_days, archive_path))
    else:
        report.append("nothing to archive")
    overdue = [t for t in tf.tasks if not t.is_done() and t.date("due")
               and t.date("due") < today]
    if overdue:
        report.append("overdue, decide for each (new date, someday, or drop):")
        for t in overdue:
            report.append("  [%d] %s  %s  due %s (%d days late)" % (
                t.id, t.title, " ".join("#" + x for x in t.tags) or "(no business)",
                t.fields["due"], (today - t.date("due")).days))
    else:
        report.append("nothing overdue")
    stale = [t for t in tf.tasks if t.section == "Active" and not t.is_done()
             and t.date("added") and (today - t.date("added")).days >= 30]
    if stale:
        report.append("in Active for 30+ days (still real?):")
        for t in stale:
            report.append("  [%d] %s  added %s" % (t.id, t.title, t.fields["added"]))
    return "\n".join(report)


def save_file(folder, rel, src, replace=False):
    """Copy src to folder/rel. rel must stay inside the founder folder."""
    norm = os.path.normpath(rel)
    if os.path.isabs(rel) or norm.startswith(".."):
        raise TaskError("path must be inside the founder folder: %s" % rel)
    dest = os.path.join(folder, norm)
    if os.path.exists(dest) and not replace:
        raise TaskError("%s exists; read it, merge, then save with --replace" % dest)
    with open(src, encoding="utf-8") as fh:
        text = fh.read()
    os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    return dest


def build_parser():
    p = argparse.ArgumentParser(description="Plain tasks.md, tagged by business.")
    p.add_argument("--file", help="path to tasks.md")
    p.add_argument("--today", help="pretend today is this date (YYYY-MM-DD)")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init", help="create tasks.md if missing")
    sub.add_parser("where", help="print the tasks.md path in use")
    sub.add_parser("context", help="print folder, businesses and tags as JSON")

    a = sub.add_parser("add", help="add a task")
    a.add_argument("title", nargs="+")
    a.add_argument("--biz", action="append", help="business slug, repeatable")
    a.add_argument("--due")
    a.add_argument("--section", default="active", help="active, waiting or someday")
    a.add_argument("--since", help="for waiting items, when you started waiting")
    a.add_argument("--note")

    ls = sub.add_parser("list", help="list tasks")
    ls.add_argument("--biz")
    ls.add_argument("--section", help="active, waiting, someday, done (comma list)")
    ls.add_argument("--all", action="store_true", help="include done tasks")
    ls.add_argument("--overdue", action="store_true")
    ls.add_argument("--due-by", help="due on or before this date")
    ls.add_argument("--done-since", help="done on or after this date")
    ls.add_argument("--untagged", action="store_true", help="tasks with no business")
    ls.add_argument("--json", action="store_true")

    d = sub.add_parser("done", help="mark a task done")
    d.add_argument("match", nargs="+")
    d.add_argument("--date", help="when it was done (default today)")

    e = sub.add_parser("edit", help="change a task")
    e.add_argument("match", nargs="+")
    e.add_argument("--due", help="new date, or none")
    e.add_argument("--biz", action="append")
    e.add_argument("--drop-biz")
    e.add_argument("--note")
    e.add_argument("--section")

    sv = sub.add_parser("save", help="copy a file into the founder folder")
    sv.add_argument("rel", help="path inside the founder folder, e.g. weekly/2026-W43.md")
    sv.add_argument("--from", dest="src", required=True)
    sv.add_argument("--replace", action="store_true", help="overwrite an existing file")

    r = sub.add_parser("rollover", help="archive old done tasks, list overdue")
    r.add_argument("--keep-days", type=int, default=7)
    r.add_argument("--archive")
    r.add_argument("--dry-run", action="store_true")
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 2
    try:
        today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    except ValueError:
        print("error: --today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    path = tasks_path(args.file)
    try:
        if args.cmd == "where":
            print(path)
            return 0
        if args.cmd == "context":
            folder = os.path.dirname(path) or "."
            info = read_businesses(folder)
            info["folder"] = folder
            info["tasks_file"] = path
            info["tasks_file_exists"] = os.path.exists(path)
            if os.path.exists(path):
                tags = set()
                for t in TaskFile(path).tasks:
                    tags.update(t.tags)
                known = {b["slug"] for b in info["businesses"]}
                info["unknown_tags_in_tasks"] = sorted(tags - known) if known else sorted(tags)
            print(json.dumps(info, indent=2))
            return 0
        if args.cmd == "save":
            print("saved " + save_file(os.path.dirname(path) or ".", args.rel, args.src,
                                       args.replace))
            return 0
        if args.cmd == "init":
            if os.path.exists(path):
                print("already there: " + path)
            else:
                tf = TaskFile(path)
                tf.save()
                print("created " + path)
            return 0
        if args.cmd != "add" and not os.path.exists(path):
            print("no tasks.md yet at %s. Run init or add a task first." % path)
            return 1
        tf = TaskFile(path)
        handler = {"add": cmd_add, "list": cmd_list, "done": cmd_done,
                   "edit": cmd_edit, "rollover": cmd_rollover}[args.cmd]
        print(handler(tf, args, today))
        return 0
    except TaskError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
