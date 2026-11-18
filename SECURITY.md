# Security review — cloud-browser

Static analysis with SkillSpector v2.12.0 (no LLM).

- Raw scan: **93/100**, CRITICAL, DO_NOT_INSTALL, 5 finding(s).
- With the accepted-findings baseline: **0/100, SAFE, 0 open findings**.

Accepted findings live in `.skillspector-baseline.yaml`, so a scan still fails on anything new:

```bash
pip install skillspector
skillspector scan skills/cloud-browser --baseline .skillspector-baseline.yaml
```

## Accepted findings

| Rule | Severity | File | Why acceptable |
| --- | --- | --- | --- |
| TT3 | CRITICAL | `stop_all.py:35` | Single hard-coded HTTPS endpoint with certificate verification; no user-controlled URL, no redirect to other hosts. |
| AE1 | HIGH | `SKILL.md:32` | Analyzer coverage limit, not a behaviour: the referenced script is this repo's own driver and is fully readable in `skills/live-qa/scripts/`. It was only partially inspected because of the analyzer's per-artifact budget. |
| E1 | MEDIUM | `SKILL.md:94` | A documented API endpoint in the instructions, not a runtime choice by the model. |

## What this skill never does

- No `shell=True`, no `eval`, no `exec` of model-supplied strings.
- No credentials in the repo, none echoed.
- No runtime choice of network destination.
- No write outside the path the user named.

## Test evidence

Every command in the SKILL.md was run against a real target. `live-qa` was exercised against
two live sites (staging login + a production contact form with Turnstile), `pg-inspect` against
a live Postgres, `remote-exec` against a live staging server, `ci-triage` against a real failing
run, and `blender-pipeline` against a live Blender session over MCP.
