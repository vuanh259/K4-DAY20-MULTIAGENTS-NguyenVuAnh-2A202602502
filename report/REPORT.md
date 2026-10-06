# Báo cáo Lab: Self evolving Agentic


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Vũ Anh | 2A202602502 | Cài đặt harness, subagents, runner và curator; chuẩn bị thí nghiệm và báo cáo |

- Cấu hình hiện tại: `LAB_MODEL=openai:gpt-6-luna`, Responses API, reasoning effort `low`, timeout 90 giây và một retry. Key GenzShop đã được kiểm tra thành công qua `OPENAI_API_BASE=https://modelapi.vn/v1`; gateway liệt kê `gpt-6-luna`, smoke test gọi `write_file` và `read_file` thành công. Harness bỏ temperature khi bật reasoning. `recursion_limit` mặc định là 60. Các lượt Gemini trước khi đổi nhà cung cấp không dùng làm kết quả OpenAI.
- Môi trường: Windows PowerShell với `.venv` Python 3.12.10; chạy test và thí nghiệm trong Docker Linux, Python 3.11.16, Deep Agents 0.7.21. Các phiên bản khác ghi trong `report/environment.json`. Toàn bộ test ngoại tuyến: **29 passed in 14.32s**.
- Hoàn thành 18 lượt đo chính (3 điều kiện × 6 tác vụ) và 3 lượt phát triển skills-auto-dev, tổng 21 lượt theo quy trình. Một pilot OpenAI/CRLF được chạy thêm và lưu riêng; curator chạy 2 lần. Tổng token của 18 lượt chính là 2075492; cả 21 lượt chính và dev là 2377154; cộng pilot CRLF là 2481923. Không tính token curator, smoke test hoặc lượt Gemini không đo hoàn chỉnh vào các tổng này. Các lượt lỗi Gemini và pilot CRLF được lưu riêng, không dùng làm dữ liệu thí nghiệm chính.
- Commit giả thuyết: `0a476d1`; tag `freeze`: `f020b4e860ee7b5a0630e5448b14bf268c8abaf4`. Giả thuyết được commit trước freeze; không chạy hoặc đọc check đánh giá trước bước này.

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)


- H1 (subagents so với baseline): Trên tập đánh giá, điểm trung bình subagents không cao hơn baseline, nhưng dùng nhiều token hơn. Baseline đã đạt 18/18 check kỹ thuật của tập học; phân chia worker không tự cung cấp các quy ước chưa biết. Lượt học subagents còn thiếu kiểm chứng ở log và đếm sai ở data. Cơ chế ngữ cảnh cô lập của `task` yêu cầu gửi lại đề và kiểm tra báo cáo (`GUIDE.md` mục 2.3, `guides/pseudocode/02_subagents.md`).
- H2 (skills-auto so với baseline): Skills-auto có điểm đánh giá trung bình cao nhất, cải thiện ít nhất 0,15 so với baseline, chủ yếu ở check quy ước đã thấy trong phản hồi học. Curator biến phản hồi quy tắc thành quy trình có thể đọc lại; cơ chế progressive disclosure giúp chọn skill theo description (`guides/pseudocode/05_skill_quality.md` mục 1 và 5). Baseline học đạt 0/9 check quy ước nên còn nhiều dư địa cải thiện.
- H3 (tác vụ học so với tác vụ đánh giá): Skills-auto đạt điểm trung bình trên tập học cao hơn tập đánh giá ít nhất 0,05. Theo `README.md` mục 2.2, tác vụ đánh giá thêm quy ước mới; skill chỉ học từ phản hồi tập học nên không có căn cứ để khôi phục chính xác quy tắc mới. Cải thiện trên học không chứng minh tổng quát hóa hoàn toàn.

## 3. Làm quen Deep Agents (Phần 0.3)

### Ba câu hỏi theo yêu cầu Phần 0

