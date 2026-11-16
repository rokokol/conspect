"""Set a course's icons from a JSON plan in the Iconic config, idempotently.

The plan maps paths relative to the course folder to Iconic specs, for example
{"content/01. Тема/Заметка.md": {"icon": "lucide-sigma"}}; keys that start
with "_" are comments. Only paths that exist get an icon, so it is safe to run
after every wave. Every "00. Вложения" folder under the course gets lucide-boxes.
Prints what it added or changed and the course notes still without an icon.
Usage: python apply_icons.py <course folder> <plan.json>
"""
import json
import os
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    course_dir, plan_path = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    vault = next(p for p in course_dir.parents if (p / ".obsidian").is_dir())
    VAULT, COURSE = vault, course_dir.relative_to(vault)
    CFG = VAULT / ".obsidian/plugins/iconic/data.json"
    plan = {k: v for k, v in json.loads(plan_path.read_text(encoding="utf-8")).items()
            if not k.startswith("_")}
    data = json.loads(CFG.read_text(encoding="utf-8"))
    icons = data["fileIcons"]
    wanted = {}
    for rel, spec in plan.items():
        key = str(COURSE / rel) if rel else str(COURSE)
        if (VAULT / key).exists():
            wanted[key] = spec
    for dp, dirs, _ in os.walk(VAULT / COURSE):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for d in dirs:
            if d == "00. Вложения":
                wanted[str(Path(dp, d).relative_to(VAULT))] = {"icon": "lucide-boxes"}
    changed = 0
    for key, spec in wanted.items():
        old = icons.get(key, {})
        new = {**old, **spec}
        if new != old:
            icons[key] = new
            changed += 1
            print(("set " if not old else "upd ") + key.removeprefix(str(COURSE) + "/"), spec)
    if changed:
        CFG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    json.loads(CFG.read_text(encoding="utf-8"))
    missing = []
    for dp, dirs, files in os.walk(VAULT / COURSE):
        # Obsidian does not index dot folders (.sources and the like), so they need no icon
        dirs[:] = [d for d in dirs if d != "00. Вложения" and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                key = str(Path(dp, f).relative_to(VAULT))
                if key not in icons:
                    missing.append(key.removeprefix(str(COURSE) + "/"))
    print(f"changed {changed}, config valid, md without icon: {len(missing)}")
    for m in missing:
        print("  missing", m)


if __name__ == "__main__":
    main()
