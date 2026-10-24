#!/usr/bin/env python3
"""A small tool for people/<name>.md files: who is due for a check-in.

Each person is one Markdown file a human can edit. The tool reads a few
"key: value" lines near the top and the dated log at the bottom:

    # Dana Kim
    how we know each other: UW entrepreneurship cohort, fall 2026
    businesses: quizpal
    cadence: monthly
    last contact: 2026-09-10
    cares about: her thesis on food access; trail running
    coming up: defends thesis 2026-11-12

    ## Log
    - 2026-09-10 coffee, talked about her thesis

Cadence words: weekly, every 2 weeks, monthly, every 2 months, quarterly,
twice a year, yearly, or "every N days". No cadence means monthly. "cadence: none"
or "cadence: paused" keeps the person out of check-in lists.

Commands:
    due [--limit 3] [--json]     people whose cadence has run out: dated news in the
                                 next 14 days first, then most overdue
    list [--json]                everyone, with days since last contact
    log NAME [--date D] [--note TEXT]   record a contact (updates last contact, adds a log line)
    add NAME [--how ...] [--cadence ...] [--cares ...] [--biz ...]   new person file
    where                        print the people folder in use

Folder (first match wins): --dir, $FOUNDER_HOME/people, people/ in a project founder/
folder at or above the current folder, ~/.founder/people. Standard library only. Python 3.8+.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

CADENCES = {
    "weekly": 7, "every week": 7, "every 2 weeks": 14, "biweekly": 14,
    "every two weeks": 14, "monthly": 30, "every month": 30, "every 2 months": 60,
    "every two months": 60, "quarterly": 91, "every 3 months": 91,
    "twice a year": 182, "every 6 months": 182, "yearly": 365, "once a year": 365,
}
PAUSED = {"none", "paused", "never", "no"}
DEFAULT_DAYS = 30
SOON_DAYS = 14  # a dated "coming up" within this many days puts someone first
FIELD_RE = re.compile(r"^\s*[-*]?\s*\**([A-Za-z][A-Za-z ]{1,40}?)\**\s*:\s*(.*?)\s*$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
LOG_RE = re.compile(r"^\s*[-*]\s+(\d{4}-\d{2}-\d{2})\b")


class PeopleError(Exception):
    pass


MARKERS = ("tasks.md", "decisions.md", "people", "weekly", "daily", "businesses")


def people_dir(explicit=None, env=None, cwd=None, home=None):
    """$FOUNDER_HOME/people, then a project founder/ at or above cwd, then ~/.founder/people."""
    if explicit:
        return explicit
    env = os.environ if env is None else env
    cwd = os.getcwd() if cwd is None else cwd
    home = os.path.expanduser("~") if home is None else home
    if env.get("FOUNDER_HOME"):
        return os.path.join(os.path.expanduser(env["FOUNDER_HOME"]), "people")
    d = os.path.abspath(cwd)
    while True:
        cands = ((d,) if os.path.basename(d) == "founder" else ()) + (os.path.join(d, "founder"),)
        for cand in cands:
            if any(os.path.exists(os.path.join(cand, m)) for m in MARKERS):
                return os.path.join(cand, "people")
        if os.path.basename(d) == "people" and os.path.basename(os.path.dirname(d)) == "founder":
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(home, ".founder", "people")


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not s:
        raise PeopleError("a person needs a name with letters or numbers")
    return s


def cadence_days(text):
    if text is None or not text.strip():
        return DEFAULT_DAYS
    t = text.strip().lower()
    t = re.sub(r"\(.*?\)", "", t).strip()
    if t in PAUSED:
        return None
    if t in CADENCES:
        return CADENCES[t]
    m = re.match(r"^every\s+(\d+)\s*(day|days|d|week|weeks|w|month|months)$", t)
    if m:
        n = int(m.group(1))
        unit = m.group(2)[0]
        return n * {"d": 1, "w": 7, "m": 30}[unit]
    for key, days in CADENCES.items():
        if t.startswith(key):
            return days
    raise PeopleError("can't read cadence %r. Use weekly, every 2 weeks, monthly, "
                      "quarterly, twice a year, yearly, every N days, or none." % text)


class Person(object):
    def __init__(self, path):
        self.path = path
        self.slug = os.path.basename(path)[:-3]
        with open(path, encoding="utf-8") as fh:
            self.lines = fh.read().splitlines()
        self.name = self.slug.replace("-", " ").title()
        self.fields = {}
        log_dates = []
        for line in self.lines:
            if line.startswith("# ") and self.name == self.slug.replace("-", " ").title():
                self.name = line[2:].strip()
                continue
            lm = LOG_RE.match(line)
            if lm:
                log_dates.append(lm.group(1))
                continue
            fm = FIELD_RE.match(line)
            if fm:
                key = fm.group(1).strip().lower()
                self.fields.setdefault(key, fm.group(2))
        self.log_dates = sorted(set(log_dates))

    def last_contact(self):
        dates = list(self.log_dates)
        raw = self.fields.get("last contact", "")
        m = DATE_RE.search(raw)
        if m:
            dates.append(m.group(0))
        valid = []
        for d in dates:
            try:
                valid.append(dt.date.fromisoformat(d))
            except ValueError:
                pass
        return max(valid) if valid else None

    def cadence(self):
        return cadence_days(self.fields.get("cadence"))

    def status(self, today):
        last = self.last_contact()
        try:
            every = self.cadence()
            bad = None
        except PeopleError as exc:
            every, bad = DEFAULT_DAYS, str(exc)
        since = (today - last).days if last else None
        if every is None:
            overdue = None
        elif last is None:
            overdue = 0  # never logged: due now, but after real overdue people
        else:
            overdue = since - every
        soon = None
        for d in DATE_RE.findall(self.fields.get("coming up", "") or ""):
            try:
                day = dt.date.fromisoformat(d)
            except ValueError:
                continue
            if 0 <= (day - today).days <= SOON_DAYS:
                soon = (day - today).days if soon is None else min(soon, (day - today).days)
        return {
            "slug": self.slug, "name": self.name, "coming_up_in_days": soon, "last_contact": last.isoformat() if last else None,
            "days_since": since, "cadence_days": every, "overdue_days": overdue,
            "due": overdue is not None and overdue >= 0,
            "how": self.fields.get("how we know each other") or self.fields.get("how we met"),
            "cares_about": self.fields.get("cares about"),
            "coming_up": self.fields.get("coming up"),
            "businesses": self.fields.get("businesses"),
            "cadence_problem": bad,
        }


def load_all(folder):
    if not os.path.isdir(folder):
        return []
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md") and not name.startswith(("_", ".")) and name.lower() != "readme.md":
            out.append(Person(os.path.join(folder, name)))
    return out


def find(folder, name):
    people = load_all(folder)
    want = slugify(name)
    for p in people:
        if p.slug == want:
            return p
    hits = [p for p in people if want in p.slug or name.lower() in p.name.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise PeopleError("no person file matches %r in %s" % (name, folder))
    raise PeopleError("more than one person matches %r: %s" % (
        name, ", ".join(p.slug for p in hits)))


def cmd_due(folder, args, today):
    rows = [p.status(today) for p in load_all(folder)]
    due = [r for r in rows if r["due"]]
    # people with dated news in the next 14 days first (the easiest, warmest note),
    # then most overdue; people never logged go after the truly overdue ones
    due.sort(key=lambda r: (r["coming_up_in_days"] is None, r["coming_up_in_days"] or 0,
                            r["last_contact"] is None, -(r["overdue_days"] or 0), r["name"]))
    total = len(due)
    due = due[:args.limit] if args.limit else due
    if args.json:
        return json.dumps({"due_total": total, "shown": due}, indent=2)
    if not due:
        return "nobody is due for a check-in"
    lines = ["%d due, showing %d:" % (total, len(due))]
    for r in due:
        if r["last_contact"]:
            when = "last contact %s (%d days ago, cadence %d days)" % (
                r["last_contact"], r["days_since"], r["cadence_days"])
        else:
            when = "no contact logged yet"
        lines.append("  %s  %s" % (r["name"], when))
        if r["coming_up"]:
            soon = r["coming_up_in_days"]
            tag = " (in %d days)" % soon if soon is not None else ""
            lines.append("    coming up: " + r["coming_up"] + tag)
    return "\n".join(lines)


def cmd_list(folder, args, today):
    rows = [p.status(today) for p in load_all(folder)]
    if args.json:
        return json.dumps(rows, indent=2)
    if not rows:
        return "no people files in %s" % folder
    out = []
    for r in rows:
        since = "%d days" % r["days_since"] if r["days_since"] is not None else "never logged"
        cad = "paused" if r["cadence_days"] is None else "every %d days" % r["cadence_days"]
        flag = "  DUE" if r["due"] else ""
        out.append("  %s  %s since contact, %s%s" % (r["name"], since, cad, flag))
    return "\n".join(out)


def cmd_log(folder, args, today):
    p = find(folder, " ".join(args.name))
    when = dt.date.fromisoformat(args.date) if args.date else today
    if when > today:
        raise PeopleError("can't log a contact in the future (%s)" % when)
    lines = list(p.lines)
    current = p.last_contact()
    newest = max(current, when) if current else when
    set_line = "last contact: %s" % newest.isoformat()
    for i, line in enumerate(lines):
        fm = FIELD_RE.match(line)
        if fm and fm.group(1).strip().lower() == "last contact":
            lines[i] = set_line
            break
    else:
        at = 1
        while at < len(lines) and FIELD_RE.match(lines[at]):
            at += 1
        if at == 1 and len(lines) > 1 and not lines[1].strip():
            at = 2
        lines.insert(at, set_line)
    entry = "- %s %s" % (when.isoformat(), (args.note or "contact").strip())
    if not any(l.strip().lower() == "## log" for l in lines):
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("## Log")
    idx = [i for i, l in enumerate(lines) if l.strip().lower() == "## log"][0]
    end = idx + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    while end - 1 > idx and not lines[end - 1].strip():
        end -= 1
    lines.insert(end, entry)
    write(p.path, lines)
    return "logged %s for %s  -> %s" % (when.isoformat(), p.name, p.path)


def cmd_add(folder, args, today):
    name = " ".join(args.name).strip()
    slug = slugify(name)
    path = os.path.join(folder, slug + ".md")
    if os.path.exists(path):
        raise PeopleError("%s already exists. Edit it instead." % path)
    cadence_days(args.cadence)  # validate early
    lines = ["# " + name]
    lines.append("how we know each other: " + (args.how or ""))
    if args.biz:
        lines.append("businesses: " + args.biz)
    lines.append("cadence: " + (args.cadence or "monthly"))
    lines.append("last contact: " + (args.last or ""))
    lines.append("cares about: " + (args.cares or ""))
    lines.append("coming up: ")
    lines += ["", "## Notes", "", "## Log"]
    if args.last:
        dt.date.fromisoformat(args.last)
        lines.append("- %s %s" % (args.last, args.note or "contact"))
    os.makedirs(folder, exist_ok=True)
    write(path, lines)
    return "created " + path


def write(path, lines):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines).rstrip("\n") + "\n")
    os.replace(tmp, path)


def main(argv=None):
    p = argparse.ArgumentParser(description="people/<name>.md check-in helper")
    p.add_argument("--dir", help="people folder")
    p.add_argument("--today", help="pretend today is YYYY-MM-DD")
    sub = p.add_subparsers(dest="cmd")
    d = sub.add_parser("due")
    d.add_argument("--limit", type=int, default=3, help="0 shows everyone due")
    d.add_argument("--json", action="store_true")
    ls = sub.add_parser("list")
    ls.add_argument("--json", action="store_true")
    lg = sub.add_parser("log")
    lg.add_argument("name", nargs="+")
    lg.add_argument("--date")
    lg.add_argument("--note")
    a = sub.add_parser("add")
    a.add_argument("name", nargs="+")
    a.add_argument("--how")
    a.add_argument("--cadence")
    a.add_argument("--cares")
    a.add_argument("--biz")
    a.add_argument("--last", help="date of last contact, YYYY-MM-DD")
    a.add_argument("--note")
    sub.add_parser("where")
    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 2
    try:
        today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
        folder = people_dir(args.dir)
        if args.cmd == "where":
            print(folder)
            return 0
        handler = {"due": cmd_due, "list": cmd_list, "log": cmd_log, "add": cmd_add}[args.cmd]
        print(handler(folder, args, today))
        return 0
    except (PeopleError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
