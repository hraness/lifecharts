# Chart format and CLI reference

The bundled CLI runs offline under Node.js 22.14 or newer, or Bun 1.3.14 or newer.
Run `node <skill-path>/scripts/lifecharts.mjs --help` to list all commands. If the
`@hraness/lifecharts` package is installed, `lifecharts` exposes the same interface.
Success exits 0, invalid input exits 1, and invalid command syntax exits 2. The CLI
writes results to stdout and errors to stderr; it never logs the source input.

## Creation JSON

`create` and `validate` accept friendly creation JSON or a complete version 1
document. Unknown fields are rejected, including profile URLs: a profile is
source material for the agent, not a document field.

| Field | Meaning |
| --- | --- |
| `title` / `name` | Optional chart title, up to 80 characters, or name up to 60 characters. Title wins when both exist. |
| `birthDate` | Optional supplied birthday, `YYYY-MM-DD` or `YYYY-MM`. Mutually exclusive with `start`. |
| `start` | Optional timeline start with the same date precision. Otherwise uses the earliest supplied chapter. |
| `asOf` | `"live"` (default), or a fixed `YYYY-MM-DD` / `YYYY-MM` date. |
| `horizonAge` | Integer 1–150, default 90. Years from the start; this is a display horizon. |
| `scale` | `"lived"` (default) or `"whole"`. |
| `theme` | `"system"` (default), `"light"`, or `"dark"`. |
| `view` | `"timeline"` (default) or `"bars"`. |
| `chapters` | Up to 30 chapters; defaults to empty when a start or birthday is supplied. |

A chapter requires `label` (1–60 characters) and `start`. Its `end` defaults to
`"present"`. Optional `id` is a unique 1–40-character ASCII letter, digit,
underscore, or hyphen identifier. Optional `color` is a six-digit hex color.
Missing IDs and colors are generated deterministically without replacing explicit
values. Dates must be real calendar dates. Explicit ends must follow starts.
Chapters cannot start before the chart.

Additional chapter fields: `description` (up to 240 characters), `url` (complete
HTTP(S), up to 500 characters, no credentials), `dateLabel` (display-only text,
up to 80 characters), and `parentId` (an existing chapter ID). Nesting cannot
contain cycles. Author parents before children when practical; the parser accepts
any order. Overlap is valid and never implies nesting by itself.

## Lossless version 1 JSON

`inspect` prints a complete document. `compile` and `edit` accept only that full
shape: `version: 1`, `title`, `start`, `startKind: "birth" | "timeline"`, `asOf`,
`horizonAge`, `scale`, `theme`, optional `view`, and `chapters` with explicit IDs
and colors. Do not use `birthDate` or `name` in a complete document.

The codec preserves month precision and optional metadata. Its canonical payload
must fit in 16 KB; reduce long descriptions or links if compilation reports that
the chart is too large. JSON edits are the full-document edit interface. There is
no patch language to silently lose unrelated fields.

Older URLs may omit `view`: the original main view used timeline while the
original embed used bars. Importing an old `/embed` URL records `view: "bars"`
to preserve its appearance. New links always record a view explicitly; complete
JSON without a view compiles as `"timeline"` in both viewer and embed.

`inspect --json` returns the document, share/edit/embed links, geometry, and
interpretation notes. `verify --json` additionally reports `verified: true`.
Use `--today YYYY-MM-DD` with those commands to inspect live geometry at a fixed
date without changing `asOf` in the document. `validate --json` returns a checked
document without generating links. `create --json` and `compile --json` return
the checked document and all three fragment URLs.

## Percentages and privacy

The lived share is elapsed chapter days divided by elapsed timeline days. The
whole share is elapsed chapter days divided by the chosen horizon's days.
Overlapping, parent, and child chapters are not additive. Future parts do not
count as elapsed. A birth-based chart may show progress toward the chosen horizon;
that progress is not a mortality estimate.

The fragment is encoded, not encrypted, and includes every document field. It is
not sent in an ordinary request to the website. The selected view, theme, and
scale apply to both the main chart and the embed. A personal social preview has
different disclosure semantics and is created explicitly in the website's share
controls. The CLI's normal output always uses a fragment URL.