1. **Bài lab có bao nhiêu agent? Mỗi agent làm gì?**

   Bản cài đặt có tác tử chính (điều phối, xử lý đề, kiểm tra kết quả), subagent `general-purpose` mặc định và ba subagent tự định nghĩa: `explorer` đọc tài liệu và dữ liệu, `implementer` sửa tệp và chạy kiểm tra, `reviewer` kiểm tra độc lập. Điều kiện `subagents` có 5 vai trò khả dụng, không có nghĩa tất cả đều được gọi. `curator` là bước gọi mô hình riêng để tạo skill từ phản hồi thất bại của tác vụ học; không phải worker thường trực của coordinator. Sáu tác vụ `code/data/logs × learn/eval` là bài toán thí nghiệm, không phải sáu agent.

   Bằng chứng: `src/lab/agent.py`, `src/lab/subagents.py`, `src/lab/curator.py`, `guides/pseudocode/02_subagents.md`.

2. **Coordinator giao tiếp với worker agents bằng cách nào?**

   Tác tử chính giao việc bằng tool `task` của Deep Agents, chọn loại subagent và gửi mô tả việc cần làm. Trong cơ chế ngữ cảnh cô lập mô tả trong lab, mỗi lần gọi tạo một subagent mới; subagent chỉ nhận nội dung giao việc, không tự thấy toàn bộ lịch sử hội thoại của tác tử chính. Vì vậy lời giao việc phải chứa đầy đủ quy tắc, đường dẫn và kết quả cần trả về. Subagent trả báo cáo cuối; tác tử chính kiểm tra trước khi sử dụng. Các tệp trong sandbox là nơi trao đổi sản phẩm công việc. Repo không cài một message queue riêng. `render_trace()` chỉ ghi luồng chính, lời gọi `task` và kết quả trả về, không ghi chi tiết mọi bước bên trong subagent.

   Bằng chứng: `SUBAGENTS_NOTE` trong `src/lab/agent.py`, `guides/pseudocode/02_subagents.md`, `src/lab/runner.py`.

