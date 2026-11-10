# Phân tích kênh tham khảo: Thế Giới Kì Quái (`@thegioikiquai`)

Ngày quan sát: 2026-11-10. Cách lấy dữ liệu: Claude in Chrome (chỉ xem, không đăng nhập), đọc trang kênh, `ytInitialPlayerResponse`, phụ đề của trình phát; đo hình bằng canvas (vẽ khung video, tính sai khác điểm ảnh) và đo âm bằng Web Audio (RMS mỗi 43 ms, tiếng ra loa đặt gain 0).

Chi tiết từng video: `docs/phan-tich/video-01.md` (Bài thuốc đẻ con trai), `video-02.md` (Sự thật về Thiên Đình mục rửa); `video-03..05.md` do agent khác làm.

Mức chắc chắn dùng trong tài liệu:
- **[Đo]** đo bằng số (canvas, Web Audio, phụ đề có mốc giờ, số liệu trang).
- **[Thấy]** nhìn trên ảnh chụp khung hình.
- **[Suy]** suy luận — riêng mọi thứ về *giọng, nhạc, hiệu ứng âm* mà không có số đo: **suy luận, chưa kiểm bằng tai**.

---

## 1. Phát hiện quan trọng nhất (đọc trước)

1. **Kênh không phải "người que giải thích tâm lý".** Đây là kênh **truyện kinh dị / "quy tắc quái đàm" kể ngôi thứ nhất**, hình là **hoạt hình truyện Trung Quốc được dịch và lồng tiếng Việt** (mô tả ghi "Bản dịch thuộc về Thế Giới Kì Quái"; chữ Hán trên đạo cụ: 孕检报告, 天庭). Nét vẽ kiểu webtoon/manhua, nhiều chi tiết. Một số series gần đây dùng nhân vật đầu tròn trắng đơn giản (thấy trên thumbnail "Người đồng nghiệp mất tích", "Tôi là hậu duệ núi Ai Lao") — gần người que hơn. [Thấy + Suy]
   → Cái học được là **nhịp dựng, cách kể, khung hình, nhận diện kênh**, không phải nét vẽ.
