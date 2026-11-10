# 05 — Viết kịch bản (tiếng Anh) cho ngách tâm lý học / tâm lý đầu tư

Tài liệu này là chuẩn cho người viết và cho lệnh `/kich-ban`. Lược đồ JSON và tập hiệu ứng: [`00-HOP-DONG.md`](00-HOP-DONG.md). Nhịp, bố cục, màu đo từ kênh tham khảo: [`02-KHUON-PHONG-CACH.md`](02-KHUON-PHONG-CACH.md) — **khi số đo ở docs/02 khác với gợi ý ở đây, theo docs/02**.

Người xem: người nước ngoài nói tiếng Anh, không chuyên tài chính / tâm lý. Mục tiêu: xem xong hiểu một hiện tượng tâm lý, nhận ra nó trong chính mình, biết một cách tránh.

---

## 1. Độ dài và cấu trúc một video

**Chủ dự án chốt: 8–15 phút, mặc định ~10 phút. Không làm dài hơn 15 phút.**

Ước tính theo số từ của lời (`loi`): Kokoro đọc ~150–160 từ/phút, cộng nghỉ giữa cảnh (~0,35s/cảnh) nên thực tế ~140–150 từ/phút video.

| Độ dài video | Số từ lời | Số cảnh (~6–14 từ/cảnh) |
|---|---|---|
| 8 phút (tối thiểu) | ~1.200 | ~120 |
| **10 phút (mặc định)** | **~1.500–1.600** | **~150** |
| 15 phút (tối đa) | ~2.200–2.300 | ~200–220 |

Ngoài khoảng 1.200–2.300 từ → cắt / thêm cho vừa. Chủ đề không đủ nội dung chắc chắn cho 8 phút thì chọn chủ đề khác hoặc gộp hai hiện tượng liên quan — **không** độn chữ, không kéo dài cảnh không lời.

### Phân bổ thời lượng theo phần

Tỉ lệ áp cho mọi độ dài; cột giữa tính cho video 10 phút (~1.550 từ).

| Phần (`phan`) | Tỉ lệ | Video 10 phút | Việc |
|---|---|---|---|
| `hook` | ~3% | ≤ 15s, ~40 từ | Một tình huống / câu hỏi / sự thật gây bất ngờ. Không chào hỏi, không giới thiệu kênh. Hứa điều người xem sẽ hiểu + mở một câu hỏi để trả lời sau. |
| `boi-canh` | ~7% | ~45s, ~120 từ | Vì sao chuyện này quan trọng với "you": mất tiền, mất thời gian, quyết định sai. |
| `giai-thich` | ~20% | ~2 phút, ~310 từ | Gọi tên khái niệm (chữ lớn trên hình), giải thích bằng lời thường, một ý mỗi câu. |
| `vi-du` | ~25% | ~2,5 phút, ~390 từ | Câu chuyện đời thường với **Max**: Max mua cổ phiếu, đi siêu thị, chọn việc… có diễn biến, có cảm xúc (khớp biểu cảm trong kho). Video dài có thể 2 ví dụ. |
| `nghien-cuu` | ~18% | ~1,8 phút, ~280 từ | Một hai nghiên cứu **có thật**: ai, năm nào, làm thí nghiệm gì, kết quả chính. Nhân vật `chuyen-gia` dẫn. |
| `cach-tranh` | ~16% | ~1,6 phút, ~250 từ | 2–4 cách cụ thể, làm được ngay. |
| `tom-tat` | ~6% | ~35s, ~90 từ | Nhắc lại 2–3 ý chính. |
| `ket` | ~5% | ~30s, ~70 từ | Một câu đọng lại + kêu gọi (subscribe / xem video liên quan / bình luận câu hỏi). Có câu miễn trừ khi nói về đầu tư. |

