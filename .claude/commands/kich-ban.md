---
description: Viết kịch bản video người que (tiếng Anh) + mô tả YouTube cho một chủ đề
argument-hint: <chủ đề, vd. "loss aversion">
---

Chủ đề: **$ARGUMENTS**

Trả lời người dùng bằng tiếng Việt. Nội dung video (lời, chữ trên hình, tiêu đề, mô tả, prompt Gemini) bằng tiếng Anh.

## 1. Đọc trước (theo thứ tự)

1. `docs/00-HOP-DONG.md` — lược đồ `kich-ban.json`, tập giá trị hợp lệ (`hieu_ung`, `lien_tuc`, `neo`, `may_quay`, `chuyen_canh.kieu`, `phan`). Bắt buộc.
2. `docs/02-KHUON-PHONG-CACH.md` — nếu có: nhịp cảnh, bố cục, màu, hiệu ứng ưa dùng. Số đo ở đây ưu tiên hơn gợi ý ở docs/05.
3. `docs/05-VIET-KICH-BAN.md` — cấu trúc, độ dài câu, giọng văn, kiểm chứng, miễn trừ, checklist.
4. `docs/04-TAO-ANH-GEMINI.md` — quy ước tên tệp, mã biểu cảm / tư thế, khuôn prompt.
5. `kho-mau/danh-muc.md` — nếu có: danh sách tệp đã có trong kho. **Ưu tiên dùng tệp đã có.** Không có tệp này → coi như kho trống.
6. `templates/kich-ban-mau.json` — nếu có, để theo đúng kiểu khoá / giá trị mặc định.

Thiếu `$ARGUMENTS` → hỏi người dùng chủ đề rồi dừng.

## 2. Đặt slug

`slug` = chủ đề tiếng Anh, chữ thường, không dấu, nối bằng `-` (vd. `loss-aversion`). Nếu `du-an/<slug>/kich-ban.json` đã tồn tại → hỏi người dùng ghi đè hay đặt slug khác (vd. thêm `-2`), không tự ghi đè.

## 3. Nghiên cứu nội dung

- Chọn 1–2 nghiên cứu **có thật** về chủ đề (gợi ý trong docs/05 mục 6). Nêu đúng tác giả, năm, thí nghiệm, kết quả chính. Không chắc chi tiết nào thì không nói chi tiết đó.
- Không bịa số. Số trong ví dụ của Max là giả định và lời phải nói rõ.
- Nghiên cứu có tranh cãi / tái lập thất bại → nói rõ trong lời hoặc chọn nghiên cứu khác.

## 4. Viết `du-an/<slug>/kich-ban.json`

- Đúng lược đồ docs/00: `tieu_de`, `ngon_ngu: "en"`, `nhac_nen` (tệp có trong kho hoặc `null`), `canh[]`.
- Đủ các `phan`: `hook` → `boi-canh` → `giai-thich` → `vi-du` → `nghien-cuu` → `cach-tranh` → `tom-tat` → `ket`. Độ dài **8–15 phút, mặc định ~10 phút** (chủ dự án chốt, không vượt 15 phút): ước theo Kokoro ~150–160 từ/phút → tổng lời **1.200–2.300 từ** (10 phút ≈ 1.500–1.600 từ), **~120–220 cảnh** (10 phút ≈ 150). Người dùng nêu độ dài khác trong khoảng 8–15 phút thì theo người dùng; ngoài khoảng → hỏi lại.
- Phân bổ thời lượng theo bảng mục 1 docs/05 (hook ~3%, boi-canh ~7%, giai-thich ~20%, vi-du ~25%, nghien-cuu ~18%, cach-tranh ~16%, tom-tat ~6%, ket ~5%). Video dài hơn thì thêm ví dụ / nghiên cứu / cách tránh, không kéo dài hook.
- **Điểm giữ chân mỗi 60–90 giây** (≤ ~220 từ giữa hai điểm): vòng lặp mở / trả lời, câu hỏi tới người xem, bước ngoặt trong chuyện Max, đổi nhịp hình (`dam`, `rung`, `nhay-trang`, `zoom-vao`, cảnh chữ lớn). Mọi vòng lặp mở phải được trả lời trong video.
- 1 câu = 1 cảnh, ~6–14 từ. `id` dạng `c001`, `c002`… duy nhất.
- Mỗi cảnh có ít nhất một thay đổi hình (lớp ảnh, biểu cảm, chữ khoá, máy quay). Max là nhân vật chính; nghiên cứu do `chuyen-gia` dẫn.
- `chu`: từ khoá IN HOA 1–4 từ, không chép nguyên câu.
- Số / ký hiệu / tên riêng khó đọc → `loi_doc`. Cảnh không lời → có `thoi_luong`.
- Chỉ dùng giá trị hiệu ứng trong tập của docs/00. Toạ độ 0..1.
- Đường dẫn ảnh theo quy ước docs/04: `nhan-vat/<ten>__<bieu-cam>__<tu-the>.png`, `dao-cu/<ten>.png`, `bieu-do/<ten>.png`, `phong-nen/<ten>.png`. Tệp chưa có vẫn được ghi (máy vẽ khung giữ chỗ) nhưng phải liệt kê ở báo cáo.
- Kênh là TÂM LÝ HỌC, không phải tư vấn tài chính: giải thích VÌ SAO con người hành xử như vậy, không bảo khán giả nên mua / bán / đầu tư gì, không nêu mã cổ phiếu / coin để khuyến nghị, không dự đoán thị trường. Chuyên gia trong video là nhà tâm lý học.
- Nói về tiền / đầu tư → phần `ket` có câu miễn trừ "This video is for educational purposes about psychology and is not financial advice."
- JSON hợp lệ (không chú thích, không dấu phẩy thừa).

