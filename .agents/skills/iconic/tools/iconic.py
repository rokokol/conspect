#!/usr/bin/env python3
"""Set, change and clear Iconic file and folder icons through the running Obsidian.

The Iconic plugin keeps its settings in memory and writes the whole object to
data.json on each save. A direct edit of data.json therefore races the plugin:
its next save can overwrite the edit, or the edit can overwrite a change made
in the UI. This tool changes the in-memory settings through `obsidian-cli eval`
and lets the plugin save them, then checks that data.json on disk agrees.

    iconic.py set PATH... [--icon ICON] [--color COLOR]
    iconic.py unset PATH... [--icon] [--color]     # no flag: remove the entry
    iconic.py apply SPEC.json | -                   # a spec of many paths
    iconic.py get PATH...

PATH is the plugin key, matched exactly: relative to the vault root, a note
with its extension, a folder without a trailing slash, "/" for the vault root.
SPEC maps PATH to {"icon": ..., "color": ...} or to null. A field that is
present sets the value, a null field removes it, and an absent field keeps the
current value. A null entry removes the whole entry. Setting an icon or a color
on a path that does not exist is refused; removing one is not.

A change prints {"after": ..., "undo": ...}. "undo" is a SPEC that puts the
old entries back through `apply`. `get` prints the current entries.

Every path is checked before any is written. A large spec is sent in parts,
and each part is one plugin save.

Global flags come before the subcommand:
    --vault DIR   vault root (default: four levels above this file)
    --offline     edit data.json directly; allowed only when Obsidian is not
                  reachable, because then no plugin holds the settings in memory

Exit codes: 0 success, 1 error, 2 usage, 3 Obsidian is not reachable
(start it, or rerun with --offline), 4 data.json on disk disagrees with the
app after the save.
"""
import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

UNREACHABLE = "The CLI is unable to find Obsidian"
DATA = ".obsidian/plugins/iconic/data.json"
FIELDS = ("icon", "color")
# The CLI transport decodes UTF-8 in pieces. A multi-byte character that a
# piece boundary splits becomes U+FFFD, and the damaged code still runs. Over
# 64 KiB this happens on most calls; from about 28 KB it happens on some calls,
# at random. The code template is ASCII, so the app checks the request for
# U+FFFD before it changes anything, and a damaged call is sent again.
MESSAGE_LIMIT = 30_000
DAMAGE = chr(0xFFFD)
ATTEMPTS = 5


class UsageError(Exception):
    pass


class AppError(Exception):
    pass


class Unreachable(Exception):
    pass


def check_ops(ops):
    """Validate a spec. Paths stay as written: a plugin key is an exact string."""
    if not isinstance(ops, dict):
        raise UsageError("spec must be a JSON object that maps paths to entries")
    if DAMAGE in json.dumps(ops, ensure_ascii=False):
        raise UsageError("spec contains U+FFFD, which marks damage in transit")
    for path, op in ops.items():
        # "/" is the key of the vault root folder; any other absolute path escapes the vault
        if path != "/" and (not path or path.startswith("/") or ".." in path.split("/")):
            raise UsageError(f"bad path: {path!r}")
        if op is not None:
            if not isinstance(op, dict) or not op:
                raise UsageError(f"{path}: entry must be null or an object with icon and/or color")
            extra = set(op) - set(FIELDS)
            if extra:
                raise UsageError(f"{path}: unknown fields {sorted(extra)}")
            for k, v in op.items():
                if v is not None and not isinstance(v, str):
                    raise UsageError(f"{path}: {k} must be a string or null")
    return ops


def undo_spec(before):
    """A spec that puts the given entries back, with explicit nulls"""
    return {p: (None if e is None else {k: e.get(k) for k in FIELDS}) for p, e in before.items()}


def merge(file_icons, ops):
    """Apply ops to a copy of fileIcons the way the plugin's updateIconSetting does.

    Returns the new mapping and the paths that would carry an icon or a color.
    """
    out = {k: dict(v) for k, v in file_icons.items()}
    needs = []
    for path, op in ops.items():
        cur = out.get(path, {})
        icon, color = cur.get("icon"), cur.get("color")
        if op is None:
            icon = color = None
        else:
            icon = op["icon"] if "icon" in op else icon
            color = op["color"] if "color" in op else color
        if icon or color:
            needs.append(path)
            entry = out.setdefault(path, {})
            for k, v in (("icon", icon), ("color", color)):
                if v:
                    entry[k] = v
                else:
                    entry.pop(k, None)
        else:
            out.pop(path, None)
    return out, needs


