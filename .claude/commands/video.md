---
description: Làm trọn một video từ chủ đề — viết kịch bản, tự chạy dựng, tự sửa lỗi, báo đường dẫn MP4
argument-hint: <chủ đề tâm lý học, vd. "why we procrastinate">
---

Người dùng KHÔNG gõ lệnh tay. Bạn tự làm hết, tự chạy mọi lệnh, chỉ hỏi khi thật sự phải chọn.

Chủ đề: $ARGUMENTS

1. Làm đúng như lệnh `/kich-ban` (đọc `.claude/commands/kich-ban.md`) để tạo `du-an/<slug>/kich-ban.json` + `mo-ta-youtube.md`. Kênh là TÂM LÝ HỌC, video 8–15 phút, ưu tiên khuôn cảnh (`docs/11-KHUON-CANH.md`), **tuân thủ `docs/12-CHINH-SACH-YOUTUBE.md`** (kể chuyện Max, không nhân vật chuyên gia, không kê đơn, khác 3 video gần nhất).
2. Báo người dùng ngắn: câu chuyện của Max, ý riêng của video, 3 tiêu đề, kết quả kiểm chính sách. Có rủi ro chính sách → sửa trước. Người dùng không phản đối thì làm tiếp (đây là bước người dùng duyệt nội dung — "dấu tay người").
3. Chạy bản nháp: `.venv\Scripts\python -m nguoique lam <slug> --nhap`. Chưa có `.venv` → làm `/cai-dat` trước.
4. Lỗi → đọc thông báo, sửa (kịch bản JSON hoặc code), chạy lại. Tối đa 3 vòng; vẫn lỗi thì báo người dùng ngắn gọn lỗi gì và cần họ làm gì.
5. Đọc cảnh báo kiểm nhịp trong kết quả; cảnh quá dài / video ngoài 8–15 phút → sửa kịch bản, chạy lại nháp.
6. Nháp ổn → chạy bản thật: `.venv\Scripts\python -m nguoique lam <slug>`.
7. Báo người dùng (ngắn): đường dẫn MP4, thumbnail, `mo-ta-youtube.md`, thời lượng, danh sách ảnh còn đang dùng hình tạm (gợi ý tạo bằng Gemini nếu họ muốn).

Nhắc khi đăng: chọn "No, it's not made for kids"; giữ nhịp 1–2 video / tuần.

Không commit, không đăng YouTube.
