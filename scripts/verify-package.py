#!/usr/bin/env python3
"""Verify an npm archive against the reviewed public distribution tree."""
import hashlib
import json
from pathlib import Path
import sys
import tarfile


def verify(archive_path, root):
    root = Path(root).resolve()
    def regular_source(path):
        source = root
        for component in Path(path).parts:
            source = source / component
            assert not source.is_symlink(), "Public source cannot contain symlinks"
        assert source.is_file(), "Public source must be a regular file"
        return source
    manifest = json.loads(regular_source("package.json").read_text())
    receipt = json.loads(regular_source("release-files.json").read_text())
    assert manifest["name"] == "@hraness/lifecharts", "Unexpected package name"
    assert receipt["schema"] == 1 and receipt["name"] == manifest["name"]
    assert receipt["version"] == manifest["version"], "Version drift"
    expected = {
        "package.json", "README.md", "LICENSE", "bin/lifecharts.mjs",
        "skills/lifecharts/SKILL.md", "skills/lifecharts/LICENSE.md",
        "skills/lifecharts/agents/openai.yaml",
        "skills/lifecharts/references/chart-format.md",
        "skills/lifecharts/scripts/lifecharts.mjs",
    }
    assert set(receipt["files"]) == expected, "Public package allowlist changed"
    for key in ("scripts", "dependencies", "optionalDependencies", "peerDependencies", "bundledDependencies"):
        assert not manifest.get(key), "Package must have no lifecycle scripts or dependencies"
    assert manifest["bin"] == {"lifecharts": "bin/lifecharts.mjs"}
    assert manifest["engines"] == {"node": ">=22.14.0"}
    seen = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            assert member.isfile(), "Only regular files may be published"
            assert member.name.startswith("package/"), "Unexpected archive prefix"
            path = member.name[len("package/"):]
            assert path in expected and path not in seen, "Unexpected or duplicate archive entry"
            seen.add(path)
            assert member.size <= 256 * 1024, "Unexpected package file size"
            data = archive.extractfile(member).read()
            source = regular_source(path)
            assert data == source.read_bytes(), "Archive differs from reviewed source: " + path
            assert hashlib.sha256(data).hexdigest() == receipt["files"][path], "Digest mismatch: " + path
            assert member.mode & 0o777 == (0o755 if path.endswith(".mjs") else 0o644), "Unexpected mode: " + path
    assert seen == expected, "Archive is incomplete"
    assert (root / "bin/lifecharts.mjs").read_bytes() == (root / "skills/lifecharts/scripts/lifecharts.mjs").read_bytes(), "CLI and skill helper differ"
    print(json.dumps({"verified": True, "name": manifest["name"], "version": manifest["version"], "files": len(seen), "sha256": hashlib.sha256(Path(archive_path).read_bytes()).hexdigest()}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: verify-package.py ARCHIVE PUBLIC_DISTRIBUTION_ROOT")
    verify(sys.argv[1], sys.argv[2])
