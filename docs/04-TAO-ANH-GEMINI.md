# 04 — Tạo kho hình bằng Gemini (bản web, miễn phí)

Mọi hình trong video (nhân vật, đạo cụ, biểu đồ, nền) tạo tay bằng **Gemini bản web** (`gemini.google.com`, tài khoản Google thường), không dùng API trả phí. Ảnh tải về → tách nền bằng `nq tach-nen` → vào `kho-mau/` → `nq kho` cập nhật danh mục.

Prompt viết bằng **tiếng Anh** (Gemini hiểu tốt hơn, và giữ đồng nhất). Chép nguyên khối trong ô code.

---

## 1. Quy tắc chung cho mọi ảnh

| Quy tắc | Lý do |
|---|---|
| **Nền trắng tinh** (`pure white background, #FFFFFF`) — trừ ảnh nền cảnh | `nq tach-nen` loang từ viền ảnh để xoá nền trắng; nền xám / có vân sẽ tách bẩn |
| **Không bóng đổ, không gradient, không vân giấy** | Bóng nối nhân vật với nền → tách nền lẹm vào nhân vật |
| **Không chữ trong ảnh** (no text, no letters, no numbers, no watermark) | Chữ do máy dựng thêm bằng tiếng Anh; chữ Gemini vẽ hay sai chính tả |
| Tỷ lệ **1:1** cho nhân vật / đạo cụ / biểu đồ; **16:9** cho nền cảnh | Khớp khung 1920×1080 |
| Một ảnh = một chủ thể, đứng giữa, chừa lề quanh | Dễ cắt sát, dễ đặt vị trí |
| Nét đen đều, dày, phẳng, tối giản | Giữ một phong cách cho cả kênh |
| Nhân vật **viền kín** (đầu tròn trắng có viền đen khép kín) | `tach-nen` giữ được phần trắng bên trong đầu |

Nếu ảnh ra nền hơi xám / có bóng: gửi lại câu *"Same image, but pure flat white background, no shadow, no texture."*

---

## 2. Bản gốc nhân vật Max (làm ĐẦU TIÊN)

Max là nhân vật chính, xuất hiện ở hầu hết cảnh. Phải có **một ảnh gốc** chuẩn rồi mọi ảnh sau đều dựa vào nó.

### Bước 2.1 — Tạo bản gốc

Mở cuộc trò chuyện mới, gửi:

```text
Create a character reference image for a minimalist stick figure named Max.
Style: flat 2D vector-like line art, uniform thick black outlines (same stroke width everywhere), no shading, no gradients, no shadows, no texture.
Max has a perfectly round white head with a thick black outline, two small solid black dot eyes, a simple curved line mouth, no hair, no nose, no ears.
Body: simple single black stick lines for torso, arms and legs, rounded line ends, no hands detail (just line ends), no clothes.
Pose: standing straight, facing the viewer, arms relaxed at the sides, neutral calm expression.
Full body visible, centered, with generous empty margin around.
Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark, no border.
Square 1:1 image.
```

Tạo vài lần, chọn bản ưng nhất (đầu tròn đều, nét đều, tỷ lệ đầu / thân dễ nhìn). Lưu thành `kho-mau/_cho-xu-ly/max__goc__dung.png` và **giữ thêm một bản riêng** (vd. `max-goc.png` trên máy) làm ảnh tham chiếu.

### Bước 2.2 — LUÔN đính kèm ảnh gốc khi tạo ảnh mới của Max

Mỗi biểu cảm / tư thế mới: bấm nút đính kèm (➕ / tải ảnh lên), chọn ảnh gốc Max, rồi gửi prompt theo khuôn dưới. Không đính kèm → Gemini vẽ ra nhân vật khác (đầu méo, nét khác, thêm tóc…).

Mẹo:
- Có thể làm nhiều ảnh trong **cùng một cuộc trò chuyện**, nhưng vẫn đính kèm lại ảnh gốc mỗi lần — lâu dần Gemini "trôi" phong cách.
- Ảnh ra lệch phong cách → bỏ, tạo lại; đừng dùng ảnh lệch làm tham chiếu tiếp.
- Biểu cảm thể hiện chủ yếu bằng **mắt, miệng, lông mày đơn giản và dáng người** — giữ tối giản.

### Khuôn prompt cho Max (thay 2 chỗ `{...}`)

```text
Using the attached reference image, draw the SAME character Max: identical round white head with thick black outline, same dot eyes, same uniform thick black stick-line body, same proportions and stroke width. Keep the exact same minimalist flat style.
Expression: {EXPRESSION}.
Pose: {POSE}.
Full body visible, centered, generous empty margin. No shading, no shadows, no gradients.
Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark.
Square 1:1 image.
```

