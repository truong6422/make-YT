# 10 — Nhân vật ghép bộ phận, máy quay theo mốc, lớp thương hiệu, hộp phụ đề

Mục tiêu: nhân vật cử động mượt, không khựng, như kênh tham khảo đo được (`02-KHUON-PHONG-CACH.md` mục 10–11, `phan-tich/video-01.md`, `video-05.md`): **cut-out** (thân + đầu đứng, tay xoay quanh vai), cử động **0,6–0,8 s ease-out**, hoạt hình **12–15 hình/giây** trên video 30 fps, miệng 2–3 hình, mắt thay hình.

Mã: `nguoique/nhan_vat_ghep.py` (rig, tư thế, hoạt cảnh — hàm thuần), `nguoique/dung_hinh.py` (vẽ), `nguoique/kichban.py` (kiểm khoá), `nguoique/hinh_tam.py` (`tao_nhan_vat_ghep_tam`). Kịch bản cũ (lớp `anh` tĩnh) chạy y như trước.

## 1. Thư mục một nhân vật

```
kho-mau/nhan-vat-ghep/<ten>/
  khung.json
  than.png  dau.png
  tay-trai-tren.png  tay-trai-duoi.png  tay-phai-tren.png  tay-phai-duoi.png
  chan-trai-tren.png chan-trai-duoi.png chan-phai-tren.png chan-phai-duoi.png
  mat/<bieu-cam>.png          mắt + lông mày + ký hiệu (mồ hôi, hơi giận…) của biểu cảm
  mat/<bieu-cam>__nham.png    (tuỳ chọn) mắt nhắm khi chớp của biểu cảm đó
  mat/nham.png                mắt nhắm chung (dự phòng)
  mieng/<bieu-cam>.png        (tuỳ chọn) miệng khi im của biểu cảm
  mieng/dong.png  mieng/ha-nho.png  mieng/ha-to.png   miệng khi nói
```
`nq hinh-tam` tạo sẵn người que tạm cho `max`, `chuyen-gia`, `ban` (đủ 16 biểu cảm hiện có + mắt nhắm + 3 miệng). Ảnh Gemini cùng tên thay được từng tệp.

Quy ước (quan trọng khi vẽ / sửa):
- Trái / phải **theo người xem**. `tay-phai` = tay bên phải khung hình.
- Vẽ mỗi bộ phận ở **góc 0**: tay, chân buông **thẳng đứng xuống**, khớp ở đầu trên; thân thẳng đứng; đầu thẳng. Hai đầu mỗi đoạn có **đầu tròn** (bằng nửa nét) để xoay không hở khớp.
- Góc: độ, **dương = ngược chiều kim đồng hồ** trên màn hình. Góc con là góc **tương đối** với cha. Ví dụ `tay-phai-tren: 100` = tay phải giơ ngang chỉ sang phải.
- Lớp mặt (`mat/…`, `mieng/…`) mặc định **cùng cỡ với `dau.png`**, chồng khít góc trên trái, xoay theo đầu.

## 2. `khung.json`

