# 11 — Thư viện khuôn cảnh (template gốc để làm video chủ đề mới)

Mục tiêu: viết kịch bản bằng **tên khuôn + vài tham số** thay vì chép tay toàn bộ `lop` / `chu` / `may_quay` cho từng cảnh. Bố cục, màu, hiệu ứng, nhịp đã đặt sẵn theo [`02-KHUON-PHONG-CACH.md`](02-KHUON-PHONG-CACH.md); tên ảnh theo [`04-TAO-ANH-GEMINI.md`](04-TAO-ANH-GEMINI.md).

- Khuôn: `templates/khuon-canh/<ten>.json` — mỗi tệp một cảnh có chỗ trống `{{ten_tham_so}}`, kèm `_mo_ta`, `_dung_khi`, `_tham_so`.
- Triển khai: `nguoique/khuon_canh.py` → `trien_khai(kb, thu_muc_khuon)`, chạy trước bước kiểm của `kichban.nap_kich_ban`.
- Kịch bản khung 10 phút: `templates/kich-ban-khung.json` (48 cảnh mẫu, chủ đề ví dụ loss aversion, có `_phan_bo`).

## 1. Cách viết một cảnh dùng khuôn

```json
{"id": "c019", "khuon": "ten-khai-niem",
 "tham_so": {"loi": "Psychologists have a name for this. It's called loss aversion.",
             "khai_niem": "LOSS AVERSION", "dinh_nghia": "Losses hurt more than gains feel good"},
 "chuyen_canh": "cat"}
```

| Quy tắc | Chi tiết |
|---|---|
| Tham số | Lấy theo thứ tự: `tham_so` của cảnh → `tham_so_chung` ở gốc kịch bản (chỉ áp cho khuôn có khai tham số đó) → `mac_dinh` của khuôn. Không có `mac_dinh` (hoặc `"bat_buoc": true`) = **bắt buộc**; thiếu → lỗi nêu rõ cảnh + tên tham số. Tham số khuôn không có (gõ nhầm) → lỗi. |
| Kiểu giá trị | `"tre": "{{tre_chu}}"` (chỗ trống đứng một mình) nhận nguyên số / null. Chỗ trống giữa chữ (`"nhan-vat/max__{{bieu_cam}}__{{tu_the}}.png"`) thay bằng chữ. |
| Ghi đè | Mọi khoá khác của cảnh (`may_quay`, `chuyen_canh`, `lop`, `chu`, `dem_sau`, `toc_do`, `phan`…) **thay nguyên** khoá cùng tên của khuôn (không trộn sâu, không điền chỗ trống). |
| Nối thêm | `lop_them`, `chu_them`, `am_thanh_them` nối vào cuối danh sách của khuôn. |
| Tắt một phần | Tham số ảnh / chữ = `""` → lớp có `anh` rỗng, chữ có `noi_dung` rỗng bị bỏ (vd. `"dao_cu": ""`, `"chu": ""`). |
| Khuôn riêng dự án | Đặt `du-an/<slug>/khuon-canh/<ten>.json` — trùng tên thì khuôn dự án thắng khuôn chung. |
| Lỗi | `LoiKhuonCanh` (con của `LoiKichBan`): khuôn không tồn tại (liệt kê khuôn có), thiếu / thừa tham số, khuôn có chỗ trống chưa khai. |

Mã biểu cảm (`bieu_cam`): `vui, tham-lam, so-hai, hoang-loan, hoi-han, tu-tin, boi-roi, soc, suy-nghi, buon, gian, nhe-nhom, dac-y, lo-lang, hao-hung, chan`. Tư thế (`tu_the`): `dung, ngoi-may-tinh, chi-tay, di-bo, cam-dien-thoai, om-dau` (docs/04 bảng 3, 4).

## 2. Bảng khuôn

Tham số **in đậm** là bắt buộc. Mọi khuôn có thêm `loi_doc` (null), `nen`, `phan` (mặc định ghi ở cột 2). Giá trị mặc định đầy đủ: mở `_tham_so` trong tệp.