3. **Có những công cụ nào được chia sẻ giữa các agent?**

   Các khả năng thao tác trên backend/sandbox gồm duyệt và xử lý tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`) và chạy shell (`execute`). `task` là công cụ tác tử chính dùng để giao việc. Bộ công cụ thực tế còn phụ thuộc cấu hình từng subagent; trường `tools` có thể tùy biến. Skill là tài liệu hướng dẫn, không phải một kho tri thức truy hồi đã được cài sẵn. Theo pseudo-code, subagent `general-purpose` kế thừa skill của tác tử chính, còn subagent tự định nghĩa cần khai báo `skills` riêng. Runner phụ trách ghi trace, token và chấm điểm; đây là hạ tầng đo thí nghiệm, không phải tool logging mà mọi worker gọi trực tiếp.

   Bằng chứng: `scripts/tour.py`, `guides/pseudocode/02_subagents.md`, `src/lab/runner.py`.

### Ba câu hỏi bổ sung theo GUIDE.md thực tế

1. **Tool mặc định và tool chạy lệnh:** kết quả `python scripts/tour.py` với Deep Agents 0.7.21 in đúng 9 tool: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, `task`. `execute` chạy lệnh shell và trả stdout/stderr kèm mã thoát.

2. **Subagent general-purpose và ngữ cảnh:** dùng cho nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và việc nhiều bước; có các công cụ như tác tử chính. Mỗi lần gọi mặc định không giữ trạng thái, chỉ thấy prompt được gửi và trả một báo cáo cuối. Vì vậy tác tử chính phải truyền đầy đủ thông tin, đồng thời tóm tắt kết quả cho người dùng.

3. **Trích hướng dẫn hành vi từ mô tả tool:**

   - `task`: “Put full detail in the prompt and state exactly what it should return — unless an agent type below says it inherits your conversation instead.”
   - `execute`: “Quote paths containing spaces (e.g. cd \"/path/with spaces\").”
   - Tour xác nhận system prompt mặc định là chuỗi rỗng `''`. Khi xây dựng agent của lab, `BASE_PROMPT` và các ghi chú bổ sung trong `agent.py` cung cấp chỉ dẫn riêng, đặc biệt quy ước đường dẫn tương đối `workspace/...`.

### Checklist và kết quả Phần 0 (06/10/2026)

- [x] GitHub API xác nhận repo `vuanh259/K4-DAY20-MULTIAGENTS-NguyenVuAnh-2A202602502` có `fork=true`, parent là `VinUni-AI20k/K4-L3L4-Track3-Day20-AdvanceMultiAgents`.
- [x] Repo đã clone, `origin` đúng tên bài nộp; đang mở trong IDE.
- [x] `.venv` hoạt động, Python 3.12.10 đáp ứng yêu cầu >=3.11.
- [x] Cài editable thành công bằng `python -m pip install -e .` (repo dùng `pyproject.toml`, không có `requirements.txt`). Deep Agents 0.7.21.
- [x] `python -m pip check`: `No broken requirements found.`
- [x] `.env` có sẵn theo mẫu; `git check-ignore .env` xác nhận được bỏ qua; `git ls-files .env` không trả tệp nào.
- [x] Điền API key và cấu hình mô hình: `.env` có `OPENAI_API_KEY` và cấu hình GPT-6 Luna.
- [x] Kết nối và tool smoke test: gateway GenzShop/modelapi.vn, model `gpt-6-luna`, thực thi `write_file` và `read_file` thành công; bằng chứng trong `report/smoke-test.json`.
- [x] `python -m pytest tests/test_01_provided.py -o addopts= -q`: **12 passed in 2.61s**. `-o addopts=` bỏ tùy chọn `-q` có sẵn để hiện dòng tổng kết. Lần đầu trong sandbox bị chặn thư mục tạm Windows; chạy lại ngoài sandbox thành công.
- [x] `python scripts/tour.py`: thành công, dùng mô hình giả, không tốn token API.
- [x] Tạo báo cáo từ `REPORT_TEMPLATE.md`; đọc `README.md`, `GUIDE.md` (repo không có `LAB_GUIDE.md`) và trả lời câu hỏi mục 3.
- [x] Kiểm tra cấu hình: `pyproject.toml`, `.env.example`, `model.py`, các prompt trong `agent.py`, định dạng subagent, ba condition trong `runner.py`.
- [x] Thêm `activate-lab.ps1` ở thư mục gốc để kích hoạt venv và UTF-8; cấu hình VS Code dùng `.venv` và đặt UTF-8 cho terminal Windows mới.

Để kích hoạt trong terminal PowerShell của người dùng:

```powershell
. .\activate-lab.ps1
```

Lưu ý cấu hình mô hình theo `src/lab/model.py`: nếu dùng Azure/cổng tương thích, điền đủ `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT_MODEL`. Cấu hình GenzShop hiện tại dùng `OPENAI_API_BASE=https://modelapi.vn/v1` để đổi endpoint của SDK. Nếu dùng OpenAI trực tiếp, cần cả `OPENAI_API_KEY` và `LAB_MODEL=openai:<tên-model-được-cấp-quyền>`; chỉ điền key sẽ không thay đổi mặc định `deepseek:deepseek-chat`. Không ghi khóa thật vào báo cáo hoặc mã nguồn.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm | Phản hồi |
|---|---|---|---|
| code-learn | rule_type_hints | E | RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value. |
| code-learn | rule_regression_tests | E | RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass. |
| code-learn | rule_changelog | E | RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets). |
| data-learn | rule_money_in_cents | E | RULE: money values in answer.json are integer cents (1606.67 USD is written 160667). |
| data-learn | rule_meta_block | E | RULE: answer.json has an object `meta` = {"source": <input file name>, "rows_in": <number of data rows in the input file, duplicates included>, "rows_used": <number of distinct orders with a known amount>}. |
| data-learn | rule_clean_csv | E | RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC); region in canonical spelling (North, South, East, West); amount in integer cents. |
| logs-learn | rule_service_names | E | RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service). |
| logs-learn | rule_sorted_errors | E | RULE: `errors` is sorted by service, then by timestamp_utc, ascending. |
| logs-learn | rule_schema_header | E | RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage". |