```jsonc
{
  "ten": "max",
  "kich_thuoc": [1024, 1024],          // khung tham chiếu = cỡ ảnh nhân vật tĩnh -> 'co' dùng như lớp ảnh
  "bieu_cam": "vui",                   // biểu cảm khi lớp không ghi
  "cham_dat": ["chan-trai-duoi", "chan-phai-duoi"],  // bộ phận có 'dau_mut' = bàn chân: giữ chân chạm đất (đi bộ tự nhún)
  "mat": {"bo_phan": "dau", "khop": [0, 0], "gan": [0, 0]},   // điểm 'khop' của ảnh mặt đặt vào điểm 'gan' của ảnh đầu
  "mieng": null,                       // không ghi = như "mat"
  "bo_phan": [
    {"ten": "than", "tep": "than.png", "cha": null, "khop": [13, 313], "gan": [512, 680], "lop": 2, "goc": 0},
    {"ten": "dau", "tep": "dau.png", "cha": "than", "khop": [210, 320], "gan": [13, 13], "lop": 3, "goc": 0},
    {"ten": "tay-phai-tren", "tep": "tay-phai-tren.png", "cha": "than", "khop": [13, 13], "gan": [13, 73], "lop": 4, "goc": 28},
    {"ten": "chan-phai-duoi", "tep": "chan-phai-duoi.png", "cha": "chan-phai-tren", "khop": [13, 13], "gan": [13, 153],
     "lop": 1, "goc": 0, "dau_mut": [13, 162]}
    // ...
  ],
  "tu_the": {"chao-kieu-rieng": {"tay-phai-tren": 140, "tay-phai-duoi": 20}}   // thêm / ghi đè tư thế cho riêng nhân vật
}
```
| Khoá bộ phận | Nghĩa |
|---|---|
| `ten` | tên bộ phận (dùng trong tư thế) |
| `tep` | PNG trong thư mục nhân vật |
| `cha` | bộ phận cha; `null` = gốc cây (một gốc là đủ) |
| `khop` | điểm xoay **trong ảnh của chính nó** (px) |
| `gan` | điểm gắn khớp **trong ảnh của cha** (px); gốc cây: vị trí trong khung `kich_thuoc` |
| `lop` | thứ tự vẽ (nhỏ vẽ trước); mặt / miệng vẽ ngay trên bộ phận mang nó |
| `goc` | góc mặc định khi tư thế không nhắc tới |
| `dau_mut` | (tuỳ chọn) điểm mút, dùng cho `cham_dat` |

Sai khung.json → cảnh báo tiếng Việt, vẽ ô giữ chỗ (luồng vẫn chạy).

## 3. Lớp nhân vật ghép trong kịch bản

Trong `canh.lop`, lớp có khoá `nhan_vat` (thay cho `anh`):
```jsonc
{"nhan_vat": "max", "vi_tri": [0.3, 0.86], "neo": "day", "co": 0.22,
 "bieu_cam": "lo-lang", "tu_the": "dung",
 "dong_tac": [{"tu_the": "chi-tay-phai", "luc": 1.2, "thoi_luong": 0.7, "easing": "ra"},
              {"bieu_cam": "soc", "luc": 2.0}],
 "chop_mat": true, "noi": true,
 "di": {"tu": [0.2, 0.86], "den": [0.6, 0.86], "luc": 0.5, "thoi_luong": 2.0, "chu_ky": 1.0},
 "nhip_hinh": 15,
 "hieu_ung": "khong", "tre": 0, "lien_tuc": "khong", "het": null, "lat": false, "am_thanh": null}
```
| Khoá | Mặc định | Nghĩa |
|---|---|---|
| `nhan_vat` | — | thư mục `kho-mau/nhan-vat-ghep/<ten>/` (hoặc cùng đường dẫn trong thư mục dự án) |
| `co` | 0,3 | bề rộng khung tham chiếu / bề rộng khung hình (như ảnh tĩnh 1024²) |
| `neo` | `giua` | `day` = **mặt đất** (bàn chân ở tư thế đứng) đặt tại `vi_tri` y |
| `bieu_cam` | `khung.json` | mã biểu cảm (`docs/04` bảng 3) → `mat/<ma>.png` |
| `tu_the` | `dung` | tư thế đầu cảnh |
| `dong_tac` | `[]` | mốc trong cảnh (giây, tính từ đầu cảnh): `tu_the` nội suy trong `thoi_luong` (0,7) với `easing`; `bieu_cam` đổi ngay tại `luc` (thay hình). Một mốc ghi được cả hai |
| `easing` | `ra` | `ra` = ease-out (cubic), `vao-ra` = ease-in-out, `nay` = ease-out-back (vượt nhẹ rồi về) |
| `chop_mat` | `true` | chớp tự động mỗi 2,5–5 s, nhắm 0,12 s; ngẫu nhiên cố định theo id cảnh + thứ tự lớp |
| `noi` | `false` | mở miệng theo giọng của cảnh (mục 4) |
| `di` | — | đi bộ: tịnh tiến `tu` → `den` từ `luc` trong `thoi_luong`, lặp `di-bo-1..4` (`chu_ky` giây / 4 hình), trộn vào/ra 0,2 s, nhún tự nhiên nhờ `cham_dat`; đi sang trái tự lật gương. Có `di` thì `vi_tri` mặc định = `tu` |
| `nhip_hinh` | gốc `nhip_hinh` → 15 | số lần cập nhật tư thế / giây (kiểu vẽ tay); `0` = mượt theo fps. Máy quay luôn 30 fps |
| `hieu_ung`, `tre`, `het`, `lat`, `am_thanh` | như lớp ảnh | |
| `lien_tuc` | `khong` | `nhun`, `run` như lớp ảnh; `lac` = đầu lắc ±4°; `tho` = đầu và vai nhích ±1–1,5° chu kỳ 3,2 s |

