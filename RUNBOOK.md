# Lab 20: chạy và kiểm tra bài nộp

Mã nguồn dùng Deep Agents 0.7.21. Bốn phần TODO đã được cài đặt trong `src/lab/agent.py`, `subagents.py`, `runner.py`, `curator.py`.

## Môi trường

Windows dùng Docker Desktop (Linux containers). Bản `Dockerfile.lab` dùng Python 3.11 và cài Git để chạy được cả test shell và kiểm tra freeze.

```powershell
docker build -f Dockerfile.lab -t lab-deepagents-day20 .
docker run --rm -v "${PWD}:/lab" lab-deepagents-day20 python -m pytest -o addopts= -q
```

Sao chép `.env.example` thành `.env` nếu chưa có, rồi điền `OPENAI_API_KEY`. Mẫu dùng `LAB_MODEL=openai:gpt-6-luna`, Responses API, reasoning effort `low`, timeout 90 giây và một retry. Harness bỏ tham số temperature khi bật reasoning. Không commit `.env`.

## Quy trình thí nghiệm

Chạy tuần tự để tránh giới hạn tốc độ API. Các lệnh dưới đây dùng thư mục hiện tại làm `/lab`; runner sao chép workspace ra thư mục tạm trong container và dọn sau khi chấm.

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition baseline --tasks learn
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition subagents --tasks learn
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.curator
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition skills-auto --tasks learn
```

Đọc phản hồi của tác vụ học và đánh giá skill. Không sửa tay skill do curator sinh. Trước khi chạy đánh giá, điền H1–H3 vào báo cáo, commit `hypotheses`, tạo commit riêng `freeze skills` và tag `freeze`. Sao lưu kết quả thử skill vào `results/skills-auto-dev/` trước khi chạy chính thức. Không chạy các lệnh tạo tag trên một bài đã đóng băng sẵn.

```powershell
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition baseline --tasks eval
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition subagents --tasks eval
docker run --rm --env-file .env -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.runner --condition skills-auto --tasks all
docker run --rm -v "${PWD}:/lab" lab-deepagents-day20 python scripts/verify_freeze.py
docker run --rm -v "${PWD}:/lab" lab-deepagents-day20 python -m lab.compare
docker run --rm -v "${PWD}:/lab" lab-deepagents-day20 python scripts/check_breakdown.py
```

Các lần chạy lại ghi đè kết quả của cùng điều kiện/tác vụ: sao lưu trước nếu cần giữ bằng chứng. Phần `skills-auto` và `verify_freeze.py` phải dùng cùng hệ điều hành vì hàm hash có sẵn của lab băm cả chuỗi đường dẫn; kiểm tra kết quả chạy Linux trong Docker.

Sản phẩm chính: `results/`, `skills/auto/`, `report/REPORT.md`, `report/table.md`. Báo cáo ghi kết quả thật, lệnh chạy, commit freeze và hạn chế. Phần mở rộng là tùy chọn và không nằm trong kết quả chính.

Gateway GenzShop: https://modelapi.vn/v1 (bien OPENAI_API_BASE). API /v1/models da xac nhan ho tro gpt-6-luna. Huong dan: https://genzshop.vn/pages/docs.php?product=codex .