Cả 9 check baseline thất bại trên tập học thuộc nhóm E (vi phạm quy ước tổ chức). Check kỹ thuật đạt 18/18: code 7/7, data 5/5, logs 6/6. Đây là bằng chứng phủ định cho giả thuyết lỗi kỹ thuật A–D phổ biến ở baseline, không chứng minh các nhóm đó không thể xảy ra ở lượt khác. Skill có thể giúp nhớ kiểu đơn vị tiền, siêu dữ liệu và định dạng đầu ra, nhưng không suy ra quy ước hoàn toàn mới.

Pilot CRLF đạt 6/10 ở code do hash test gốc khác xuống dòng; đã lưu riêng ở results/crlf-pilot và loại khỏi bảng, curator. Sau chuẩn hóa Python trong sandbox, code baseline đạt 7/10 và tests_not_modified đạt; không sửa tasks gốc.

## 5. Điều kiện `subagents` (Phần 2.3)

Ba worker riêng: `explorer` chỉ đọc đặc tả và báo nguyên nhân; `implementer` thực hiện thay đổi và kiểm tra; `reviewer` kiểm tra độc lập, không sửa. Description chỉ rõ khi gọi và system prompt giới hạn phạm vi. Worker `general-purpose` của thư viện vẫn khả dụng.

| Tác vụ học | Worker được gọi | Số lần | Baseline token | Subagents token | Baseline giây | Subagents giây |
|---|---|---:|---:|---:|---:|---:|
| code-learn | explorer | 1 | 132533 | 120680 | 72,7 | 102,6 |
| data-learn | general-purpose | 1 | 49289 | 123304 | 54,5 | 73,1 |
| logs-learn | general-purpose | 1 | 60942 | 134454 | 49,9 | 122,7 |

Code: lời giao việc yêu cầu đọc docstring/test, không sửa test, dùng đường dẫn workspace; tác tử chính sau đó sửa và chạy pytest cùng kiểm tra biên (vết có `6 passed`). Data: lời giao việc nêu chuẩn hóa vùng, múi giờ, sentinel và trùng lặp, nhưng nhấn mạnh tính toán số tiền đã biết; đầu ra đếm 13 đơn và check `north_q1_orders` thất bại. Logs: lời giao việc bảo worker đọc README và tạo errors.json nhưng không nhắc lại đầy đủ schema; báo cáo worker nói 24 bản ghi với `occurrences`/`triage`, còn tác tử chính không gọi tool kiểm tra sau đó. Check chấm thiếu `errors` và `counts_by_service`: đây là lỗi đặc tả/kiểm chứng, không phải lỗi hạ tầng.

Điểm học subagents lần lượt 7/10, 4/8, 0/9, so với baseline 7/10, 5/8, 6/9. Token callback tính cả worker; tool_calls và vết chỉ đo luồng chính. Không suy đoán các bước nội bộ worker từ vết này.

## 6. Self-evolving: skill do curator sinh (Phần 3)

Curator chạy 2 lần (một lần đầu và một lần chạy lại, trong giới hạn tối đa hai lần chạy lại). Lần đầu tạo 2 skill hợp lệ nhưng skill dữ liệu bị validator từ chối vì marker `orders`; lưu nguyên hai skill ở `report/curator-attempt-1`, không sửa tay. Lần hai dùng thuật ngữ records trong văn xuôi và tạo 3 skill hợp lệ. Không xóa hoặc sửa nội dung bộ skill cuối.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| code-fix-workflow | Quy trình sửa package, không nhúng tên hàm hoặc đáp án của đề | Khớp các quy tắc type hints, regression và changelog; giới hạn tối thiểu 3 là quy ước học nên cần xét phạm vi áp dụng | 8 dòng toàn tệp, 4 dòng thân; description kích hoạt sửa bug có yêu cầu typed API/test/changelog |
| records-data-workflow | Quy trình JSON và cleaned CSV; header/vùng là quy ước tổ chức được phép giữ nhưng giới hạn khả năng chuyển sang schema khác | Đúng cents, định nghĩa meta và UTC; thiếu tên bắt buộc clean.csv, header region không thích ứng với category ở eval | 11 dòng toàn tệp, 7 dòng thân; description bao quát chuyển dữ liệu bảng thành JSON/CSV |
| log-triage-output | Quy tắc đầu ra log, không giữ dữ liệu hay đáp án cụ thể | Đúng chuẩn hóa service, thứ tự và schema; có dòng dư `=== END===` do model sinh nhưng không mâu thuẫn quy tắc | 8 dòng toàn tệp, 4 dòng thân kể cả delimiter dư; description kích hoạt tổng hợp service logs |

