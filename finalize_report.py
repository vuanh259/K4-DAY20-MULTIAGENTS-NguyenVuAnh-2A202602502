"""Fill the final report from recorded statistics; preserve preregistered hypotheses."""
import json
from pathlib import Path


def main():
    report = Path("report/REPORT.md")
    text = report.read_text(encoding="utf-8")
    prefix = text.split("## 7. Kết quả so sánh", 1)[0]
    prefix = "\n".join(line for line in prefix.splitlines() if not line.startswith(">"))
    prefix = prefix.replace("29 passed in 13.54s", "29 passed in 14.32s")
    prefix = prefix.replace("Commit của tag `freeze`: chưa thực hiện (thuộc Phần 4).",
        "Commit giả thuyết: `0a476d1`; tag `freeze`: `f020b4e860ee7b5a0630e5448b14bf268c8abaf4`. Giả thuyết được commit trước freeze; không chạy hoặc đọc check đánh giá trước bước này.")
    prefix = prefix.replace("Trước freeze: hoàn thành 6 lượt baseline/subagents học và 3 lượt skills-auto-dev; smoke test kết nối và tools thành công qua gateway GenzShop.",
        "Hoàn thành 18 lượt đo chính (3 điều kiện × 6 tác vụ) và 3 lượt phát triển skills-auto-dev, tổng 21 lượt theo quy trình. Một pilot OpenAI/CRLF được chạy thêm và lưu riêng; curator chạy 2 lần. Tổng token của 18 lượt chính là 2075492; cả 21 lượt chính và dev là 2377154; cộng pilot CRLF là 2481923. Không tính token curator, smoke test hoặc lượt Gemini không đo hoàn chỉnh vào các tổng này.")
    prefix = prefix.replace("Nếu dùng OpenAI trực tiếp, cần cả", "Cấu hình GenzShop hiện tại dùng `OPENAI_API_BASE=https://modelapi.vn/v1` để đổi endpoint của SDK. Nếu dùng OpenAI trực tiếp, cần cả")
    stats = json.loads(Path("report/statistics.json").read_text(encoding="utf-8"))
    task_stats = json.loads(Path("report/task-statistics.json").read_text(encoding="utf-8"))
    table = Path("report/table.md").read_text(encoding="utf-8").strip()
    breakdown = Path("report/check-breakdown.txt").read_text(encoding="utf-8").strip()
    base, sub, skill = (stats[c] for c in ("baseline", "subagents", "skills-auto"))
    delta_learn = skill["learn"]["mean_score"] - base["learn"]["mean_score"]
    delta_eval = skill["eval"]["mean_score"] - base["eval"]["mean_score"]
    gap = skill["learn"]["mean_score"] - skill["eval"]["mean_score"]
    cost_table = ["| Điều kiện | Token TB toàn bộ | Token TB eval | Giây TB eval | Điểm / triệu token (tất cả) | Điểm / triệu token (eval) |",
                  "|---|---:|---:|---:|---:|---:|"]
    for condition in ("baseline", "subagents", "skills-auto"):
        s = stats[condition]
        cost_table.append(f"| {condition} | {s['all']['mean_tokens']:.1f} | {s['eval']['mean_tokens']:.1f} | {s['eval']['mean_seconds']:.1f} | {s['all']['score_per_million_tokens']:.2f} | {s['eval']['score_per_million_tokens']:.2f} |")
    noise_table = ["| Tác vụ | Điểm dev | Điểm sau freeze | Δ điểm | Token dev | Token sau freeze | Δ token |",
                   "|---|---:|---:|---:|---:|---:|---:|"]
    for dev in task_stats["skills-auto-dev"]:
        current = next(r for r in task_stats["skills-auto"] if r["task"] == dev["task"])
        noise_table.append(f"| {dev['task']} | {dev['passed']}/{dev['total']} | {current['passed']}/{current['total']} | {current['score']-dev['score']:.4f} | {dev['tokens']['total']} | {current['tokens']['total']} | {current['tokens']['total']-dev['tokens']['total']:+d} |")
    calls_table = ["| Tác vụ | Worker | Subagent calls | Skills đọc trong skills-auto |",
                   "|---|---|---:|---:|"]
    workers = {"code-learn": "explorer", "data-learn": "general-purpose", "logs-learn": "general-purpose",
               "code-eval": "explorer", "data-eval": "explorer", "logs-eval": "general-purpose"}
    for r in task_stats["subagents"]:
        sr = next(s for s in task_stats["skills-auto"] if s["task"] == r["task"])
        calls_table.append(f"| {r['task']} | {workers[r['task']]} | {r['subagent_calls']} | {sr['skills_read']} |")
    tail = f"""## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng dưới được sinh bằng module có sẵn `lab.compare`; bản độc lập ở [table.md](table.md). Điểm trung bình là trung bình điểm chuẩn hóa của từng tác vụ, không phải tỷ lệ cộng gộp mọi check.

{table}

Đầu ra nguyên văn của `scripts/check_breakdown.py`:

```text
{breakdown}
```

Kiểm chứng `scripts/verify_freeze.py`: **checked 6 runs of skill conditions: OK**. Cả 18 lượt chính có `error=null`, token > 0, `skills_modified=false`, và đủ run.json/trace.md. Không chạy lại một lượt chính nào để chọn điểm tốt; chỉ chạy lại pilot CRLF trước khi có bộ kết quả baseline chính. Phản hồi eval không được đưa trở lại curator. Xem [submission-audit.json](submission-audit.json), [statistics.json](statistics.json) và [task-statistics.json](task-statistics.json).

Thống kê gọi worker và đọc skill:

{chr(10).join(calls_table)}

`explorer` được gọi 3 lần và `general-purpose` 3 lần; implementer/reviewer riêng không được gọi ở các lượt này. Trong eval, code/data giao việc đọc/phân tích rồi tác tử chính thực hiện; log giao việc tạo output, sau đó tác tử chính đọc lại và chạy kiểm tra JSON/counts. Cách kiểm chứng log eval tốt hơn log learn, nhưng không cung cấp quy ước ẩn nên vẫn đạt 6/10. Hai tác vụ data đọc cả skill dữ liệu lẫn skill log; skill log không tạo thêm điểm cho dữ liệu bảng.

## 8. Phân tích

1. **Điểm học và đánh giá, kiểm tra giả thuyết.** Skills-auto tăng điểm học từ {base['learn']['mean_score']:.4f} lên {skill['learn']['mean_score']:.4f} (Δ={delta_learn:.4f}) và điểm đánh giá từ {base['eval']['mean_score']:.4f} lên {skill['eval']['mean_score']:.4f} (Δ={delta_eval:.4f}, tương đương {delta_eval*100:.2f} điểm phần trăm). Subagents học giảm xuống {sub['learn']['mean_score']:.4f}, còn eval bằng baseline {sub['eval']['mean_score']:.4f}. H1 được số liệu lượt đo này ủng hộ: không tăng điểm eval nhưng token cao hơn. H2 được ủng hộ: skills-auto cao nhất và Δ eval > 0,15. H3 được ủng hộ: khoảng cách học–eval của skills-auto là {gap:.4f} > 0,05. Không có điều kiện tăng điểm học mà không tăng điểm eval so với baseline; tuy nhiên khoảng cách học–eval vẫn cho thấy tổng quát hóa chưa đầy đủ.

2. **Check kỹ thuật và quy ước.** Baseline đạt 18/18 kỹ thuật ở cả học và eval, nhưng 0/9 và 0/12 quy ước. Skills-auto giữ 18/18 kỹ thuật và tăng quy ước lên 7/9 học, 7/12 eval. Do đó hiệu quả chính là chuyển quy ước đã học vào ngữ cảnh tác tử, không phải bằng chứng cải thiện năng lực tính toán/sửa bug. Ba quy ước mới của eval (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) đều không đạt ở skills-auto, phù hợp với việc chúng không có trong skill. Các quy ước còn lại chuyển được 7/9; meta và clean.csv của data vẫn thiếu hoặc sai.

3. **Cơ chế và lỗi còn lại.** Ở logs-eval, vết có đọc `skills/log-triage-output/SKILL.md`, tạo JSON với schema_version=2/generated_by=log-triage, chuẩn hóa service, sắp xếp errors và assert lại ordering/counts: ba check quy ước cũ tăng từ không đạt lên đạt. `rule_source_line` không đạt vì skill không hướng dẫn giữ số dòng nguồn. Ở code-eval, vết đọc code-fix-workflow rồi thêm regression/type hints/changelog; ba check này đạt nhưng version bump không đạt. Ở data-eval, skills_read=2 nhưng `meta.source` dùng đường dẫn kèm workspace thay vì tên tệp; meta sai dù câu trả lời nói đã có meta. Skill dữ liệu không giữ tên bắt buộc clean.csv; tác tử không tạo tệp này. Header chứa region và bốn hướng trong skill cũng quá hẹp khi dữ liệu mới dùng category. Đây là giới hạn ngữ nghĩa của skill và áp dụng một phần, không phải không đọc skill.

4. **Chi phí token.** Dùng chỉ số ∑ điểm chuẩn hóa / ∑ token × 10^6, không gọi đây là chi phí tiền vì chưa có thông tin giá và routing/billing của gateway.

{chr(10).join(cost_table)}

Trên eval, skills-auto dùng {skill['eval']['mean_tokens']/base['eval']['mean_tokens']:.2f} lần token baseline để tăng {delta_eval:.4f} điểm; subagents dùng {sub['eval']['mean_tokens']/base['eval']['mean_tokens']:.2f} lần mà không tăng điểm. Baseline tốt nhất về điểm trên mỗi token khi tính cả sáu tác vụ và riêng eval; skills-auto tốt nhất về điểm tuyệt đối. Riêng tập học, skills-auto đạt {skill['learn']['score_per_million_tokens']:.2f} điểm/triệu token so với baseline {base['learn']['score_per_million_tokens']:.2f}. Trong thí nghiệm này, subagents không đáng chi phí thêm nếu mục tiêu là đạt check; kết luận không áp dụng cho mọi loại dự án.

5. **Rò rỉ và quá khớp.** Curator chỉ đọc run role=learn của baseline; không đọc hoặc đưa eval vào prompt. Validator loại skill chứa marker eval; lần đầu một từ thông thường bị trùng marker và bị loại, không phải phát hiện đáp án eval trong skill. Giả thuyết được commit trước tag; eval chạy sau tag; hash xác nhận bộ skill không đổi. Skill không chứa đáp án số hoặc tên hàm của đề; tên file đầu ra/keys/region là quy ước được phép giữ. Dấu hiệu quá hẹp là header region không thích ứng với category ở data-eval; không gọi mọi khoảng cách học–eval là quá khớp vì eval thêm quy tắc mới. Sau freeze chỉ đọc check eval để giải thích kết quả trong báo cáo, không chỉnh skill, harness hay tái huấn luyện curator.

6. **Nhiễu của cùng bộ skill.** Các lượt dev được giữ nguyên trong results/skills-auto-dev và so với lượt chính sau freeze:

{chr(10).join(noise_table)}

Điểm của cả ba tác vụ không đổi, nhưng token trung bình tăng từ {stats['skills-auto-dev']['learn']['mean_tokens']:.1f} lên {skill['learn']['mean_tokens']:.1f} ({(skill['learn']['mean_tokens']/stats['skills-auto-dev']['learn']['mean_tokens']-1)*100:.2f}%), còn thời gian trung bình giảm từ 89,8 xuống 73,6 giây. Data sau freeze đọc thêm một skill so với dev. Không thấy nhiễu điểm ở hai lần quan sát này, nhưng không thể kết luận điểm luôn ổn định; nhiễu chi phí vẫn rõ. Đây không phải vòng học thứ hai vì skill byte-for-byte không đổi.

"""
    limitations = text.split("## 9. Hạn chế và tính hợp lệ", 1)[1].split("## 10. Kết luận", 1)[0].strip()
    tail += "## 9. Hạn chế và tính hợp lệ\n\n" + limitations
    tail += """

## 10. Kết luận

Skills-auto có điểm đánh giá cao nhất trong lượt đo này (0,8253), tăng 0,2279 so với baseline nhờ 7 check quy ước đã học. Nó không khôi phục được ba quy ước mới và vẫn thiếu hai quy ước dữ liệu. Subagents không tăng điểm đánh giá và dùng khoảng 2,26 lần token baseline. Baseline có hiệu quả điểm trên token tốt nhất trên tập đánh giá, còn skills-auto ưu tiên chất lượng tuyệt đối. Bước tiếp theo là lặp thí nghiệm ở thư mục riêng và kiểm tra ngữ nghĩa skill/đầu ra trước khi chốt bộ skill cho một thí nghiệm mới.

## Phụ lục

### Lệnh tái lập và thứ tự đã thực hiện

Trên Windows dùng Docker Desktop Linux containers; shell tác tử cần /bin/sh. Cài key vào .env (không commit), giữ endpoint/model theo .env.example. Có thể dot-source activate-lab.ps1 cho terminal Windows; thí nghiệm và verify_freeze chạy trong container để tránh khác biệt hash đường dẫn giữa Windows/Linux.

```powershell
docker build -f Dockerfile.lab -t lab-deepagents-day20 .
docker run --rm -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m pytest -o addopts= -q
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python check_gateway.py
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python check_model.py
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition baseline --tasks learn
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition subagents --tasks learn
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.curator
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition skills-auto --tasks learn
Move-Item -LiteralPath results/skills-auto -Destination results/skills-auto-dev
git add .env.example pyproject.toml src report results skills .gitattributes
git commit -m hypotheses
git commit --allow-empty -m "freeze skills"
git tag freeze
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition baseline --tasks eval
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition subagents --tasks eval
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python -m lab.runner --condition skills-auto --tasks all
docker run --rm --env-file .env -v "${PWD}:/lab" -w /lab lab-deepagents-day20 python collect_reports.py
python finalize_report.py
```

Các lệnh trên mô tả tái lập từ bản chưa freeze; không tạo lại tag hay ghi đè kết quả đã nộp. Nếu muốn đo thêm, dùng --results results-replication và giữ bộ kết quả chính. Thực tế có thêm một baseline code-learn pilot lỗi CRLF (archive rồi chạy lại), và hai lần curator (lần đầu archive 2 skill hợp lệ, lần hai tạo bộ cuối). Đợt curator thứ hai và việc lưu kết quả dev đều xảy ra trước commit hypotheses; từ freeze không thay đổi skills/auto. Tệp collect_reports.py chỉ gọi module so sánh và các script kiểm tra có sẵn, rồi tổng hợp metadata; không gọi mô hình hoặc chỉnh skill.

### Tài liệu làm căn cứ

- [README: thiết kế thí nghiệm](../README.md), mục 2.1–2.2.
- [GUIDE: trình tự học, curator, freeze, đánh giá](../GUIDE.md), Phần 2–5.
- [Pseudo-code subagents](../guides/pseudocode/02_subagents.md): vai trò và ngữ cảnh cô lập.
- [Chất lượng skill](../guides/pseudocode/05_skill_quality.md): progressive disclosure, tính tổng quát và áp dụng một phần.
- [Hướng dẫn GenzShop Codex](https://genzshop.vn/pages/docs.php?product=codex): endpoint modelapi.vn/v1 và Responses API; model gpt-6-luna được xác nhận trực tiếp qua danh sách model của gateway.

### Ghi chú tính toàn vẹn

- Không làm phần thưởng tùy chọn; hoàn thành các phần bắt buộc 0–5.
- Giữ nguyên các tệp được cung cấp và nguồn workspace của đề; chỉ cài đặt bốn module sinh viên cùng cấu hình/hỗ trợ chạy.
- .env được gitignore, không nằm trong index; rà soát khóa thật trong source/report/results/skills đạt PASS.
- Các lỗi Gemini trước khi chọn gateway nằm riêng ở results/infrastructure-pilot và results/gemini-infrastructure-attempts; không được đưa vào curator, bảng so sánh hay phân tích hiệu quả cuối.
- Chưa chuyển sang nhà cung cấp khác sau freeze. Kết quả ghi model ID/usage mà gateway trả về, không xác nhận routing nội bộ hoặc giá thanh toán.
"""
    report.write_text(prefix.rstrip() + "\n\n" + tail, encoding="utf-8")
    print("Completed report/REPORT.md from verified results.")


if __name__ == "__main__":
    main()
