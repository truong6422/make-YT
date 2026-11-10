# Mẫu nhân vật thử (Gemini) — đợt 2026-11-10

Định hướng: theo phần "Bài học" ở `docs/doi-thu/nhom-1-kenh-lon.md` và `docs/doi-thu/nhom-2-moi-noi.md` — một nhân vật chính cố định "Max", hoodie cam #FF7A1A + chỏm tóc vểnh đen, quần navy, bảng màu cam / navy / teal #2EC4B6 / trắng ngà.

**ĐÃ CHỐT (2026-11-10, người dùng chọn)**: **V1 + biểu cảm V2** — tỷ lệ chibi vừa của V1, kiểu biểu cảm mạnh của V2 (miệng há to, má hồng). Prompt bản gốc cuối cùng và prompt Brainy / bạn / đám đông đã ghi vào `docs/04-TAO-ANH-GEMINI.md` mục 2 và 5. V3 không cần tạo nữa.

**Trạng thái**: đã có `V1-max.png`, `V2-max.png`. Gemini báo **hết lượt tạo ảnh** ở lần thứ 3 (mở lại 11:36 ngày 11/11/2026) → **chưa có** `V3-max.png`, `brainy.png`, `dr-mira.png`, `thumbnail-thu.png`. Prompt cho các ảnh còn lại ghi sẵn bên dưới.

Lưu ý chung: mọi ảnh Gemini có **dấu sao Gemini mờ ở góc phải dưới** (watermark hệ thống, prompt không tắt được) — cần xoá / che khi dùng thật. Ảnh xuất 16:9 đúng yêu cầu.

Kinh nghiệm: tạo phương án mới **trong cùng cuộc trò chuyện** làm Gemini vẽ gần y hệt ảnh trước (lần V2 đầu bị trùng V1, đã bỏ) → mỗi phương án nên mở **cuộc trò chuyện mới**; ngược lại, khi cần giữ đúng nhân vật (Brainy / Dr. Mira / thumbnail theo V1) thì làm tiếp trong cuộc trò chuyện của V1 hoặc tải V1 lên làm ảnh tham chiếu.

---

## V1 "chibi vừa" — `V1-max.png` (đạt, lần 1)

Prompt:

