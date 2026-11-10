# Hình tạm & thumbnail

Hai module chỉ dùng Pillow + numpy (không thêm thư viện):

| Module | Hàm | Việc |
|---|---|---|
| `nguoique/hinh_tam.py` | `tao_bo_hinh_tam(kho, ghi_de=False) -> list[Path]` | Vẽ bộ người que TẠM + SFX TẠM vào `kho-mau/` để làm video đầu tiên khi chưa có ảnh Gemini |
| `nguoique/thumbnail.py` | `tao_thumbnail(cau_hinh_thumb, ra, kho, font_path) -> Path` | Thumbnail PNG 1280x720 từ khoá `thumbnail` trong `kich-ban.json` |

## 1. Bộ hình tạm (`nq hinh-tam`)

```
nq hinh-tam            # chỉ tạo tệp còn thiếu, rồi tự lập lại danh mục kho (như `nq kho`)
nq hinh-tam --ghi-de   # vẽ lại tất cả (đè cả ảnh thật cùng tên — cẩn thận)
```

**Tên tệp dùng đúng mã tiếng Việt không dấu của [docs/04](04-TAO-ANH-GEMINI.md)** (bảng 3, 4, 6, 7) — nên ảnh Gemini cùng tên thay thế được ảnh tạm, và mọi tệp `templates/kich-ban-mau.json` tham chiếu đều có (trừ nhạc nền `nhac-nen/curious-light.mp3`: tự tải từ YouTube Audio Library, thiếu thì dựng không nhạc).

Tạo ra (PNG nền trong suốt 1024x1024, nét đen dày, đầu tròn trắng, vẽ 2x rồi thu nhỏ):

- `nhan-vat/max__<bieu-cam>__<tu-the>.png` — 16 biểu cảm × 7 tư thế = 112 tệp
  - biểu cảm: `vui, tham-lam, so-hai, hoang-loan, hoi-han, tu-tin, boi-roi, soc, suy-nghi, buon, gian, nhe-nhom, dac-y, lo-lang, hao-hung, chan`
  - tư thế: `dung` (đứng), `chi-tay` (chỉ sang phải — dùng `"lat": true` để chỉ sang trái), `om-dau`, `ngoi`, `ngoi-may-tinh` (ngồi, bàn + laptop bên phải), `cam-dien-thoai` (điện thoại có biểu đồ, tay phải), `di-bo` (bước sang phải)
- Nhân vật phụ (kiểu dáng Max + dấu nhận dạng):
  - `chuyen-gia__<bc>__<tt>.png` (kính tròn + nơ đỏ): biểu cảm `tu-tin, vui, suy-nghi, boi-roi, soc, lo-lang` × tư thế `dung, chi-tay`
  - `ban__<bc>__<tt>.png` (chỏm tóc 3 nét): `vui, tham-lam, so-hai, buon, hoi-han` × `dung, chi-tay`
  - Đám đông 16:9 (1024x576, 7 người): `dam-dong__hao-hung__chay`, `dam-dong__hoang-loan__bo-chay` (chạy sang trái), `dam-dong__soc__nhin-len`
- `dao-cu/`: `tien, bao-tien, dong-xu, co-phieu-xanh, co-phieu-do, bo-nao, can, can-lech, dong-ho, dong-ho-cat, bong-den, dau-hoi, may-tinh, dien-thoai, mui-ten-len, mui-ten-xuong` (.png)
- `bieu-do/`: `tang` (xanh), `giam` (đỏ), `giam-manh` (lên rồi lao xuống đỏ), `tang-giam` (đoạn lên xanh, đoạn xuống đỏ), `cot-tang` (5 cột) — có trục + mũi tên
- `phong-nen/van-phong.png` (1920x1080, nét xám mảnh trên nền trắng ngà, không trong suốt)
- `am-thanh/` (wav 16-bit mono 48 kHz, tổng hợp bằng numpy): `pop, whoosh, ding, tick, cash, buzz`

Muốn thêm tổ hợp nhân vật phụ: sửa `NHAN_VAT_PHU` / `DAM_DONG` trong `nguoique/hinh_tam.py`.

Tệp đã có được giữ nguyên, nên khi thay dần bằng ảnh Gemini cùng tên thì chạy lại lệnh không mất ảnh thật.
Ảnh tạm chỉ để chạy thử luồng / video đầu — đủ rõ cảm xúc nhưng đơn giản; nên thay bằng ảnh Gemini (`docs/04-TAO-ANH-GEMINI.md`) trước khi đăng đều.

