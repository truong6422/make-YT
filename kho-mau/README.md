# Kho mẫu

Kho hình và âm thanh dùng chung cho mọi video. Kịch bản tham chiếu tệp bằng đường dẫn tương đối với thư mục này (vd. `nhan-vat/max__vui__dung.png`) — máy tìm trong thư mục dự án trước, rồi tới `kho-mau/`.

Sau khi thêm / xoá tệp, chạy `nq kho` để cập nhật `danh-muc.json` + `danh-muc.md` (Claude đọc `danh-muc.md` khi viết kịch bản để ưu tiên ảnh đã có).

## Thư mục

| Thư mục | Chứa | Định dạng |
|---|---|---|
| `nhan-vat/` | Nhân vật (Max, nhân vật phụ) theo biểu cảm × tư thế | PNG nền trong |
| `dao-cu/` | Đạo cụ: tiền, cổ phiếu, bộ não, đồng hồ… | PNG nền trong |
| `bieu-do/` | Biểu đồ tăng / giảm, đường giá | PNG nền trong |
| `phong-nen/` | Nền cảnh: phòng, văn phòng, sàn giao dịch, đường phố | PNG / JPG 16:9 |
| `nhac-nen/` | Nhạc nền miễn bản quyền | MP3 / WAV / OGG |
| `am-thanh/` | Hiệu ứng âm thanh ngắn (pop, whoosh, tick…) | WAV / MP3 |
| `font/` | Font cho phụ đề / chữ trên hình (vd. `Inter-Bold.ttf`) | TTF / OTF |
| `_cho-xu-ly/` | Ảnh Gemini vừa tải về, chưa tách nền. `nq kho` bỏ qua thư mục bắt đầu bằng `_` | PNG / JPG |

## Tên tệp

- Chữ thường, không dấu, nối bằng `-`; phần tách nghĩa dùng `__` (hai gạch dưới).
- Nhân vật: `nhan-vat/<ten>__<bieu-cam>__<tu-the>.png` — vd. `max__lo-lang__dung.png`, `max__tham-lam__cam-dien-thoai.png`.
- Đạo cụ: `dao-cu/<ten>.png` — vd. `bao-tien.png`, `co-phieu-xanh.png`.
- Biểu đồ: `bieu-do/<ten>.png` — vd. `tang.png`, `giam-manh.png`.
- Nền: `phong-nen/<ten>.png` — vd. `van-phong.png`.
- Âm thanh: `am-thanh/<ten>.wav`, nhạc: `nhac-nen/<tam-trang>-<ten>.mp3` — vd. `curious-light.mp3`.

Bảng mã biểu cảm / tư thế và prompt tạo ảnh: [`docs/04-TAO-ANH-GEMINI.md`](../docs/04-TAO-ANH-GEMINI.md).

Quy trình ảnh: Gemini → lưu vào `_cho-xu-ly/` → `nq tach-nen kho-mau/_cho-xu-ly --ra kho-mau/nhan-vat` (hoặc `dao-cu`, `bieu-do`) → `nq kho`.

## Nhạc nền và hiệu ứng âm thanh lấy ở đâu

Chỉ dùng nguồn **miễn bản quyền cho phép dùng trên YouTube có kiếm tiền**, ví dụ YouTube Audio Library (trong YouTube Studio). Mỗi nguồn có điều kiện riêng (có bản yêu cầu ghi công trong mô tả) — đọc kỹ giấy phép từng tệp và ghi lại nguồn. Chi tiết nguồn, cách chọn và chuẩn âm lượng: [`docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md`](../docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md).

## Không đưa vào kho

- Tệp có bản quyền của người khác: nhạc thương mại, hình / nhân vật / âm thanh cắt từ kênh khác (kể cả kênh tham khảo), font không cho phép dùng thương mại.
- Ảnh chụp người thật, logo thương hiệu.
- Tệp không rõ nguồn. Không chắc giấy phép → không dùng.
