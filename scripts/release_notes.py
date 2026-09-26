#!/usr/bin/env python3
"""Render and check Lifecharts GitHub Release pages.

The page follows the Hraness release page standard: a summary and changes
copied from the version's CHANGELOG.md section, generated Install and Verify
sections, then the release.json identity record as a trailing HTML comment.
"""

import argparse
import json
import pathlib
import re
import sys

REPOSITORY = 'hraness/lifecharts'
PRODUCT = 'Lifecharts'
PACKAGE = '@hraness/lifecharts'
IDENTITY_OPEN = '<!-- lifecharts-release '
IDENTITY_CLOSE = ' -->'
RECEIPT_KEYS = ['schema', 'name', 'version', 'tag', 'sourceSha', 'archive', 'sha256', 'integrity']
STABLE = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)')
HEADING = re.compile(r'## v?(?P<version>\S+)(?: - \d{4}-\d{2}-\d{2})?')


class ReleaseNotesError(Exception):
    pass


def changelog_section(text, version):
    """Return (summary, bullets) from the version's CHANGELOG.md section."""
    if not STABLE.fullmatch(version):
        raise ReleaseNotesError(f'Stable version required, got {version!r}')
    lines = text.replace('\r\n', '\n').split('\n')
    start = None
    for index, line in enumerate(lines):
        if re.fullmatch(rf'## v?{re.escape(version)}\b.*\bunreleased\b.*', line.rstrip(), re.IGNORECASE):
            raise ReleaseNotesError(f'CHANGELOG.md section {version} still says Unreleased')
        match = HEADING.fullmatch(line.rstrip())
        if match and match['version'] == version:
            if start is not None:
                raise ReleaseNotesError(f'CHANGELOG.md has more than one {version} section')
            start = index + 1
    if start is None:
        raise ReleaseNotesError(f'CHANGELOG.md has no section for {version}')
    end = next((i for i in range(start, len(lines)) if lines[i].startswith('## ')), len(lines))
    body = '\n'.join(lines[start:end]).strip()
    if not body:
        raise ReleaseNotesError(f'CHANGELOG.md section {version} is empty')
    if re.search(r'\bunreleased\b', body, re.IGNORECASE):
        raise ReleaseNotesError(f'CHANGELOG.md section {version} still says Unreleased')
    if re.search(r'^#', body, re.MULTILINE):
        raise ReleaseNotesError(f'CHANGELOG.md section {version} must hold only a summary and a bulleted list')
    blocks = re.split(r'\n\s*\n', body)
    summary = [b for b in blocks if not b.lstrip().startswith('- ')]
    bullets = [b for b in blocks if b.lstrip().startswith('- ')]
    if len(summary) != 1 or blocks[0] != summary[0]:
        raise ReleaseNotesError(f'CHANGELOG.md section {version} must open with one summary paragraph')
    if not bullets or blocks[1:] != bullets:
        raise ReleaseNotesError(f'CHANGELOG.md section {version} needs a bulleted list of changes after the summary')
    return summary[0].strip(), '\n'.join(b.rstrip() for b in bullets)


def check_receipt(receipt):
    if not isinstance(receipt, dict) or list(receipt) != RECEIPT_KEYS:
        raise ReleaseNotesError('Release record has unexpected fields')
    version = receipt['version']
    if receipt['schema'] != 1 or receipt['name'] != PACKAGE or not STABLE.fullmatch(version):
        raise ReleaseNotesError('Release record has an unexpected package or version')
    if receipt['tag'] != f'v{version}' or receipt['archive'] != f'hraness-lifecharts-{version}.tgz':
        raise ReleaseNotesError('Release record tag or archive does not match its version')
    if not re.fullmatch(r'[0-9a-f]{40}', receipt['sourceSha']) or not re.fullmatch(r'[0-9a-f]{64}', receipt['sha256']):
        raise ReleaseNotesError('Release record has an invalid commit or digest')
    if not re.fullmatch(r'sha512-[A-Za-z0-9+/]{86}==', receipt['integrity']):
        raise ReleaseNotesError('Release record has an invalid integrity value')
    return receipt


def title(receipt):
    return f"{PRODUCT} {check_receipt(receipt)['tag']}"


