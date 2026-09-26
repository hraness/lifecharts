# Release Lifecharts

This repository contains the public Lifecharts CLI and Agent Skill distribution.
The versioned archive on an immutable GitHub Release is canonical. npm receives
the same archive as an optional mirror. A delayed npm mirror does not invalidate
the GitHub release.

## Prepare a version

1. Submit the complete distribution through a pull request. Keep `package.json`,
   the CLI version, skill, and `release-files.json` consistent. The file manifest
   records each package file's SHA-256; generated website source and history do
   not belong in this repository.
2. Add the version's section to `CHANGELOG.md` in the same pull request: a
   `## X.Y.Z` heading (optionally `## vX.Y.Z` or `## X.Y.Z - YYYY-MM-DD`), one
   summary paragraph, then one bullet per change a user would notice. The
   release page copies this section word for word, so follow `STYLE.md`. CI
   fails when the package version has no such section, when it is empty, or
   when it still says Unreleased.
3. Merge after review and both Package CI jobs pass. CI checks the exact npm
   archive and an isolated installation on Node 22.14.0 and 24.20.0, plus Bun
   execution. The package has no install scripts or runtime dependencies.
4. Have a repository administrator verify immutability immediately before tagging:

   ```sh
   test "$(gh api repos/hraness/lifecharts/immutable-releases --jq '.enabled')" = true
   ```

   The setting endpoint requires Administration-read access, which the workflow's
   `GITHUB_TOKEN` cannot carry. A false result or failed lookup stops the release.
5. Create an annotated `v<version>` tag on that reviewed main commit and push the
   exact tag. Use a new stable version for changed bytes; never move a release tag.

`release.yml` checks the version, public repository identity, and main ancestry.
It packs once, verifies the archive, renders the release page, creates a
draft titled `Lifecharts vX.Y.Z`, uploads the archive with `release.json` and `SHA256SUMS`, and publishes the
draft. It then reads back every asset and verifies the archive's GitHub release
attestation. An existing draft can resume with missing assets; differing assets
stop the workflow. A completed matching release is verified without another
publication. A published release without `immutable: true` fails verification.

If a release run fails after creating a draft, inspect the existing release and
merge any controller repair through reviewed main. Repeat the administrator
immutability preflight, then recover the existing version without moving its tag:

```sh
gh workflow run release.yml --repo hraness/lifecharts --ref main -f version=1.0.0
```

Recovery runs the reviewed main workflow while CI, packaging, and `release.json`
use the original tag's commit. The tag must still belong to main history. Drafts
are resolved through the paginated release list because GitHub's published-tag
endpoint can return 404 for a draft. A unique matching draft is refreshed by its
release ID; conflicting source, duplicate matches, or an incomplete bounded list
stop before another release is created. Existing uploaded bytes remain unchanged.

Release immutability must be enabled before the first publication:

```sh
gh api --method PUT repos/hraness/lifecharts/immutable-releases
gh api repos/hraness/lifecharts/immutable-releases
```