Khoá gốc `nhip_hinh` (số, 0..60) đặt nhịp chung cho mọi nhân vật ghép của video.

**Thư viện tư thế** (`TU_THE_GHEP`): `dung`, `chi-tay-phai`, `chi-tay-trai`, `om-dau`, `gio-hai-tay`, `nhun-vai`, `khoanh-tay`, `vay-tay` (cẳng tay phải tự vẫy ±18°, 0,5 s), `suy-nghi-tay-cam`, `di-bo-1..4` (hướng sang phải). Tư thế lạ → cảnh báo khi nạp kịch bản, vẽ `dung` nếu `khung.json` cũng không có.

## 4. Khớp miệng

- `dung_video(..., bao_giong=None)`: tự tính cho cảnh có lớp `noi: true` — đọc `ds[i]["giong"]` bằng `am_thanh_io.giai_ma` (16 kHz) → RMS mỗi 1/15 s. Có thể truyền sẵn `bao_giong={id cảnh: np.ndarray}`.
- Ngưỡng theo mức tham chiếu (phân vị 90 các ô có tiếng): < 0,18 → `dong`, < 0,55 → `ha-nho`, còn lại `ha-to`; **mỗi hình giữ tối thiểu 0,15 s** cho đỡ giật.
- Không có bao giọng (thiếu ffmpeg, đọc lỗi) nhưng cảnh có giọng: mở–đóng theo **chu kỳ 0,56 s** (đo video 03/04 — kênh không khớp từng âm).
- Khi không nói: `mieng/<bieu-cam>.png`, không có thì `mieng/dong.png`.

## 5. Máy quay, thương hiệu, phụ đề

**Máy quay theo mốc** (đổi khung toàn → cận không cắt):
```json
"may_quay": {"kieu": "zoom-cham", "muc": 0.03,
             "moc": [{"luc": 0, "zoom": 1.0, "tam": [0.5, 0.5]},
                     {"luc": 2.4, "zoom": 1.35, "tam": [0.3, 0.6], "thoi_luong": 0.8, "easing": "vao-ra"}]}
```
Mốc đầu là trạng thái ban đầu (`thoi_luong` 0); mốc sau mặc định 0,8 s `vao-ra`. `zoom` 1..4, `tam` 0..1. `kieu` (nếu ghi) cộng thêm lên mốc.

**Máy quay cầm tay**: `"may_quay": "lac-tay"` (lệch ngang ±0,6 % khung, chu kỳ 2,4 s — đo video 03/04), hoặc cộng lên kiểu khác: `{"kieu": "zoom-cham", "lac_tay": true}`.

**Hiệu ứng vào `bay-luon`** (lớp ảnh / chữ): lướt vào theo cung cong từ dưới phải trong 0,6 s, ease-out không vượt đích. `truot-*` nay 0,4 s ease-out (đo 270–600 ms).

**Lớp thương hiệu cố định cả video** (khoá gốc, vẽ sau máy quay và chuyển cảnh, trước phụ đề):
```json
"thuong_hieu": {"anh": "logo/kenh.png", "vi_tri": [0.94, 0.06], "co": 0.06, "do_mo": 0.8}
```
`vi_tri` = tâm logo; `co` = **chiều cao** logo / chiều cao khung (khác lớp ảnh); `do_mo` = độ hiện 0..1 (0,8 = đục 80 %). Có thể là danh sách nhiều mục.