2. Video **dài 30–50 phút**, đăng **~1–2 video/ngày**. [Đo]
3. **Đổi hình mỗi ~3,7–4,8 s** (trung vị), 60 s đầu dày hơn (~3 s). [Đo]
4. **Máy quay luôn chuyển động chậm** (đẩy vào / lia) trong cảnh; cảnh dài được "chia" bằng đổi khung toàn → cận thay vì vẽ mới. [Đo + Thấy]
5. Chuyển cảnh **gần như toàn cắt thẳng**; thêm **nháy đen 0,1–0,3 s** khoảng 2 lần/phút ở video #1. [Đo]
6. Hoạt hình kiểu **cut-out**: thân đứng yên, tay xoay quanh khớp vai có ease-out, mắt thay hình; **miệng không khớp lời**; chuyển động bước ~10–20 hình/giây. [Đo + Thấy]
7. **Giọng đọc nhanh, liền**: 212–244 âm tiết/phút, nhanh dần về cuối; nghỉ ~31–36 lần/phút, trung vị ~420–430 ms; mỗi cụm lời ~1,6 s. [Đo]
8. **Nhạc nền rất nhỏ hoặc không có**: lúc nghỉ còn −47 dBFS (video #1, thấp hơn giọng ~24 dB) hoặc −60 dBFS (video #2). [Đo mức; loại âm: chưa kiểm bằng tai]
9. **~60–65 % lần cắt rơi đúng chỗ ngắt câu**, sát đầu câu mới; phần còn lại cắt giữa câu dài. [Đo]
10. Nhận diện kênh **cố định suốt video**: intro 3 s (khung REC + clapper + tên kênh), dải đỏ tên kênh ở mép trên, logo tròn góc phải, phụ đề cứng ở đáy. **Không có chữ từ khoá bật lên, không có lời kêu gọi đăng ký.** [Thấy + Đo]

---

## 2. Trang kênh

| Mục | Giá trị | Mức |
|---|---|---|
| Tên / handle | Thế Giới Kì Quái / `@thegioikiquai` | Đo |
| Người đăng ký | 208 N (208.000) | Đo |
| Số video | 717 | Đo |
| Mô tả kênh | "Cảm ơn vì đã xem kênh của tớ :3" | Đo |
| Avatar | vòng tròn đỏ sẫm, chữ "THẾ GIỚI KÌ QUÁI" trắng viết tay | Thấy |
| Thể loại YouTube | People & Blogs | Đo |
| Từ khoá video | `quytac, quytackila, kinhdiquytac, thegioikiquai` | Đo |

### 2.1. 30 video mới nhất (tab Video → Mới nhất)

| # | Tiêu đề (rút gọn, bỏ hậu tố "\| Thế Giới Kì Quái") | Thời lượng | Lượt xem | Đăng |
|---|---|---|---|---|
| 1 | (Full) Nhật kí hóng hớt nhóm chat ma | 33:19 | 19 N | 22 giờ |
| 2 | (Full) Chuyến xe chở chú rể giấy | 33:49 | 33 N | 2 ngày |
| 3 | (Full) Tai họa khi thờ Tà Phật | 37:50 | 40 N | 2 ngày |
| 4 | (Full) Tiểu thuyết tiên tri án mạng | 35:16 | 50 N | 3 ngày |
| 5 | (Full) Đừng sai thứ tự khi chơi Oẳn Tù Tì | 32:42 | 74 N | 4 ngày |
| 6 | (Full) Cốt quỷ học cách làm mẹ | 33:47 | 98 N | 5 ngày |
| 7 | (Full) Cách giấu con gà nặng 60kg | 36:17 | 83 N | 6 ngày |
| 8 | (Full) Tiếng khóc dưới giếng chuyển sinh | 29:01 | 50 N | 6 ngày |
| 9 | (Full) Công thức nấu cao trường sinh | 45:40 | 101 N | 9 ngày |
| 10 | (Full) Thủ khoa đội lốt cá biệt | 51:51 | 219 N | 10 ngày |
| 11 | (Full) Tuyệt đối đừng nuôi mèo không da | 34:35 | 110 N | 10 ngày |
| 12 | (Full) Bi kịch vụ án phía dưới quạt trần | 36:33 | 134 N | 11 ngày |
| 13 | (Full) Đêm bốc mộ trúng phải duyên âm | 35:04 | 121 N | 11 ngày |
| 14 | (Full) Mắt phải của tôi nhìn thấy ma | 32:25 | 160 N | 13 ngày |
| 15 | (Full) Cương thi bé nhỏ của mẹ tôi | 32:11 | 96 N | 2 tuần |
| 16 | (Full) Hủ tục minh hôn | 30:11 | 211 N | 2 tuần |
| 17 | (Full) Ăn trộm nhầm nhà có án mạng | 35:06 | 189 N | 2 tuần |
| 18 | (Full) Khi mọi quy tắc bị đảo ngược | 38:01 | 196 N | 2 tuần |
| 19 | (Full) Thứ giả giọng người trong rừng cấm | 31:06 | 156 N | 2 tuần |
| 20 | (Full) Quy tắc của người bạn đã chết | 47:05 | 197 N | 2 tuần |
| 21 | (Full) Bí ẩn tộc người không đầu | 51:40 | 215 N | 2 tuần |
| 22 | (Full) Hiệu trưởng trị đám nổi loạn | 34:07 | 173 N | 2 tuần |
| 23 | (Full) Vác bụng bầu đi bắt ghen: Tôi phát hiện vợ mình không phải người | 45:46 | 70 N | 2 tuần |
| 24 | (Full) Màn giả Gay của 2 gấu đực | 32:26 | 116 N | 3 tuần |
| 25 | (Full) Bóng ma trong đêm cắm trại | 35:51 | 113 N | 3 tuần |
| 26 | (Full) Nỗi ám ảnh với con số 5 | 42:11 | 124 N | 3 tuần |
| 27 | (Full) Lời thề cắt máu năm 13 tuổi | 44:07 | 275 N | 3 tuần |
| 28 | (Full) Điều cấm kị khi gặp xe tang | 30:47 | 258 N | 3 tuần |
| 29 | (Full) Mùi hương phân hủy trong lớp học | 29:46 | 165 N | 3 tuần |
| 30 | (Full) Nuôi béo bạn trai để ăn thịt | 31:00 | 205 N | 3 tuần |

- **Tần suất**: 30 video trong ~21 ngày → **~1,4 video/ngày** (có ngày 2 video). [Đo]
- **Thời lượng**: 29:01–51:51, trung vị ~35 phút. [Đo]
- **Lượt xem** video 2–3 tuần tuổi: 70 N–275 N, trung vị ~170 N (≈ 0,8× số người đăng ký). [Đo]

### 2.2. 30 video nhiều xem nhất (tab Video → Phổ biến)

| # | Tiêu đề | Thời lượng | Lượt xem | Tuổi |
|---|---|---|---|---|
| 1 | (Full) Bài thuốc đẻ con trai | 30:36 | 1,9 Tr | 1 năm |
| 2 | (Full) Sự thật về Thiên Đình mục rửa | 23:51 | 693 N | 8 tháng |
| 3 | (Full) Lừa đảo và buôn người ở Campuchia | 25:36 | 672 N | 2 năm |
| 4 | (Full) Thằng chồng tôi là gay | 22:24 | 631 N | 1 năm |
| 5 | (Full) Tôi là hậu duệ núi Ai Lao | 36:33 | 592 N | 1 tháng |
| 6 | (Full) Cái giá của Trọng Nam Khinh Nữ | 18:56 | 586 N | 1 năm |
| 7 | (Full) Chú chuột Jerry kinh dị | 24:38 | 514 N | 1 năm |
| 8 | (Full) Làng ma trên núi Ai Lao | 39:59 | 481 N | 9 tháng |
| 9 | (Full) Tuyệt đối đừng đánh chó | 32:33 | 477 N | 1 năm |
| 10 | (Full) Bí ẩn xương dưới ao | 18:09 | 464 N | 2 năm |
| 11 | (Phần 1) Lạc vào Backroom | 10:27 | 451 N | 2 năm |
| 12 | (Full) 3 cái túi cứu mạng | 19:45 | 440 N | 1 năm |
| 13 | (Full) Thảm họa chất thải phóng xạ | 14:25 | 439 N | 2 năm |
| 14 | (Full) Khi kẻ bị OCD chơi game kinh dị | 39:26 | 438 N | 1 tháng |
| 15 | (Full) Vị vua của các loài quỷ | 21:40 | 438 N | 11 tháng |
| 16 | (Full) Bí mật dưới xe xiên bẩn | 34:49 | 435 N | 3 tháng |
| 17 | (Trọn bộ) Vua Zombie lụy tình tôi | 25:56 | 429 N | 10 tháng |
| 18 | (Full) Sát nhân khóc thét khi gặp tôi | 23:34 | 427 N | 9 tháng |
| 19 | (Full) Quỷ ăn thịt gõ cửa làng | 29:26 | 425 N | 6 tháng |
| 20 | (Truyện ngắn) Cánh đồng đầu người | 19:14 | 418 N | 2 năm |
| 21 | (Full) Nữ phụ quậy nát giới Gay | 27:27 | 407 N | 2 tháng |
| 22 | (Full) Trò chơi sung sướng nhất | 34:52 | 393 N | 10 tháng |
| 23 | (Full) Con gấu nguy hiểm | 15:06 | 380 N | 2 năm |
| 24 | (Full) Oan hồn trên dốc núi | 30:12 | 365 N | 9 tháng |
| 25 | (Full) Quy tắc sinh viên năm nhất | 19:39 | 361 N | 1 năm |
| 26 | (Full) Bí mật của chó thành tinh | 19:14 | 353 N | 2 năm |
| 27 | (Full) Thảm họa tận thế Zombie | 12:55 | 350 N | 2 năm |
| 28 | (Full) Sưu tầm bộ phận cơ thể | 17:44 | 342 N | 2 năm |
| 29 | (Full) Quy tắc làm đứa con ngoan | 26:39 | 339 N | 1 năm |
| 30 | (Full) Thế nào mới là ác quỷ? | 30:06 | 331 N | 1 năm |

- Video nổi bật cũ hơn **ngắn hơn** (10–25 phút); kênh kéo dài dần lên 30–50 phút. [Đo]
- Một video vượt xa phần còn lại (1,9 Tr ≈ 2,7× video thứ 2) — đề tài xã hội gần gũi (trọng nam khinh nữ) bọc trong kinh dị. Đề tài xã hội/đạo đức xuất hiện nhiều trong top: trọng nam khinh nữ ×2, lừa đảo Campuchia, đồng tính, OCD. [Đo + Suy]

## 3. Công thức tiêu đề [Đo trên 60 tiêu đề + Suy]

Khuôn: **`(Full) <cụm 3–9 từ> | Thế Giới Kì Quái`**
- Tiền tố định dạng: `(Full)` gần như mọi video (biến thể `(Trọn bộ)`, `(Phần 1)`, `(Truyện ngắn)`) — báo cho người xem "xem một lần là hết truyện".
- Hậu tố tên kênh cố định.
- Lõi tiêu đề là **cụm danh từ gây tò mò**, không dấu chấm than, không chữ in hoa toàn bộ, không emoji. Mẫu lặp:
  - **Quy tắc / điều cấm**: "Quy tắc sinh viên năm nhất", "Điều cấm kị khi gặp xe tang", "Đừng sai thứ tự khi chơi…", "Tuyệt đối đừng nuôi/đánh…".
  - **Bí ẩn / bí mật / sự thật**: "Bí ẩn xương dưới ao", "Bí mật dưới xe xiên bẩn", "Sự thật về Thiên Đình mục rửa".
  - **Cái giá / hậu quả**: "Cái giá của Trọng Nam Khinh Nữ", "Tai họa khi thờ Tà Phật".
  - **Nghịch lý / đảo vai**: "Sát nhân khóc thét khi gặp tôi", "Cốt quỷ học cách làm mẹ", "Thủ khoa đội lốt cá biệt".
  - **Ngôi thứ nhất**: "Tôi là hậu duệ…", "Mắt phải của tôi…", "Cương thi bé nhỏ của mẹ tôi".
- Đồ vật/chi tiết cụ thể, lạ ("con gà nặng 60kg", "mèo không da", "con số 5") làm móc tò mò.

## 4. Thumbnail [Thấy, trên ~10 thumbnail]

- Một khung hình đẹp nhất trong truyện (hoặc ghép), **2–3 nhân vật**, biểu cảm mạnh (sợ, cười quỷ dị), nền tối.
- **Chữ tiêu đề rút gọn đặt lên ảnh**: hoặc chữ đỏ viền trắng dày ở mép trên ("Nhật Kí Hóng Hớt / Nhóm Chat Ma", "Chuyến xe chở chú rể giấy", "Người đồng nghiệp mất tích"), hoặc chữ đỏ trên **dải đen** ở mép dưới ("Lừa đảo và buôn người ở Campuchia", "Cái giá của Trọng Nam Khinh Nữ"). 1–2 dòng, chữ đậm.
- **Logo kênh tròn đỏ ở góc trên phải** (lặp lại logo trong video).
- Bảng màu: đỏ máu + đen + xám; điểm sáng là khuôn mặt nhân vật.
- Video top cũ (#1, #2) không có chữ trên thumbnail — chỉ cảnh nhân vật. [Thấy]

## 5. Mô tả & thẻ [Đo]

Mô tả tối giản: dòng tiêu đề, "Cảm ơn các cậu đã đón xem :33", 4 hashtag, dòng bản quyền bản dịch. Không có chương (timestamps), không link, không CTA.

## 6. Cách dựng (tổng hợp 2 video phân tích sâu)

### 6.1. Khung và nhận diện [Thấy + Đo màu]
- Intro **3,0 s**: nền giấy xám, khung ngắm máy quay 4 góc, chấm đỏ "REC", clapper vẽ tay, tên kênh hiện dần kiểu đánh máy; video #2 thêm ~2,3 s lặng trước câu đầu.
- **Dải tên kênh** ngang mép trên (~7 % chiều cao), chuyển màu `#800212` → `#580917` → `#1A1A1A`, chữ in hoa nghiêng; **logo tròn đỏ góc trên phải**; có suốt video.
- **Phụ đề cứng** ở đáy giữa: video #1 hộp đen đặc, chữ trắng, hộp giữ cả lúc lặng; video #2 chữ trắng viền đen, không hộp. Cỡ ~3,5–4 % chiều cao khung (~38–43 px ở 1080p), 1–2 dòng.
- Không có chữ từ khoá / tiêu đề phần trên hình.

### 6.2. Bố cục [Thấy]
- Cảnh toàn: nhân vật đứng chạm đáy khung, cao 70–90 % khung; nhóm 3–4 người xếp hàng ngang.
- Hai nhân vật: 1/3 trái – 1/3 phải, đối mặt.
- Cận: mặt chiếm ~60 % khung, lệch tâm nhẹ; đạo cụ (kẹo, phiếu khám) đặt giữa dưới.
- Nền vẽ đầy đủ (nhà, phòng khám, vườn), màu tối ít bão hoà (xám `#303030`–`#707070`, xanh rêu `#305030`, xanh đêm `#101030`), điểm nhấn đỏ.
- Nét viền đen, dày vừa.

### 6.3. Nhịp hình [Đo]
| | Video #1 | Video #2 |
|---|---|---|
| Khoảng giữa 2 lần cắt (trung vị) | 3,7 s | 4,8 s |
| 60 s đầu | ~3–4 s | ~3 s |
| Nháy đen 0,1–0,3 s | 4 lần / 2 phút | không thấy |
| Hình khác nhau mỗi giây | 10–20 | ~12 |
| Máy quay | đẩy vào chậm, đổi khung toàn→cận | đẩy/lia chậm, có lia đưa nhân vật mới vào khung |

### 6.4. Hoạt hình nhân vật [Thấy + Đo]
- **Cut-out / puppet**: thân, đầu cố định; **tay là bộ phận rời xoay quanh vai** (nâng tay ~0,6–0,8 s, ease-out); **mắt thay hình** (liếc, cụp mí); biểu cảm đổi giữa các cảnh bằng hình khác.
- **Không khớp miệng với lời kể** (người kể ở ngoài hình).
- Không thấy squash/stretch, overshoot; không thấy nhún khi đứng yên. Chưa bắt được chớp mắt (mẫu ít).
- Nhân vật mới **vào khung bằng lia máy quay** hoặc cắt sang cảnh có sẵn họ — không thấy hiệu ứng "bật lên".
- Hiệu ứng vẽ chồng: đường tốc độ (cảnh quát), hào quang + tia điện (biến đổi), chớp sét trắng (cảnh doạ), mắt đỏ phát sáng, giọt mồ hôi.

### 6.5. Âm thanh [Đo mức; loại âm: chưa kiểm bằng tai]
| | Video #1 | Video #2 |
|---|---|---|
| Tốc độ đọc | 212 âm tiết/phút | 244 âm tiết/phút (215 → 266) |
| Khoảng nghỉ / phút | ~36 | ~31 |
| Nghỉ trung vị (p25–p75) | 421 ms (248–640) | 432 ms (259–600) |
| Cụm lời liền | 1,6 s | 1,7 s |
| Mức giọng (trung vị / đỉnh) | −24 / −13 dBFS | −21 / −10 dBFS |
| Mức nền khi nghỉ | −47 dBFS | −60 dBFS |
| Cắt cảnh trùng chỗ nghỉ | ~60 % | ~65 % |

- Giọng: [Suy, chưa kiểm bằng tai] một giọng kể duy nhất xuyên suốt, kể cả lời thoại các nhân vật; câu ngắn (trung vị 13 âm tiết).
- Nhạc nền: video #1 có lớp nền liên tục rất nhỏ (~24 dB dưới giọng), video #2 gần như im khi nghỉ. Không đo được có hạ nhạc khi nói hay không.
- Hiệu ứng âm: trong khoảng nghỉ đỉnh chỉ −35…−45 dBFS → không có tiếng động lớn chen giữa câu; intro có chuỗi tiếng ngắn cách ~0,5 s (có thể là tiếng máy ảnh / đánh máy — chưa kiểm bằng tai).

### 6.6. Cấu trúc kịch bản [Đo trên phụ đề ASR]
1. **Câu 1 = xung đột** (không chào, không giới thiệu kênh): "Mẹ tôi đã sinh liên tiếp ba bé gái nhưng bà muốn có một đứa con trai." / "Ngọc Đế … quát hỏi tôi: Ngươi có biết mình phạm tội gì không?"
2. **Nâng cược trong 10–20 s**: "Lần mang thai này là cơ hội cuối cùng."
3. **Câu báo trước ở ~25–30 s**: "Sau này tôi mới biết viên kẹo đó không đơn giản."
4. Lùi về bối cảnh (in medias res → flashback) khi mở bằng cảnh giữa truyện.
5. Thân: chuỗi biến cố leo thang, nhịp đọc nhanh dần (video #2 +24 % từ phút 1 đến phút 21).
6. **Kết bằng một câu hình ảnh / đảo nghĩa** ("Tiên giới vốn làm gì có bầu trời."), không tóm tắt, **không kêu gọi đăng ký**.

## 7. Giới hạn

- Chỉ phân tích sâu 2 video; số đo âm trên 120 s đầu mỗi video, số đo cắt cảnh trên 120–180 s đầu.
- Không nghe được: chất giọng (nam/nữ, AI hay người), thể loại nhạc, tên hiệu ứng âm — chỉ có mức to nhỏ.
- Phụ đề là ASR: dấu câu và mốc từng từ thô → số đo "nghỉ theo dấu câu" độ tin thấp; tốc độ tính theo âm tiết tiếng Việt.
- Ngưỡng phát hiện cắt cảnh nhạy với chuyển động máy quay nhanh (sai số ±0,3 s ở lần quét x4, ±50 ms ở lần phát thật).
- Không đọc được bình luận (khung bình luận không tải ở bố cục cửa sổ hẹp lúc đầu).
- Nhận định "hình là của xưởng Trung Quốc" dựa trên dòng "Bản dịch" + chữ Hán trong hình; chưa xác định tên nguồn.