Ba lượt Phần 3.4 được lưu nguyên ở `results/skills-auto-dev`: code 10/10 (178702 token, 145,2 giây), data 6/8 (56587 token, 51,3 giây), logs 9/9 (66373 token, 72,9 giây); mỗi lượt đọc 1 skill, skills_modified=false. Điểm trung bình 0,9167. Code bổ sung type hints, regression/changelog; log áp dụng đủ ba quy ước. Data đạt integer cents nhưng meta không đúng và tên CSV không phải clean.csv. Skill đã bỏ sót tên clean.csv dù feedback có nêu; đọc skill không bảo đảm áp dụng đủ. Không sửa tay skill để khắc phục.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng dưới được sinh bằng module có sẵn `lab.compare`; bản độc lập ở [table.md](table.md). Điểm trung bình là trung bình điểm chuẩn hóa của từng tác vụ, không phải tỷ lệ cộng gộp mọi check.

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 4/8 | 6/8 |
| logs-learn | 6/9 | 0/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.40 | 0.92 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.83 |
| **Mean tokens per run** | 78,324 | 148,514 | 119,076 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

Đầu ra nguyên văn của `scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          75,727      0/3     
baseline      learn    18/18         0/9           80,921      0/3     
subagents     eval     18/18         0/12         170,882      0/3     
subagents     learn    11/18         0/9          126,146      0/3     
skills-auto   eval     18/18         7/12         130,895      3/3     
skills-auto   learn    18/18         7/9          107,258      3/3
```

Kiểm chứng `scripts/verify_freeze.py`: **checked 6 runs of skill conditions: OK**. Cả 18 lượt chính có `error=null`, token > 0, `skills_modified=false`, và đủ run.json/trace.md. Không chạy lại một lượt chính nào để chọn điểm tốt; chỉ chạy lại pilot CRLF trước khi có bộ kết quả baseline chính. Phản hồi eval không được đưa trở lại curator. Xem [submission-audit.json](submission-audit.json), [statistics.json](statistics.json) và [task-statistics.json](task-statistics.json).

Thống kê gọi worker và đọc skill:

| Tác vụ | Worker | Subagent calls | Skills đọc trong skills-auto |
|---|---|---:|---:|
| code-eval | explorer | 1 | 1 |
| code-learn | explorer | 1 | 1 |
| data-eval | explorer | 1 | 2 |
| data-learn | general-purpose | 1 | 2 |
| logs-eval | general-purpose | 1 | 1 |
| logs-learn | general-purpose | 1 | 1 |

`explorer` được gọi 3 lần và `general-purpose` 3 lần; implementer/reviewer riêng không được gọi ở các lượt này. Trong eval, code/data giao việc đọc/phân tích rồi tác tử chính thực hiện; log giao việc tạo output, sau đó tác tử chính đọc lại và chạy kiểm tra JSON/counts. Cách kiểm chứng log eval tốt hơn log learn, nhưng không cung cấp quy ước ẩn nên vẫn đạt 6/10. Hai tác vụ data đọc cả skill dữ liệu lẫn skill log; skill log không tạo thêm điểm cho dữ liệu bảng.

## 8. Phân tích

