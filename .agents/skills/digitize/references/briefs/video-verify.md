# Brief: verifier of topic notes, discrete math re-digitization

Course: "Дискретная математика", lecturer В. Б. Алексеев (ВМК МГУ). Notes in `~/Projects/conspect/04. Дискретная математика/content/` were just written by authors from the lectures. You check them. You EDIT NOTHING: you find defects and report them

Read `briefs/common.md` first (rules for every digitization agent; its list of frequent findings is where you look first), then `~/.cache/discrete-math-digitization/briefs/author.md`: it states the rules the authors followed and where the sources are (`transcripts/`, `subs/`, `teachin-synopsis.pdf` read as page images, `frame.sh` for board frames, `markup/`, `map.md`). Load the `conspect` skill for the style rules

To settle what the lecturer actually said (Whisper drops words), use `~/.cache/discrete-math-digitization/listen.sh NN MM:SS MM:SS`: six readings of the window

Your role is given in your task:

- **fidelity** — every timecode link opens the right moment (compare with the transcript; `t=` seconds equal the shown time); every definition, statement and proof matches what the lecturer says and writes (transcript + synopsis + board frames for disputed formulas); nothing from the note's blocks in `map.md` is missing; nothing outside the lecture is presented as the lecture's; lecturer slips are footnoted correctly
- **math** — read every proof in full and check every step is valid and complete; check every definition is exact; recompute every computed value with python (truth tables, СДНФ/СКНФ, Zhegalkin polynomials, class membership, counts, codes, examples) and show the code you ran; check notation against `notation.md` section "Дискретная математика"
- **figures** — open every embedded PNG at full size; check it matches the text and is correct (vertex/edge counts, colourings proper, labels readable, legend for every visual convention on the figure); check the script in `.sources/figures/` reproduces it

## Report (besides what `common.md` requires)

- Coverage first: which notes you read in full, how many proofs checked, how many values recomputed, how many figures opened, how many timecodes checked out of how many
- Then findings, most severe first. Each: file, line or heading, what is wrong, evidence (timecode, synopsis page, python output), the proposed fix
- Say plainly when a note has no findings