---

## 3. Bảng biểu cảm (16) — dán vào `{EXPRESSION}`

| Mã tệp | Tiếng Anh | Câu dán vào `{EXPRESSION}` |
|---|---|---|
| `vui` | happy | `happy, big simple smile, eyes slightly curved` |
| `tham-lam` | greedy | `greedy, wide hungry grin, eyes shining with small sparkles, leaning forward eagerly` |
| `so-hai` | fearful | `fearful, eyes wide, small open wavy mouth, body slightly shrinking back` |
| `hoang-loan` | panicked | `panicked, eyes huge, mouth wide open screaming, a few small sweat drops flying off the head` |
| `hoi-han` | regretful | `regretful, eyes looking down, sad downturned mouth, slumped shoulders` |
| `tu-tin` | confident | `confident, slight smirk, chin up, chest out` |
| `boi-roi` | confused | `confused, one eyebrow raised, squiggly mouth, head tilted` |
| `soc` | shocked | `shocked, eyes extremely wide, mouth a big round O, a few short motion lines around the head` |
| `suy-nghi` | thinking | `thinking, eyes looking up to the side, small flat mouth, one hand touching the chin` |
| `buon` | sad | `sad, droopy eyes, downturned mouth, one small tear` |
| `gian` | angry | `angry, slanted eyebrows, gritted teeth line, small steam puffs above the head` |
| `nhe-nhom` | relieved | `relieved, eyes closed, gentle smile, small exhale puff near the mouth` |
| `dac-y` | smug | `smug, half-closed eyes, one-sided smirk, arms crossed` |
| `lo-lang` | anxious | `anxious, worried eyebrows, wobbly mouth, one sweat drop on the head` |
| `hao-hung` | excited | `excited, sparkling eyes, huge open smile, arms raised` |
| `chan` | bored | `bored, half-closed eyes, flat straight mouth, head resting heavily` |

Ghi chú: biểu cảm có tư thế riêng trong câu (vd. `arms crossed`, `arms raised`) có thể xung đột với `{POSE}` — khi đó ưu tiên `{POSE}` và bỏ phần tư thế trong câu biểu cảm.

## 4. Bảng tư thế (6) — dán vào `{POSE}`

| Mã tệp | Tiếng Anh | Câu dán vào `{POSE}` |
|---|---|---|
| `dung` | standing | `standing, facing the viewer, arms relaxed` |
| `ngoi-may-tinh` | sitting at desk with laptop | `sitting on a simple chair at a simple desk, looking at an open laptop on the desk, desk and laptop drawn in the same thick black line style` |
| `chi-tay` | pointing | `standing and pointing to the right side with one arm fully extended, as if presenting something` |
| `di-bo` | walking | `walking to the right, side view, one leg forward, arms swinging` |
| `cam-dien-thoai` | holding phone with chart | `standing, holding a smartphone in front of the face, the phone screen shows a simple line chart (no numbers, no text)` |
| `om-dau` | head in hands | `standing with both hands holding the head, elbows out` |

Tổ hợp đầy đủ 16 × 6 = 96 ảnh — **không cần làm hết**. Làm theo nhu cầu kịch bản (`/kich-ban` liệt kê ảnh thiếu kèm prompt).

### Ví dụ prompt hoàn chỉnh

`max__lo-lang__cam-dien-thoai.png`:

```text
Using the attached reference image, draw the SAME character Max: identical round white head with thick black outline, same dot eyes, same uniform thick black stick-line body, same proportions and stroke width. Keep the exact same minimalist flat style.
Expression: anxious, worried eyebrows, wobbly mouth, one sweat drop on the head.
Pose: standing, holding a smartphone in front of the face, the phone screen shows a simple line chart (no numbers, no text).
Full body visible, centered, generous empty margin. No shading, no shadows, no gradients.
Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark.
Square 1:1 image.
```

---

## 5. Nhân vật phụ

Tạo bản gốc riêng cho từng nhân vật phụ (một lần), rồi cũng đính kèm bản gốc đó khi làm biểu cảm khác. Đính kèm **cả ảnh gốc Max** khi tạo bản gốc nhân vật phụ để cùng phong cách.

**Bạn của Max** — `nhan-vat/ban__<bieu-cam>__<tu-the>.png`
```text
Using the attached reference image of Max ONLY as a style reference, create a NEW minimalist stick figure character: Max's friend. Same flat style, same uniform thick black outlines, same round white head shape and stick body proportions. Distinguishing feature: a simple short spiky hair tuft drawn with three black lines on top of the head.
Expression: friendly smile. Pose: standing, facing the viewer, one hand waving.
Full body, centered, generous margin. No shading, no shadows.
Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark. Square 1:1 image.
```