| Khuôn | `phan` mặc định · hình | Dùng khi | Tham số | Ví dụ `tham_so` |
|---|---|---|---|---|
| `mo-bai-cau-hoi` | hook · nền tối, Max sốc run, dấu hỏi bật, chữ đỏ, máy `dam` | Câu 1–3 hook; câu hỏi thẳng người xem giữa video (≤ 1 lần/30 s) | **loi**, chu (`WHY?`), bieu_cam (`soc`), tu_the, dao_cu (`dao-cu/dau-hoi.png`), tre_dao_cu, tre_chu | `{"loi": "Why does losing $100 hurt more…?", "chu": "WHY?"}` |
| `dat-van-de` | boi-canh · phòng, Max lo, tiền rơi, `zoom-ra`, nháy đen | Vì sao chuyện này quan trọng; câu báo trước | **loi**, chu (""), bieu_cam (`lo-lang`), tu_the, dao_cu (`dao-cu/tien.png`), tre_dao_cu | `{"loi": "Max had saved two thousand dollars.", "bieu_cam": "vui"}` |
| `hai-lua-chon` | giai-thich · chia đôi trái/phải, vạch giữa, nhãn xanh / đỏ, Max lưỡng lự giữa | Bài toán lựa chọn, mời đoán | **loi, nhan_a, nhan_b**, anh_a, anh_b, bieu_cam (`boi-roi`), tre_a, tre_b | `{"nhan_a": "WIN $150", "nhan_b": "LOSE $100"}` |
| `so-sanh-truoc-sau` | vi-du · Max trước (trái) / Max sau trượt vào (phải) | Bước ngoặt, kết quả khi áp dụng mẹo | **loi**, nhan_truoc (`BEFORE`), nhan_sau (`AFTER`), bieu_cam_truoc/tu_the_truoc, bieu_cam_sau/tu_the_sau, tre_sau | `{"nhan_truoc": "DAILY", "nhan_sau": "YEARLY"}` |
| `bieu-do-tang` | vi-du · Max hào hứng nhún + biểu đồ lên phóng to, số xanh, máy đứng yên | Giá lên, lãi trên giấy | **loi**, chu (`+20%`), bieu_do (`bieu-do/tang.png`), bieu_cam, tre_bieu_do, tre_chu | `{"loi": "Green was up twenty percent.", "chu": "+20%"}` |
| `bieu-do-giam` | vi-du · nền tối, chớp trắng, `rung`, biểu đồ sập + hit, Max ôm đầu | Cú sốc thua lỗ (≤ 1 lần/phút) | **loi**, chu (`-30%`), bieu_do (`bieu-do/giam-manh.png`), bieu_cam (`hoang-loan`), tu_the (`om-dau`) | `{"chu": "-20%", "tu_the": "dung"}` |
| `ten-khai-niem` | giai-thich · chớp trắng, Max chỉ tay, tên khái niệm gõ chữ lớn + định nghĩa | Lần đầu gọi tên hiệu ứng tâm lý | **loi, khai_niem**, dinh_nghia (""), mau_chu (`#D64545`), tre_chu, tre_dinh_nghia | `{"khai_niem": "LOSS AVERSION"}` (hoặc qua `tham_so_chung`) |
| `trich-nghien-cuu` | nghien-cuu · văn phòng, Brainy bên phải, thẻ vàng "TÁC GIẢ, NĂM", kết quả xanh | Câu dẫn nghiên cứu **có thật** | **loi, tac_gia, nam**, ket_qua (""), nhan_vat, tre_ket_qua | `{"tac_gia": "KAHNEMAN & TVERSKY", "nam": 1979, "loi_doc": "In nineteen seventy-nine…"}` |
| `con-so-lon` | nghien-cuu · một con số khổng lồ phóng to + chú thích, Max nhỏ góc | Số liệu bất ngờ (có nguồn / nói rõ giả định) | **loi, con_so**, chu_phu (""), mau_so, tre_so | `{"con_so": "2x", "chu_phu": "PAIN VS JOY"}` |
| `danh-sach-3-y` | cach-tranh · 1./2./3. trượt vào lần lượt, Max suy nghĩ, máy đứng yên | Liệt kê 3 dấu hiệu / lý do / bước | **loi, y_1, y_2, y_3**, tieu_de (""), mau_y, tre_1/2/3 | `{"tieu_de": "3 WAYS", "y_1": "…", "y_2": "…", "y_3": "…"}` |
| `vi-du-doi-thuong` | vi-du · Max to ở bàn máy tính / cầm điện thoại, đạo cụ tuỳ chọn | Khuôn "ngựa thồ" kể chuyện Max | **loi**, bieu_cam (`suy-nghi`), tu_the (`ngoi-may-tinh`), dao_cu (""), chu (""), nen (`phong-nen/phong.png`), may_quay, vi_tri_x, lien_tuc | `{"tu_the": "cam-dien-thoai", "bieu_cam": "lo-lang"}` |
| `dam-dong` | vi-du · đám đông chạy vào, Max nhỏ nhìn theo, `lia-phai` | Bầy đàn, FOMO, social proof | **loi**, chu (`EVERYONE'S BUYING`), dam_dong, hieu_ung_dam_dong, bieu_cam | `{"dam_dong": "nhan-vat/dam-dong__hoang-loan__bo-chay.png", "hieu_ung_dam_dong": "truot-trai"}` |
| `noi-tam` | giai-thich · Max lắc lư, bộ não, hai suy nghĩ trong hộp xanh / đỏ | Cơ chế trong đầu, giằng co | **loi, suy_nghi_1**, suy_nghi_2 (""), dao_cu (`dao-cu/bo-nao.png`), tre_1, tre_2 | `{"suy_nghi_1": "SELL", "suy_nghi_2": "WAIT"}` |
| `meo-tranh` | cach-tranh · Max chỉ tay, bóng đèn + ding, "TIP #n" + gạch đầu dòng | Mỗi cách tránh | **loi, meo**, nhan (`TIP #1`), dao_cu (`dao-cu/bong-den.png`), tre_meo | `{"nhan": "TIP #2", "meo": "RULES BEFORE BUYING"}` |
| `tom-tat` | tom-tat · nháy đen, "QUICK RECAP", 3 từ khoá ngang | 1–2 cảnh tóm tắt | **loi, y_1, y_2**, y_3 (""), tieu_de, tre_1/2/3 | `{"y_1": "LOSSES FEEL BIGGER", "y_2": "WE HOLD LOSERS"}` |
| `mien-tru` | ket · NOT FINANCIAL ADVICE + "Do your own research." | Bắt buộc khi nói về tiền / đầu tư | (không bắt buộc) loi = câu miễn trừ chuẩn docs/05, chu, chu_phu | `{}` |
| `ket-keu-goi` | ket · Max chỉ tay về SUBSCRIBE, `zoom-ra`, trộn mờ | Cảnh cuối, CTA ≤ 6 s | **loi**, chu (`SUBSCRIBE`), chu_phu (""), tre_chu | `{"chu_phu": "NEXT: SUNK COST"}` |

