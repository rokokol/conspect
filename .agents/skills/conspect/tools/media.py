"""The walk over the vault's figure scripts and sandbox pages for lint.py --figures and --pages.

A figure script is a .py file of a course's .sources that saves a figure and is not a kit, a
test or a page builder; check_numbers.py runs it under its course's interpreter. A sandbox is
a built page that matches the pages glob; check_page.py opens it with the configured steps.
Both lists of courses and interpreters live in media.json beside this file.

The texts of a figure exist only once it is drawn, so a script runs whole and, as always,
writes its figures over the old ones in the attachments, which git does not keep: a walk over
the figures is a redrawing.

A result is cached by a digest of everything that can change it: the file, the modules of its
course, the shared files, the checker and the interpreter. A cached file is not run again, so
a second run over an unchanged vault takes seconds. A run that failed is never cached: the
cause may be the machine, not the file. The cache belongs to the machine, because each machine
has its own interpreters.
"""
import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile

TOOLS = pathlib.Path(__file__).resolve().parent
CONFIG = TOOLS / "media.json"
CACHE = pathlib.Path(os.environ.get("XDG_CACHE_HOME") or pathlib.Path.home() / ".cache") / "conspect-lint" / "media.json"
FIGURE_CHECK = TOOLS / "check_numbers.py"
PAGE_CHECK = TOOLS / "check_page.py"

# code → what the finding says; lint.py's catalogue holds the level and the rule
CODES = ("figure-dotted-number", "figure-failed",
         "page-error", "page-scroll", "page-paragraph-long", "page-dotted-number")
FIGURE_CODES = {c for c in CODES if c.startswith("figure-")}
PAGE_CODES = {c for c in CODES if c.startswith("page-")}

SKIP_DIRS = {"interactive", "__pycache__", "vendor"}
# a kit, a test and a demo of a kit are tools, not figures: a demo draws where it is told
KIT = re.compile(r"(^test_|^demo_|^course\.py$|fig\.py$|^figkit\.py$|^theme\.py$|_common\.py$|^__init__\.py$|^conftest\.py$)")
SAVES = re.compile(r"savefig\(|\bsave\(|\.save\(|imwrite\(|\bgif\(|^@fig\(", re.M)
TIMEOUT = 900


def load_config(path=None):
    """media.json with ~ expanded in every command"""
    cfg = json.loads(pathlib.Path(path or CONFIG).read_text(encoding="utf-8"))
    expand = lambda cmd: [os.path.expanduser(a) for a in cmd]  # noqa: E731
    cfg["figures"] = {course: expand(cmd) for course, cmd in cfg.get("figures", {}).items()}
    if "pages" in cfg:
        cfg["pages"]["python"] = expand(cfg["pages"]["python"])
    return cfg


class Cache:
    """{key: {"digest": …, "findings": [[code, msg], …]}}, written after every put"""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        try:
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.data = {}

    def get(self, key, digest):
        hit = self.data.get(key)
        return [tuple(f) for f in hit["findings"]] if hit and hit["digest"] == digest else None

    def put(self, key, digest, findings):
        self.data[key] = {"digest": digest, "findings": [list(f) for f in findings]}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.path)


def _files(path):
    """A file, or every file of a folder but bytecode, in a fixed order"""
    path = pathlib.Path(path)
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def _digest(*parts):
    h = hashlib.sha256()
    for part in parts:
        if isinstance(part, pathlib.Path):
            for f in _files(part):
                h.update(f.as_posix().encode() + b"\0" + f.read_bytes() + b"\0")
        else:
            h.update(json.dumps(part, ensure_ascii=False).encode() + b"\0")
    return h.hexdigest()


def course_of(path):
    """The nearest folder that holds a .sources, or None"""
    for p in [path, *path.parents]:
        if (p / ".sources").is_dir():
            return p
    return None


def in_scope(item, roots):
    """No roots is the whole vault. A root takes what lies under it, and a root inside a
    course takes the whole course: a note's figures and pages live elsewhere in its course"""
    if not roots:
        return True
    course = course_of(item)
    return any(root == item or root in item.parents or (course and (course == root or course in root.parents))
               for root in roots)