**Chuyên gia** — `nhan-vat/chuyen-gia__<bieu-cam>__<tu-the>.png`
```text
Using the attached reference image of Max ONLY as a style reference, create a NEW minimalist stick figure character: an expert / professor. Same flat style, same uniform thick black outlines, same round white head and stick body. Distinguishing features: simple round glasses drawn as two black circles, and a simple bow tie.
Expression: calm, knowing smile. Pose: standing, holding a simple pointer stick, pointing to the right.
Full body, centered, generous margin. No shading, no shadows.
Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark. Square 1:1 image.
```

**Đám đông** — `nhan-vat/dam-dong__<bieu-cam>__<tu-the>.png` (vd. `dam-dong__hao-hung__chay.png`)
```text
In the same minimalist flat style as the attached reference image of Max (uniform thick black outlines, round white heads, stick bodies), draw a crowd of 7 simple stick figures, all identical in style but slightly different sizes, grouped together.
They are all {excited, running to the right in the same direction | panicked, running away to the left | standing and looking up at the same point}.
No shading, no shadows. Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark.
16:9 image.
```
(Chọn một vế trong `{...}`; mã tư thế tương ứng: `chay`, `bo-chay`, `nhin-len`.)

---

## 6. Đạo cụ — `dao-cu/<ten>.png`

Khuôn chung (thay `{OBJECT}`):

```text
A single {OBJECT}, drawn in a minimalist flat 2D line art style: uniform thick black outlines, flat fills only where stated, no shading, no gradients, no shadows, no texture.
Centered, generous empty margin. Pure white background (#FFFFFF). No text, no letters, no numbers, no symbols, no watermark. Square 1:1 image.
```

| Tệp | `{OBJECT}` |
|---|---|
| `tien.png` | `small stack of banknotes, flat light green fill` |
| `bao-tien.png` | `money bag tied at the top, flat light beige fill, no dollar sign` |
| `dong-xu.png` | `pile of three gold coins, flat yellow fill, plain faces` |
| `co-phieu-xanh.png` | `rounded rectangle card with a bold upward arrow, flat green fill (#2E7D32)` |
| `co-phieu-do.png` | `rounded rectangle card with a bold downward arrow, flat red fill (#E53935)` |
| `bo-nao.png` | `simple cartoon human brain, flat light pink fill` |
| `can.png` | `balance scale with two pans, perfectly level, no fill` |
| `can-lech.png` | `balance scale with two pans, left pan clearly lower than the right, no fill` |
| `dong-ho.png` | `round wall clock with two hands, no numbers on the face` |
| `dong-ho-cat.png` | `hourglass with sand, flat light yellow sand` |
| `bong-den.png` | `glowing light bulb with short rays around it, flat yellow fill` |
| `dau-hoi.png` | `big bold question mark shape, flat black fill` (riêng mục này cho phép dấu "?") |
| `may-tinh.png` | `simple open laptop seen from the front-side, plain blank screen` |
| `dien-thoai.png` | `smartphone, plain blank screen` |
| `mui-ten-len.png` | `bold upward arrow, flat green fill` |
| `mui-ten-xuong.png` | `bold downward arrow, flat red fill` |

Với `dau-hoi.png`, bỏ chữ `no symbols` trong khuôn.

## 7. Biểu đồ — `bieu-do/<ten>.png`

```text
A simple {CHART}, minimalist flat line art, uniform thick black axis lines with no tick labels, no numbers, no grid text, no title.
No shading, no shadows. Centered, generous margin. Pure white background (#FFFFFF). No text, no letters, no numbers, no watermark. Square 1:1 image.
```

| Tệp | `{CHART}` |
|---|---|
| `tang.png` | `line chart with one thick green line going steadily up from bottom-left to top-right` |
| `giam.png` | `line chart with one thick red line going steadily down` |
| `giam-manh.png` | `line chart with a thick line rising then crashing sharply down at the end, the crash part red` |
| `tang-giam.png` | `line chart with one thick black zigzag line, volatile ups and downs` |
| `cot-tang.png` | `bar chart with five green bars increasing in height left to right` |
| `nen-do-xanh.png` | `candlestick chart with about ten simple candles, green and red, overall upward trend` |

Số liệu / nhãn trục (nếu cần) do máy dựng thêm bằng lớp `chu` trong kịch bản.

## 8. Nền cảnh — `phong-nen/<ten>.png` (16:9)

