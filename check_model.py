"""Small live model and tool smoke test; uses a temporary workspace, never prints keys."""
import json
import tempfile
from pathlib import Path
from langchain_core.callbacks import UsageMetadataCallbackHandler
from langchain_core.messages import AIMessage
from lab.agent import build_agent


def main():
    usage = UsageMetadataCallbackHandler()
    with tempfile.TemporaryDirectory(prefix="lab-smoke-") as tmp:
        root = Path(tmp)
        (root / "workspace").mkdir()
        graph = build_agent(root)
        output = graph.invoke(
            {"messages": [{"role": "user", "content":
                "Use the file tools to create workspace/smoke.txt containing exactly OK, "
                "then read the file and reply with OK. Do not use the shell."}]},
            config={"callbacks": [usage], "recursion_limit": 20},
        )
        assert (root / "workspace" / "smoke.txt").read_text(encoding="utf-8").strip() == "OK"
        calls = [c["name"] for m in output["messages"] if isinstance(m, AIMessage) for c in m.tool_calls]
        assert "write_file" in calls and "read_file" in calls, calls
        record = {"status": "OK", "tools": calls, "usage": usage.usage_metadata}
        Path("report").mkdir(exist_ok=True)
        Path("report/smoke-test.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print("OpenAI connection + file tool calling: OK", flush=True)
        print("Tools:", ", ".join(calls), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Model smoke test failed: {type(exc).__name__}; status={getattr(exc, 'status_code', None)}", flush=True)
        body = getattr(exc, "body", {})
        if isinstance(body, dict):
            print("API error code:", body.get("code") or body.get("error", {}).get("code"), flush=True)
        raise SystemExit(1)