1. **Điểm học và đánh giá, kiểm tra giả thuyết.** Skills-auto tăng điểm học từ 0.6639 lên 0.9167 (Δ=0.2528) và điểm đánh giá từ 0.5973 lên 0.8253 (Δ=0.2279, tương đương 22.79 điểm phần trăm). Subagents học giảm xuống 0.4000, còn eval bằng baseline 0.5973. H1 được số liệu lượt đo này ủng hộ: không tăng điểm eval nhưng token cao hơn. H2 được ủng hộ: skills-auto cao nhất và Δ eval > 0,15. H3 được ủng hộ: khoảng cách học–eval của skills-auto là 0.0914 > 0,05. Không có điều kiện tăng điểm học mà không tăng điểm eval so với baseline; tuy nhiên khoảng cách học–eval vẫn cho thấy tổng quát hóa chưa đầy đủ.

2. **Check kỹ thuật và quy ước.** Baseline đạt 18/18 kỹ thuật ở cả học và eval, nhưng 0/9 và 0/12 quy ước. Skills-auto giữ 18/18 kỹ thuật và tăng quy ước lên 7/9 học, 7/12 eval. Do đó hiệu quả chính là chuyển quy ước đã học vào ngữ cảnh tác tử, không phải bằng chứng cải thiện năng lực tính toán/sửa bug. Ba quy ước mới của eval (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) đều không đạt ở skills-auto, phù hợp với việc chúng không có trong skill. Các quy ước còn lại chuyển được 7/9; meta và clean.csv của data vẫn thiếu hoặc sai.

3. **Cơ chế và lỗi còn lại.** Ở logs-eval, vết có đọc `skills/log-triage-output/SKILL.md`, tạo JSON với schema_version=2/generated_by=log-triage, chuẩn hóa service, sắp xếp errors và assert lại ordering/counts: ba check quy ước cũ tăng từ không đạt lên đạt. `rule_source_line` không đạt vì skill không hướng dẫn giữ số dòng nguồn. Ở code-eval, vết đọc code-fix-workflow rồi thêm regression/type hints/changelog; ba check này đạt nhưng version bump không đạt. Ở data-eval, skills_read=2 nhưng `meta.source` dùng đường dẫn kèm workspace thay vì tên tệp; meta sai dù câu trả lời nói đã có meta. Skill dữ liệu không giữ tên bắt buộc clean.csv; tác tử không tạo tệp này. Header chứa region và bốn hướng trong skill cũng quá hẹp khi dữ liệu mới dùng category. Đây là giới hạn ngữ nghĩa của skill và áp dụng một phần, không phải không đọc skill.

4. **Chi phí token.** Dùng chỉ số ∑ điểm chuẩn hóa / ∑ token × 10^6, không gọi đây là chi phí tiền vì chưa có thông tin giá và routing/billing của gateway.

| Điều kiện | Token TB toàn bộ | Token TB eval | Giây TB eval | Điểm / triệu token (tất cả) | Điểm / triệu token (eval) |
|---|---:|---:|---:|---:|---:|
| baseline | 78324.5 | 75727.7 | 51.5 | 8.05 | 7.89 |
| subagents | 148514.2 | 170882.3 | 122.1 | 3.36 | 3.50 |
| skills-auto | 119076.7 | 130895.0 | 78.3 | 7.31 | 6.30 |

Trên eval, skills-auto dùng 1.73 lần token baseline để tăng 0.2279 điểm; subagents dùng 2.26 lần mà không tăng điểm. Baseline tốt nhất về điểm trên mỗi token khi tính cả sáu tác vụ và riêng eval; skills-auto tốt nhất về điểm tuyệt đối. Riêng tập học, skills-auto đạt 8.55 điểm/triệu token so với baseline 8.20. Trong thí nghiệm này, subagents không đáng chi phí thêm nếu mục tiêu là đạt check; kết luận không áp dụng cho mọi loại dự án.

