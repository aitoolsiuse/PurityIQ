"""Read/update the queue.md status table."""
import os
import re
import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_PATH = os.path.join(REPO, "queue.md")

HEADER = "| ID | slug | status | date |\n|---|---|---|---|\n"


def _read_rows():
    if not os.path.exists(QUEUE_PATH):
        return []
    rows = []
    with open(QUEUE_PATH) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-"}:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0].upper() == "ID":
                continue
            rows.append(cells)
    return rows


def _write_rows(rows):
    with open(QUEUE_PATH, "w") as f:
        f.write(HEADER)
        for r in rows:
            f.write("| " + " | ".join(r) + " |\n")


def upsert(post_id, slug, status, date=None):
    date = date or datetime.date.today().isoformat()
    rows = _read_rows()
    for r in rows:
        if r[0] == post_id:
            r[1] = slug
            r[2] = status
            r[3] = date
            break
    else:
        rows.append([post_id, slug, status, date])
    rows.sort(key=lambda r: r[0])
    _write_rows(rows)


if __name__ == "__main__":
    import sys
    upsert(*sys.argv[1:4])
