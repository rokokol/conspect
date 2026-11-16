# Brief: author of topic notes, discrete math re-digitization

Course: "Дискретная математика", lecturer В. Б. Алексеев (ВМК МГУ), 21 video lectures on the Teach-in YouTube channel. The owner's Obsidian vault is `~/Projects/conspect`. The old notes of this course were poor (math errors, missing proofs), so we write the notes FROM SCRATCH from the lectures. Notes are written in Russian. You write the notes assigned to you in your task, nothing else

## Read first

0. `briefs/common.md` — rules for every digitization agent: file edits, scratch files, resource limits, facts, report
1. Load the `conspect` skill (Skill tool) and follow it: it is the only standard for how a note looks. Then read its files: `presets/lecture.md`, `references/frontmatter.md` (type B), `references/callouts.md`, `references/theorem-proof-patterns.md`, `references/notation.md` (section "Дискретная математика" is for this course), `references/wikilinks.md` (timecode anchors), `references/math.md`. The skill lives in `~/Projects/conspect/.agents/skills/conspect/`
2. `~/.cache/discrete-math-digitization/map.md` — the approved topic map: every note, its MOC, its folder and the exact lecture blocks it takes. Your note covers exactly its blocks
3. `~/.cache/discrete-math-digitization/markup/L01-07.md`, `L08-14.md`, `L15-21.md` — per-lecture block tables with timecodes, synopsis pages, lecturer's slips and notation

## Sources (all under ~/.cache/discrete-math-digitization/)

- `transcripts/LNN.whisper.txt` — Whisper transcript `[HH:MM:SS] text`. Use it for timecodes and for what the lecturer actually says. If it is missing, use `subs/LNN.txt` (auto-subs, correct times, bad words)
- `teachin-synopsis.pdf` — student synopsis, A4. Read the pages as images with the Read tool and `pages` (page ranges are in the markup). Use it for formulas and proof structure. Students made it; it has errors (the markup lists the known ones). When it disagrees with the lecture, the lecture wins
- `frame.sh NN MM:SS` — writes one board frame PNG from the video and prints its path; then Read the PNG. Use it to settle a formula or to see a drawing. Videos may still be downloading; if `video/LNN.mp4` is absent, skip
- `playlist.txt` — lecture number and YouTube id
- `old/` — the old notes. Use them only as a checklist of topics; never copy their text, they contain errors

## Content rules

- Follow the lecturer's own definitions, method, order and proofs. Do not substitute a textbook proof. Every theorem the lecturer proves gets its full proof, readable and multiline (the skill's theorem-proof pattern). A statement he gives without proof is marked as such
- Cover every block of your note's ranges, except organisational asides. A historical or motivating aside that carries a fact goes into a footnote
- Whisper sometimes drops or garbles words, which looks like a slip. Before footnoting any slip, confirm it in `subs/LNN.txt` and by listening: `~/.cache/discrete-math-digitization/listen.sh NN MM:SS MM:SS` (lecture number, window start and end) prints six readings of the window. A slip he corrects within a few seconds gets no footnote
- A lecturer's slip that he does not correct himself: write the correct version and add a footnote saying what was said or written, with the timecode link, and how it differs. A synopsis error needs no footnote
- Material beyond the lecture follows the boundary in `common.md`. A name he does not say, such as "алгоритм Краскала", goes in bold and into the aliases, with no footnote. Added material, such as a problem or a number he does not give, gets the footnote "не из лекции". Never present added material as the lecture's
- Every H2 with lecture content and every callout with a theorem, definition or proof carries a timecode in its title: `[12:34](https://www.youtube.com/watch?t=754&v=<id>)`. Seconds in `t=` must equal the shown time. Take every timecode from the Whisper transcript at the second the lecturer starts that block (the theorem is announced, the definition begins); the markup times come from auto-subs and are off by 10–30 s, so use them only to find the place. A note taking several lectures links each block to its own video
- Notation: the section "Дискретная математика" of `notation.md`, and its general table: `\leqslant`/`\geqslant`, never `\le`/`\ge`. The lecturer's own symbols are listed in the markup
- Density: a working notebook, not a textbook. Paragraph ≤ 60 words, figure caption ≤ 40. No intro blockquote, no roadmap, no "Смежное" tail, no trailing full stops at paragraph end, straight quotes
- Worked examples: give the lecturer's examples. Check every computed value yourself with python (truth tables, polynomials, counts, codes) before writing it

## Owner's style decisions (after wave 1)

- A statement the lecturer gives without proof keeps a nested collapsed `> > [!note]- Без доказательства` block with what he says instead (e.g. "проверяется перебором"), one per callout
- A proof the lecturer only sketches or calls "аналогично" may be written out in full, with no marker. Your own derivations and conclusions also get no marker, but never write "лектор показывает" about them
- A note is not a report of your work. Check values with python, scripts or transcripts, but never write how you checked: no "при оцифровке", "проверено скриптом", "в python", "по Whisper и автосубтитрам". "Не из лекции" is the only marker the reader needs
- No course logistics: exams, tickets, tests, homework, "оставляет упражнениям", "на следующей лекции". Keep the content without the frame ("на экзамене путают X и Y" → "X и Y часто путают"); a forward reference becomes a link to the note. The conspect skill holds the full rule
- Timecodes are written `MM:SS` (two-digit minutes, `07:27`) or `H:MM:SS` (`1:05:57`), never `1:24` for 1 min 24 s
- The markup tables may misattribute ("на экзамене", "лектор подтверждает"); a claim about what he says must be checked in the transcript
- A short example not from the lecture is welcome where the lecturer gives none and the idea is hard to grasp without one: verify it with python and mark it with a footnote "не из лекции"
- When the lecturer misnames a concept, the heading uses the correct name and a footnote says what he called it, with the timecode
- Reference notes of wave 1 for density and form: `content/01. Функции алгебры логики/` (all six)