GitHub locks the assets and tag when the draft is published. Follow GitHub's
[immutable release guidance](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases)
and [repository API](https://docs.github.com/en/rest/repos/repos#enable-immutable-releases).

## Release page

`scripts/release_notes.py` builds the page from `CHANGELOG.md` in the tagged
commit and the release's `release.json`, following the Hraness release page
standard (`RELEASES.md` in hraness/.github):

1. the version's summary paragraph and, under `## Changes`, its bullets;
2. `## Install`, with the versioned GitHub Release archive command and then the
   npm command for the same version;
3. `## Verify`, with the `SHA256SUMS` asset, the archive digest, the full source
   commit, and a link to this guide pinned to the tag;
4. the `release.json` record as one trailing HTML comment,
   `<!-- lifecharts-release {...} -->`, which forms the last bytes of the body.

The workflow fails before creating a release when the section is missing, empty,
or says Unreleased. It never uses GitHub's generated notes. On a retry it reads
the identity record after the last `<!-- lifecharts-release ` marker, requires
the body to end with `-->`, and requires the title and every byte above the
record to match a fresh render, so a hand-edited page stops the run for
inspection. To correct a published page, change `CHANGELOG.md` and the page in
the same reviewed change:

```sh
python3 scripts/release_notes.py render --receipt release.json \
  --changelog CHANGELOG.md --out notes.md --title-out title.txt
gh release edit vX.Y.Z --repo hraness/lifecharts \
  --title "$(cat title.txt)" --notes-file notes.md
```

Download `release.json` from the release first. Run
`python3 -m unittest discover -s scripts -p 'test_*.py'` after changing the
renderer.

## Verify a release

Download the archive and its checksum file, then check the digest and confirm
with GitHub that the archive is the one attached to the immutable release:

```sh
version=X.Y.Z
gh release download "v$version" --repo hraness/lifecharts \
  --pattern "hraness-lifecharts-$version.tgz" --pattern SHA256SUMS --pattern release.json
sha256sum --check SHA256SUMS   # macOS: shasum -a 256 --check SHA256SUMS
gh release verify-asset "v$version" "hraness-lifecharts-$version.tgz" --repo hraness/lifecharts
```

`release.json` records the tag, the full source commit, and the archive's
SHA-256 and npm integrity value. The npm mirror publishes the same bytes, so
`npm view @hraness/lifecharts@$version dist.integrity` matches its `integrity`.

## Establish npm publishing once

npm requires the package to exist before a trusted publisher can be configured.
An authorized npm maintainer must make the first publication of the already
verified canonical tarball using a valid session and any required 2FA. Confirm
the npm account has access to the `hraness` scope before publishing. Keep account
authentication and tokens out of this repository and workflow secrets.

```sh
npm whoami --registry=https://registry.npmjs.org
npm publish /absolute/path/to/hraness-lifecharts-1.0.0.tgz \
  --ignore-scripts --access public --registry=https://registry.npmjs.org
```

After that package exists, configure the exact public repository, workflow, and
`npm-release` environment as a trusted publisher. Use a supported authenticated
npm session with account 2FA for this configuration:

```sh
npm trust github @hraness/lifecharts --repo hraness/lifecharts \
  --file npm-mirror.yml --environment npm-release --allow-publish
npm trust list @hraness/lifecharts
```

The workflow uses GitHub-hosted runners and npm 11.19.0 with `id-token: write`.
The package's `repository.url` must identify `hraness/lifecharts`, matching the
OIDC publisher. npm automatically attaches provenance for this public workflow
and package. See [trusted publishing](https://docs.npmjs.com/trusted-publishers/)
and [npm trust prerequisites](https://docs.npmjs.com/cli/v11/commands/npm-trust/).

Preserve existing organization, environment, package, and staged-approval
requirements. If npm requires staging, the mirror stops; it does not weaken that
policy or substitute a token. Staged versions require a maintainer's 2FA approval
before publication, and the staged bytes must match the canonical archive.
[npm's staged publishing rules](https://docs.npmjs.com/cli/v11/commands/npm-stage/)
also require the package to exist already.

## Mirror a completed release

Dispatch `npm-mirror.yml` from main with the exact stable version:

```sh
gh workflow run npm-mirror.yml --repo hraness/lifecharts --ref main -f version=1.0.0
```

The workflow resolves the immutable release, checks out its exact public commit,
downloads its existing archive, verifies the hashes and package files, and tests
an isolated installation. A separate OIDC job publishes those bytes without
checking out or executing package code. It verifies npm's public integrity,
downloaded bytes, and latest tag. An already published matching version is a
read-only verification; a conflicting version stops. The first session-based
publication does not acquire OIDC provenance retroactively.

If publication returns an uncertain result or npm scanning delays the download,
inspect that exact registry version and the workflow output before dispatching
again. Do not replace a release, repack the npm mirror, move tags backward, or
retry a possibly accepted publication blindly. Keep the successful GitHub release
available while resolving an npm authentication or approval requirement.