def plugin_order(keys):
    """Order keys as Object.entries(x).sort() does in the plugin.

    The default comparator compares "key,[object Object]" by UTF-16 code units.
    """
    return sorted(keys, key=lambda k: (k + ",[object Object]").encode("utf-16-be"))


def chunk(ops, limit):
    """Split ops so that each part serialises to at most limit bytes"""
    parts, cur, size = [], {}, 2
    for path, op in ops.items():
        # The braces of a one-item object take the place of the ", " separator
        item = len(json.dumps({path: op}, ensure_ascii=False).encode())
        if cur and size + item > limit:
            parts.append(cur)
            cur, size = {}, 2
        cur[path] = op
        size += item
    if cur:
        parts.append(cur)
    return parts


APPLY_JS = r"""(async()=>{
const ops=__OPS__;
if(JSON.stringify([ops,__BASE__]).includes(String.fromCharCode(0xfffd)))return JSON.stringify({damaged:true});
if(app.vault.adapter.basePath!==__BASE__)return JSON.stringify({error:"Obsidian has another vault open: "+app.vault.adapter.basePath});
const p=app.plugins.plugins.iconic;
if(!p)return JSON.stringify({error:"Iconic plugin is not loaded"});
const plan=[],missing=[],fields=new Set();
for(const [id,op] of Object.entries(ops)){
  const cur=p.settings.fileIcons[id]??{};
  let icon=cur.icon??null,color=cur.color??null;
  if(op===null){icon=null;color=null}else{if("icon" in op)icon=op.icon;if("color" in op)color=op.color}
  if((icon||color)&&!app.vault.getAbstractFileByPath(id))missing.push(id);
  if((icon||null)!==(cur.icon??null))fields.add("icon");
  if((color||null)!==(cur.color??null))fields.add("color");
  plan.push([id,icon,color]);
}
if(missing.length)return JSON.stringify({error:"no such file or folder",missing});
if(__WRITE__){
  for(const [id,icon,color] of plan)p.updateIconSetting(p.settings.fileIcons,id,icon,color);
  for(let i=0;p.isSaving;i++){if(i>200)return JSON.stringify({error:"Iconic is still saving after 10 s"});await sleep(50)}
  await p.saveSettings();
  if(fields.size)p.ruleManager?.triggerRulings("file",...fields);
  p.refreshManagers("file","folder");
}
return JSON.stringify({entries:Object.fromEntries(plan.map(([id])=>[id,p.settings.fileIcons[id]??null]))});
})()"""


def apply_js(ops, base, write=True):
    return (APPLY_JS.replace("__OPS__", json.dumps(ops, ensure_ascii=False))
            .replace("__BASE__", json.dumps(base, ensure_ascii=False))
            .replace("__WRITE__", "true" if write else "false"))


def ops_budget(base):
    """Bytes left for the ops JSON once the code and the base path are in the command"""
    return MESSAGE_LIMIT - len(apply_js({}, base).encode()) - 1024


def parse_eval(out):
    """Read `eval` output: the CLI prints app errors on stdout and exits 0"""
    text = out.strip()
    if text.startswith("Error: "):
        raise AppError(text[len("Error: "):])
    if not text.startswith("=> "):
        raise AppError(f"unexpected CLI output: {text[:200]!r}")
    try:
        value = json.loads(text[3:])
        if isinstance(value, str):
            value = json.loads(value)
    except json.JSONDecodeError:
        raise AppError(f"CLI output is not JSON: {text[:200]!r}") from None
    if isinstance(value, dict) and "error" in value:
        detail = value["error"]
        if value.get("missing"):
            detail += ": " + ", ".join(value["missing"])
        raise AppError(detail)
    return value


def cli_binary():
    found = os.environ.get("OBSIDIAN_CLI") or shutil.which("obsidian-cli")
    if not found:
        raise AppError("obsidian-cli not found; set OBSIDIAN_CLI to the CLI binary")
    return found


