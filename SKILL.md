---
name: msd-sequence-diagram
description: >-
  Build UML sequence diagrams in the native .msd syntax of the macOS app
  "SequenceDiagram" (sequencediagram.org / the Mac app). Use this skill whenever
  the user wants a sequence diagram, interaction diagram, or call flow that they
  will open or paste into the SequenceDiagram Mac app — including phrasings like
  "make a sequence diagram", "нарисуй диаграмму последовательности", ".msd",
  "sequence diagram for the login flow", "diagram how this API request works",
  "turn this description into a sequence diagram", or when they hand you a text
  description / code / user story and ask for the message flow between services,
  actors, or components. Produces native .msd text (NOT Mermaid), following the
  app's exact conventions for participants, arrows, frames, notes, and
  activation. Prefer this over generic Mermaid output whenever the SequenceDiagram
  app is the intended target.
---

# SequenceDiagram.app native `.msd` diagrams

Turn a text description (or code, or a user story) into a sequence diagram written
in the **native `.msd` DSL** of the macOS *SequenceDiagram* app. The output must
open cleanly in that app and match its house conventions — this is deliberately
**not** Mermaid, even though the two syntaxes rhyme.

## Why native, not Mermaid

Users pick this app for its native format: `title`, participant `box`es, `ref`
frames, custom `#style` colours, dividers, and a richer arrow set that Mermaid
doesn't have. If you emit Mermaid, those features silently disappear and some
lines fail to parse. The single most common mistake is drifting into Mermaid
habits (reversed aliases, one-line notes, bare guards). The reference and the
linter exist to stop that.

## Workflow

1. **Understand the flow.** From the user's description, extract: the participants
   (actors/services/components), the ordered messages between them, and the
   control structure (loops, conditionals, optional/parallel paths, error
   handling). Ask a brief clarifying question only if the flow is genuinely
   ambiguous — otherwise make a sensible interpretation and proceed.

2. **Read the syntax reference.** Open `references/native-syntax.md` before
   writing. It has the full DSL plus a "Mermaid-vs-native differences" section
   listing the exact traps. Consult it rather than relying on memory — the
   native details (alias order, `[guard]` brackets, `end note` blocks) are easy
   to get subtly wrong.

3. **Write the `.msd`.** Follow the conventions below. Build participants first
   (in the order they should appear left-to-right), then the messages, wrapping
   groups in interaction frames as needed.

4. **Lint it.** Run the linter to catch Mermaid leakage and unbalanced
   frames/notes/boxes before delivering:

   ```
   python3 scripts/lint_msd.py path/to/diagram.msd
   ```

   Fix every ERROR; review each WARN (some are intentional, most are real). A
   clean run is "no known red flags", not a full parse guarantee — still eyeball
   the result.

5. **Deliver.** Save the diagram as a `.msd` file and send it to the user with
   SendUserFile so they can open it directly in the app. Also show the `.msd`
   text inline in your reply (in a plain code block, no `mermaid` tag) with a
   one-line summary of the flow, so they can read or tweak it without opening
   the file. If they only wanted the text, still offer the file.

## House conventions

These make output look like it came from a careful user of the app, and keep
diagrams readable. They are defaults — follow the user's explicit wishes over
them.

- **Declare participants explicitly and in reading order** at the top when there
  are more than two, so left-to-right order is intentional rather than accidental.
  Alias long names: `participant "Payment Gateway" as pg`. Remember native alias
  order is `"Display Name" as code`.
- **Arrow convention** (unless the user specifies otherwise): synchronous
  call/request `->` (solid filled); reply/return `-->>` (dotted open);
  async / fire-and-forget `->>` (solid open). Being consistent here is what makes
  a diagram readable at a glance.
- **Show control flow with frames**, not prose. A retry is a `loop`, an
  either/or is `alt … else`, a maybe-path is `opt`, concurrent work is `par`.
  Put the condition in `[brackets]`.
- **Activation** (`+b` / `-b`) is worth adding when it clarifies who is doing work
  during a call, especially in request/response pairs. Don't overdo it on trivial
  one-shot messages.
- **Notes** explain intent that the messages alone don't carry (preconditions,
  side effects, "token cached here"). Use the multi-line `note over …` / `end
  note` block form with quoted text. The app does **not** wrap note text: anything
  longer than a short phrase goes in a `"""` block with manual line breaks of about
  60–80 characters, otherwise the note stretches across the whole diagram.
- **Title**: add a `title` line when the diagram represents a named flow — it's
  free context and native-only. **Always quote it**: `title "Login flow"`, or for a
  multi-line title `title` followed by a `"""` … `"""` block. A bare `title Login flow`
  breaks the whole file in the app (nothing renders); the linter rejects it.
- **Colours / `#style`**: only add when the user asks. Defaults look fine.
- **Group participants in `box`es** when they belong to distinct systems
  (front end vs back end, your services vs a third party) and it aids clarity.

## Minimal shape to copy

```
title "Login flow"

participant User
participant Browser
box "Backend" #e8f5e9
  participant "Auth Service" as auth
  participant "User DB" as db
end box

User->Browser: enter credentials
Browser->auth: POST /login
+auth
auth->db: find user by email
db-->>auth: user record
alt [password valid]
  auth-->>Browser: 200 + session token
  note over Browser
  """
  Token stored in an httpOnly cookie;
  the SPA never reads it from JavaScript
  """
  end note
else [invalid]
  auth-->>Browser: 401 Unauthorized
end
-auth
Browser-->>User: show result
```

## Reference & tools

- `references/native-syntax.md` — complete native `.msd` DSL: participants, boxes,
  the full arrow table, self-signals, activation, all frame keywords, notes/refs,
  dividers, spacing, `#style` properties, found/lost messages, and the
  Mermaid-vs-native cheat sheet. Read it before writing.
- `scripts/lint_msd.py` — heuristic linter; run on every generated file.

If the user explicitly wants **Mermaid** output instead (e.g. for GitHub or a
`.mmd` file), the app also supports Mermaid — note the differences in the
reference, or just produce standard Mermaid `sequenceDiagram` syntax. This skill's
default and specialty is native `.msd`.
