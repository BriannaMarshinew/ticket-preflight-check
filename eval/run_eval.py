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

import os, json, time, argparse, re
import anthropic

parser = argparse.ArgumentParser(description="Run preflight eval against labeled issues")
parser.add_argument("--model", default="claude-sonnet-4-6", help="Model to use")
parser.add_argument("--runs", type=int, default=3, help="Runs per issue (for variance)")
parser.add_argument("--genre", help="Filter to a specific genre (bug-report, vague-feature, etc.)")
parser.add_argument("--issue", help="Run a single issue by ID")
parser.add_argument("--output-dir", default="results", help="Output directory")
args = parser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)

env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

client = anthropic.Anthropic()


def load_skill_prompt():
    skill_path = os.path.join(repo_root, "SKILL.md")
    with open(skill_path) as f:
        content = f.read()
    # Strip YAML frontmatter
    if content.startswith("---"):
        end = content.index("---", 3)
        content = content[end + 3:].strip()
    return content


SYSTEM_PROMPT = load_skill_prompt()

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
    print(f"Prompt: {os.path.join(repo_root, 'SKILL.md')}")
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
