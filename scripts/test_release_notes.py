#!/usr/bin/env python3
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import release_notes as rn  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
RECEIPT = {
    'schema': 1,
    'name': '@hraness/lifecharts',
    'version': '2.1.0',
    'tag': 'v2.1.0',
    'sourceSha': '0123456789abcdef0123456789abcdef01234567',
    'archive': 'hraness-lifecharts-2.1.0.tgz',
    'sha256': 'ab' * 32,
    'integrity': 'sha512-' + 'A' * 86 + '==',
}
CHANGELOG = """# Changelog

## Unreleased

- Work in progress.

## v2.1.0 - 2026-10-01

Charts keep their colors when you edit them.

- `lifecharts compile` keeps each chapter's color.
- `lifecharts verify` names the chapter with an invalid color.

## 2.0.0

Older notes.

- Older change.
"""


class ChangelogSection(unittest.TestCase):
    def test_reads_summary_and_changes(self):
        summary, bullets = rn.changelog_section(CHANGELOG, '2.1.0')
        self.assertEqual(summary, 'Charts keep their colors when you edit them.')
        self.assertEqual(bullets.splitlines(), [
            "- `lifecharts compile` keeps each chapter's color.",
            '- `lifecharts verify` names the chapter with an invalid color.',
        ])

    def test_plain_heading_without_date(self):
        self.assertEqual(rn.changelog_section(CHANGELOG, '2.0.0')[0], 'Older notes.')

    def test_missing_section_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'no section'):
            rn.changelog_section(CHANGELOG, '2.2.0')

    def test_empty_section_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'empty'):
            rn.changelog_section('## 2.2.0\n\n## 2.1.0\n\nText.\n\n- Change.\n', '2.2.0')

    def test_unreleased_section_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'Unreleased'):
            rn.changelog_section('## 2.2.0\n\nUnreleased.\n\n- Change.\n', '2.2.0')
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'Unreleased'):
            rn.changelog_section('## 2.2.0 - Unreleased\n\nText.\n\n- Change.\n', '2.2.0')
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'no section'):
            rn.changelog_section('## Unreleased\n\nText.\n\n- Change.\n', '2.2.0')

    def test_section_without_changes_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'bulleted list'):
            rn.changelog_section('## 2.2.0\n\nOnly a summary.\n', '2.2.0')

    def test_section_without_summary_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'summary'):
            rn.changelog_section('## 2.2.0\n\n- Change.\n', '2.2.0')

    def test_duplicate_section_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'more than one'):
            rn.changelog_section('## 2.2.0\n\nA.\n\n- B.\n\n## v2.2.0\n\nA.\n\n- B.\n', '2.2.0')

    def test_repository_changelog_covers_package_version(self):
        version = json.loads((ROOT / 'package.json').read_text())['version']
        rn.changelog_section((ROOT / 'CHANGELOG.md').read_text(), version)


