---
name: cloud-browser
description: Run browsing in a hosted cloud browser (stealth managed Chrome, managed proxies, live preview, session recording) instead of locally, and guarantee it is stopped so it stops billing. Use when a site blocks the local headless browser, when browsing must survive the local machine, when a session must be recorded, or when a cloud browser may already be running and needs cleanup.
allowed-tools:
  - Bash
  - Read
permissions:
  - network
  - env
license: MIT
---

# Hosted cloud browser

Third-party providers, reached through the `agent-browser` CLI's built-in providers
(`-p browseruse`, `-p browserbase`, `-p kernel`, `-p browserless`, `-p agentcore`).
Setup for each provider is owned upstream — this skill covers the pattern and the one
thing the docs skip: **stopping the thing so it stops costing money.**

Two ways to drive it, same result: your agent's native browser tool if it has one
(pi's `agent_browser`, a Playwright/Chrome-DevTools MCP server), otherwise the CLI
from a shell, which works in every agent:

```bash
agent-browser -p browseruse open https://example.com
```

**Not for:** ordinary browsing where a local browser works — that is faster and free, so use `live-qa` instead. Reach for this when a site blocks local headless, or a run must outlive your machine.

## Portability

Works in any agent that can run shell commands (pi, Claude Code, Codex, Cursor,
Gemini CLI, …): the instructions are plain Markdown and the helper is a stdlib
script. Commands use `$SKILL_DIR` for this skill's own directory — the folder that
holds this `SKILL.md`. Set it once per session, for example:

```bash
SKILL_DIR=~/.claude/skills/cloud-browser     # or ~/.codex/skills/…, ~/.pi/agent/skills/…, .cursor/skills/…
```

## Preconditions

- `agent-browser` on PATH (`agent-browser doctor` lists provider state; a provider
  shows "KEY not set" only when its credential is missing for *that* process). With
  a native browser tool, the equivalent is `agent_browser ["doctor"]`.
- The provider's key exported **from the shell that launched the agent**. A key
  added to a shell config after launch is invisible to the running process;
  restart from a login shell if doctor still reports it missing.

## Start a session

Provider flags are launch-scoped, so the first call must be a fresh session:

```bash
agent-browser -p browseruse open https://example.com
# native tool equivalent (pi): { "args": ["-p","browseruse","open","https://example.com"],
#                                "sessionMode": "fresh" }
```

Then the normal flow applies: `snapshot -i`, act on refs, re-snapshot after any
navigation or rerender. Follow-up calls use the default sessionMode.

## Stop it — always

`close` succeeds only after the provider acknowledges the stop; on failure the
session id is kept so a retry can release it. A failed stop leaves a real browser
running and billing (browser time **plus** proxy traffic).

When a run ends abnormally (crash, timeout, forgotten tab), sweep instead of
guessing:

```
python3 "$SKILL_DIR/scripts/stop_all.py" --dry-run     # what is running, and since when
python3 "$SKILL_DIR/scripts/stop_all.py" --yes         # stop them all
python3 "$SKILL_DIR/scripts/stop_all.py" --yes --keep <session-id>
```

It needs `BROWSER_USE_API_KEY`, uses the REST API directly (`X-Browser-Use-API-Key`,
no `Bearer`), and prints each id, its start time, and the stop result. Do not run
it with `--yes` on a shared account without saying so first: it stops *every*
browser the key can see.

## Provider knobs (browseruse)

| Variable | Effect |
| --- | --- |
| `BROWSER_USE_PROFILE_ID` | persistent cookies/logins profile |
| `BROWSER_USE_PROXY_COUNTRY` | managed proxy country; `none`/`direct` disables |
| `BROWSER_USE_ENABLE_RECORDING` | capture the session as video (off by default) |

## REST fallback (no CLI provider)

Create, hand the `cdpUrl` to your browser tool (`agent-browser --cdp` or the native
equivalent), then stop explicitly:

```bash
curl --fail-with-body -sS https://api.browser-use.com/api/v4/browsers \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" -d '{"proxyCountryCode":"us"}'
curl --fail-with-body -sS -X PATCH \
  https://api.browser-use.com/api/v4/browsers/<id> \
  -H "X-Browser-Use-API-Key: $BROWSER_USE_API_KEY" \
  -H "Content-Type: application/json" -d '{"action":"stop"}'
```

## Cost and limits

Check quota before a long job: `GET /api/v2/billing/account`. Providers differ in
concurrency, retention, and whether proxy traffic is metered separately — read the
provider's own page rather than assuming; these numbers change. Prefer a local
browser for anything that does not need stealth, residential egress, or
persistence, and prefer a recording only when it is the deliverable.

## When not to use this

- Ordinary local QA, screenshots, or clicking through your own app: use the local
  browser. Cloud adds latency and cost for no gain.
- Anything requiring credentials you cannot put in a cloud browser, or a site whose
  terms forbid automation.
