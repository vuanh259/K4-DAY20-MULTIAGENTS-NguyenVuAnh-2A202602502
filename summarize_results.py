"""Summarize recorded runs only; does not invoke models or change skills."""
import json
from pathlib import Path
from statistics import mean


def main():
    summary = {}
    tasks = {}
    for condition in ("baseline", "subagents", "skills-auto", "skills-auto-dev"):
        runs = [json.loads(p.read_text(encoding="utf-8"))
                for p in sorted((Path("results") / condition).glob("*/run.json"))]
        tasks[condition] = [{k: r[k] for k in ("task", "passed", "total", "score", "tokens",
                            "seconds", "subagent_calls", "skills_read", "error")} for r in runs]
        summary[condition] = {}
        for role in ("learn", "eval", "all"):
            selected = [r for r in runs if role == "all" or r["role"] == role]
            if not selected:
                continue
            checks = [c for r in selected for c in r["checks"]]
            technical = [c for c in checks if not c["name"].startswith("rule_")]
            rules = [c for c in checks if c["name"].startswith("rule_")]
            summary[condition][role] = {
                "runs": len(selected), "mean_score": mean(r["score"] for r in selected),
                "mean_tokens": mean(r["tokens"]["total"] for r in selected),
                "mean_seconds": mean(r["seconds"] for r in selected),
                "technical": [sum(c["passed"] for c in technical), len(technical)],
                "rules": [sum(c["passed"] for c in rules), len(rules)],
                "runs_reading_skills": sum(r["skills_read"] > 0 for r in selected),
                "subagent_calls": sum(r["subagent_calls"] for r in selected),
                "score_per_million_tokens": (sum(r["score"] for r in selected)
                    / sum(r["tokens"]["total"] for r in selected) * 1_000_000),
                "errors": [r["task"] for r in selected if r["error"]],
            }
    Path("report/statistics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    Path("report/task-statistics.json").write_text(
        json.dumps(tasks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
