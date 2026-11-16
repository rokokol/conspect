"""Open a built page in headless Chromium, run steps, save screenshots.

Fails on any console error or uncaught exception, so a page that throws while
drawing is never reported as working. Fails too on a visible paragraph longer
than the conspect paragraph limit, read from the conspect skill, and on a
decimal number written with a dot in the text or on a canvas, by the rule of
ddlc_figures' ddlc_numbers.

Usage: python check_page.py [--json] <page.html> <outdir> [step ...]
A step is "set:<id>=<value>", "click:<id>@<fx>,<fy>", "hover:<id>@<fx>,<fy>",
"drag:<id>@<fx>,<fy>><fx>,<fy>", "wait:<ms>" (for a page that animates),
"click_button:<id>" (a click on an element by id, whatever its place),
"width:<px>" (a viewport that wide; the run then fails if the page scrolls sideways),
"dark" or "shot:<name>".
--json prints the report as one JSON object on the last line instead:
{"errors": [...], "overflow": "...", "long": [...], "dotted": [...]}. lint.py --pages reads it.
"""
import json
import re
import sys
from pathlib import Path


def vault():
    """The Obsidian vault this checker lives in: the nearest parent with .obsidian."""
    return next(p for p in Path(__file__).resolve().parents if (p / ".obsidian").is_dir())


# The rule of a decimal number written with a dot is the figures' own, so a page and a figure
# are held to one rule; the browser is the one the sandbox kit's own tests open
sys.path.insert(0, str(vault() / "Scripts/ddlc_figures"))
sys.path.insert(0, str(vault() / "Scripts"))
from ddlc_numbers import dotted_numbers  # noqa: E402
from sandbox_kit.browser import chromium  # noqa: E402


# A page is read like a conspect: the paragraph limit is the conspect skill's own rule.
_rule = re.search(r"Абзац прозы — не длиннее (\d+) слов",
                  (vault() / ".agents/skills/conspect/SKILL.md").read_text(encoding="utf-8"))
PARAGRAPH_MAX_WORDS = int(_rule.group(1))

# Every visible paragraph after the steps, including text the page script wrote.
LONG_PARAGRAPHS_JS = """(limit) => Array.from(document.querySelectorAll('p'))
  .filter((p) => p.offsetParent !== null)
  .map((p) => p.innerText.trim())
  .filter((t) => t.split(/\\s+/).filter(Boolean).length > limit)
  .map((t) => t.split(/\\s+/).length + ' words: ' + t.slice(0, 60))"""


# Every text a canvas draws, recorded from the first script of the page on. A page that sets
# indices draws a label one glyph at a time, each where the last one ended, so a call that
# starts at the end of the previous one on the same canvas continues its text: 0 . 5 is 0.5
CANVAS_TEXT_INIT = """window.__canvasText = [];
let run = null;
for (const name of ["fillText", "strokeText"]) {
  const draw = CanvasRenderingContext2D.prototype[name];
  CanvasRenderingContext2D.prototype[name] = function (text, x, ...rest) {
    const s = String(text), w = this.measureText(s).width, a = this.textAlign;
    const left = a === "center" ? x - w / 2 : a === "right" || a === "end" ? x - w : x;
    if (run && run.ctx === this && Math.abs(left - run.end) < 1) {
      run.text += s;
      window.__canvasText[run.i] = run.text;
    } else {
      run = { ctx: this, text: s, i: window.__canvasText.push(s) - 1 };
    }
    run.end = left + w;
    return draw.call(this, text, x, ...rest);
  };
}"""

# Every visible text of the page after the steps, and every text a canvas drew. An input keeps
# the dot its value is parsed with, code is code, and data-keep-dots marks a dot that is not a
# decimal one, such as the number of a problem
PAGE_TEXT_JS = """() => {
  const out = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n; (n = walk.nextNode());) {
    const el = n.parentElement;
    if (!el || el.closest("input, textarea, select, code, pre, script, style, [data-keep-dots]")) continue;
    if (!el.getClientRects().length) continue;
    const t = n.textContent.trim();
    if (t) out.push(t);
  }
  return out.concat(window.__canvasText || []);
}"""

