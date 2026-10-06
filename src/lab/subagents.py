"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {"name": "explorer", "description": "Use before changing an unfamiliar project or dataset to inspect its specifications and report relevant facts.",
         "system_prompt": "Read the task specifications, README, docstrings and representative input. Report requirements, edge cases and relevant paths. Do not modify files. Separate observations from assumptions."},
        {"name": "implementer", "description": "Use to implement a nontrivial code fix or data/log transformation after the requirements are known.",
         "system_prompt": "Implement the delegated requirements in the supplied workspace. Fix root causes rather than symptoms. Inspect inputs, handle edge cases, run focused tests and report actual changed files and validation results."},
        {"name": "reviewer", "description": "Use after implementation to independently verify outputs against specifications and edge cases.",
         "system_prompt": "Independently inspect the delegated output and run relevant checks. Compare behavior with README and docstrings, verify formatting and boundary cases. Do not modify files. Report evidence, failures and remaining uncertainty."},
    ]