**Hộp nền phụ đề** (config `phu_de`, lõi chỉ đọc; mặc định không có hộp): `hop_nen: "#000000"`, `do_duc_hop: 0.75`, `giu_hop_khi_lang: false` (true = hộp rộng ≥ 80 % khung, vẫn hiện khi không có lời — như video #1).

Cắt cảnh và `toi-den` 0,15–0,3 s giữ nguyên như cũ.

## 6. Hiệu năng (Ryzen 5500U, mục tiêu ≤ 60 ms/khung 1080p với 2 nhân vật)

- Mỗi bộ phận: thu theo tỉ lệ một lần, **xoay đệm theo góc lượng tử 1°** (LRU 1500 ảnh / nhân vật). Nhịp 15 hình/s → nửa số khung không phải tính lại tư thế; ảnh xoay trùng góc lấy từ đệm.
- Dán thẳng từng bộ phận lên khung (không tạo ảnh trung gian), trừ lúc mờ dần (`mo-dan`, `het`) mới ghép vào một ảnh bao cho khớp không đậm.
- `bat-len` / `phong-to` lượng tử tỉ lệ 4 % để đệm trúng.
- Chưa đo trên máy thật (máy viết code không có Python) — chạy `pytest tests/test_nhan_vat_ghep.py -k hieu_nang` trên máy Acer để xem số ms.

## 7. Tạo bộ phận bằng Gemini (nền trắng, mỗi bộ phận một ảnh)

Theo quy tắc chung `04-TAO-ANH-GEMINI.md` mục 1 (nền trắng tinh, không bóng, không chữ), **đính kèm ảnh gốc Max** mỗi lần. Tạo từng bộ phận riêng, rồi `nq tach-nen` → `kho-mau/nhan-vat-ghep/max/`.

Đầu (không mặt — mặt là lớp riêng):
```text
Using the attached reference image of Max, draw ONLY his head: the same head shape, light peach skin, short black hair with the same black cowlick tuft, same thick black outline, completely blank face (no eyes, no mouth, no eyebrows, no blush). No neck, no hoodie. Head centered, upright, generous empty margin around it (the head fills about half of the image width).
Flat 2D, no shading, no shadow. Pure white background (#FFFFFF). No text. Square 1:1 image.
```
Tay / chân / thân (một đoạn):
```text
Using the attached reference image of Max, draw ONLY his {PART}, as a separate cut-out piece for puppet animation: perfectly vertical and straight, same colors, same thick black outline, rounded ends so it can rotate at the joint. Nothing else in the image. Centered, generous margin.
Pure white background (#FFFFFF). No shading, no text. Tall portrait image 1:3.
```
`{PART}`: `upper arm in the orange hoodie sleeve` / `forearm in the orange hoodie sleeve ending in a simple peach mitten hand` / `thigh in navy pants` / `lower leg in navy pants ending in a teal shoe seen from the front` / `torso in the orange hoodie, no arms, no head, no legs`.

Mắt theo biểu cảm (cùng khung với đầu, để chồng khít):
```text
Using the attached head image, draw ONLY the facial features for this expression: {EXPRESSION} — eyes and eyebrows only (plus sweat drop / tear if the expression has one), placed exactly where they would sit on that head. Do NOT draw the head or hair, do NOT draw a mouth. Big round white eyes with black outline and solid black pupils, thick black eyebrows, flat pink blush only if the expression is embarrassed. Same thick black flat line style.
Pure white background (#FFFFFF). No text. Same size and framing as the attached head image.
```
Miệng: như trên nhưng `ONLY the mouth: {closed straight line | small open oval | wide open oval with a little red tongue}`; mắt nhắm: `ONLY two closed eyes drawn as short horizontal lines`.

Sau khi tách nền: mở ảnh, đo toạ độ khớp (px) bằng trình xem ảnh bất kỳ, ghi vào `khung.json` (chép khung của bộ tạm `nq hinh-tam` rồi sửa số). Ảnh mặt phải cùng cỡ ảnh đầu (cắt cùng khung), nếu không thì khai `mat.khop` / `mat.gan`.

## 8. Ví dụ trong `templates/kich-ban-mau.json`

c02 (chỉ tay vào chữ khoá), c07 (chuyên gia nói + chỉ tay), c09 (đổi biểu cảm hào hứng → sốc → hoảng loạn ôm đầu), c10 (Max đi bộ vào khung rồi chỉ tay).
