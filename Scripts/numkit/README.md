# numkit

The numerical mechanisms that the interactive pages of the vault courses share: a formula parser without `eval`, adaptive quadrature, LU, eigenvalues of a real matrix, and the editor of a degenerate kernel with a chart. A course keeps only its own mathematics and takes the rest from here, so a mechanism has one source

The fonts, the theme, the number format and the page assembly are not here: they belong to `sandbox_kit`, and numkit only calls what the page already has

## What is inside

- `numkit.js` — pure functions with no DOM, one ES module
  - `parseExpression`, `compileExpression`, `evalConstant`, `ExprError`, `FUNCTION_NAMES` read a formula such as `sin(x)*t^2` into a function, with error codes and positions that point at the bad character
  - `integrate`, `EvalError` compute an integral by adaptive Gauss-Kronrod with a global error estimate
  - `luDecompose`, `luSolve`, `luDet`, `det`, `norm1`, `cond1` solve and measure a dense system
  - `eigenvalues` gives the eigenvalues of a real matrix, `deltaCoefficients` the coefficients of `det(I - lambda A)`
  - `compileProblem` reads the text of a degenerate kernel `K(x,t) = sum alpha_k(x) beta_k(t)` with its interval and right-hand side
  - `EPS` is the machine epsilon, exported so that a course module does not declare it a second time
- `kernel-editor.js` — browser code: the editor of the interval and the kernel terms, the report of a bad formula, a line chart on a canvas (linear or logarithmic axes, `aspect`, dots at the vertices), and the helpers `fmt`, `sci`, `sciText` and `sciHtml` (a number as the notes write it: plain from 10^-3 to 10^4, else m·10^k), `sumOfTerms`, `sub`, `ticks`, `decadeTicks`, `pow10`, `logRange`, `yRange`
- `kernel-editor.css` — the layout of that editor and nothing else: no colours and no fonts
- `embed.py` — the texts above, ready to put into a page template
- `testkit.mjs` — the assertions that numeric tests need: `near`, `nearAll`, `rel`, `matchAll`, `dot`, `mulVec`
- `numkit.test.mjs`, `test_embed.py`, `export_fixtures.py` — the tests and the reference data

A matrix is a flat row-major array of `n*n` numbers everywhere

## Use in a course page

A page is one classic script, so the build inlines the modules with their `import` and `export` removed, and every exported name becomes a global of the page. A course module must not declare a name that numkit exports, and it calls numkit by name

In the course build:

```python
import course  # puts the vault's scripts folder on sys.path
from numkit import embed
from sandbox_kit import page as kit

parts = {
    "/*NUMKIT*/": embed.numkit_js(),
    "/*COURSE*/": embed.strip_module(Path("course.js").read_text(encoding="utf-8")),
    # a page with the kernel editor also takes:
    "/*KERNEL_JS*/": embed.kernel_editor_js(),
    "/*KERNEL_CSS*/": course_input_css + embed.kernel_editor_css(),
}
```

In the template, `/*NUMKIT*/` stands before the course module, and each marker stands exactly once, which `sandbox_kit.page.build_page` checks

In the course module, import what it uses. The build removes the line, and `node --test` can still import the module as it is

```js
import { integrate, norm1 } from "../../../Scripts/numkit/numkit.js";
```

The editor needs four globals from the page: `$(id)`, `esc(s)`, `css(name)` and `formatNumber`. The last two come from the theme script of `sandbox_kit`. The page styles its own inputs, buttons, `.warn` and `canvas`, and the editor CSS goes after those rules so that its size of small inputs wins. The linear algebra course is the working example: `05. Линейная алгебра/.sources/interactive/build_pages.py`

One command rebuilds every sandbox of a course. For linear algebra it is

```bash
PY=<python with fonttools and brotli> bash "05. Линейная алгебра/.sources/interactive/install_pages.sh"
```

## Limits to know

- The parser takes the variables that the caller names in `compileExpression(src, names)`, for example `["x", "s"]`; `parseExpression` alone knows `x` and `t`. A formula that uses `x`, `t`, `s` or `y` outside `names` is a `bad-variable` error. Constants are `pi` and `e`, functions are those in `FUNCTION_NAMES`
- The messages of the parser, `integrate` and the editor are in Russian
- `compileProblem` and the editor assume the form `K(x,t) = sum alpha_k(x) beta_k(t)`
- `eigenvalues` throws after 60 iterations without convergence, for example on a matrix with NaN

## Tests

The tests compare the code with another method, not with a copy of itself: sympy for the parser, mpmath for the quadrature, numpy and exact characteristic polynomials for the eigenvalues. The reference data is `fixtures.json`, which is not in git

```bash
PY=<python with numpy, sympy and mpmath>
$PY "Scripts/numkit/export_fixtures.py"
node --test "Scripts/numkit/numkit.test.mjs"
(cd "Scripts" && $PY -m unittest numkit.test_embed)
```

A course test imports `testkit.mjs` for its assertions. In `node --test`, compare large arrays element by element and stop at the first miss, because `deepEqual` on a large float array uses gigabytes
