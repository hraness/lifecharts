# Lifecharts

Turn dates and chapters into a life chart you can open, edit, share, and embed at [lifecharts.io](https://lifecharts.io). This package includes a local CLI and the Lifecharts agent skill. Commands create and validate chart links without uploading your data.

Use Node.js 22.14 or newer, or Bun 1.3.14 or newer. The package has no runtime dependencies or installation scripts.

## Run the CLI

The immutable GitHub Release archive is the canonical distribution. The commands below target version 1.0.2 and require its published immutable release. The prior published version is 1.0.1.

```sh
npx --yes --package=https://github.com/hraness/lifecharts/releases/download/v1.0.2/hraness-lifecharts-1.0.2.tgz lifecharts --help
```

When this version is available on npm, its archive is an exact-byte mirror:

```sh
npx --yes @hraness/lifecharts@1.0.2 --help
npm install --global @hraness/lifecharts@1.0.2
```

Run `lifecharts` without arguments for a brief introduction and command help. Piped output stays plain.

Write your chapters into `timeline.json`:

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

The example is illustrative; use your own facts. A birthday is optional. If you know it, use `birthDate` instead of `start`. Dates can preserve month precision. Chapters can overlap.

```sh
lifecharts create timeline.json > timeline.url
lifecharts verify timeline.url
lifecharts inspect timeline.url > chart.json
# Edit chart.json, then compile the complete document:
lifecharts compile chart.json > updated.url
```

Without a global installation, use this pinned command prefix before the command and arguments:

```sh
npx --yes --package=https://github.com/hraness/lifecharts/releases/download/v1.0.2/hraness-lifecharts-1.0.2.tgz lifecharts create timeline.json --json
```

`create --json` returns the complete document, share link, edit link, and embed link. Use `-` for stdin. Quote complete URLs in shell commands.

## Use with an agent

```sh
npx skills add https://lifecharts.io --skill lifecharts
```

Ask your agent: “Make a life chart from these résumé dates, preserve overlaps, and give me a verified Lifecharts link.” Or provide an existing link and ask for an edit.

The same skill is included at `skills/lifecharts/SKILL.md` in this package. From inside the installed package directory, its standalone helper runs with either runtime:

```sh
node skills/lifecharts/scripts/lifecharts.mjs --help
bun skills/lifecharts/scripts/lifecharts.mjs --help
```

Read [the format reference](skills/lifecharts/references/chart-format.md) for limits, date precision, nested chapters, and display options. A LinkedIn profile is context for your agent; this CLI does not fetch profiles or infer missing personal facts.

## Sharing and release verification

The returned URL contains the chart. Anyone with it can read its title, dates, chapters, notes, and links. Ordinary fragment links keep that data outside the page request. Named social preview images are a separate opt-in action on the website.

Releases include the package archive, `release.json`, and `SHA256SUMS`. Verify the archive checksum before installing from a downloaded file. Published GitHub releases are immutable. The npm mirror can follow later without delaying the canonical release.

## Optional development support

`lifecharts support` shows optional support for continued development. Features
remain free and no account is required. Accounts presents current terms; the
person confirms payment in their browser. Lifecharts has no product newsletter
and does not look up an email address for support.

Useful standalone chart work may print shared agent discovery on stderr. Read
`lifecharts support protocol --json` for the closeout procedure. Imported runners,
help, templates, validation, failed commands and unattended CI stay quiet.
`HRANESS_SUPPORT=off` or `HRANESS_SUPPORT_AUDIENCE=off` disables incidental offers.
The default audience is an agent, including in a PTY; a human operator can opt
into terminal rendering with `HRANESS_SUPPORT_AUDIENCE=human`.

`lifecharts support dismiss`, `snooze`, `enable`, and `status --json` manage
separate local preferences across participating tools. An acknowledged invitation
starts the shared seven-day cooldown; discovery alone does not. These commands
never read a chart, sign up, open a browser, or pay.
