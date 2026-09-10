---
name: lifecharts
description: Create, inspect, and edit personal life timelines and career charts on Lifecharts from user-supplied facts, dates, résumés, or authorized profile material; return a verified chart link and lossless JSON.
---

# Lifecharts

Lifecharts makes a life timeline whose document travels in its URL. Use the
bundled checked CLI to create, inspect, edit, validate, and share it. No account,
API key, or source checkout is required. Run it with Node.js 22.14 or newer:

```sh
node <skill-path>/scripts/lifecharts.mjs --help
```

Bun 1.3.14 or newer also works; replace `node` with `bun`. The
`@hraness/lifecharts` package includes this skill and exposes the same commands
through its `lifecharts` executable. Use the bundled script when the skill is
already installed; no separate package installation is needed.

## Create a useful chart

Start with the facts the user supplies: chapters, dates, a résumé, or authorized
profile material. A birthday and LinkedIn profile are optional. If a profile
is inaccessible, ask for the relevant pasted text. The CLI does not fetch URLs.
Do not infer birthdays from graduation years, invent personal milestones, or
turn vague years into precise dates. Ask for the missing month when it matters;
preserve supplied month-only dates as `YYYY-MM`.

Write a small JSON file with a title or name and chapters. Use `birthDate` only
when supplied; otherwise use `start` or let the earliest chapter establish the
timeline start. Chapter IDs and colors are generated when omitted. Add explicit
IDs when authoring parent/child relationships. Use `end: "present"` for ongoing
chapters; future dates represent plans, not facts that have already happened.

```json
{
  "name": "Sam",
  "start": "2016-06",
  "view": "bars",
  "chapters": [
    { "label": "Design school", "start": "2016-06", "end": "2020-05" },
    { "label": "Independent work", "start": "2020-06", "end": "present" }
  ]
}
```

That example is illustrative. Replace it with the user's facts before delivery.
`templates list`, `templates life`, and `templates career` supply other editable
examples. Read [references/chart-format.md](references/chart-format.md) for
field limits, nesting, display choices, and exact editing.

`view: "timeline"` aligns chapters by date and makes overlap visible;
`view: "bars"` emphasizes each chapter's share of the elapsed timeline.
Choose the view that suits the story. Preserve intentional overlap and nesting;
chapter percentages need not add to 100. The default `scale: "lived"` shows
elapsed time. A whole-life horizon is a display setting the user chooses, never
a prediction or individualized estimate of lifespan. Without a birthday, don't
describe chapter shares as percentages of the person's whole life.

```sh
node <skill-path>/scripts/lifecharts.mjs create input.json --json > created.json
```

The result contains the canonical `document`, a verified `url`, `editUrl`, and
`embedUrl`. Save the document as the editable source and the complete URL in
`final.url`. No create or edit command uploads anything.

## Edit without losing information

Inspect the complete original URL or a file containing it:

```sh
node <skill-path>/scripts/lifecharts.mjs inspect original.url > chart.json
```

Edit that lossless JSON and preserve IDs, ordering, parent IDs, date precision,
descriptions, links, theme, and unrelated chapters. Compile the edited document:

```sh
node <skill-path>/scripts/lifecharts.mjs compile chart.json > final.url
node <skill-path>/scripts/lifecharts.mjs verify final.url --json
```

Read the verification output and check the requested edit and preserved details.
Never construct or repair the encoded fragment manually. A file can contain one
URL, fragment, or JSON document; use `-` to read stdin. Quote URLs in shell
commands. Failures return nonzero with an actionable message.

## Deliver

Return the complete verified `https://lifecharts.io/view#t=1.…` link with a short
description of the result. Save lossless JSON so the user can keep editing or
paste it into Lifecharts. Use the returned `embedUrl` when they request an embed;
the view, scale, and theme travel with the link.

The URL contains the supplied chart data. Anyone receiving it can read and pass
on those details. Ordinary web requests do not send its fragment to Lifecharts;
pasting it into a hosted agent sends it to that provider. Personal social-card
previews are a separate opt-in share action in the website. Keep the ordinary
fragment link unless the user asks to publish a preview.