OVERFLOW_JS = """() => {
  const d = document.documentElement;
  return d.scrollWidth > d.clientWidth ? 'content ' + d.scrollWidth + ' px in a viewport of ' + d.clientWidth + ' px' : '';
}"""


def main():
    from playwright.sync_api import sync_playwright

    args = sys.argv[1:]
    as_json = "--json" in args
    page_path, outdir, *steps = [a for a in args if a != "--json"]
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=chromium())
        pg = b.new_page(viewport={"width": 1100, "height": 900})
        pg.add_init_script(CANVAS_TEXT_INIT)
        pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
        pg.on("pageerror", lambda e: errors.append(str(e)))
        narrow = False
        pg.goto(Path(page_path).resolve().as_uri())
        pg.wait_for_timeout(300)
        for s in steps:
            kind, _, arg = s.partition(":")
            if kind == "set":
                el, val = arg.split("=", 1)
                pg.evaluate("([id, v]) => { const e = document.getElementById(id);"
                            " if (e.type === 'checkbox') e.checked = v === 'true'; else e.value = v;"
                            " e.dispatchEvent(new Event('input', {bubbles: true})); }", [el, val])
            elif kind in ("click", "hover"):
                el, _, pos = arg.partition("@")
                fx, fy = map(float, pos.split(","))
                # The mouse acts only inside the viewport; a canvas below the fold is scrolled to first.
                pg.locator(f"#{el}").scroll_into_view_if_needed()
                box = pg.locator(f"#{el}").bounding_box()
                at = (box["x"] + fx * box["width"], box["y"] + fy * box["height"])
                pg.mouse.click(*at) if kind == "click" else pg.mouse.move(*at)
            elif kind == "drag":
                el, _, pos = arg.partition("@")
                src, _, dst = pos.partition(">")
                (fx, fy), (gx, gy) = (map(float, src.split(",")), map(float, dst.split(",")))
                pg.locator(f"#{el}").scroll_into_view_if_needed()
                box = pg.locator(f"#{el}").bounding_box()
                pg.mouse.move(box["x"] + fx * box["width"], box["y"] + fy * box["height"])
                pg.mouse.down()
                pg.mouse.move(box["x"] + gx * box["width"], box["y"] + gy * box["height"], steps=8)
                pg.mouse.up()
            elif kind == "wait":
                pg.wait_for_timeout(int(arg))
            elif kind == "click_button":
                pg.locator(f"#{arg}").click()
            elif kind == "width":
                pg.set_viewport_size({"width": int(arg), "height": 900})
                narrow = True
            elif kind == "dark":
                pg.emulate_media(color_scheme="dark")
            elif kind == "shot":
                pg.wait_for_timeout(200)
                pg.screenshot(path=str(outdir / f"{arg}.png"), full_page=True)
            else:
                raise SystemExit(f"unknown step {s}")
        long = pg.evaluate(LONG_PARAGRAPHS_JS, PARAGRAPH_MAX_WORDS)
        dotted = sorted({t for t in pg.evaluate(PAGE_TEXT_JS) if dotted_numbers(t)})
        # only after a width step: a page that scrolls sideways at phone width is broken there
        overflow = pg.evaluate(OVERFLOW_JS) if narrow else None
        b.close()
    if as_json:
        report = {"errors": errors, "overflow": overflow or "", "long": long, "dotted": dotted}
        print(json.dumps(report, ensure_ascii=False))
        sys.exit(1 if any(report.values()) else 0)
    if errors:
        print("PAGE ERRORS:", *errors, sep="\n  ")
    if overflow:
        print("HORIZONTAL SCROLL:", overflow)
        errors.append("horizontal scroll")
    if long:
        print(f"LONG PARAGRAPHS (limit {PARAGRAPH_MAX_WORDS} words):", *long, sep="\n  ")
    if dotted:
        print("DOTTED NUMBERS (write them with toComma or formatNumber):", *(t[:80] for t in dotted), sep="\n  ")
    if errors or long or dotted:
        sys.exit(1)
    print("ok, no console errors, no long paragraphs, no dotted numbers")


if __name__ == "__main__":
    main()
