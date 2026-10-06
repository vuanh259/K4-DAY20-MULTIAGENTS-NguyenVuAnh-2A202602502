# Lượt thử trước thí nghiệm chính

Lượt `baseline/data-learn` đầu tiên dùng cấu hình Gemini mặc định (chưa đặt timeout hoặc thinking level). Đã ghi trace của ba tool call đầu, sau đó không có trạng thái mới trong nhiều phút; container được dừng để tránh chờ vô hạn. Vì bị dừng trước khi runner ghi bản ghi hoàn chỉnh, lượt này không có `run.json`, không biết tổng token và không dùng để tính điểm hoặc làm đầu vào curator.

Sau đó cấu hình thống nhất mọi lượt chính và curator: `thinking_level=low`, timeout mỗi yêu cầu 90 giây, `max_retries=1`. Trace thử được giữ nguyên tại đây để công khai sự cố, không đưa vào bảng so sánh.