Ví dụ dùng trong cảnh (`co` = bề rộng ảnh / bề rộng khung; ảnh vuông 1024 nên `co` 0.18–0.24 là cỡ nhân vật vừa):
```json
{"anh": "nhan-vat/max__hoang-loan__om-dau.png", "vi_tri": [0.3, 0.86], "neo": "day", "co": 0.2, "hieu_ung": "bat-len", "lien_tuc": "run", "am_thanh": "am-thanh/pop.wav"}
```

## 2. Thumbnail (`nq thumbnail <du-an>`)

Đọc khoá `thumbnail` trong `du-an/<ten>/kich-ban.json` (khoá thêm: lõi không kiểm, không cảnh báo), ghi `du-an/<ten>/thumbnail.png` (hoặc `--ra <tệp.png>`). Không có khoá `thumbnail` → dùng `{"chu": tieu_de}` (thường quá dài — nên tự viết). `templates/kich-ban-mau.json` có sẵn ví dụ.

```jsonc
"thumbnail": {
  "nen": "#FFD54F",                       // mã màu hoặc ảnh (phong-nen/...), cắt phủ kín khung
  "chu": "YOU SELL *TOO EARLY*",          // *...* = chữ nhấn (màu mau_nhan)
  "mau_chu": "#111111", "mau_nhan": "#E53935",
  "mau_vien": "#FFFFFF", "vien": null,    // viền chữ px (ở 1280x720); null = tự tính
  "bong": true,                           // bóng đổ dưới chữ
  "vi_tri_chu": [0.32, 0.5], "rong_chu": 0.58, "can_le": "giua",   // tuỳ chọn; mặc định tự né nhân vật
  "nhan_vat": [{"anh": "nhan-vat/max__soc__dung.png", "vi_tri": [0.75, 0.6], "co": 0.8, "lat": false}],
  "mui_ten": {"tu": [0.5, 0.5], "den": [0.7, 0.4], "mau": "#E53935", "day": 0.022},
  "khoanh_tron": {"tam": [0.75, 0.4], "ban_kinh": 0.15, "mau": "#E53935"}
}
```
- Toạ độ 0..1 theo khung. `co` = chiều cao nhân vật / chiều cao khung (ảnh tự cắt sát phần trong suốt).
- Tối đa 2 nhân vật; ảnh thiếu thì bỏ qua + cảnh báo. Đường dẫn tìm trong `kho-mau/` rồi thư mục dự án.
- Cỡ chữ tự chọn lớn nhất vừa vùng (≤ 3 dòng). Font: tham số → `C:/Windows/Fonts/arialbd.ttf` → font mặc định Pillow.
- `mui_ten` / `khoanh_tron` nhận một object hoặc danh sách.

## 3. Nguyên tắc thumbnail cho kênh tâm lý

1. **Một cảm xúc rõ** — chọn đúng một: sốc, hối hận, tham, sợ. Mặt nhân vật phải đọc được ở cỡ tem (≈ 160px rộng): dùng `soc`, `hoang-loan`, `hoi-han`, `tham-lam` thay vì `suy-nghi`.
2. **≤ 5 từ, thường 2–4** — không lặp lại tiêu đề, mà bổ sung cho nó (tiêu đề "Why You Sell Winners Too Early" → thumbnail "*TOO EARLY*?"). Nhấn 1–2 từ mang cảm xúc / con số.
3. **Tương phản mạnh** — nền một màu sáng phẳng (vàng `#FFD54F`, cam, xanh nhạt) + chữ đen viền trắng + nhấn đỏ; hoặc nền tối + chữ trắng + nhấn vàng. Không quá 3 màu chính. Thử thu nhỏ còn 20% xem còn đọc được không.
4. **Bố cục 2 khối** — chữ một bên, nhân vật lớn bên kia (cao ≥ 60% khung). Tránh góc dưới phải (YouTube đè thời lượng video).
5. **Một điểm dẫn mắt** — mũi tên hoặc khoanh tròn vào chi tiết gây tò mò (biểu đồ lao xuống, túi tiền), không dùng cả hai cùng lúc nếu rối.
6. **Nhất quán kênh** — cùng nhân vật Max, cùng font, cùng bảng màu để người xem nhận ra kênh; đổi màu nền theo chủ đề (đỏ = mất tiền, xanh = cách tránh).
7. **Trung thực** — không hứa điều video không có (YouTube phạt clickbait sai lệch, kênh tài chính càng phải cẩn thận).

## 4. Nối lệnh (đã làm)

`nguoique/cli.py` đã có `nq hinh-tam [--ghi-de]` (gọi `hinh_tam.tao_bo_hinh_tam(kho_mau(ch), ghi_de)` rồi `kho.lap_danh_muc`) và `nq thumbnail <du-an> [--ra <tệp>]` (đọc `kich-ban.json` thô để giữ khoá `thumbnail`, font = `phu_de.font` trong `config.yaml`). Cả hai import lười.