Ghi chú bố cục: nhân vật toàn cảnh `co` 0,55–0,7 chạm đáy; chữ nằm trong vùng an toàn (y 0,12–0,8); `hai-lua-chon`, `so-sanh-truoc-sau`, `noi-tam`, `ten-khai-niem` được 2 chữ trong một cảnh (cặp đối / tên + định nghĩa) — các khuôn khác ≤ 1 chữ khoá.

Ảnh mới ngoài danh sách docs/04: **`dao-cu/vach-chia.png`** (vạch chia đôi màn hình) — prompt khuôn đạo cụ docs/04 mục 6 với `{OBJECT}` = `single thick vertical hand-drawn black line, slightly wobbly, no fill`, ảnh dọc 1:2.

## 3. Làm video chủ đề mới trong 3 bước

1. **Chép khung**: `nq moi <slug>` rồi thay `du-an/<slug>/kich-ban.json` bằng nội dung `templates/kich-ban-khung.json` (hoặc gọi `/kich-ban <chủ đề>` — lệnh ưu tiên khuôn). Đổi `tieu_de`, `tham_so_chung.khai_niem`, `thumbnail` (nếu có).
2. **Viết lời theo phần**: giữ thứ tự và `_phan_bo` của khung (hook ≤ 15 s → bối cảnh → ví dụ Max → giải thích → nghiên cứu → Max quay lại → cách tránh → tóm tắt → kết). Mỗi cảnh: sửa `loi` + chữ trong `tham_so`; chọn khuôn khác nếu ý khác (bảng mục 2). Nhân bản cảnh tới ~150 cảnh / ~1.550 từ (khung có 48 cảnh mẫu); mỗi cảnh đổi ít nhất một trong biểu cảm / tư thế / đạo cụ / khuôn. Mọi nghiên cứu phải đối chiếu bài gốc (docs/05 mục 4).
3. **Kiểm và dựng**: `nq dung <slug> --nhap` (khuôn được triển khai khi `kichban.nap_kich_ban` nạp kịch bản — cần đã nối `trien_khai` vào hàm này; lỗi tham số in rõ cảnh nào) → `nq kiem-nhip <slug>` → bổ sung ảnh còn thiếu theo docs/04 → `nq dung <slug>`.

## 4. Thêm khuôn mới

Tạo `templates/khuon-canh/<ten-moi>.json` (chữ thường, `-`):

```json
{"_mo_ta": "…bố cục…", "_dung_khi": "…",
 "_tham_so": {"loi": {"bat_buoc": true, "mo_ta": "…", "vi_du": "…"},
              "chu": {"mac_dinh": "", "mo_ta": "…"}},
 "canh": {"phan": "vi-du", "loi": "{{loi}}", "may_quay": "zoom-cham", "lop": [], "chu": [{"noi_dung": "{{chu}}"}]}}
```

Mọi chỗ trống phải khai trong `_tham_so`; tham số bắt buộc phải có `vi_du` (test `tests/test_khuon_canh.py` triển khai mọi khuôn bằng `mac_dinh` / `vi_du` rồi chạy `kiem_kich_ban`). Không đặt `id` trong khuôn.
