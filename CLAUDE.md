# Người Que

Repo tự động dựng video YouTube hoạt hình người que về **tâm lý học con người** cho người xem nước ngoài.

**Định vị kênh: kênh TÂM LÝ HỌC, không phải kênh / chuyên gia tài chính.** Tiền bạc, mua sắm, đầu tư chỉ là một mảng ví dụ để giải thích thiên kiến và hành vi con người (bên cạnh quan hệ, thói quen, công việc, mạng xã hội…). Không đưa lời khuyên đầu tư, không gợi ý mua / bán mã nào, không dự đoán thị trường; người kể là người kể chuyện giáo dục; nhân vật: Max (người đi làm 25–30 tuổi, hoodie cam) và Brainy (bộ não hồng, kể nghiên cứu) — **không có nhân vật chuyên gia / bác sĩ** (chính sách YouTube, xem docs/12). Khoảng 60–70% chủ đề là tâm lý đời sống chung, 30–40% là tâm lý tiền bạc. Python 3.11, gói `nguoique/`, lệnh `nq` (Pillow vẽ khung → ffmpeg; giọng Kokoro chạy local). Đọc `README.md` để nắm quy trình.

## Ngôn ngữ
- **Trả lời người dùng bằng tiếng Việt.** Tài liệu, thông báo CLI, tên lệnh: tiếng Việt.
- **Nội dung video bằng tiếng Anh**: lời đọc (`loi`), chữ trên hình, phụ đề, tiêu đề / mô tả YouTube, prompt Gemini.
- Định danh trong code: tiếng Việt không dấu, snake_case.

## Luôn theo
- `docs/00-HOP-DONG.md` — lệnh, chữ ký module, `config.yaml`, lược đồ `kich-ban.json`, tập giá trị hiệu ứng. Không tự đổi giao diện đã chốt ở đây.
- `docs/02-KHUON-PHONG-CACH.md` — nhịp cảnh, bố cục, màu, hiệu ứng khi viết kịch bản.
- `docs/05-VIET-KICH-BAN.md` — cấu trúc kịch bản, kiểm chứng nguồn, không bịa số liệu / nghiên cứu.
- `docs/04-TAO-ANH-GEMINI.md` — tên tệp và prompt khi cần ảnh mới.
- `docs/12-CHINH-SACH-YOUTUBE.md` — **chính sách kiếm tiền YouTube**: mỗi video một câu chuyện riêng của Max (không làm hàng loạt theo khuôn), không nhân vật AI đóng chuyên gia / bác sĩ, không kê đơn sức khoẻ / tinh thần / tài chính, chủ đề cần tránh, danh sách kiểm bắt buộc cho mọi kịch bản.

## Quy tắc cứng
- **Không `git commit` / `git push`** khi người dùng chưa yêu cầu.
- **Không thêm thư viện** ngoài danh sách trong `docs/00-HOP-DONG.md` khi chưa hỏi người dùng.
- **Không gọi API trả phí** (OpenAI, ElevenLabs, Gemini API, dịch vụ TTS / ảnh trả tiền…). Chi phí duy nhất của dự án là tài khoản Claude.
- Không dùng mô hình giọng có giấy phép phi thương mại làm mặc định (kênh sẽ bật kiếm tiền).
- Không đưa vào repo tệp có bản quyền của người khác (nhạc, hình, font không cho phép), không sao chép hình / nhân vật / lời của kênh tham khảo.
- Thông báo lỗi tiếng Việt, kèm cách sửa.

## Lệnh Claude Code
Người dùng KHÔNG gõ lệnh tay — Claude tự chạy mọi lệnh `nq`, tự đọc lỗi và sửa.
- `/cai-dat` — cài lần đầu + kiểm + test + dựng thử.
- `/video <chủ đề>` — làm trọn một video (kịch bản → `nq lam` nháp → sửa → bản thật).
- `/kich-ban <chủ đề>` — viết `du-an/<slug>/kich-ban.json` + `mo-ta-youtube.md`.
- `/phan-tich-kenh <thư mục phan-tich/...>` — cập nhật docs/01, docs/02 từ kết quả `nq phan-tich`.
- Người dùng cũng có thể tự làm bằng giao diện trình duyệt: bấm đúp `giao-dien.bat` hoặc `nq giao-dien` (http://127.0.0.1:8770 — dự án, kho hình, hàng việc, cài đặt).
