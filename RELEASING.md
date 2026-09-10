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
2. Merge after review and both Package CI jobs pass. CI checks the exact npm
   archive and an isolated installation on Node 22.14.0 and 24.20.0, plus Bun
   execution. The package has no install scripts or runtime dependencies.
3. Have a repository administrator verify immutability immediately before tagging:

   ```sh
   test "$(gh api repos/hraness/lifecharts/immutable-releases --jq '.enabled')" = true
   ```

   The setting endpoint requires Administration-read access, which the workflow's
   `GITHUB_TOKEN` cannot carry. A false result or failed lookup stops the release.
4. Create an annotated `v<version>` tag on that reviewed main commit and push the
   exact tag. Use a new stable version for changed bytes; never move a release tag.

`release.yml` checks the version, public repository identity, and main ancestry.
It packs once, verifies the archive, creates a
draft, uploads the archive with `release.json` and `SHA256SUMS`, and publishes the
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