## Frontmatter (type B), exact shape

```yaml
---
title: Алексеев В. Б. — Дискретная математика — <Тема>
up: "[[fNN. <Тема MOC> — MOC]]"
prev: "[[<previous note in map order>]]"
next: "[[<next note in map order>]]"
lectures:
  - "1"
sources:
  - "[Лекция 01 — Функции алгебры логики](https://www.youtube.com/watch?v=SAhzEOVDNEI)"
created: 2026-10-03
summary: <one sentence>
tags:
  - мгу
  - алексеев
aliases:
  - <terms this note owns>
---
```

- `prev`/`next`: the note before/after yours in the numbered list of `map.md` (note 1 has no `prev`, note 41 has no `next`). These targets may not exist yet; that is fine
- `lectures`: every lecture the note takes blocks from. `sources`: one line per lecture, with the lecture title from the markup
- Aliases: the terms the note defines and someone would search for, lowercase unless a proper name; a name of a concept, never a descriptive phrase ("функции двух переменных", "константа 0 и константа 1" are not aliases). An abbreviation the note expands (ФАЛ, ДНФ, КОД, СФЭ) goes into the aliases of the note that owns it. Before adding one, grep the vault for the same alias in other notes (`grep -rn "  - <alias>$" --include='*.md' ~/Projects/conspect ~/myWiki | grep -v "04. Дискретная математика/f"`); ignore the old `fNN.` notes of this course, they will be deleted. Report any collision with another course instead of adding a duplicate silently

## Links

- Inside the course: link to the other notes by their exact names from `map.md` (they may not exist yet), with `#heading` where useful. A recap by the lecturer of earlier material is a link to the owning note, never a re-definition
- Across courses (mandatory where the concept is already in the vault; check the target with ls/grep first): architecture `~/Projects/conspect/17. Архитектура компьютеров/content/03. Элементная база цифровых ЭВМ/` ("Логические вентили", "Комбинационные схемы", "Арифметико-логическое устройство"); probability `~/Projects/conspect/11. Теория вероятностей и математическая статистика/content/01. Комбинаторика/` ("Перестановки, размещения, сочетания"), "Случайный граф (модель Эрдёша–Реньи)"; ML "Энтропия и кросс-энтропия", "Решающее дерево"; networks `~/Projects/conspect/16. Компьютерные сети/content/` (spanning tree in STP, topologies). Link inside the word that already stands in the text
- Block anchors `^id` only where something links to them
- Obsidian matches aliases case-insensitively: "КОД" (кратчайшее остовное дерево) already exists, so a coding note never takes the bare alias "код"; use a precise alias such as "алфавитный код" or "кодовое слово"
- In one line (paragraph, list item, callout line) the same term links to its note once; a repeated mention stays plain text. Different terms of one note may each get a link
- A cross-course abbreviation (ОС, CPU, СЛАУ…) may already have a term note in `~/Projects/conspect/00. Термины/` (`presets/term.md` of the skill): link to it instead of expanding it again. An abbreviation of this course (ФАЛ, ДНФ, СФЭ…) is expanded once in its owning note of this course

## Figures

- Truth tables, class membership tables, code tables: markdown tables
- Graphs, trees, planar drawings, colourings, code trees, circuits: a matplotlib script `~/Projects/conspect/04. Дискретная математика/.sources/figures/NN/<name>.py` that writes `<name>.png` into the topic folder `content/NN. <Тема>/00. Вложения/`. It does `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` and `import dmfig`: `dmfig` sets the course root and the ddlc theme, and gives colour roles (`VERTEX`, `EDGE`, `HIGHLIGHT`, `MUTED`, `COLOURS` for colourings, palette `P`), `draw_graph(ax, pos, edges, ...)` and `save(fig, topic_number, name)` that writes the PNG into the right topic folder. Read `dmfig.py` before your first figure. Python: `~/.cache/discrete-math-digitization/.venv/bin/python` (matplotlib, networkx, sympy). Look at every PNG you produce at full size before embedding it. A legend for any visual convention goes on the figure itself
- Automaton diagrams and flowcharts may be Mermaid: load the `mermaid` skill first
- Embed with the bare name: `![[name.png|400]]`

## Writing and checking

- Create each note with the Write tool at `~/Projects/conspect/04. Дискретная математика/content/NN. <Тема>/<Note>.md` (create the folder's `00. Вложения/` with an empty `.nomedia` file if you add images). Do not edit any other note, any MOC, or the old `fNN.` notes
- Run `python3 ~/Projects/conspect/.agents/skills/conspect/tools/lint.py --all "<path of your note>"` and fix every finding of level "достоверно" that comes from your text. Findings about links to notes that do not exist yet are expected

## Report (besides what `common.md` requires)

- The files you created
- Coverage: for each block of your ranges, where it went (or why it was dropped)
- Lecturer slips you footnoted; synopsis errors you met; outside material you added and how you marked it
- Alias collisions and anything you could not settle (with timecode)
- Lint result after your fixes
