# SequenceDiagram.app — Native syntax (`.msd`) reference

This is the complete DSL for the macOS app *SequenceDiagram* (native `.msd` format).
It is **not** Mermaid — the two look similar but differ in important places (aliases are
reversed, notes/frames use multi-line `end` blocks, guards use `[...]`, etc.). When the
target is `.msd`, follow only the rules on this page.

## Table of contents
1. Participants
2. Participant boxes
3. Signals (messages)
4. Arrow styles (full table)
5. Self-signals & multi-line messages
6. Lifeline activation
7. Interaction frames
8. Notes & references
9. Comments, title, dividers, spacing
10. Styling
11. Found / lost messages
12. Gotchas & Mermaid-vs-native differences

---

## 1. Participants

Created **implicitly** the first time they appear in a signal, or **explicitly** with
`participant`. Quote names that contain spaces. Give a short alias with `as`.

```
participant Alice
participant "Mr Ed" as ed
Alice->ed: Hello
```

**Order**: participants appear in the order first mentioned. To force a different order,
declare them with `participant` *before* any signals:

```
participant b
participant a
a->b: Hello        # b is still drawn on the left
```

**With an alias, the display name is always in quotes**: `participant "Display Name" as
code`. The alias after `as` is the participant's identifier from then on — signals use it
as the endpoint (`code->other: ...`), the quoted name is only what is drawn. An unquoted
name before `as` (`participant Human as user`) breaks parsing in the app. Without an alias
a bare single-word name is fine: `participant Alice`.

**Alias order is native-specific**: display name FIRST, then `as`, then the short code:

```
participant "Wilbur Post" as w      # native:  "Full Name" as code
```

(In Mermaid it is the opposite — `code as Full Name`. Do not mix them up.)

Line break inside a display name: `\n` is NOT used here — use `<br/>` inside the name, or a
`"""` block followed by `as code` (the form the app itself writes):

```
participant "Keycloak<br/>client open-webui-bridge" as kc

participant
"""
Request logger
Outbox
""" as OBX
```

## 2. Participant boxes

Group participants visually. Label and background colour are optional.
(Boxes are native-only; Mermaid has no equivalent.)

```
box "Front End"
  participant Browser
  participant "API Gateway" as gw
end box

box "Services" #e8f5e9
  participant Auth
  participant Users
end box
```

## 3. Signals (messages)

`source ARROW target: message`. The message after the colon is optional.

```
a->b: Here a sends a message to b
b->a: Reversed direction
a->b:                     # unlabelled signal (colon, no text)
```

## 4. Arrow styles (full native table)

Pick the arrow to convey meaning. UML convention: solid + filled head = synchronous call;
dotted + open head = reply/return.

| Syntax     | Line   | Arrowhead              |
|------------|--------|------------------------|
| `->`       | solid  | filled                 |
| `->>`      | solid  | open                   |
| `-->`      | dotted | filled                 |
| `-->>`     | dotted | open                   |
| `<-`       | solid  | filled, points left    |
| `<<-`      | solid  | open, points left      |
| `<--`      | dotted | filled, points left    |
| `<->`      | solid  | filled, double-headed  |
| `<-->`     | dotted | filled, double-headed  |
| `<<->>`    | solid  | open, double-headed    |
| `<<-->>`   | dotted | open, double-headed    |
| `-\`       | solid  | lower (lost)           |
| `--\`      | dotted | lower (lost)           |
| `/-`       | solid  | upper (found)          |
| `/--`      | dotted | upper (found)          |

Recommended default convention:
- **request / call** → `->`  (solid filled)
- **response / return** → `-->>`  (dotted open)
- **async / fire-and-forget** → `->>`  (solid open)

## 5. Self-signals & multi-line messages

Self-signal: same participant on both sides — drawn as a loop-back arrow. Good for internal
processing or recursion.

```
a->a: validate input
```

Multi-line message text: use `\n` (native). (Mermaid uses `<br/>` — different.)

```
a->b: Line one\nLine two\nLine three
```

## 6. Lifeline activation

Activation boxes show a participant is actively processing.

Long form:
```
a->b: request
activate b
b-->>a: response
deactivate b
```

Native shorthand — each on its own line:

| Shorthand | Meaning              |
|-----------|----------------------|
| `+b`      | activate b           |
| `-b`      | deactivate b         |
| `*+b`     | create and activate b|

```
a->b: request
+b
b-->>a: response
-b
```

Destroy a lifeline (terminates it with an X; it can't send/receive afterwards):
```
a->b: shutdown
destroy b
```

Note: native activation shorthand is standalone lines (`+b`), NOT inline modifiers on the
arrow. (Inline `->>+b` is Mermaid-only.)

## 7. Interaction frames

Group part of the diagram in a labelled box. Every frame ends with `end`.
Guard/condition goes in **square brackets** (native). Frames nest to any depth.

Native frame keywords:

| Keyword  | Meaning                     |
|----------|-----------------------------|
| `alt`    | alternative (if/else)       |
| `opt`    | optional (if, no else)      |
| `loop`   | loop / iteration            |
| `par`    | parallel execution          |
| `neg`    | negative / invalid          |
| `region` | critical region             |
| `group`  | custom-labelled group       |

```
alt [condition is true]
  a->b: do something
else [otherwise]
  a->b: do something else
end

loop [while items remain]
  a->b: process next item
end

opt [user is admin]
  a->b: show admin panel
end

group Initialisation
  a->b: setup
  b->c: configure
end
```

Nesting and mixing types:
```
loop [for each item]
  alt [item is valid]
    a->b: process item
  else [invalid]
    a->c: log error
  end