Nền **không cần** tách nền; giữ nét mảnh, nhạt để nhân vật nổi lên trên.

```text
A minimalist background scene: {SCENE}.
Style: simple flat 2D line art with thin light gray outlines (#BDBDBD) on an off-white background, very sparse details, lots of empty space in the center and lower half for characters. No people, no characters, no shading, no shadows, no gradients.
No text, no letters, no numbers, no signs with writing, no logos, no watermark. Wide 16:9 image.
```

| Tệp | `{SCENE}` |
|---|---|
| `phong.png` | `a cozy living room with a sofa on the left and a window on the right` |
| `van-phong.png` | `an office with a desk, a computer monitor and a potted plant at the edges` |
| `san-giao-dich.png` | `a stock trading floor with a row of large blank screens on the back wall` |
| `duong-pho.png` | `a city street with a few simple buildings in the background and a sidewalk` |
| `phong-ngu.png` | `a bedroom at night with a bed and a window showing a moon` |
| `san-khau.png` | `an empty stage with simple curtains on both sides` |

---

## 9. Đặt tên tệp

- Nhân vật: `nhan-vat/<ten>__<bieu-cam>__<tu-the>.png` — vd. `max__hoang-loan__om-dau.png`
- Đạo cụ: `dao-cu/<ten>.png` · Biểu đồ: `bieu-do/<ten>.png` · Nền: `phong-nen/<ten>.png`
- Chữ thường, không dấu, nối bằng `-`, phần tách nghĩa bằng `__`. Dùng đúng mã ở bảng 3, 4 để `/kich-ban` tìm thấy.

## 10. Quy trình xử lý

1. Tạo ảnh trên Gemini → tải về (nút tải xuống, lấy bản kích thước đầy đủ).
2. Đổi tên theo mục 9, lưu vào `kho-mau/_cho-xu-ly/`.
3. Tách nền vào đúng thư mục (mỗi loại chạy riêng):
   ```powershell
   nq tach-nen kho-mau/_cho-xu-ly --ra kho-mau   # tự xếp: dao-cu__x -> dao-cu/, bieu-do__x -> bieu-do/, còn lại -> nhan-vat/
   ```
   Đạo cụ / biểu đồ: đổi `--ra kho-mau/dao-cu` hoặc `--ra kho-mau/bieu-do` (nên để mỗi loại một thư mục con trong `_cho-xu-ly/` rồi chạy theo từng thư mục). Nền cảnh **không tách nền** — chép thẳng vào `kho-mau/phong-nen/`.
4. Mở vài PNG kết quả kiểm: đầu Max vẫn trắng bên trong, viền không bị gặm. Hỏng → tạo lại ảnh với nền trắng sạch hơn.
5. Cập nhật danh mục:
   ```powershell
   nq kho
   ```
6. Xoá ảnh đã xử lý trong `_cho-xu-ly/`.

---

## 11. Bộ tối thiểu để làm video đầu tiên (~25 ảnh)

| # | Tệp | Ghi chú |
|---|---|---|
| 1 | `nhan-vat/max__goc__dung.png` | bản gốc, làm đầu tiên |
| 2 | `nhan-vat/max__vui__dung.png` | |
| 3 | `nhan-vat/max__tham-lam__cam-dien-thoai.png` | |
| 4 | `nhan-vat/max__so-hai__dung.png` | |
| 5 | `nhan-vat/max__hoang-loan__om-dau.png` | |
| 6 | `nhan-vat/max__hoi-han__dung.png` | |
| 7 | `nhan-vat/max__tu-tin__chi-tay.png` | dẫn chuyện / giải thích |
| 8 | `nhan-vat/max__boi-roi__dung.png` | |
| 9 | `nhan-vat/max__soc__dung.png` | |
| 10 | `nhan-vat/max__suy-nghi__dung.png` | |
| 11 | `nhan-vat/max__lo-lang__cam-dien-thoai.png` | |
| 12 | `nhan-vat/max__nhe-nhom__dung.png` | |
| 13 | `nhan-vat/max__suy-nghi__ngoi-may-tinh.png` | |
| 14 | `nhan-vat/max__hao-hung__dung.png` | |
| 15 | `nhan-vat/chuyen-gia__tu-tin__chi-tay.png` | cảnh nghiên cứu |
| 16 | `nhan-vat/dam-dong__hao-hung__chay.png` | cảnh bầy đàn / FOMO |
| 17 | `dao-cu/bao-tien.png` | |
| 18 | `dao-cu/tien.png` | |
| 19 | `dao-cu/co-phieu-xanh.png` | |
| 20 | `dao-cu/co-phieu-do.png` | |
| 21 | `dao-cu/bo-nao.png` | |
| 22 | `dao-cu/can-lech.png` | |
| 23 | `dao-cu/bong-den.png` | |
| 24 | `bieu-do/tang.png` | |
| 25 | `bieu-do/giam-manh.png` | |
| 26 | `phong-nen/van-phong.png` | tuỳ chọn — nền trắng `#FFFFFF` vẫn dùng được |

