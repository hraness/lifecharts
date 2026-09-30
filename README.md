# Lifecharts

Lifecharts is a free life timeline maker. Add the chapters of your life, like a city, a school, a job, or a relationship, by hand or with your agent, and share the result.

This package includes a local CLI and the Lifecharts agent skill. Commands create and validate chart links without uploading your data. Use Node.js 22.14 or newer, or Bun 1.3.14 or newer. The package has no runtime dependencies or installation scripts.

## Run the CLI

The immutable GitHub Release archive is the canonical distribution. The commands below target version 1.1.0 and require its published immutable release. The prior published version is 1.0.5.

```sh
npx --yes --package=https://github.com/hraness/lifecharts/releases/download/v1.1.0/hraness-lifecharts-1.1.0.tgz lifecharts --help
```

When this version is available on npm, its archive is an exact-byte mirror:

```sh
npx --yes @hraness/lifecharts@1.1.0 --help
npm install --global @hraness/lifecharts@1.1.0
```

Run `lifecharts` without arguments for a short start screen, and `lifecharts --help` for every command. Piped output stays plain.

Supported macOS and Linux global npm and Bun installs check once a day before
chart commands and install newer releases automatically. The requested command
starts after the new version is verified. Chart files and URLs stay local.

Automatic updates start with Lifecharts 1.1.0. Upgrade an older installation
once with the install command above. Downloading updates requires an
authenticated [GitHub CLI](https://cli.github.com/) (`gh`).

```sh
lifecharts update check
lifecharts update status --json
lifecharts update disable
lifecharts update enable
```

Run `lifecharts update` to install immediately. `HRANESS_NO_UPDATE=1` skips
automatic checks for one invocation; CI and help also skip them. An exact Bun
version stays pinned until `update enable`. npm does not reliably retain its
original global install constraint, so use `update disable` to keep a version.
Canonical release archive URLs track releases by default. Project installs,
temporary npx/bunx runs, source trees, and copied skill helpers do not replace
themselves. A running Lifecharts command protects its installation from updates.
On Windows, update Lifecharts through npm or Bun.

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
npx --yes --package=https://github.com/hraness/lifecharts/releases/download/v1.1.0/hraness-lifecharts-1.1.0.tgz lifecharts create timeline.json --json
```

`create --json` returns the complete document, share link, edit link, and embed link. Use `-` for stdin. Quote complete URLs in shell commands.

## Use with an agent

```sh
npx skills add https://lifecharts.io --skill lifecharts
```

Ask your agent: “Make a life timeline from these résumé dates, preserve overlaps, and give me a verified Lifecharts link.” Or provide an existing link and ask for an edit.

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

`lifecharts support` shows optional paid support for continued development;
every feature stays free and no account is needed. Agents read `lifecharts
support protocol --json` for the closeout procedure.

## License

The CLI and skill are available under the [MIT License](LICENSE). Notices for
the bundled third-party code are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The research tables at
[lifecharts.io/data](https://lifecharts.io/data) are licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the government and
research sources they cite keep their own terms.