class RenderedBody(unittest.TestCase):
    def test_title(self):
        self.assertEqual(rn.title(RECEIPT), 'Lifecharts v2.1.0')

    def test_body_shape(self):
        body = rn.render_body(RECEIPT, CHANGELOG)
        self.assertTrue(body.startswith('Charts keep their colors when you edit them.\n\n## Changes\n\n- `lifecharts compile`'))
        headings = [line for line in body.splitlines() if line.startswith('#')]
        self.assertEqual(headings, ['## Changes', '## Install', '## Verify'])
        self.assertIn('npm install --global https://github.com/hraness/lifecharts/releases/download/v2.1.0/hraness-lifecharts-2.1.0.tgz\n', body)
        self.assertIn('npm install --global @hraness/lifecharts@2.1.0\n', body)
        self.assertIn('`SHA256SUMS`', body)
        self.assertIn(RECEIPT['sourceSha'], body)
        self.assertIn('https://github.com/hraness/lifecharts/blob/v2.1.0/RELEASING.md#verify-a-release', body)
        self.assertTrue(body.endswith(' -->'))
        self.assertEqual(body.count('<!--'), 1)
        visible = body[:body.rindex('<!--')]
        self.assertIn(RECEIPT['sha256'], visible)
        self.assertNotIn(RECEIPT['integrity'], visible)
        for banned in ['latest', 'Unreleased', 'Older', "What's Changed", 'Full Changelog', 'Generated with', 'Automated release', 'Canonical GitHub release for', '—']:
            self.assertNotIn(banned, visible)

    def test_identity_parses(self):
        notes, receipt = rn.parse_identity(rn.render_body(RECEIPT, CHANGELOG))
        self.assertEqual(receipt, RECEIPT)
        self.assertEqual(notes, rn.render_notes(RECEIPT, CHANGELOG))
        self.assertEqual(rn.verify_body(rn.render_body(RECEIPT, CHANGELOG), RECEIPT, CHANGELOG), RECEIPT)

    def test_identity_uses_last_marker(self):
        body = rn.render_body(RECEIPT, CHANGELOG)
        decoy = '<!-- lifecharts-release {"schema":1} -->'
        self.assertEqual(rn.parse_identity(decoy + '\n\n' + body)[1], RECEIPT)

    def test_tampered_notes_detected(self):
        body = rn.render_body(RECEIPT, CHANGELOG).replace('keeps each', 'kept each')
        rn.parse_identity(body)
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'notes differ'):
            rn.verify_body(body, RECEIPT, CHANGELOG)

    def test_tampered_identity_detected(self):
        body = rn.render_body(RECEIPT, CHANGELOG)
        other = dict(RECEIPT, sha256='cd' * 32)
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'differs from release.json'):
            rn.verify_body(body, other, CHANGELOG)
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'canonical'):
            rn.parse_identity(body.replace('{"schema":1,', '{"schema": 1,'))

    def test_trailing_text_after_identity_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'end with'):
            rn.parse_identity(rn.render_body(RECEIPT, CHANGELOG) + '\n')
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'malformed|no identity'):
            rn.parse_identity(rn.render_body(RECEIPT, CHANGELOG) + '\nextra -->')

    def test_missing_identity_fails(self):
        with self.assertRaisesRegex(rn.ReleaseNotesError, 'no identity'):
            rn.parse_identity('Notes only. <!-- other -->')

    def test_invalid_receipt_rejected(self):
        with self.assertRaises(rn.ReleaseNotesError):
            rn.render_body(dict(RECEIPT, tag='v2.1.1'), CHANGELOG)

    def test_cli_render_fails_before_writing_for_missing_section(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory)
            (path / 'release.json').write_text(json.dumps(dict(RECEIPT, version='3.0.0', tag='v3.0.0', archive='hraness-lifecharts-3.0.0.tgz')))
            (path / 'CHANGELOG.md').write_text(CHANGELOG)
            code = rn.main(['render', '--receipt', str(path / 'release.json'), '--changelog', str(path / 'CHANGELOG.md'), '--out', str(path / 'notes.md')])
            self.assertEqual(code, 1)
            self.assertFalse((path / 'notes.md').exists())

    def test_cli_render_writes_body_and_title(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory)
            (path / 'release.json').write_text(json.dumps(RECEIPT, indent=2) + '\n')
            (path / 'CHANGELOG.md').write_text(CHANGELOG)
            code = rn.main(['render', '--receipt', str(path / 'release.json'), '--changelog', str(path / 'CHANGELOG.md'), '--out', str(path / 'notes.md'), '--title-out', str(path / 'title.txt')])
            self.assertEqual(code, 0)
            self.assertEqual((path / 'notes.md').read_text(), rn.render_body(RECEIPT, CHANGELOG))
            self.assertEqual((path / 'title.txt').read_text(), 'Lifecharts v2.1.0')


if __name__ == '__main__':
    unittest.main()
