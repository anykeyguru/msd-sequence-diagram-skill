# msd-sequence-diagram

A Claude skill that writes UML sequence diagrams in the **native `.msd` syntax** of the macOS app
[Sequence Diagram](https://www.macsequencediagram.com), not Mermaid. It carries the full DSL
reference, the house conventions, and a linter that catches Mermaid leakage and the app's parser
traps before the file is opened.

```
SKILL.md                     instructions Claude follows (frontmatter name/description = trigger)
references/native-syntax.md  complete native DSL + Mermaid-vs-native differences
scripts/lint_msd.py          heuristic linter: python3 scripts/lint_msd.py diagram.msd
tests/                       linter regression cases (tests/run.sh)
package.sh                   builds dist/msd-sequence-diagram.zip for claude.ai
```

## Install

**Claude Code** loads skills from `~/.claude/skills/`. Clone straight there and the working copy
is the installed skill:

```bash
git clone git@github.com:anykeyguru/msd-sequence-diagram-skill.git ~/.claude/skills/msd-sequence-diagram
```

**claude.ai** keeps its own copy. Build the archive and upload it in Settings → Capabilities →
Skills (replace the existing `msd-sequence-diagram`, or delete it and upload anew):

```bash
./package.sh        # runs the tests, then writes dist/msd-sequence-diagram.zip
```

The archive contains only the skill (`SKILL.md`, `references/`, `scripts/`) in one top-level
folder; README, tests and this script stay out.

## Rules learned the hard way

These are in the skill and enforced by the linter; listed here because they are not obvious
from the app's documentation:

- **Title must be quoted**: `title "Login flow"`, or `title` followed by a `"""` block.
  A bare `title Login flow` breaks the whole file in the app: nothing renders. Linter: ERROR.
- **The app never wraps note text.** Long text in one quoted line stretches the note across the
  whole diagram. Use a `"""` block with manual line breaks of 60–80 characters. Linter: WARN
  above 80.
- `<br/>` is the line break inside participant and box names (or a `"""` name block followed by
  `as code`); `\n` is the line break inside message text.
- When the app saves a file it prepends a `#//# Created using Sequence Diagram for Mac` comment
  header. Keep it.

## Changing the skill

1. Edit `SKILL.md`, the reference or the linter.
2. Add a case to `tests/cases/` named by the expected verdict: `ok-*.msd`, `warn-*.msd`, `err-*.msd`.
3. `tests/run.sh` must pass, including the "Minimal shape to copy" example from `SKILL.md`.
4. `./package.sh` and re-upload the zip to claude.ai.