5. **Rò rỉ và quá khớp.** Curator chỉ đọc run role=learn của baseline; không đọc hoặc đưa eval vào prompt. Validator loại skill chứa marker eval; lần đầu một từ thông thường bị trùng marker và bị loại, không phải phát hiện đáp án eval trong skill. Giả thuyết được commit trước tag; eval chạy sau tag; hash xác nhận bộ skill không đổi. Skill không chứa đáp án số hoặc tên hàm của đề; tên file đầu ra/keys/region là quy ước được phép giữ. Dấu hiệu quá hẹp là header region không thích ứng với category ở data-eval; không gọi mọi khoảng cách học–eval là quá khớp vì eval thêm quy tắc mới. Sau freeze chỉ đọc check eval để giải thích kết quả trong báo cáo, không chỉnh skill, harness hay tái huấn luyện curator.

6. **Nhiễu của cùng bộ skill.** Các lượt dev được giữ nguyên trong results/skills-auto-dev và so với lượt chính sau freeze:

| Tác vụ | Điểm dev | Điểm sau freeze | Δ điểm | Token dev | Token sau freeze | Δ token |
|---|---:|---:|---:|---:|---:|---:|
| code-learn | 10/10 | 10/10 | 0.0000 | 178702 | 167979 | -10723 |
| data-learn | 6/8 | 6/8 | 0.0000 | 56587 | 81195 | +24608 |
| logs-learn | 9/9 | 9/9 | 0.0000 | 66373 | 72601 | +6228 |

Điểm của cả ba tác vụ không đổi, nhưng token trung bình tăng từ 100554.0 lên 107258.3 (6.67%), còn thời gian trung bình giảm từ 89,8 xuống 73,6 giây. Data sau freeze đọc thêm một skill so với dev. Không thấy nhiễu điểm ở hai lần quan sát này, nhưng không thể kết luận điểm luôn ổn định; nhiễu chi phí vẫn rõ. Đây không phải vòng học thứ hai vì skill byte-for-byte không đổi.

## 9. Hạn chế và tính hợp lệ

1. Chỉ ba tác vụ mỗi vai trò, mỗi điều kiện chính chạy một lần: một lỗi schema hoặc một lượt bất thường ảnh hưởng lớn đến trung bình; không có kiểm định ý nghĩa thống kê hay khoảng tin cậy.
2. Mô hình sinh không tất định dù dùng cùng cấu hình reasoning low: so sánh skills-auto-dev với lượt học sau freeze chỉ là ước lượng nhiễu thô, không tách được nhiễu từ hiệu ứng thứ tự.
3. Tác vụ được giảng viên thiết kế với quy ước ẩn: việc nhớ cents/meta/changelog có lợi rõ, nhưng không đại diện cho mọi dự án thực tế. Quy ước mới không thể suy ra chỉ từ quy tắc cũ.
4. Chỉ dùng một model qua gateway bên thứ ba: model ID, token usage và hành vi do gateway báo; chưa kiểm chứng routing nội bộ, chi phí thanh toán hay độ ổn định ở nhà cung cấp khác.
5. Các worker riêng không phải lúc nào được chọn; worker general-purpose vẫn có thể chạy. Vì vậy kết quả đo điều kiện harness có subagents, không cô lập tác dụng của từng vai trò explorer/implementer/reviewer.
6. Trace chỉ chứa luồng chính và mỗi nội dung bị render_trace giới hạn 1500 ký tự. Token callback tính cả worker, nhưng không thể suy ra đầy đủ các thao tác nội bộ worker hay mọi dòng output từ trace.
7. Curator thiếu tên clean.csv và để lại delimiter dư trong một skill. Skill hợp lệ về định dạng không bảo đảm đầy đủ về ngữ nghĩa; không sửa tay để bảo toàn thí nghiệm tự tiến hóa.
8. Checkout Windows cần chuẩn hóa CRLF trong Python sandbox, và kiểm chứng hash skills phải chạy trong Docker Linux do hash_dir dùng cách viết đường dẫn theo hệ điều hành. Các nguồn tasks và grader gốc giữ nguyên; pilot lỗi môi trường được tách khỏi số liệu chính.

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
