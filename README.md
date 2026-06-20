# ticket-preflight-check

An agent skill that reads a ticket from the perspective of a developer about to implement it and surfaces gaps that would cause blockers, misdirection, or thrown-away work.

Not a linter. Not a checklist. It reads the ticket the way a developer would and asks: what's going to block me?

## Try it

Paste a ticket into your agent and say:

> Run a preflight check on this ticket before I start implementing.

Or point your agent at a GitHub issue URL if you have GitHub MCP connected.

## Install

Drop the `SKILL.md` file into your agent's skills directory. For Claude Code, that's `~/.claude/skills/` or your project's `.claude/skills/` folder.

## What it does

The skill identifies 7 categories of gaps:

| Category | Example |
|----------|---------|
| Requirements | "The ticket bundles two deliverables — which is in scope?" |
| Contract | "No API surface proposed — no shape, methods, or data model" |
| Configuration | "Missing OS/Node version in environment block" |
| Scope | "Blast radius is larger than implied — ownership unclear" |
| Dependency | "Upstream PR #30660 merge status unknown — work may be blocked" |
| Edge case | "Crash may be data-dependent — only tested with /products/1" |
| Wrong mental model | "PostgREST returns 200 even when zero rows match — this is by design, not a bug" |

For bug reports, it also checks for missing reproduction steps, error messages, and environment info — the fields developers rank as most important for starting work ([Bettenburg et al., FSE 2008](https://eecs481.org/readings/bugreport.pdf)).

## Output

```markdown
## Preflight Report

**Risk level:** Medium

### Confirmed
- Reproduction repo provided
- Environment info complete

### Gaps
- **Scope gap:** Ticket bundles two distinct deliverables (CNA defaults vs. build detection). Which is in scope?
  - Why it matters: A developer could fix one and leave the actual blocker unresolved.
  - Suggested action: Confirm which problem is the primary target.

### Accepted Unknowns
[Developer fills in after review]
```

## Evaluated performance

Tested against 12 real GitHub issues across 6 repos and 5 genres.

| Metric | Score |
|--------|-------|
| Recall | 0.95 |
| Precision | 0.63 |
| Risk accuracy | 10/12 |

**Genres tested:** bug reports (Next.js), vague feature requests (VS Code, React DevTools), dependency-blocked tickets (Prisma/next-auth/Vercel), API contract issues (tRPC, Supabase), tracking issues (Rust compiler).

The skill correctly identifies tracking/meta issues as non-implementable and assigns Low risk.

See `eval/` for the full benchmark dataset and runner.

## Eval

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Run all 12 benchmark issues
python eval/run_eval.py

# Single run, faster
python eval/run_eval.py --runs 1

# Different model
python eval/run_eval.py --model claude-opus-4-8

# Filter by genre
python eval/run_eval.py --genre api-contract
```

Compare outputs against `eval/ground-truth.md`. See `eval/README.md` for scoring details.
