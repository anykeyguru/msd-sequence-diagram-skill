#!/usr/bin/env python3
"""
Lint a SequenceDiagram.app native .msd file.

The most common failure mode when generating .msd is that Mermaid syntax leaks
in (they look alike). This catches those cases plus a few structural mistakes so
the output actually parses in the app. It is a heuristic linter, not a full
parser — a clean run means "no known red flags", not "provably perfect".

Usage:
    python3 lint_msd.py path/to/diagram.msd
    python3 lint_msd.py -            # read from stdin

Exit code 0 = no errors, 1 = errors found.
"""
import re
import sys

__version__ = "1.1.0"

FRAME_KW = ("alt", "opt", "loop", "par", "neg", "region", "group", "critical",
            "break", "rect")


# Longest line of note/ref text before the note visibly stretches across lifelines.
NOTE_LINE_MAX = 80


def lint(text):
    errors = []   # things that will break / are wrong syntax
    warnings = []  # things that are probably Mermaid-isms or style issues

    lines = text.splitlines()

    # Track frame open/close balance (accounting for note/ref end blocks).
    open_frames = 0
    in_note_block = False
    open_boxes = 0
    in_title_block = False   # inside title """ ... """
    note_text_block = False  # inside the """ text of a note/ref
    title_needs_block = 0    # line number of a bare `title` waiting for its """ block

    for i, raw in enumerate(lines, 1):
        line = raw.strip()

        # --- title: the app only accepts a quoted title -------------------
        #   title "One line"            or   title
        #                                    """
        #                                    Multi-line text
        #                                    """
        # Unquoted text after `title` breaks parsing of the WHOLE file in
        # SequenceDiagram.app (nothing renders), so this is an ERROR.
        if in_title_block:
            if line == '"""':
                in_title_block = False
            continue
        if title_needs_block:
            if not line:
                continue
            if line == '"""':
                in_title_block = True
                title_needs_block = 0
                continue
            errors.append((title_needs_block, "bare 'title' must be followed by a \"\"\" block "
                                               "(title / \"\"\" / text / \"\"\")."))
            title_needs_block = 0
        if re.match(r"^title\b", line, re.IGNORECASE):
            rest = line[5:].strip()
            if not rest:
                title_needs_block = i
            elif rest == '"""':
                in_title_block = True
            elif not (len(rest) >= 2 and rest.startswith('"') and rest.endswith('"')):
                errors.append((i, "title text must be quoted: title \"" + rest.strip('"') + "\" "
                                  "(unquoted title breaks the whole diagram in the app)."))
            continue

        if not line:
            continue

        low = line.lower()

        # --- Mermaid leakage ---------------------------------------------
        if line.startswith("```"):
            errors.append((i, "Markdown code fence in file — .msd is raw text, "
                              "no ``` fences."))
            continue
        if low.startswith("sequencediagram"):
            errors.append((i, "'sequenceDiagram' header is Mermaid — native .msd "
                              "has no diagram-type header."))
        if low.startswith("%%"):
            errors.append((i, "'%%' is a Mermaid comment — native comments start "
                              "with '#'."))
        # One-line note (Mermaid): "Note over a: text"
        if re.match(r"^(note|ref)\s+(left of|right of|over)\b.*:", low):
            errors.append((i, "One-line note/ref is Mermaid. Native uses a block:\n"
                              "        note over a\n        \"text\"\n        end note"))
        # Inline activation modifier on an arrow (Mermaid): ->>+b / --x / -)
        if re.search(r"[-<>x)/\\]\+\w", line) and ":" in line and "->" in line.replace(">>", "->"):
            # crude: a '+' glued to target right before/after arrowhead
            if re.search(r">>?\+", line) or re.search(r"\)\s*\+", line):
                warnings.append((i, "Inline '+'/'-' activation looks like Mermaid; "
                                    "native uses standalone '+b' / '-b' lines."))
        # <br/> is the native line break INSIDE participant/box names; only in
        # message text is it a Mermaid-ism (native messages use \n).
        if re.search(r"<br\s*/?>", low) and not re.match(r"^(participant|actor|box)\b", low):
            warnings.append((i, "'<br/>' is Mermaid line-break; native messages use '\\n'."))
        # Mermaid arrows that don't exist in native
        if re.search(r"-x\w|--x\w|-\)\w|--\)\w", line):
            warnings.append((i, "'-x' / '-)' arrows are Mermaid-only; native has no "
                                "cross/async arrowheads (see arrow table)."))

        # --- Participant names --------------------------------------------
        # `participant "Display Name" as code`: the display name is ALWAYS in
        # quotes when an alias is given; the alias after `as` is what signals
        # use as endpoints (code->other: ...). An unquoted name before `as`
        # (participant Человек as user) breaks parsing in SequenceDiagram.app.
        m = re.match(r"^(participant|actor)\s+(.+?)\s+as\s+(\S+)\s*$", line, re.IGNORECASE)
        if m and not m.group(2).startswith('"'):
            errors.append((i, "with an alias the display name must be quoted: "
                              f'{m.group(1)} "{m.group(2)}" as {m.group(3)} — signals then '
                              f"use the alias ({m.group(3)}->...)."))

        # --- Frame guard style -------------------------------------------
        m = re.match(r"^(alt|opt|loop|par|neg|region)\b(.*)$", low)
        if m:
            rest = m.group(2).strip()
            if rest and not rest.startswith("["):
                warnings.append((i, f"'{m.group(1)}' guard should be in [brackets] "
                                    f"(native). Got bare text: {rest!r}"))

        # --- Structure counting ------------------------------------------
        if re.match(r"^(note|ref)\s+(left of|right of|over)\b", low) and not line.endswith(":"):
            in_note_block = True
            note_text_block = False
            continue
        if in_note_block:
            if low in ("end note", "end ref"):
                in_note_block = False
                continue
            # Note/ref text is drawn exactly as written: one long quoted line
            # becomes one note stretched across the whole diagram. Long text goes
            # in a """ block with manual line breaks, each line <= NOTE_LINE_MAX.
            if line == '"""':
                note_text_block = not note_text_block
                continue
            if note_text_block:
                if len(line) > NOTE_LINE_MAX:
                    warnings.append((i, f"note/ref line is {len(line)} chars; break it "
                                        f"(<= {NOTE_LINE_MAX} per line) so the note does not "
                                        "stretch across the diagram."))
            elif len(line.strip('"')) > NOTE_LINE_MAX:
                warnings.append((i, f"single-line note/ref text is {len(line.strip(chr(34)))} chars; "
                                    "use a \"\"\" block with manual line breaks:\n"
                                    "        note over a\n        \"\"\"\n        first line\n"
                                    "        second line\n        \"\"\"\n        end note"))
            continue

        if low.startswith("box"):
            open_boxes += 1
        elif low == "end box":
            open_boxes -= 1
            if open_boxes < 0:
                errors.append((i, "'end box' without matching 'box'."))
                open_boxes = 0
        elif re.match(r"^(%s)\b" % "|".join(FRAME_KW), low):
            open_frames += 1
        elif low == "end" or low.startswith("end "):
            if low not in ("end box", "end note", "end ref"):
                open_frames -= 1
                if open_frames < 0:
                    errors.append((i, "'end' without a matching frame keyword."))
                    open_frames = 0

    if title_needs_block:
        errors.append((title_needs_block, "bare 'title' at end of file without a \"\"\" block."))
    if in_title_block:
        errors.append((len(lines), "title \"\"\" block not closed with \"\"\"."))
    if in_note_block:
        errors.append((len(lines), "note/ref block not closed with 'end note'/'end ref'."))
    if open_frames > 0:
        errors.append((len(lines), f"{open_frames} interaction frame(s) not closed with 'end'."))
    if open_boxes > 0:
        errors.append((len(lines), f"{open_boxes} box(es) not closed with 'end box'."))

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        print("usage: lint_msd.py <file.msd | ->", file=sys.stderr)
        sys.exit(2)
    src = sys.argv[1]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()

    errors, warnings = lint(text)
    for ln, msg in errors:
        print(f"ERROR  line {ln}: {msg}")
    for ln, msg in warnings:
        print(f"WARN   line {ln}: {msg}")
    if not errors and not warnings:
        print("OK — no known red flags.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