> Generate an image, 16:9 landscape: a character reference sheet for an original YouTube psychology mascot named Max, "medium chibi" proportions. Max is an ordinary young adult (about 25-30), ethnically ambiguous with neutral light peach skin, big head about 1/3 of total body height, soft rounded body. Big round white eyes with solid black pupils, thick expressive black eyebrows, simple line mouth, no nose (or a tiny dot nose). Signature look: a bright orange hoodie (#FF7A1A) and a single black cowlick tuft sticking up on top of his short black hair; plain navy blue pants and simple shoes. Layout: on the left, Max standing full body facing front, neutral friendly pose; on the right, a 2x2 grid of four head-only expression studies of Max: happy (big smile), scared (eyebrows up, trembling mouth), shocked (eyes wide, mouth open O), embarrassed (blushing cheeks, awkward smile, looking aside). Palette limited to orange, navy, teal (#2EC4B6) and off-white. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, at most one very subtle flat shadow, pure white background #FFFFFF, no text, no letters, no numbers, no labels, no watermark. Avoid: plain white round stick-figure head, leaf sprout on head, realistic face, excessive detail.

Nhận xét:
- Đúng định hướng: hoodie cam, chỏm tóc vểnh rất rõ (đọc được cả ở cỡ nhỏ), mắt to tròn, lông mày dày, không mũi, giày teal, nền trắng, không chữ.
- Tỷ lệ đầu ~1/3 đúng; mặt tròn dễ thương, thân thiện.
- Biểu cảm: vui / sợ / sốc rõ; **xấu hổ thiếu má hồng** (chỉ liếc + cười gượng) — cần bổ sung khi chốt.
- Hơi "trẻ con", gần kiểu chibi Á; tóc + đầu tròn khá phổ biến — nhận diện dựa nhiều vào chỏm tóc + màu cam.

## V2 "cartoon phương Tây" — `V2-max.png` (đạt, lần 2)

Lần 1 (bỏ): tạo trong cùng cuộc trò chuyện với V1 → ra gần như y hệt V1 (đầu vẫn ~1/3).

Prompt lần 2 (cuộc trò chuyện mới):

> Generate an image, 16:9 landscape: a character reference sheet for an original YouTube psychology mascot named Max, drawn in a Western TV explainer cartoon style. IMPORTANT proportions: realistic-ish adult cartoon, head only about 1/4 of total body height (NOT chibi, NOT big-headed), long slim arms and long legs, tall lanky body, visible neck, slightly oval head. Max is an ordinary adult about 28, ethnically ambiguous with neutral light peach skin. Big round white eyes with solid black pupils, thick expressive black eyebrows, simple mouth, tiny or no nose. Signature look: bright orange hoodie (#FF7A1A) and a single black cowlick tuft sticking up on top of short black hair; plain navy blue slim pants and simple sneakers. Layout: left side Max standing full body facing front, relaxed pose, hands in hoodie pocket; right side a 2x2 grid of four head-and-shoulders expression studies: happy, scared, shocked (eyes wide, mouth open), embarrassed (blushing, awkward smile, looking aside). Palette only orange, navy, teal (#2EC4B6) and off-white. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, pure white background #FFFFFF, no text, no letters, no numbers, no labels, no watermark. Avoid plain white round stick-figure head, leaf sprout on head, realistic face, excessive detail.

Nhận xét:
- Đúng tỷ lệ ~1/4, chân tay dài, trông người lớn hơn — hợp khán giả trưởng thành của kênh tâm lý.
- Có **hai** hình toàn thân gần như giống nhau (thừa một), không ảnh hưởng nhưng khi chốt chỉ cần một.
- Biểu cảm rõ nhất trong hai bản (xấu hổ có má hồng, sợ có miệng mở); chân dung kèm cổ áo hoodie giúp giữ màu nhận diện cả khi chỉ có đầu.
- Đầu nhỏ hơn → ở thumbnail toàn thân mặt sẽ nhỏ; dùng thumbnail cần cắt cận đầu-vai.

## V3 "tối giản đậm" — CHƯA TẠO (hết lượt)

Prompt đã gửi (bị từ chối vì hết lượt, dùng lại nguyên văn, mở cuộc trò chuyện mới):

> Generate an image, 16:9 landscape: a character reference sheet for an original YouTube psychology mascot named Max in a BOLD MINIMAL GEOMETRIC style, designed to read instantly at tiny thumbnail size. Build him from simple geometric shapes: a big rounded-square head, a trapezoid/rectangle hoodie body, simple tube arms and legs, mitten hands. Head about 1/3 of body height. Face with very few strokes: two big round white eyes with solid black dot pupils, two thick bold black eyebrow bars, one simple mouth shape, no nose. Ethnically ambiguous neutral light peach skin. Signature look: bright solid orange hoodie (#FF7A1A) and one bold black cowlick spike on top of a simple black hair cap; plain navy blue pants. Very thick, uniform black outlines (extra heavy line weight), large flat color areas, almost no interior lines. Layout: left side Max standing full body facing front; right side a 2x2 grid of four head-only expressions: happy, scared, shocked (eyes wide, mouth open circle), embarrassed (flat pink blush blocks, awkward smile, eyes looking aside). Palette only orange, navy, teal (#2EC4B6), off-white. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, no shading, pure white background #FFFFFF, no text, no letters, no numbers, no labels, no watermark. Avoid plain white round stick-figure head, leaf sprout on head, realistic face, excessive detail.

## Brainy — CHƯA TẠO (prompt đề xuất, làm tiếp trong cuộc trò chuyện V1 hoặc tải V1 làm tham chiếu)

> Generate an image, 16:9 landscape, in exactly the same style as the Max character sheet (medium chibi, flat 2D): a sidekick character named Brainy — a small cute pink brain (soft pink, simple brain folds drawn with a few thick lines) with big round white eyes with solid black pupils, thick expressive black eyebrows, a small simple mouth, and thin black stick arms and legs with tiny mitten hands. Brainy is the voice inside Max's head: curious, slightly mischievous. Show Brainy full body front view, plus three small poses: pointing up with an idea, panicking with hands on head, smug arms crossed. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, pure white background #FFFFFF, no text, no letters, no numbers, no labels, no watermark.

## Dr. Mira — ĐÃ BỎ (2026-11-10: rủi ro chính sách "nhân vật AI đóng chuyên gia", xem docs/12). Giữ prompt để tham khảo, không tạo.

> Generate an image, 16:9 landscape, in exactly the same style as the Max character sheet (medium chibi, head about 1/3 of body, flat 2D): Dr. Mira, a friendly female psychologist about 40, ethnically ambiguous warm medium skin, big round white eyes with black pupils, thick expressive eyebrows, tiny or no nose, round black glasses, dark hair in a neat bun, teal cardigan (#2EC4B6) over an off-white top, navy skirt or pants, simple shoes, holding a small clipboard. Show her full body front view, plus three head expressions: warm smile, thoughtful (hand on chin), gently surprised. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, pure white background #FFFFFF, no text, no letters, no numbers, no labels, no watermark.

## Thumbnail thử — CHƯA TẠO (prompt đề xuất, dùng V1)

> Generate an image, 16:9 YouTube thumbnail composition using the same Max character (medium chibi style, orange hoodie #FF7A1A, black cowlick, big round eyes, thick eyebrows): Max large on the RIGHT half of the frame, occupying about 50% of the image, cropped from waist up, extremely shocked expression (eyes huge, eyebrows high, mouth wide open), hands raised near his cheeks, a few bold black shock lines around his head. Solid flat bright yellow background (#FFD23F). The LEFT 45% of the frame is empty flat yellow, reserved for title text later — leave it completely empty. Flat 2D vector illustration, thick uniform black outlines, flat colors, no gradients, no text, no letters, no numbers, no watermark.
