# Changelog

Each release page on GitHub copies its summary and changes from the matching section below. Add the section for a new version in the pull request that bumps it.

## 1.0.3 - 2026-09-25

The CLI, agent skill, and npm package now describe Lifecharts as a way to turn the chapters of your life into one timeline you can share. Chart links, file formats, and commands work as before.

- `lifecharts --help` opens with “Lifecharts: Turn the chapters of your life into one timeline you can share”.
- Running `lifecharts` with no arguments in a terminal shows “Chart your life in chapters.” beside the logo.
- A chart created without a `title` or `name` is titled “My life timeline” instead of “My life chart”.
- `lifecharts --version` prints `Lifecharts CLI 1.0.3 · timeline format 1`.
- The npm package description and the agent skill's short description use the new wording.