Video dài hơn 10 phút: phần tăng thêm dồn vào `vi-du`, `nghien-cuu`, `cach-tranh` (thêm ví dụ / nghiên cứu / cách), giữ `hook` ≤ 15s và `boi-canh` ≤ 1 phút.

### Điểm giữ chân mỗi 60–90 giây

Cứ **60–90 giây lời** (~150–220 từ, ~15–20 cảnh) phải có một điểm giữ chân — người xem hay bỏ ở các mốc này:
- **Vòng lặp mở / trả lời** (open loop): hứa một điều ở trước, trả lời ở sau (*"But that's not the strangest part. We'll get there."*). Hook mở một vòng, giữa video mở thêm 1–2 vòng.
- **Câu hỏi thẳng tới người xem** (*"Be honest — have you done this?"*), hoặc mời đoán trước khi nói kết quả nghiên cứu.
- **Bước ngoặt nhỏ** trong chuyện của Max (tưởng thắng hoá thua), hoặc số liệu bất ngờ (có nguồn).
- **Đổi nhịp hình**: đổi nền / nhân vật / bố cục, máy quay `dam` hoặc `rung`, chuyển cảnh `nhay-trang` / `zoom-vao`, cảnh chữ lớn — đặt ngay tại điểm giữ chân.

Khi viết, ghi dấu các điểm này (vd. đoạn lời bắt đầu bằng câu chuyển ý) và kiểm khoảng cách giữa hai điểm liền nhau ≤ 90 giây (≈ 220 từ).

## 2. Câu và cảnh

- **1 câu ≈ 1 cảnh ≈ 2–5 giây** giọng đọc (~6–14 từ). Câu dài hơn 18 từ → tách ra.
- Mỗi cảnh có **một thay đổi hình**: nhân vật đổi biểu cảm, thêm đạo cụ, hiện chữ khoá, đổi máy quay. Không để hai cảnh liền nhau giống hệt.
- Chữ trên hình (`chu`) chỉ là **từ khoá** (1–4 từ, IN HOA), không chép nguyên câu lời — phụ đề đã lo phần đó.
- Câu đọc phải nghe tự nhiên khi đọc to: tránh ngoặc đơn, gạch đầu dòng, viết tắt lạ. Số / ký hiệu dễ đọc sai thì đặt `loi_doc` (vd. `"loi": "$1,000"`, `"loi_doc": "one thousand dollars"`).
- Cảnh không lời (hiệu ứng, chuyển đoạn) phải có `thoi_luong`.
- Ưu tiên ảnh đã có trong `kho-mau/danh-muc.md`; ảnh mới đặt tên đúng quy ước [`04-TAO-ANH-GEMINI.md`](04-TAO-ANH-GEMINI.md).

## 3. Giọng văn

- **Kể chuyện**, ngôi **"you"**: *"You open your app. Your stock is down 20%. What do you do?"*
- Câu ngắn, từ phổ thông (trình độ ~lớp 8). Thuật ngữ thì giải thích ngay câu sau.
- Hài nhẹ, tự giễu, không chế giễu người xem.
- Nhịp: câu ngắn – câu ngắn – câu dài hơn một chút. Dùng câu hỏi tu từ để chuyển ý.
- Không giật tít sai sự thật; hook phải được video trả lời.
- Không nói "in this video I will…", "hey guys, welcome back".

## 4. Kiểm chứng — bắt buộc

- **Chỉ trích nghiên cứu có thật** và nói đúng những gì nghiên cứu tìm ra. Không chắc → không đưa vào, hoặc nói chung chung ("researchers have found…") mà không gắn tên / số.
- **Không bịa số liệu**, không làm tròn kiểu phóng đại. Ví dụ minh hoạ với Max dùng số giả định thì nói rõ ("Let's say Max invests $1,000").
- Nghiên cứu đã bị phản bác / tái lập thất bại (vd. thí nghiệm kẹo dẻo, mứt chọn lựa, ego depletion) thì nói rõ hạn chế hoặc tránh dùng.
- **Ghi nguồn vào mục "Sources" trong mô tả YouTube** (`mo-ta-youtube.md`): tác giả, năm, tên bài, tạp chí, đường dẫn DOI nếu có.
- Danh sách nghiên cứu ở mục 6 là **điểm khởi đầu để tra lại**, không phải nguồn đã kiểm — luôn đối chiếu bài gốc trước khi dựng.

