# msd-sequence-diagram skill: maintainer notes

This repository is a Claude skill: it writes sequence diagrams in the native `.msd` syntax of
Sequence Diagram for Mac (`/Applications/Sequence Diagram.app`) and lints them. Public repo:
https://github.com/anykeyguru/msd-sequence-diagram-skill. Users install it with `git clone`
into `~/.claude/skills/msd-sequence-diagram` (or a project's `.claude/skills/`), or upload the
release zip to claude.ai, and update it with `/msd-sequence-diagram update`.

## What lives where

| Path | Role | Notes |
|---|---|---|
| `SKILL.md` | what Claude follows when the skill runs | frontmatter `name: msd-sequence-diagram`, description ≤ 1024 chars (claude.ai limit, tested) |
| `references/native-syntax.md` | the native DSL and the Mermaid traps | every rule the app enforces is written here |
| `scripts/lint_msd.py` | linter | standalone, stdlib only; `__version__` must equal `VERSION` |
| `scripts/check_app.sh` | is the app installed | `MSD_APP_PATH` overrides the path for tests |
| `scripts/update.sh` | self-update behind `/msd-sequence-diagram update` | ships to users; never make it destructive |
| `tests/` | `tests/run.sh` runs everything | linter cases are committed in `tests/cases/` |
| `package.sh` | builds `dist/msd-sequence-diagram.zip` for claude.ai | runs the tests first |
| `.github/workflows/` | `tests.yml` on every push/PR, `release.yml` on `v*` tags | runner pinned to `ubuntu-24.04` |

## Invariants

- Python 3.9+ and the standard library only.
- Shell scripts work with both BSD (macOS) and GNU (CI) tools.
- Every rule the linter enforces has a case in `tests/cases/`, named by the expected verdict
  (`ok-*`, `warn-*`, `err-*`). A rule learned from the app (the file did not open) is written
  in the reference, in `SKILL.md` if it changes how Claude writes, and in the linter.
- `update.sh` never overwrites local changes or diverged history, never deletes a folder that is
  not this skill, and backs up zip installs outside the skills folder.
- Documentation in this repository is in English.

## Releasing

Semantic versioning: patch for fixes, minor for new rules or features, major when the format
Claude writes changes incompatibly.

1. Bump `VERSION` and `__version__` in `scripts/lint_msd.py` to the same value.
2. `tests/run.sh` → `all passed`.
3. Commit and push to `main`; wait for the `tests` workflow to be green.
4. Tag and push: `git tag v<VERSION> && git push origin v<VERSION>`.
5. The `release` workflow checks the tag equals `VERSION`, runs the tests, builds the zip and
   publishes a GitHub release with `msd-sequence-diagram.zip` attached. Check that the release
   exists and has the asset.

Commits and pushes are made by the owner. An assistant prepares the change, runs the tests and
hands over the commit message; it commits, pushes or tags only when the owner explicitly says so.
