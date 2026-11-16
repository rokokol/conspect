# Brief: interactive sandboxes for the discrete math course

Course: `~/Projects/conspect/04. Дискретная математика/` (notes in `content/NN. Тема/`). The owner wants interactive HTML pages ("песочницы") on key topics, the same model as the ML course `~/Projects/conspect/13. Машинное обучение/Тренировки по ML/.sources/interactive/` — read its `README` in `.sources/README.md`, `build_pages.py`, `install_pages.sh`, `check_page.py`, `pages/_common.*` and one page (e.g. `pages/entropy.html`) before you start

## Rules

- Read `briefs/common.md` first: the rules for every digitization agent. Its resource limits apply to every `node --test`, playwright and Chromium run
- Load the `conspect` skill: its section "Вложения" defines the `▶` line in a note and the page name `<тема>-песочница.html`. Pages are Russian; paragraph ≤ 60 words (check_page enforces it)
- Fonts and colours come from `sandbox_kit`: it subsets and inlines the vault fonts, and its `theme.js` gives the ddlc palette roles. The course sets no font and types no hex. A canvas reads every colour through `css()` from `theme.js` at each redraw, never from a cache: the role (`--text`) or any CSS expression (`color-mix(...)`). Do not add a course-local `col()`. Light and dark theme
- Every decimal number goes through `toComma` or `formatNumber` from `sandbox_kit/number.js`. At 1x a screenshot shows a gap after the comma ("2, 3839"); at 3x it reads "2,1346". This is downscaling, not a font defect
- A page works offline from a file link: no CDN, no fetch; everything inlined by the build
- One source of truth: course-agnostic machinery is never copied into a course. The build (font subsetting and inlining, palette CSS, number formatting) is `~/Projects/conspect/Scripts/sandbox_kit/`; the headless page checker is the conspect skill's `tools/check_page.py`. Only course-specific code stays in a course
- The discrete-math logic lives in one module `.sources/interactive/dmcore.js` (pure functions, ES module), tested by `node --test` against a python reference (`export_fixtures.py` using sympy/networkx and plain python, writing `fixtures.json`, git-ignored). Load the `tests` skill before writing tests; every test must be seen failing once
- Python: `~/.cache/discrete-math-digitization/.venv/bin/python` (has playwright, sympy, networkx; install nothing globally). Chromium for playwright as the ML checker does it (from nix)
- Each page is checked with `check_page.py` in light and dark, and the course passes `lint.py --pages "<course>"` from the conspect skill. A green `check_page` checks the console and paragraph length, not contrast. Open with Read every plot of every tab in the dark theme and at 390 px width, and name in the report each screenshot you opened
- After a change to the shared kit, rebuild the pages of every course that uses it: `PY=<venv> bash interactive/install_pages.sh` in the course `.sources`, then `lint.py --pages`
- After a page is installed into its topic's `00. Вложения/`, add its `▶` line to the owning note (Edit), in the section whose mechanism the page lets you touch

## Pages (owning note → page)

1. "Полином Жегалкина" → `boolean-песочница.html`: enter a truth table (n ≤ 4) or a formula; see СДНФ, СКНФ, the fast algorithm step by step to the Zhegalkin polynomial, membership in T0, T1, L, S, M with the witness for each "не лежит". One `▶` line, in "Полином Жегалкина" (the section on the fast algorithm); the line names the class check too
2. "Сокращённая ДНФ и метод Нельсона" → `nelson-песочница.html`: a CNF in, the Nelson steps (D1, D2) shown, the reduced DNF out
3. "Кратчайшее остовное дерево" → `mst-песочница.html`: a weighted graph (preset K5 from the note + editable weights), the algorithm step by step, accepted/rejected edges
4. "Критерий взаимной однозначности кода" → `code-graph-песочница.html`: type code words; see G_φ, the cycle through Λ if any, and the ambiguous word with its two parsings
5. "Теорема редукции и метод Хаффмана" → `huffman-песочница.html`: frequencies in; merges step by step, the tree, the code, its cost and the entropy
6. "Код Хэмминга" → `hamming-песочница.html`: choose n, set data bits, see the code word; flip any bit; see the syndrome and the corrected position
7. "Теорема Мура" → `automaton-песочница.html`: the 3-state automaton of the note (and an editable table); run an input word from any state; see the classes R_m refine step by step

Build them in this order; after page 1 and the shared kit, stop and report (the session will review before you continue)

## Report (besides what `common.md` requires)

Files created/changed (with the shared kit and the ML switch-over), test results (counts, seen-failing evidence), check_page results and what the screenshots show, `▶` lines added, anything unresolved