## 5. Miễn trừ

Video có nói về đầu tư / tiền: thêm vào phần `ket` (lời đọc hoặc chữ trên hình) và đầu mô tả YouTube:

> This video is for educational purposes only and is not financial advice. Do your own research or consult a licensed professional before making investment decisions.

Không khuyên mua / bán mã cổ phiếu, coin cụ thể. Không hứa lợi nhuận.

---

## 6. 30 chủ đề khởi đầu

Nghiên cứu ghi bên dưới là gợi ý để tra lại (mục 4).

| # | Chủ đề | Hook gợi ý | Nghiên cứu để tra |
|---|---|---|---|
| 1 | Loss aversion | "Losing $100 hurts about twice as much as winning $100 feels good. And it's costing you money." | Kahneman & Tversky 1979, *Prospect Theory* |
| 2 | Disposition effect | "Why do you sell your winners too early and hold your losers forever?" | Shefrin & Statman 1985; Odean 1998 |
| 3 | Sunk cost fallacy | "You hate the movie. You paid for the ticket. So you stay. Why?" | Arkes & Blumer 1985 |
| 4 | FOMO | "Everyone is getting rich except you. At least, that's what your phone tells you." | Przybylski et al. 2013 |
| 5 | Herd behavior | "Would you say a line is longer than it really is, just because everyone else did?" | Asch conformity experiments (1950s); Banerjee 1992 |
| 6 | Anchoring | "A random number can change how much you're willing to pay. Even a wheel of fortune." | Tversky & Kahneman 1974 |
| 7 | Overconfidence | "The more you trade, the less you earn. Researchers checked thousands of accounts." | Barber & Odean 2000; 2001 |
| 8 | Mental accounting | "Why does a $50 bonus feel easier to waste than $50 from your salary?" | Thaler 1985, 1999 |
| 9 | Hedonic treadmill | "Lottery winners weren't much happier than everyone else. So why do we chase more?" | Brickman, Coates & Janoff-Bulman 1978 |
| 10 | Confirmation bias | "You don't research your investment. You research reasons you were right." | Wason 1960; Nickerson 1998 (review) |
| 11 | Endowment effect | "The moment you own a coffee mug, you think it's worth more." | Kahneman, Knetsch & Thaler 1990 |
| 12 | Status quo bias | "Most people never change their default settings. Including the ones that cost them money." | Samuelson & Zeckhauser 1988 |
| 13 | Default effect & saving | "One checkbox doubled how many people saved for retirement." | Madrian & Shea 2001 |
| 14 | Present bias | "You want to start saving. Next month. Every month." | Laibson 1997; O'Donoghue & Rabin 1999 |
| 15 | Framing effect | "Same facts, different words, opposite decisions." | Tversky & Kahneman 1981 |
| 16 | Availability heuristic | "Are you more afraid of sharks or of falling coconuts? Your brain might be lying to you." | Tversky & Kahneman 1973 |
| 17 | Gambler's fallacy | "Red came up five times in a row. Black is due, right? Wrong." | Tversky & Kahneman 1971; Croson & Sundali 2005 |
| 18 | Hindsight bias | "'I knew it all along.' No, you didn't." | Fischhoff 1975 |
| 19 | Dunning–Kruger effect | "The less you know, the more confident you might feel." (nêu cả tranh luận về hiệu ứng) | Kruger & Dunning 1999 |
| 20 | Choice overload | "More options should make you happier. Sometimes they make you freeze." (nêu kết quả tái lập lẫn lộn) | Iyengar & Lepper 2000; Scheibehenne et al. 2010 |
| 21 | Social proof | "A small sign in a hotel room changed how many guests reused their towels." | Goldstein, Cialdini & Griskevicius 2008 |
| 22 | Decoy effect | "Why is there a medium popcorn that nobody buys?" | Huber, Payne & Puto 1982 |
| 23 | Scarcity mindset | "Being short on money can make you think less clearly." | Mani, Mullainathan, Shafir & Zhao 2013 |
| 24 | Illusion of control | "People bet more when they throw the dice themselves." | Langer 1975 |
| 25 | Money and happiness | "Does happiness stop rising after a certain income? Two famous studies disagreed — then teamed up." | Kahneman & Deaton 2010; Killingsworth 2021; Killingsworth, Kahneman & Mellers 2023 |
| 26 | Planning fallacy | "Your project will take longer than you think. Even when you know this rule." | Buehler, Griffin & Ross 1994 |
| 27 | Myopic loss aversion | "Checking your portfolio every day might make you a worse investor." | Benartzi & Thaler 1995 |
| 28 | Ostrich effect | "When markets fall, investors log in less. Why do we look away?" | Karlsson, Loewenstein & Seppi 2009 |
| 29 | Peak-end rule | "People chose MORE pain over less. Because of how it ended." | Kahneman et al. 1993 |
| 30 | Negativity bias | "One bad comment ruins your day. Ten good ones don't fix it." | Baumeister et al. 2001 |