def identity_comment(receipt):
    record = json.dumps(check_receipt(receipt), separators=(',', ':'), ensure_ascii=True)
    return IDENTITY_OPEN + record + IDENTITY_CLOSE


def render_notes(receipt, changelog):
    """Everything above the identity record."""
    check_receipt(receipt)
    version, tag, sha = receipt['version'], receipt['tag'], receipt['sourceSha']
    summary, bullets = changelog_section(changelog, version)
    base = f'https://github.com/{REPOSITORY}'
    asset = f"{base}/releases/download/{tag}/{receipt['archive']}"
    return (
        f'{summary}\n\n'
        f'## Changes\n\n{bullets}\n\n'
        '## Install\n\n'
        'Install this version from the archive attached to this release:\n\n'
        f'```sh\nnpm install --global {asset}\n```\n\n'
        'Or install the same archive from npm:\n\n'
        f'```sh\nnpm install --global {PACKAGE}@{version}\n```\n\n'
        '## Verify\n\n'
        f"`SHA256SUMS` on this release lists the SHA-256 of `{receipt['archive']}` "
        f"(`{receipt['sha256']}`) and `release.json`. "
        f'The archive was built from commit [`{sha}`]({base}/commit/{sha}). '
        f'[Verify a release]({base}/blob/{tag}/RELEASING.md#verify-a-release) '
        'shows how to check the checksum and confirm with GitHub that a downloaded archive is the one attached to this release.\n\n'
    )


def render_body(receipt, changelog):
    return render_notes(receipt, changelog) + identity_comment(receipt)


def parse_identity(body):
    """Return (notes, receipt) from a release body ending in the identity record."""
    if not isinstance(body, str) or not body.endswith('-->'):
        raise ReleaseNotesError('Release body must end with the identity record')
    start = body.rfind(IDENTITY_OPEN)
    if start < 0:
        raise ReleaseNotesError('Release body has no identity record')
    comment = body[start:]
    if not comment.endswith(IDENTITY_CLOSE) or comment.count('-->') != 1:
        raise ReleaseNotesError('Release identity record is malformed')
    try:
        receipt = json.loads(comment[len(IDENTITY_OPEN):-len(IDENTITY_CLOSE)])
    except json.JSONDecodeError as error:
        raise ReleaseNotesError('Release identity record is not valid JSON') from error
    check_receipt(receipt)
    if identity_comment(receipt) != comment:
        raise ReleaseNotesError('Release identity record is not in its canonical form')
    return body[:start], receipt


def verify_body(body, receipt, changelog):
    """Check a published body against the release record and changelog."""
    notes, identity = parse_identity(body)
    if identity != receipt:
        raise ReleaseNotesError('Release identity record differs from release.json')
    if notes != render_notes(receipt, changelog):
        raise ReleaseNotesError('Release notes differ from the rendered changelog, Install, and Verify sections')
    return identity


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    render = commands.add_parser('render', help='Write the release body for a release.json record')
    render.add_argument('--receipt', required=True, type=pathlib.Path)
    render.add_argument('--changelog', default='CHANGELOG.md', type=pathlib.Path)
    render.add_argument('--out', required=True, type=pathlib.Path)
    render.add_argument('--title-out', type=pathlib.Path)
    check = commands.add_parser('check', help='Check that CHANGELOG.md has a releasable section')
    check.add_argument('--version', required=True)
    check.add_argument('--changelog', default='CHANGELOG.md', type=pathlib.Path)
    args = parser.parse_args(argv)
    try:
        changelog = args.changelog.read_text(encoding='utf-8')
        if args.command == 'check':
            changelog_section(changelog, args.version)
            print(f'CHANGELOG.md has a releasable {args.version} section')
            return 0
        receipt = json.loads(args.receipt.read_text(encoding='utf-8'))
        body = render_body(receipt, changelog)
        verify_body(body, receipt, changelog)
        args.out.write_text(body, encoding='utf-8')
        if args.title_out:
            args.title_out.write_text(title(receipt), encoding='utf-8')
        return 0
    except (OSError, ReleaseNotesError) as error:
        print(f'release notes: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
