"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
from pathlib import Path
import os
import sys

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    env = {
        "PATH": os.pathsep.join([str(Path(sys.executable).parent), "/usr/local/bin", "/usr/bin", "/bin"]),
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
    }
    return LocalShellBackend(root_dir=sandbox, virtual_mode=True,
                             inherit_env=False, env=env, timeout=120)


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"Unknown agent mode: {mode}")
    kwargs = {}
    prompt = BASE_PROMPT
    if mode == "subagents":
        kwargs["subagents"] = [{**s, "system_prompt": s["system_prompt"] + " " + PATHS_NOTE}
                               for s in get_subagents()]
        prompt += SUBAGENTS_NOTE
    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt += SKILLS_NOTE
    if model is None:
        model = make_model()
        if os.getenv("LAB_MODEL", "").startswith("google_genai:"):
            from langchain.chat_models import init_chat_model
            model = init_chat_model(
                os.environ["LAB_MODEL"], temperature=model.temperature,
                thinking_level=os.getenv("LAB_THINKING_LEVEL", "low"),
                timeout=float(os.getenv("LAB_MODEL_TIMEOUT", "90")),
                max_retries=int(os.getenv("LAB_MODEL_MAX_RETRIES", "1")),
            )
        elif os.getenv("LAB_MODEL", "").startswith("openai:"):
            model.use_responses_api = os.getenv("LAB_USE_RESPONSES_API", "true").lower() == "true"
            model.reasoning = {"effort": os.getenv("LAB_REASONING_EFFORT", "low")}
            if model.reasoning["effort"] != "none":
                model.temperature = None
            model.request_timeout = float(os.getenv("LAB_MODEL_TIMEOUT", "90"))
            model.max_retries = int(os.getenv("LAB_MODEL_MAX_RETRIES", "1"))
            model.root_client = model.root_client.with_options(timeout=model.request_timeout, max_retries=model.max_retries)
            model.root_async_client = model.root_async_client.with_options(timeout=model.request_timeout, max_retries=model.max_retries)
            model.client = model.root_client.chat.completions
            model.async_client = model.root_async_client.chat.completions
    return create_deep_agent(model=model,
                             system_prompt=prompt, backend=make_backend(sandbox), **kwargs)