def run_eval(vault, code):
    """Run code in the app. Every call here is safe to repeat: a write sets absolute values."""
    if len(code.encode()) > MESSAGE_LIMIT:
        raise AppError(f"command is over {MESSAGE_LIMIT} bytes; the CLI would damage it")
    for _ in range(ATTEMPTS):
        r = subprocess.run([cli_binary(), f"vault={vault.name}", "eval", f"code={code}"],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if UNREACHABLE in r.stdout + r.stderr:
            raise Unreachable()
        if r.returncode != 0:
            raise AppError(f"CLI exited {r.returncode}: {(r.stdout + r.stderr).strip()[:300]}")
        if DAMAGE in r.stdout:
            continue
        value = parse_eval(r.stdout)
        if isinstance(value, dict) and value.get("damaged"):
            continue
        return value
    raise AppError(f"the CLI damaged the request or the reply {ATTEMPTS} times in a row")


def read_data(vault):
    return json.loads((vault / DATA).read_text(encoding="utf-8"))


def online(vault, ops, write):
    base = str(vault)
    parts = chunk(ops, ops_budget(base))
    # A read-only pass first checks every part for missing paths, so a refusal
    # leaves no partial batch. It also gives the old entries for the undo spec.
    before = {}
    for part in parts:
        before.update(run_eval(vault, apply_js(part, base, write=False))["entries"])
    if not write:
        return before, before, 0
    after = {}
    for part in parts:
        after.update(run_eval(vault, apply_js(part, base))["entries"])
    disk = read_data(vault)["fileIcons"]
    bad = [p for p, e in after.items() if disk.get(p) != e]
    if bad:
        sys.stderr.write("data.json disagrees with the app for: " + ", ".join(bad) + "\n")
        return before, after, 4
    return before, after, 0


def offline(vault, ops, write):
    try:
        run_eval(vault, "1")
    except Unreachable:
        pass
    except AppError as e:
        raise AppError(f"cannot confirm that Obsidian is closed: {e}") from None
    else:
        raise AppError("Obsidian is running; drop --offline so the plugin makes the change")
    data = read_data(vault)
    new, needs = merge(data["fileIcons"], ops)
    if write:
        missing = [p for p in needs if not (vault / p).exists()]
        if missing:
            raise AppError("no such file or folder: " + ", ".join(missing))
        before = {p: data["fileIcons"].get(p) for p in ops}
        data["fileIcons"] = {k: new[k] for k in plugin_order(new)}
        (vault / DATA).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return before, {p: new.get(p) for p in ops}, 0
    before = {p: data["fileIcons"].get(p) for p in ops}
    return before, before, 0


def build_ops(args):
    if args.cmd == "set":
        if args.icon is None and args.color is None:
            raise UsageError("set needs --icon and/or --color")
        op = {k: v for k, v in (("icon", args.icon), ("color", args.color)) if v is not None}
        return {p: dict(op) for p in args.paths}
    if args.cmd == "unset":
        fields = [k for k in FIELDS if getattr(args, k)]
        return {p: ({k: None for k in fields} if fields else None) for p in args.paths}
    if args.cmd == "apply":
        src = sys.stdin if args.spec == "-" else open(args.spec, encoding="utf-8")
        with src:
            return json.load(src)
    raise UsageError(f"unknown command {args.cmd}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[4])
    ap.add_argument("--offline", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set", help="set an icon and/or a color")
    s.add_argument("paths", nargs="+")
    s.add_argument("--icon")
    s.add_argument("--color")
    u = sub.add_parser("unset", help="remove the icon, the color, or the whole entry")
    u.add_argument("paths", nargs="+")
    u.add_argument("--icon", action="store_true")
    u.add_argument("--color", action="store_true")
    a = sub.add_parser("apply", help="apply a JSON spec of many paths")
    a.add_argument("spec")
    g = sub.add_parser("get", help="print the current entries")
    g.add_argument("paths", nargs="+")
    args = ap.parse_args(argv)
    vault = args.vault.resolve()
    try:
        write = args.cmd != "get"
        if write:
            ops = check_ops(build_ops(args))
        else:
            ops = {p: {} for p in check_ops({p: None for p in args.paths})}
        before, after, code = (offline if args.offline else online)(vault, ops, write)
    except UsageError as e:
        ap.error(str(e))
    except Unreachable:
        sys.stderr.write("Obsidian is not reachable. Start it and rerun, or rerun with --offline "
                         "if it must stay closed.\n")
        return 3
    except (AppError, OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"error: {e}\n")
        return 1
    out = {"after": after, "undo": undo_spec(before)} if write else after
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
