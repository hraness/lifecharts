# Changelog

Each release page on GitHub copies its summary and changes from the matching section below. Add the section for a new version in the pull request that bumps it.

## 1.0.4 - 2026-09-26

Error messages now say what was wrong and give one command to run next, and every command has its own help. Chart links, file formats and exit codes work as before.

- A mistyped command, option, template or help topic is named, with the closest match: `lifecharts crate` prints `✗ Unknown command "crate". Did you mean "create"?` then `→ lifecharts --help`.
- `lifecharts create --help`, `create -h` and `lifecharts help create` show that command's usage and an example instead of the full help.
- The five support lines at the end of `lifecharts --help` are now one, and help fits in 80 columns.
- `lifecharts --version` prints `lifecharts 1.0.4`; `lifecharts --version --json` adds the timeline format.
- Outside UTF-8 terminals, `✗` and `→` become `FAIL` and `->`.

## 1.0.3 - 2026-09-25

The CLI, agent skill, and npm package now describe Lifecharts as a way to turn the chapters of your life into one timeline you can share. Chart links, file formats, and commands work as before.

- `lifecharts --help` opens with “Lifecharts: Turn the chapters of your life into one timeline you can share”.
- Running `lifecharts` with no arguments in a terminal shows “Chart your life in chapters.” beside the logo.
- A chart created without a `title` or `name` is titled “My life timeline” instead of “My life chart”.
- `lifecharts --version` prints `Lifecharts CLI 1.0.3 · timeline format 1`.
- The npm package description and the agent skill's short description use the new wording.
