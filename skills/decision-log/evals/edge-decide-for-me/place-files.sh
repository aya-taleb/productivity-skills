#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
python3 -I - <<'PY'
import datetime as dt, os, re
today = dt.date.today()
def week(n):
    y, w, _ = (today + dt.timedelta(weeks=n)).isocalendar()
    return "%d-W%02d" % (y, w)
def sub(text):
    text = re.sub(r"@D([+-]\d+)@", lambda m: (today + dt.timedelta(days=int(m.group(1)))).isoformat(), text)
    return re.sub(r"@W([+-]?\d+)@", lambda m: week(int(m.group(1))), text)
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        path = os.path.join(root, name)
        if name.endswith((".md", ".txt", ".vtt")) or name == "active":
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(sub(body))
        if "@" in name:
            os.rename(path, os.path.join(root, sub(name)))
PY
