"""Generate supplied comparison/verification artifacts inside the Linux lab container."""
import json
import ast
import os
import subprocess
import sys
from pathlib import Path

from lab.curator import validate_skill
from summarize_results import main as summarize


def main():
    commands = {
        "table.md": [sys.executable, "-m", "lab.compare"],
        "check-breakdown.txt": [sys.executable, "scripts/check_breakdown.py"],
        "freeze-verification.txt": [sys.executable, "scripts/verify_freeze.py"],
    }
    for name, command in commands.items():
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        Path("report", name).write_text(result.stdout, encoding="utf-8")
        print(name + ":\n" + result.stdout)
    records = []
    for condition in ("baseline", "subagents", "skills-auto"):
        paths = sorted((Path("results") / condition).glob("*/run.json"))
        assert len(paths) == 6, (condition, len(paths))
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            assert not record["error"], (condition, record["task"], "runtime error")
            assert record["tokens"]["total"] > 0
            assert not record["skills_modified"]
            assert path.with_name("trace.md").is_file()
            records.append(record)
    for path in Path("skills/auto").glob("*/SKILL.md"):
        assert not validate_skill(path.read_text(encoding="utf-8"), path.parent.name)
    protected = ["tasks", "tests", "scripts", "src/lab/model.py", "src/lab/tasks.py",
                 "src/lab/grading.py", "src/lab/testing.py", "src/lab/compare.py"]
    files = subprocess.run(["git", "ls-tree", "-r", "--name-only", "freeze~2", "--", *protected],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    for filename in files:
        original = subprocess.run(["git", "show", "freeze~2:" + filename],
                                  check=True, capture_output=True).stdout
        # Git's Windows checkout changes LF to CRLF; compare canonical original bytes.
        assert original.replace(b"\r\n", b"\n") == Path(filename).read_bytes().replace(b"\r\n", b"\n"), filename
    immutable = {
        "src/lab/agent.py": ["PATHS_NOTE", "BASE_PROMPT", "SKILLS_NOTE", "SUBAGENTS_NOTE"],
        "src/lab/runner.py": ["render_trace", "main", "CONDITIONS"],
        "src/lab/curator.py": ["validate_skill", "parse_skill_blocks", "SAFE_NAME"],
    }
    for filename, names in immutable.items():
        original = subprocess.run(["git", "show", "freeze~2:" + filename],
                                  check=True, capture_output=True, text=True).stdout
        def nodes(source):
            found = {}
            for node in ast.parse(source).body:
                if isinstance(node, ast.FunctionDef):
                    found[node.name] = ast.dump(node)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            found[target.id] = ast.dump(node)
            return found
        old, new = nodes(original), nodes(Path(filename).read_text(encoding="utf-8"))
        assert all(old[name] == new[name] for name in names), filename
    keys = [v for k, v in os.environ.items() if len(v) >= 8
            and any(part in k.upper() for part in ("KEY", "TOKEN", "SECRET"))]
    for directory in ("src", "report", "results", "skills"):
        for path in Path(directory).rglob("*"):
            if path.is_file() and path.suffix in (".py", ".md", ".json", ".txt"):
                assert not any(key in path.read_text(encoding="utf-8", errors="ignore") for key in keys), str(path)
    audit = {"primary_runs": len(records), "runtime_errors": 0, "skills_modified": 0,
             "primary_tokens_total": sum(r["tokens"]["total"] for r in records),
             "provided_sources_unchanged": True,
             "secret_scan": "PASS", "freeze_verification": "OK"}
    Path("report/submission-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    summarize()
    print("Submission audit: OK")


if __name__ == "__main__":
    main()
