#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const archive = process.argv[2];
if (!archive || process.argv.length !== 3) throw new Error('Usage: check-package.mjs ARCHIVE');
const root = await mkdtemp(join(tmpdir(), 'lifecharts-install-'));
function run(command, args, input) {
  const result = spawnSync(command, args, { cwd: root, encoding: 'utf8', input, timeout: 30_000, env: { ...process.env, HRANESS_SUPPORT_AUDIENCE: 'off', npm_config_cache: join(root, 'cache'), npm_config_update_notifier: 'false' } });
  assert.equal(result.status, 0, `${command} failed: ${result.stderr}`);
  return result.stdout.trim();
}
try {
  await writeFile(join(root, 'package.json'), '{"private":true}\n');
  run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', '--offline', resolve(archive)]);
  const installed = join(root, 'node_modules/@hraness/lifecharts');
  const manifest = JSON.parse(await readFile(join(installed, 'package.json'), 'utf8'));
  assert.equal(run('npm', ['exec', '--offline', '--', 'lifecharts', '--version']), `Lifecharts CLI ${manifest.version} · timeline format 1`);
  const cli = join(installed, 'bin/lifecharts.mjs');
  if (Number(manifest.version.split('.')[0]) >= 1 && manifest.version !== '1.0.0' && manifest.version !== '1.0.1') {
    const protocol = JSON.parse(run(process.execPath, [cli, 'support', 'protocol', '--json']));
    assert.equal(protocol.offer.product.id, 'lifedaysleft');
    assert.deepEqual(protocol.offer.actions.map(action => action.kind), ['support']);
    assert.deepEqual(protocol.commands.protocol, [process.execPath, cli, 'support', 'protocol', '--json']);
    assert.equal(protocol.offer.emailSuggestion, undefined);
  }
  const fixture = { name: 'Morgan', view: 'bars', chapters: [
    { label: 'University', start: '2012-09', end: '2016-05' },
    { label: 'Design work', start: '2016-06', end: 'present' },
    { label: 'Mentoring', start: '2020-01', end: 'present' },
  ] };
  const created = JSON.parse(run(process.execPath, [cli, 'create', '-', '--json'], JSON.stringify(fixture)));
  assert.equal(created.document.startKind, 'timeline');
  assert.equal(created.document.view, 'bars');
  assert.equal(created.document.chapters.length, 3);
  assert.ok(created.url.startsWith('https://lifecharts.io/view#t=1.'));
  const inspected = JSON.parse(run(process.execPath, [cli, 'inspect', created.url]));
  assert.deepEqual(inspected, created.document);
  inspected.title = 'Morgan’s chapters';
  const updated = run(process.execPath, [cli, 'compile', '-'], JSON.stringify(inspected));
  const verified = JSON.parse(run(process.execPath, [cli, 'verify', updated, '--json']));
  assert.equal(verified.verified, true);
  assert.deepEqual(verified.document, inspected);
  assert.match(run(process.execPath, [join(installed, 'skills/lifecharts/scripts/lifecharts.mjs'), '--help']), /Lifecharts/);
  const invalid = spawnSync(process.execPath, [cli, 'create', '-'], { input: '{"birthDate":"invalid"}', encoding: 'utf8', timeout: 10_000 });
  assert.equal(invalid.status, 1);
  console.log(JSON.stringify({ installed: true, runtime: process.version, name: manifest.name, version: manifest.version, created: true, edited: true, verified: true }));
} finally {
  await rm(root, { recursive: true, force: true });
}
