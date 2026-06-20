# Evaluation Benchmark

12 real GitHub issues across 6 repos and 5 genres, with annotated ground-truth gaps. Use this to test the preflight skill against your own model or prompt changes.

## Quick start

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Run all 12 issues (default: claude-sonnet-4-6, 3 runs each)
python run_eval.py

# Faster: single run per issue
python run_eval.py --runs 1

# Different model
python run_eval.py --model claude-opus-4-8

# Filter by genre
python run_eval.py --genre api-contract

# Single issue
python run_eval.py --issue supabase-28041
```

Results are saved to `results/<model>/<issue-id>.json`.

## Dataset

### Genres

| Genre | Count | Tests |
|-------|-------|-------|
| bug-report | 5 | Structural gaps, wrong mental model, scope/ownership |
| vague-feature | 2 | Requirements, contract, scope definition |
| blocked-dependency | 1 | Dependency chains, multi-package ownership |
| api-contract | 3 | Contract assumptions, wrong mental model |
| epic-spike | 1 | Recognizing non-implementable tickets |

### Issues

| ID | Repo | Genre | Label |
|----|------|-------|-------|
| nextjs-65599 | vercel/next.js | bug-report | implementer-ambiguous |
| nextjs-74559 | vercel/next.js | bug-report | implementer-ambiguous |
| nextjs-74769 | vercel/next.js | bug-report | bad |
| nextjs-74518 | vercel/next.js | bug-report | bad |
| nextjs-74558 | vercel/next.js | bug-report | borderline |
| vscode-226561 | microsoft/vscode | vague-feature | bad |
| react-27758 | facebook/react | vague-feature | borderline |
| prisma-20567 | prisma/prisma | blocked-dependency | implementer-ambiguous |
| trpc-5581 | trpc/trpc | api-contract | good-feature-request |
| supabase-28041 | supabase/supabase | api-contract | bad |
| rust-129080 | rust-lang/rust | epic-spike | tracking-issue |
| trpc-6892 | trpc/trpc | api-contract | good-feature-request |

## Ground truth

`ground-truth.md` contains annotated gaps for each issue from an **implementer perspective** — what a developer assigned to this ticket would need to resolve before writing code.

## Scoring

See the scoring rubric in the project root (`scoring-rubric.md`). Key rules:

- **Semantic match** — a predicted gap matches a ground-truth gap when it refers to the same underlying missing/wrong thing (wording doesn't need to match)
- **Category match scored separately** — a gap can be a TP even if the category label differs
- **Good/implementer-ambiguous issues** — scored on whether surfaced gaps are genuinely blocking, not on gap count
- **Tracking issues** — skill should recognize these as non-implementable and assign Low risk

## Baseline results (v1.1 prompt, claude-opus-4-8)

| Metric | Phase 1 (5 bugs) | Phase 2 (7 diverse) | Combined |
|--------|-----------------|---------------------|----------|
| Precision | 0.69 | 0.59 | 0.63 |
| Recall | 0.87 | 1.00 | 0.95 |
| F1 | 0.76 | 0.73 | 0.74 |

## Files

| File | Purpose |
|------|---------|
| `run_eval.py` | Eval runner script |
| `issues.json` | 12 labeled issues with verbatim bodies |
| `ground-truth.md` | Annotated expected gaps per issue |
| `results/` | Output directory (gitignored) |
