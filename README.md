# cloud-browser

<h3 align="center">Hosted browser sessions — plus the sweep that stops the ones nobody closed.</h3>

<p align="center">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-3DA639?style=flat-square"></a>
  <img alt="agents" src="https://img.shields.io/badge/works%20in-pi%20%7C%20Claude%20Code%20%7C%20Codex%20%7C%20Cursor-4B5563?style=flat-square">
  <img alt="skillspector" src="https://img.shields.io/badge/SkillSpector-0%2F100%20SAFE-2EA043?style=flat-square">
  <img alt="tokens" src="https://img.shields.io/badge/session%20cost-~94%20tok-6E7681?style=flat-square">
</p>

<p align="center">
  <img alt="cloud-browser demo" src="skills/cloud-browser/assets/demo.gif" width="820">
</p>

## Install

One command for each agent — the skill is plain Markdown plus a script, so nothing is coupled to one ecosystem.

```bash
# Claude Code (plugin, stays updatable)
claude plugin marketplace add ibrahimbdr/appit-skills
claude plugin install cloud-browser@appit-skills

# pi
pi install git:github.com/ibrahimbdr/cloud-browser

# any agent that reads a skills directory
git clone git@github.com:ibrahimbdr/cloud-browser.git
cp -r cloud-browser/skills/cloud-browser ~/.claude/skills/      # or ~/.codex/skills/, .cursor/skills/, …
```

## Why this exists

Provider pages explain how to start a cloud browser; none explain the failure that costs money — a session that never got closed. This ships the sweep.

## Use

- Start: `agent-browser -p browseruse open <url>` (or your native browser tool)`
- Sweep: `scripts/stop_all.py --dry-run` then `--yes [--keep ID]`
- Record: `BROWSER_USE_ENABLE_RECORDING=1` before launch`

## Requires

- `agent-browser` on PATH (`agent-browser doctor` lists provider state).
- The provider credential exported from the shell that launched your agent.
- Python 3.9+ for the sweep (`stop_all.py`).

## What you get

- Dry-run by default; `--yes` stops **every** browser the key can see — only run it when the user agreed.
- Provider limits are deliberately not tabulated: they change, and a stale comparison is worse than none.
- Renamed from a vendor-product name so it does not read as an official integration.

## Cost

| | tokens |
| --- | --- |
| always-on (the description, every session) | ~94 |
| on invoke | ~1k |

The demo above is regenerated from a real run: `demos/cloud-browser.json` holds the captured
output, `tools/make_demo.py` renders it. No invented screenshots.

## Security

Static analysis with SkillSpector: **0/100, SAFE, 0 open findings** against the committed
baseline. Every accepted finding is listed with its reason in [SECURITY.md](SECURITY.md).
The skill never uses `shell=True`, never reads or stores a credential, and never chooses a
network destination at runtime.

## Part of the Appit collection

Browser QA · CI triage · Postgres · runbooks · SSH · Trello · cloud browsers · OpenDesign · Blender —
one marketplace: [appit-skills](https://github.com/ibrahimbdr/appit-skills).

## License

MIT. See [LICENSE](LICENSE).
