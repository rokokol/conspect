# Brief: lecture markup for the discrete math re-digitization

Course: "Дискретная математика", lecturer В. Б. Алексеев (ВМК МГУ), 21 video lectures (Teach-in playlist). We rewrite the Obsidian notes from scratch, organised by TOPIC, not by lecture. Your job is the markup that lets the session build the topic map. You do not write notes. Read `briefs/common.md` first: the rules for every digitization agent

## Sources (all under ~/.cache/discrete-math-digitization/)

- `teachin-synopsis.pdf` — a student synopsis of every lecture, 108 A4 pages. READ PAGES AS IMAGES with the Read tool and the `pages` parameter (max 20 pages per call); `pdftotext` garbles indices and bars. Page ranges: L1 6–10, L2 11–14, L3 15–19, L4 20–25, L5 26–29, L6 30–33, L7 34–37, L8 38–41, L9 42–47, L10 48–51, L11 52–56, L12 57–62, L13 63–67, L14 68–73, L15 74–77, L16 78–81, L17 82–85, L18 86–91, L19 92–96, L20 97–103, L21 104–108. Students made it; it can contain errors
- `transcripts/LNN.whisper.txt` — Whisper transcript, lines `[HH:MM:SS] text` (may not exist yet for later lectures)
- `subs/LNN.txt` — YouTube auto-subs, same format, worse words but correct times. Use when the Whisper file is missing. Run `python3 vtt2txt.py subs/LNN.ru-orig.vtt` if `subs/LNN.txt` is missing but the .vtt exists
- `playlist.txt` — lecture number and YouTube id
- `old/` — the old notes (poor quality, with known errors). Only for context; never copy text from them
- `frame.sh NN MM:SS` — extracts one board frame as PNG (only if the video is downloaded; optional)

## What to return (as your final text, in Russian; do not write files)

For each lecture assigned to you, a block:

```
## LNN — <title from the synopsis>
video: https://www.youtube.com/watch?v=<id>   length: H:MM:SS
synopsis pages: a–b

| Start | End | Block | Kind | Synopsis p. | Notes |
|---|---|---|---|---|---|
| 00:02:37 | 00:09:10 | Определение ФАЛ, таблица истинности | def | 6 | |
...
```

- One row per coherent block: a definition, a theorem with its proof, a lemma, an example, an algorithm, a recap of the previous lecture, an organisational aside
- Kind: `def`, `thm` (with proof), `thm-np` (no proof given), `lemma`, `example`, `algo`, `recap`, `aside`, `remark`
- Start = the second the lecturer starts this block in the video (from the transcript). Be precise to ~10 s
- Mark recaps of earlier material explicitly (`recap`) with what lecture they repeat
- Notes: lecturer's slips you notice (a wrong formula said or written), places where the synopsis disagrees with what the lecturer says, named results (e.g. "теорема Поста", "лемма о несамодвойственной функции"), notation the lecturer uses

After the tables, a section `### Нотация лектора`: the symbols he uses (how he writes the set {0,1}^n, tuples, negation, conjunction, closure, classes, graph quantities p, q, r, code lengths and the like), as LaTeX, with synopsis page

Then `### Предложение по заметкам`: which topic notes these blocks naturally fall into (a topic note is one concept bundle, e.g. "Полином Жегалкина", "Теорема Поста о полноте", "Планарные графы"), with the block rows each note would take. Keep proofs with their theorems. Do not split a concept across notes without reason

Be complete: every minute of the lecture belongs to some row. Do not invent material that is not in the lecture
