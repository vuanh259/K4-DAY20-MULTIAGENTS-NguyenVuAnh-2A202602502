# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Vũ Anh | 2A202602502 | Cài đặt harness, subagents, runner và curator; chuẩn bị thí nghiệm và báo cáo |

- Cấu hình hiện tại: `LAB_MODEL=openai:gpt-6-luna`, Responses API, reasoning effort `low`, timeout 90 giây và một retry. Key GenzShop đã được kiểm tra thành công qua `OPENAI_API_BASE=https://modelapi.vn/v1`; gateway liệt kê `gpt-6-luna`, smoke test gọi `write_file` và `read_file` thành công. Harness bỏ temperature khi bật reasoning. `recursion_limit` mặc định là 60. Các lượt Gemini trước khi đổi nhà cung cấp không dùng làm kết quả OpenAI.
- Môi trường: Windows PowerShell với `.venv` Python 3.12.10; chạy test và thí nghiệm trong Docker Linux, Python 3.11.16, Deep Agents 0.7.21. Các phiên bản khác ghi trong `report/environment.json`. Toàn bộ test ngoại tuyến: **29 passed in 13.54s**.
- Trước freeze: hoàn thành 6 lượt baseline/subagents học và 3 lượt skills-auto-dev; smoke test kết nối và tools thành công qua gateway GenzShop. Các lượt lỗi Gemini và pilot CRLF được lưu riêng, không dùng làm dữ liệu thí nghiệm chính.
- Commit của tag `freeze`: chưa thực hiện (thuộc Phần 4).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

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

Lưu ý cấu hình mô hình theo `src/lab/model.py`: nếu dùng Azure/cổng tương thích, điền đủ `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT_MODEL`. Nếu dùng OpenAI trực tiếp, cần cả `OPENAI_API_KEY` và `LAB_MODEL=openai:<tên-model-được-cấp-quyền>`; chỉ điền key sẽ không thay đổi mặc định `deepseek:deepseek-chat`. Không ghi khóa thật vào báo cáo hoặc mã nguồn.

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
| records-data-workflow | Quy trình JSON và cleaned CSV; header/vùng là quy ước tổ chức được phép giữ | Đúng đơn vị cents, meta, loại dữ liệu thiếu và UTC theo feedback; rows_used chỉ đếm bản ghi có amount | 11 dòng toàn tệp, 7 dòng thân; description bao quát chuyển dữ liệu bảng thành JSON/CSV |
| log-triage-output | Quy tắc đầu ra log, không giữ dữ liệu hay đáp án cụ thể | Đúng chuẩn hóa service, thứ tự và schema; có dòng dư `=== END===` do model sinh nhưng không mâu thuẫn quy tắc | 8 dòng toàn tệp, 4 dòng thân kể cả delimiter dư; description kích hoạt tổng hợp service logs |

Ba lượt Phần 3.4 được lưu nguyên ở `results/skills-auto-dev`: code 10/10 (178702 token, 145,2 giây), data 6/8 (56587 token, 51,3 giây), logs 9/9 (66373 token, 72,9 giây); mỗi lượt đọc 1 skill, skills_modified=false. Điểm trung bình 0,9167. Code bổ sung type hints, regression/changelog; log áp dụng đủ ba quy ước. Data đạt integer cents nhưng meta không đúng và tên CSV không phải clean.csv. Skill đã bỏ sót tên clean.csv dù feedback có nêu; đọc skill không bảo đảm áp dụng đủ. Không sửa tay skill để khắc phục.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
