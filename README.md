# msd-sequence-diagram

[![tests](https://github.com/anykeyguru/msd-sequence-diagram-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/anykeyguru/msd-sequence-diagram-skill/actions/workflows/tests.yml)

A Claude skill that writes UML sequence diagrams in the **native `.msd` syntax** of the macOS app
[Sequence Diagram](https://www.macsequencediagram.com), not Mermaid. It carries the full DSL
reference, the house conventions, and a linter that catches Mermaid leakage and the app's parser
traps before the file is opened.

## Requirements

- **Sequence Diagram for Mac** at `/Applications/Sequence Diagram.app`
  ([macsequencediagram.com](https://www.macsequencediagram.com), Mac App Store): the `.msd`
  files are made to be opened there. `scripts/check_app.sh` checks it.
- `git` and Python 3.9+ (the linter uses the standard library only).

## Install

The skill is a folder named `msd-sequence-diagram` with `SKILL.md` at its top.

### Claude Code (CLI, desktop app, IDE extensions)

For yourself, in every project:

```bash
git clone https://github.com/anykeyguru/msd-sequence-diagram-skill.git ~/.claude/skills/msd-sequence-diagram
```

For everyone working in one repository, commit it into the project instead:

```bash
git clone https://github.com/anykeyguru/msd-sequence-diagram-skill.git .claude/skills/msd-sequence-diagram
rm -rf .claude/skills/msd-sequence-diagram/.git
```

Start a new Claude Code session (skills are read at start-up) and ask «нарисуй диаграмму
последовательности …» or type `/msd-sequence-diagram`.

### claude.ai (web and desktop chat)

Download `msd-sequence-diagram.zip` from the [latest release](https://github.com/anykeyguru/msd-sequence-diagram-skill/releases/latest),
or build it from a clone with `./package.sh` (writes `dist/msd-sequence-diagram.zip`). Then
Settings → Capabilities → Skills → Upload skill. To update, delete the old one and upload the
new zip.

### Asking an AI assistant to install it

You can say to Claude Code (or another agent with a shell): *"install the skill
https://github.com/anykeyguru/msd-sequence-diagram-skill"*. The steps below are written for
that assistant.

> **Instructions for an AI assistant installing this skill**
>
> 1. Check that this is macOS and that `git` and `python3` (3.9 or newer) are available. If
>    `~/.claude/skills/msd-sequence-diagram` already exists, do not overwrite it: run
>    `bash ~/.claude/skills/msd-sequence-diagram/scripts/update.sh` instead and report its output.
> 2. Install for the user (all projects) unless they asked for this project only:
>    `git clone https://github.com/anykeyguru/msd-sequence-diagram-skill.git ~/.claude/skills/msd-sequence-diagram`.
>    For this project only: clone into `.claude/skills/msd-sequence-diagram` of the repository and
>    remove its `.git`. The folder name must be `msd-sequence-diagram`, the same as `name:` in `SKILL.md`.
> 3. Verify: `cat ~/.claude/skills/msd-sequence-diagram/VERSION` prints a version, and
>    `bash ~/.claude/skills/msd-sequence-diagram/tests/run.sh` ends with `all passed`.
> 4. **Required app**: run `bash ~/.claude/skills/msd-sequence-diagram/scripts/check_app.sh`. It must
>    find `/Applications/Sequence Diagram.app`. If it is missing, tell the user the skill is
>    installed but the diagrams open only in Sequence Diagram for Mac
>    (https://www.macsequencediagram.com, Mac App Store); do not install the app without asking.
> 5. Tell the user the installed version, whether the app was found, that the skill appears in new
>    sessions, and that `/msd-sequence-diagram update` updates it later.
>
> In claude.ai (no shell) the assistant cannot install skills: point the user to the claude.ai
> steps above.

### Update

In Claude Code type:

```
/msd-sequence-diagram update
```

The skill runs `scripts/update.sh` and reports old → new version and what changed. You can also
run it yourself:

```bash
bash ~/.claude/skills/msd-sequence-diagram/scripts/update.sh
```

- installed with `git clone`: fast-forwards to `main` of this repository; if you changed files in
  the installed copy, or committed to it, it refuses and says how to resolve it, nothing is
  overwritten;
- installed by copying or unzipping: the old copy goes to `~/.cache/msd-sequence-diagram/` and is
  replaced by a fresh clone (so the next update is a fast-forward).

The new version is picked up from the next session.

## Repository

```
SKILL.md                       instructions Claude follows: commands, app check, workflow, conventions
CLAUDE.md                      maintainer notes: invariants, changing, releasing
VERSION                        skill version (= lint_msd.__version__)
references/native-syntax.md    complete native DSL + Mermaid-vs-native differences
scripts/lint_msd.py            heuristic linter: python3 scripts/lint_msd.py diagram.msd
scripts/check_app.sh           is /Applications/Sequence Diagram.app installed
scripts/update.sh              self-update from this repository
tests/                         tests/run.sh: linter cases, app check, self-update, release metadata
package.sh                     builds dist/msd-sequence-diagram.zip for claude.ai
.github/workflows/tests.yml    runs tests/run.sh on every push and pull request
.github/workflows/release.yml  tag v<VERSION> → tests + zip for claude.ai on a GitHub release
```

## Rules learned the hard way

These are in the skill and enforced by the linter; listed here because they are not obvious
from the app's documentation:

- **Title must be quoted**: `title "Login flow"`, or `title` followed by a `"""` block.
  A bare `title Login flow` breaks the whole file in the app: nothing renders. Linter: ERROR.
- **The app never wraps note text.** Long text in one quoted line stretches the note across the
  whole diagram. Use a `"""` block with manual line breaks of 60–80 characters. Linter: WARN
  above 80.
- **A participant with an alias has its display name in quotes**: `participant "Display Name"
  as code`; every signal then uses the alias (`code->other: …`). An unquoted
  `participant Name as code` breaks parsing in the app. Linter: ERROR.
- `<br/>` is the line break inside participant and box names (or a `"""` name block followed by
  `as code`); `\n` is the line break inside message text.
- When the app saves a file it prepends a `#//# Created using Sequence Diagram for Mac` comment
  header. Keep it.

## Tests

```bash
tests/run.sh
```

Runs on GitHub Actions for every push and pull request (Python 3.9 and 3.13 on Ubuntu 24.04).

- linter cases in `tests/cases/`, named by the expected verdict (`ok-*`, `warn-*`, `err-*`),
  plus the "Minimal shape to copy" example from `SKILL.md`;
- `check_app.sh` with a stand-in app folder: found and missing;
- self-update against a local repository: fast-forward, already up to date, local changes
  refused, diverged copy refused, zip install backed up and replaced, a foreign folder left alone;
- `VERSION` equals `lint_msd.__version__`; `SKILL.md` has its name and a description within
  claude.ai's 1024-character limit.

## Changing the skill

1. Edit `SKILL.md`, the reference or the linter.
2. Add a case to `tests/cases/` named by the expected verdict: `ok-*.msd`, `warn-*.msd`, `err-*.msd`.
3. `tests/run.sh` must pass; GitHub Actions runs it again on push.
4. Bump `VERSION` and `__version__` in `scripts/lint_msd.py` together.
5. Release: push a tag `v<VERSION>` (`git tag v1.1.0 && git push origin v1.1.0`). The release
   workflow runs the tests and attaches `msd-sequence-diagram.zip` for claude.ai.