def figure_scripts(vault, config):
    """(script, interpreter) for every figure script of every configured course"""
    for course, cmd in sorted(config.get("figures", {}).items()):
        sources = vault / course / ".sources"
        if not sources.is_dir():
            continue
        for p in sorted(sources.rglob("*.py")):
            if SKIP_DIRS & set(p.relative_to(sources).parts):
                continue
            if not KIT.search(p.name) and SAVES.search(p.read_text(encoding="utf-8")):
                yield p, cmd


def _run(cmd, cwd):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return "timeout", "", f"дольше {TIMEOUT} с"


def _tail(err, n=2):
    lines = [ln for ln in err.strip().splitlines() if ln.strip()]
    return " · ".join(lines[-n:]) or "без вывода"


def check_figures(vault, config, roots, cache, checker=None, log=print):
    """(findings as (code, rel, line, msg), rels walked)"""
    checker = pathlib.Path(checker or FIGURE_CHECK)
    shared = [vault / p for p in config.get("figures_shared", [])]
    shared_digest = _digest(checker, *shared)
    findings, walked, course_digests = [], set(), {}
    for script, cmd in figure_scripts(vault, config):
        if not in_scope(script, roots):
            continue
        rel = script.relative_to(vault).as_posix()
        walked.add(rel)
        sources = vault / next(p for p in script.relative_to(vault).parents if p.name == ".sources")
        if sources not in course_digests:
            course_digests[sources] = _digest(*[p for p in _files(sources) if p.suffix == ".py"])
        digest = _digest(shared_digest, course_digests[sources], cmd, rel)
        hit = cache.get(rel, digest)
        if hit is None:
            log(f"рисунок: {rel}")
            rc, out, err = _run([*cmd, str(checker), script.name], script.parent)
            # the checker discards the script's output, but a library that writes to the
            # descriptor itself can still reach stdout: a text line starts with the script
            texts = [ln.split("\t", 2)[2] for ln in out.splitlines()
                     if ln.count("\t") >= 2 and ln.split("\t", 1)[0].endswith(".py")]
            if rc == 0 or (rc == 1 and texts):
                hit = [("figure-dotted-number", t) for t in texts]
                cache.put(rel, digest, hit)
            else:
                hit = [("figure-failed", f"код {rc}: {_tail(err)}")]
        findings += [(code, rel, 0, msg) for code, msg in hit]
    return findings, walked


def page_files(vault, config):
    pages = config.get("pages")
    return sorted(vault.glob(pages["glob"])) if pages else []


def check_pages(vault, config, roots, cache, checker=None, log=print):
    """(findings as (code, rel, line, msg), rels walked)"""
    checker = pathlib.Path(checker or PAGE_CHECK)
    pages = config.get("pages")
    if not pages:
        return [], set()
    shared_digest = _digest(checker, *[vault / p for p in pages.get("shared", [])], pages["python"], pages["steps"])
    findings, walked = [], set()
    for page in page_files(vault, config):
        if not in_scope(page, roots):
            continue
        rel = page.relative_to(vault).as_posix()
        walked.add(rel)
        digest = _digest(shared_digest, page)
        hit = cache.get(rel, digest)
        if hit is None:
            log(f"страница: {rel}")
            with tempfile.TemporaryDirectory() as shots:
                rc, out, err = _run([*pages["python"], str(checker), "--json", str(page), shots, *pages["steps"]],
                                    page.parent)
            try:
                report = json.loads(out.strip().splitlines()[-1]) if rc in (0, 1) else None
            except (ValueError, IndexError):
                report = None
            if report is None:
                hit = [("page-error", f"проверка не отработала, код {rc}: {_tail(err)}")]
            else:
                hit = ([("page-error", e) for e in report.get("errors", [])]
                       + ([("page-scroll", report["overflow"])] if report.get("overflow") else [])
                       + [("page-paragraph-long", t) for t in report.get("long", [])]
                       + [("page-dotted-number", t) for t in report.get("dotted", [])])
                cache.put(rel, digest, hit)
        findings += [(code, rel, 0, msg) for code, msg in hit]
    return findings, walked
