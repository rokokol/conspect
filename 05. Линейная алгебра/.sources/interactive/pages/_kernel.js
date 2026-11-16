// The presets of the pages that take a degenerate kernel. The editor, the error report and the chart
// are numkit's kernel-editor.js. The presets come from presets.json, the one list of the course
// (the build writes it in).
const PRESETS = /*PRESETS_JSON*/[];
const presetsFor = (page) => PRESETS.filter((p) => p.pages.includes(page));
