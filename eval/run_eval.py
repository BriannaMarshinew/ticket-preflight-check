"""
Eval runner for ticket-preflight-check skill.
Runs the preflight prompt against 12 labeled GitHub issues and saves outputs.

Usage:
  pip install anthropic
  export ANTHROPIC_API_KEY=sk-ant-...
  python run_eval.py                    # all 12 issues
  python run_eval.py --genre bug-report # only bug reports
  python run_eval.py --runs 1           # single run (faster, no variance check)
  python run_eval.py --model claude-sonnet-4-6  # different model
"""

import os, json, time, argparse
import anthropic

parser = argparse.ArgumentParser(description="Run preflight eval against labeled issues")
parser.add_argument("--model", default="claude-sonnet-4-6", help="Model to use")
parser.add_argument("--runs", type=int, default=3, help="Runs per issue (for variance)")
parser.add_argument("--genre", help="Filter to a specific genre (bug-report, vague-feature, etc.)")
parser.add_argument("--issue", help="Run a single issue by ID")
parser.add_argument("--output-dir", default="results", help="Output directory")
args = parser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))

env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a preflight evaluation agent. Your job is to read a software ticket and identify gaps — things the ticket assumes, leaves undefined, or gets wrong — that would cause a developer to get blocked mid-implementation.

You are not a generic checklist. Every gap you identify must be specific to this ticket's content. Do not surface gaps that don't apply.

## Gap Categories

- **Requirements gap** — Acceptance criteria are ambiguous, incomplete, or contradictory. It's unclear what "done" means.
- **Contract gap** — The ticket assumes a data shape, API response, interface, or error behavior that may not match reality or isn't specified.
- **Configuration gap** — The work depends on a feature flag, environment variable, permission, version, or system setting that isn't confirmed.
- **Scope gap** — The ticket implies a contained change but the actual blast radius may be larger, or it's unclear which system owns the problem.
- **Dependency gap** — The work depends on another ticket, PR, migration, or external system state that isn't confirmed ready. Includes upstream fixes not yet merged, services not yet deployed, or data not yet available.
- **Edge case gap** — Identifiable inputs or states the ticket doesn't address: nulls, empty states, error paths, permission boundaries, concurrent states.
- **Wrong mental model** — The ticket's premise appears to misunderstand how the system works. The "bug" may be expected behavior.

## Structural completeness rule

If any of the following high-value fields are missing or empty, flag each as a formal gap — not a Note. These are the fields developers rank as most important for starting work:

1. **Reproduction steps** — must be specific, not "see above" or blank
2. **Error messages / stack traces** — if the ticket describes a failure, the actual error output must be present
3. **Environment / version info** — OS, runtime version, dependency versions relevant to the bug

Only flag these when genuinely absent or empty. Do not flag them on feature requests or tickets where they don't apply.

## Output Format

Return a preflight report in this exact structure:

```
## Preflight Report

**Risk level:** Low | Medium | High

### Confirmed
[What the ticket does provide clearly — be brief]

### Gaps
For each gap:
- **[Category]:** [Specific description of the gap]
  - Why it matters: [what breaks or gets wasted if this isn't resolved]
  - Suggested action: [what to do to resolve it]

### Accepted Unknowns
[Leave empty — developer fills this in after review]

### Notes
[Any observations that don't fit the above — optional]
```

If the ticket has no meaningful gaps, say so explicitly. Do not manufacture gaps to appear thorough."""

USER_TEMPLATE = """Evaluate the following ticket for implementation readiness. Identify any gaps that would block or misdirect a developer during implementation.

---
{ticket_content}
---"""


def run_issue(issue, max_retries=3):
    ticket = f"Title: {issue['title']}\n\n{issue['body']}"
    user_msg = USER_TEMPLATE.format(ticket_content=ticket)
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=args.model,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_msg}],
            )
            return response.content[0].text
        except anthropic.OverloadedError:
            if attempt < max_retries - 1:
                wait = 30 * (attempt + 1)
                print(f"overloaded, retrying in {wait}s...", end=" ", flush=True)
                time.sleep(wait)
            else:
                raise


def main():
    issues_path = os.path.join(script_dir, "issues.json")
    with open(issues_path) as f:
        issues = json.load(f)

    if args.genre:
        issues = [i for i in issues if i["genre"] == args.genre]
    if args.issue:
        issues = [i for i in issues if i["id"] == args.issue]

    if not issues:
        print("No issues matched filters.")
        return

    out_dir = os.path.join(script_dir, args.output_dir, args.model)
    os.makedirs(out_dir, exist_ok=True)

    print(f"Model: {args.model}")
    print(f"Issues: {len(issues)}")
    print(f"Runs per issue: {args.runs}")
    print(f"Output: {out_dir}")
    print()

    for issue in issues:
        print(f"{'=' * 60}")
        print(f"{issue['id']} ({issue['genre']}, {issue['label']})")
        print(f"  {issue['title'][:70]}")
        runs = []
        for r in range(1, args.runs + 1):
            print(f"  Run {r}/{args.runs}...", end=" ", flush=True)
            text = run_issue(issue)
            runs.append(text)
            print("done")
            if r < args.runs:
                time.sleep(1)

        out_path = os.path.join(out_dir, f"{issue['id']}.json")
        with open(out_path, "w") as f:
            json.dump(
                {
                    "id": issue["id"],
                    "label": issue["label"],
                    "genre": issue["genre"],
                    "title": issue["title"],
                    "source": issue.get("source", ""),
                    "model": args.model,
                    "runs_count": args.runs,
                    "runs": runs,
                },
                f,
                indent=2,
            )
        print(f"  -> {out_path}")
        print()
        print("--- Run 1 output ---")
        print(runs[0])
        print()

    print(f"\nDone. {len(issues)} issues x {args.runs} runs saved to {out_dir}/")


if __name__ == "__main__":
    main()