### Ưu tiên khuôn cảnh

- Đọc `docs/11-KHUON-CANH.md` và `templates/kich-ban-khung.json` trước khi viết. **Mặc định viết cảnh dạng khuôn**: `{"id": "c012", "khuon": "<ten>", "tham_so": {...}}` (17 khuôn trong `templates/khuon-canh/`), đi theo thứ tự phần và `_phan_bo` của khung; đặt `tham_so_chung.khai_niem` ở gốc.
- Cần khác bố cục: ghi đè khoá (`may_quay`, `chuyen_canh`, `lop`…) hoặc `lop_them` / `chu_them` trong chính cảnh đó; chỉ viết cảnh thủ công đầy đủ khi không khuôn nào hợp.
- Tham số bắt buộc của mỗi khuôn phải có; tên tham số đúng `_tham_so` của tệp khuôn (sai → `LoiKhuonCanh`). Hai cảnh liền nhau không cùng khuôn với cùng biểu cảm / đạo cụ.
- Báo cáo ảnh thiếu tính theo đường dẫn **sau khi điền** tham số (vd. `nhan-vat/max__<bieu_cam>__<tu_the>.png`).

## 5. Viết `du-an/<slug>/mo-ta-youtube.md`

Tiếng Anh, gồm:
1. **3 tiêu đề đề xuất** (≤ 70 ký tự, gây tò mò nhưng đúng nội dung).
2. **Description**: 2–3 câu mở đầu có từ khoá; dòng miễn trừ "not financial advice" (nếu liên quan đầu tư).
3. **Chapters**: mốc thời gian **ước tính** (giả định ~2,6 từ/giây giọng đọc + nghỉ giữa cảnh), bắt đầu `0:00`; ghi chú tiếng Việt cho người dùng rằng cần chỉnh lại theo video thật.
4. **Tags**: 10–15 tag.
5. **Sources**: mọi nghiên cứu đã nhắc — tác giả, năm, tên bài, tạp chí, DOI / đường dẫn nếu biết chắc. Không biết chắc DOI thì không ghi DOI.
6. **Thumbnail ideas**: 2–3 ý (biểu cảm Max, đạo cụ, ≤ 4 từ chữ lớn).
7. **Disclosure** (nếu cần): dòng công khai nội dung tổng hợp, vd. "Narration uses an AI-generated voice. Illustrations were created with AI assistance." — kèm ghi chú tiếng Việt rằng người dùng tự quyết bật nhãn "Altered or synthetic content" trên YouTube theo chính sách hiện hành.
8. Nhạc / âm thanh cần ghi công (nếu tệp nhạc trong kho yêu cầu).

## 6. Tự kiểm

Chạy qua checklist mục 7 của docs/05. Đếm số cảnh và **tổng số từ** của `loi`, ước tổng thời lượng (từ ÷ ~150 từ/phút + ~0,35s/cảnh); ngoài 8–15 phút thì sửa trước khi báo. Liệt kê mốc các điểm giữ chân (ước theo số từ) để kiểm khoảng cách ≤ 90 giây. Soát lại mọi giá trị hiệu ứng có trong tập hợp lệ.

## 7. Báo cáo cho người dùng (tiếng Việt)

- Đường dẫn 2 tệp đã tạo, số cảnh, tổng số từ, thời lượng ước tính, mốc các điểm giữ chân.
- Nghiên cứu đã dùng + điểm nào người dùng nên tự kiểm lại.
- **Ảnh còn thiếu** (so với `kho-mau/danh-muc.md`): bảng gồm tên tệp, số cảnh dùng, và **prompt Gemini tiếng Anh hoàn chỉnh** dựng từ khuôn ở docs/04 (nhắc đính kèm ảnh gốc Max với ảnh nhân vật Max).
- Âm thanh / nhạc còn thiếu.
- Bước tiếp: `nq may-chu` (cửa sổ riêng) → `nq dung <slug> --nhap` → `nq dung <slug>` → `nq thumbnail <slug>` (nếu đã ghi khoá `thumbnail` trong kich-ban.json, xem docs/06).

Không commit.
