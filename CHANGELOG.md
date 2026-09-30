# Changelog

Each release page on GitHub copies its summary and changes from the matching section below. Add the section for a new version in the pull request that bumps it.

## 1.1.0 - 2026-09-30

Lifecharts keeps supported global installations up to date before ordinary commands, with controls for checking releases and turning automatic updates off.

- Check for a stable release at most once a day on supported global Bun and npm installations on macOS and Linux. Downloads use the authenticated GitHub CLI and verified immutable release archives.
- Add `lifecharts update`, `update check`, `update status`, `update enable`, and `update disable`, with JSON output for scripts. Preserve exact Bun version pins and saved opt-outs.
- Wait for running commands before replacing the installation, then run the requested command with its original arguments and input. CI, help, support commands, nested tools, and `HRANESS_NO_UPDATE=1` skip automatic checks.
- Keep copied Agent Skill helpers, source checkouts, project dependencies, and Windows installations on their existing update workflow. Document the one-time upgrade for older CLI installations.

## 1.0.5 - 2026-09-26

Running `lifecharts` with no arguments now shows a short start screen, and agents get errors as JSON they can read. Chart links, file formats and exit codes work as before.

- `lifecharts` alone prints what it does and five commands to start with. `lifecharts --help` still lists every command.
- With `--json`, or when an agent runs it, an error is one JSON object on stdout, such as `{"ok":false,"error":{"code":"unknown-command","message":"…","next":"lifecharts --help"}}`, with the same exit code. People still see `✗` and `→` on stderr.
- If a command's input is an error saved from an earlier lifecharts command, it says so and quotes that error instead of reporting an unsupported field.
- Root help ends with one support line. The support commands agents use are listed under `lifecharts help advanced` and work as before.
- A person running lifecharts at a terminal sees support invitations as text, and a script that can't be identified sees none.

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