end
```

Indentation is for readability only; the parser keys off keywords and `end`. But DO indent —
it keeps nested frames legible.

## 8. Notes & references

Notes attach text to a lifeline: `left of`, `right of`, or `over`. Native notes are a
multi-line block ending with `end note`, and the text is quoted.

**Text is drawn exactly as written — the app does not wrap it.** A long text in one quoted
line becomes one long note stretched across the whole diagram. For anything longer than a
short phrase, put the text in a `"""` block and break the lines by hand, about 60–80
characters each, at sentence or clause boundaries:

```
note over spa, bridge
"""
Without the patch the SPA hides the form and sends an empty signin,
and with an empty database it shows "create admin account".
Identity still only arrives through the signin below.
"""
end note
```

Short one-liners can stay in plain quotes:

```
note left of a
"This is a note on the left of a"
end note

note over a
"Centred over a"
end note

note over a, b
"This note spans a and b"
end note
```

References (`ref`) look like notes but point to an interaction defined elsewhere. Native-only.
Same positioning: `ref left of`, `ref right of`, `ref over`.

```
ref over Alice, Bob
"See Authentication sequence"
end ref
```

The same `"""` block form and the same manual line breaks apply to `ref` text.

## 9. Comments, title, dividers, spacing

Comment: line starting with `#` (unless it's a `#style` directive).
```
# this line is ignored
a->b: Hello
```

Title (native-only), centred at the top. **The text MUST be quoted.** An unquoted title
(`title Authentication Flow`) breaks parsing of the whole file in SequenceDiagram.app —
nothing renders. Two valid forms:

```
title "Authentication Flow"
```

```
title
"""
Authentication Flow
second line of the title
"""
```

Use the `"""` block form for a multi-line title (it is what the app itself writes when you
edit a title in its UI).

Divider — horizontal line with centred label, to separate phases:
```
== Initialisation complete ==
```

Extra vertical spacing between elements:
```
||          # default extra gap
||50||      # exactly 50px gap
```

## 10. Styling

Customise colours with a `#style` block. Values are hex `RRGGBB` (optionally followed by an
alpha 0.0–1.0). `#style-reset` restores defaults. (Native-only.)

```
#style
#participantBgColor: 2196F3
#participantTextColor: FFFFFF
#participantBorderColor: 1976D2
#signalLineColor: 333333
#signalMessageColor: 333333
#canvasBgColor: FAFAFA
#end style
```

Available properties: `#activationBoxBgColor`, `#activationBoxBorderColor`,
`#arrowHeadColor`, `#canvasBgColor`, `#destroyMarkerColor`, `#dividerBgColor`,
`#dividerLineColor`, `#dividerTextColor`, `#iFrameBgColor`, `#iFrameBorderColor`,
`#iFrameLabelBgColor`, `#iFrameLabelBorderColor`, `#iFrameLabelTextColor`,
`#iFrameRefLabelTextColor`, `#noteBgColor`, `#noteBorderColor`, `#noteTextColor`,
`#participantBgColor`, `#participantBorderColor`, `#participantTextColor`,
`#signalLineColor`, `#signalMessageColor`, `#signalTerminatorColor`, `#timelineColor`,
`#titleTextColor`.

Only add a `#style` block if the user asks for custom colours; otherwise leave defaults.

## 11. Found / lost messages

`*` = found (incoming from outside the diagram), `**` = lost (outgoing to outside).

```
*->a: incoming request from outside
a->**: fire and forget to outside
```

## 12. Gotchas & Mermaid-vs-native differences

These are the most common ways a diagram silently becomes Mermaid instead of native `.msd`:

- **Alias order**: native is `"Display Name" as code`; Mermaid is `code as Display Name`.
- **Guards**: native puts the condition in `[brackets]` after the keyword
  (`loop [while x]`); Mermaid writes it bare (`loop while x`).
- **Notes**: native uses a multi-line `note over a` … `end note` block with the text in
  quotes; Mermaid uses a one-liner `Note over a: text`.
- **Line breaks in messages**: native `\n`; Mermaid `<br/>`.
- **Activation**: native shorthand is standalone `+b` / `-b` lines; Mermaid uses inline
  `->>+b`.
- **Quoted name + alias**: `participant "Display Name" as code`; signals then use `code`.
  Unquoted `participant Name as code` breaks parsing in the app. The linter treats it as an
  ERROR.
- **Title must be quoted**: `title "Text"` or `title` + `"""` block. Bare `title Text` (as in
  Mermaid's `title Text`) breaks the whole diagram in the app. The linter treats it as an ERROR.
- **Long note/ref text**: the app never wraps it. Use a `"""` block with lines of at most
  ~80 characters; one long quoted line stretches the note across the whole diagram. The
  linter warns above 80 characters.
- **`<br/>` vs `\n`**: `<br/>` is correct inside participant/box display names; `\n` is the line
  break inside message text. Do not swap them.
- **App header**: when the app saves a file it prepends a `#//# Created using Sequence Diagram for
  Mac …` comment block. It is a normal comment; keep it, do not strip it.
- **Native-only features** (safe to use, no Mermaid equivalent): `title`, `box`, `ref`,
  `group`, `neg`, `region`, `#style`, dividers `==`, spacing `||`, found/lost `*`/`**`,
  and the extended arrow set (`<->`, `-\`, `/-`, etc.).
- Do **not** emit ```` ```mermaid ```` fences or `sequenceDiagram` headers — native `.msd`
  has no diagram-type header line; the file starts straight with `title`, `participant`, or
  the first signal.