Thời gian ước tính: 2–3 giờ (gồm tạo lại ảnh hỏng và tách nền).

---

## 12. Điều khoản dùng ảnh Gemini cho mục đích thương mại

**Tra cứu ngày 2026-11-10, chủ yếu từ nguồn thứ cấp (blog, trang so sánh) — chưa đọc trực tiếp văn bản điều khoản của Google. Trước khi bật kiếm tiền, tự đọc lại Điều khoản dịch vụ Google, Chính sách sử dụng bị cấm của Generative AI, và trang trợ giúp Gemini Apps.**

Những gì các nguồn nói (mức chắc chắn khác nhau):
- Google **không nhận quyền sở hữu** nội dung người dùng tạo bằng Gemini (nhiều nguồn dẫn trang trợ giúp / cộng đồng Gemini). — *khá chắc*.
- Phần lớn nguồn thứ cấp cho rằng **được dùng thương mại**; một nguồn nói điều khoản không cấm nhưng cũng **không cấp giấy phép thương mại rõ ràng**. — *không chắc*, cách đọc khác nhau.
- Tài khoản cá nhân **không được Google bồi hoàn / bảo vệ** nếu bị kiện vi phạm sở hữu trí tuệ (chỉ bản doanh nghiệp / Vertex AI có). — *khá chắc*. Vì vậy prompt không nhắc tên nhân vật, thương hiệu, phong cách của tác giả / kênh có thật.
- Ảnh có **SynthID** (thuỷ vân ẩn) và siêu dữ liệu C2PA; dấu lấp lánh hiển thị có thể tắt nhưng SynthID vẫn còn. Cố gỡ SynthID có thể vi phạm điều khoản — *không chắc với ảnh Gemini, nguồn nói về Veo*. **Không cố gỡ SynthID.**
- Quyền tác giả với ảnh do AI tạo hoàn toàn ở nhiều nước (vd. Mỹ) còn hạn chế → người khác có thể dùng lại hình của mình; kịch bản, lời, cách dựng mới là phần mình bảo vệ được. — *nguyên tắc chung, không phải tư vấn pháp lý*.
- YouTube yêu cầu khai báo **nội dung bị chỉnh sửa / tổng hợp trông như thật**; hoạt hình người que rõ ràng không phải người thật thường không thuộc diện này — *không chắc, xem lại chính sách YouTube lúc đăng*. Giọng đọc AI có thể nêu trong mô tả cho minh bạch.

Nguồn:
- [terms.law — What Gemini's Terms Actually Say](https://www.terms.law/ai-output-rights/gemini/)
- [licenseorg.com — Google Gemini Image Generation](https://licenseorg.com/guide/ai-content/google-gemini-image)
- [horadecodar.com.br — Posso usar imagem gerada pelo Gemini comercialmente?](https://horadecodar.com.br/imagem-gemini-uso-comercial/)
- [workalizer.com — Gemini's Commercial Use & SynthID Watermarks](https://workalizer.com/insights/gemini/navigating-geminis-commercial-use-synthid-watermarks-essential-insights-and-gemini-alerts-for-workspace-users)
- [Search Engine Journal — Google lets you turn off visible watermarks in Gemini](https://searchenginejournal.com/google-lets-you-turn-off-visible-watermarks-in-gemini/586145)
- [flowith.io — Veo FAQ: commercial rights, watermarks](https://flowith.io/blog/veo-faq-commercial-rights-watermarks)

---

## 13. Bộ phận nhân vật ghép (tuỳ chọn — cử động tay, chớp mắt, khớp miệng)

Ngoài ảnh nguyên người ở trên, Max có thể làm dạng **ghép bộ phận** (đầu trống mặt, từng đoạn tay / chân / thân thẳng đứng, mắt và miệng là lớp riêng) để máy xoay khớp. Prompt từng bộ phận (nền trắng, đính kèm ảnh gốc Max), cách tách nền và ghi toạ độ khớp: [`10-NHAN-VAT-GHEP.md`](10-NHAN-VAT-GHEP.md) mục 7. Chưa làm thì `nq hinh-tam` đã có bộ tạm trong `kho-mau/nhan-vat-ghep/`.
