---
description: Đọc kết quả `nq phan-tich` và cập nhật docs/01 (phân tích kênh) + docs/02 (khuôn phong cách)
argument-hint: <thư mục phan-tich/...>
---

Thư mục kết quả: **$ARGUMENTS**

Trả lời bằng tiếng Việt.

## 1. Kiểm đầu vào

- Thiếu `$ARGUMENTS` hoặc thư mục không tồn tại → liệt kê các thư mục con trong `phan-tich/` (nếu có), hỏi người dùng chọn, rồi dừng.
- Đọc `docs/00-HOP-DONG.md` (tập hiệu ứng / máy quay / chuyển cảnh hiện có) và bản hiện tại của `docs/01-PHAN-TICH-KENH.md`, `docs/02-KHUON-PHONG-CACH.md` (nếu có).

## 2. Đọc kết quả

- `$ARGUMENTS/bao-cao.md` — số liệu đo được (số cảnh, độ dài cảnh, nhịp lời, thời lượng, bản chép lời nếu có…).
- Mọi ảnh `$ARGUMENTS/tong-quan-*.jpg` — xem từng ảnh: bố cục, cỡ / vị trí nhân vật, màu nền, cách đặt chữ, đạo cụ, kiểu chuyển cảnh, phụ đề.
- Tệp khác trong thư mục (nếu có, vd. chép lời) — đọc khi cần đối chiếu.

## 3. Cập nhật `docs/01-PHAN-TICH-KENH.md`

Thêm (không xoá phần cũ) một mục cho video vừa phân tích:
- Nguồn: tên thư mục, URL / tệp gốc nếu `bao-cao.md` có ghi, ngày phân tích.
- Số liệu đo được: thời lượng, số cảnh, độ dài cảnh trung bình / trung vị / ngắn nhất / dài nhất, tốc độ lời (từ/phút) nếu có, cấu trúc các phần theo mốc thời gian.
- Quan sát từ ảnh tổng quan: bố cục, màu, chữ, nhịp hình.
- **Ghi rõ nguồn cho từng con số**: "(đo: `<thư mục>/bao-cao.md`)" hoặc "(quan sát: `tong-quan-03.jpg`)". Phân biệt rõ số **đo được** và nhận xét **ước lượng bằng mắt**.
- Có nhiều video đã phân tích → cập nhật bảng tổng hợp so sánh.

## 4. Cập nhật `docs/02-KHUON-PHONG-CACH.md`

Chuyển số liệu thành quy tắc dùng được khi viết kịch bản, mỗi quy tắc kèm nguồn đo:
- Nhịp: độ dài cảnh mục tiêu, số từ mỗi câu, thời lượng từng phần (`hook`, `boi-canh`…).
- Bố cục: vị trí / cỡ (`co`) nhân vật, vùng đặt chữ, lề phụ đề — viết bằng toạ độ 0..1 theo lược đồ docs/00.
- Màu nền, màu chữ nhấn (mã màu).
- Ánh xạ hiệu ứng quan sát được → giá trị có sẵn trong docs/00 (`hieu_ung`, `lien_tuc`, `may_quay`, `chuyen_canh.kieu`).
- Hiệu ứng quan sát được nhưng **chưa có** trong docs/00 → ghi vào mục "Đề xuất hiệu ứng mới" (mô tả, ví dụ mốc thời gian). **Không sửa code lõi, không sửa docs/00.**

Nguyên tắc: học cấu trúc / nhịp / cách dựng; **không** ghi lại để sao chép hình, nhân vật, lời, nhạc của kênh tham khảo.

## 5. Báo cáo cho người dùng

Tóm tắt các thay đổi chính trong docs/01 và docs/02, các số đo quan trọng, đề xuất hiệu ứng mới (nếu có), và điểm chưa chắc (vd. phát hiện cảnh bị nhiễu, chép lời thiếu).

Không commit.