Dự phòng: spotlight effect (Gilovich et al. 2000), home bias (French & Poterba 1991), bandwagon trong bong bóng (Shiller, *Irrational Exuberance*).

---

## 7. Checklist trước khi dựng

**Nội dung**
- [ ] Hook ≤ 15 giây, không chào hỏi, có lời hứa được trả lời trong video.
- [ ] Tổng lời 1.200–2.300 từ (8–15 phút; mặc định ~1.550 từ ≈ 10 phút), ~120–220 cảnh; phân bổ phần gần bảng mục 1.
- [ ] Có điểm giữ chân ít nhất mỗi 60–90 giây (≤ ~220 từ giữa hai điểm); mọi vòng lặp mở đều được trả lời.
- [ ] Đủ các phần: hook → bối cảnh → giải thích → ví dụ Max → nghiên cứu → cách tránh → tóm tắt → kết.
- [ ] Mọi nghiên cứu / số liệu đã đối chiếu bài gốc; ghi nguồn trong `mo-ta-youtube.md`.
- [ ] Số giả định được nói rõ là giả định.
- [ ] Có câu miễn trừ "not financial advice" (nếu nói về đầu tư); không khuyên mã cụ thể.
- [ ] Không chép lời / ý tưởng đặc trưng của kênh khác.

**Câu chữ**
- [ ] Mỗi cảnh một câu, ~6–14 từ; không câu > 18 từ.
- [ ] Đọc to toàn bộ một lượt: trôi, không vấp.
- [ ] Số, ký hiệu, tên riêng khó đọc đã có `loi_doc` hoặc trong `tu-dien-doc.yaml`.
- [ ] Chữ trên hình là từ khoá ngắn, đúng chính tả tiếng Anh.

**Kỹ thuật**
- [ ] `id` cảnh duy nhất; giá trị `hieu_ung`, `lien_tuc`, `may_quay`, `chuyen_canh.kieu`, `neo` nằm trong tập ở docs/00.
- [ ] Cảnh không lời có `thoi_luong`.
- [ ] Đường dẫn ảnh / âm thanh đúng tên trong `kho-mau/danh-muc.md`; ảnh thiếu đã liệt kê kèm prompt.
- [ ] Hai cảnh liền nhau không trùng hình hoàn toàn.
- [ ] Chạy `nq dung <slug> --nhap` xem hết một lượt trước bản thật.
