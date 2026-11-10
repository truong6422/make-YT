# Khuôn phong cách cho kênh mới (tiếng Anh · tâm lý học & tâm lý đầu tư · người que)

Nguồn số đo: [`01-PHAN-TICH-KENH.md`](01-PHAN-TICH-KENH.md) và 5 bản đo [`phan-tich/video-01.md`](phan-tich/video-01.md) … [`video-05.md`](phan-tich/video-05.md). Tập hiệu ứng: [`00-HOP-DONG.md`](00-HOP-DONG.md). Khi khác với gợi ý trong `05-VIET-KICH-BAN.md`, theo tài liệu này (05 đã ghi như vậy).

> **Kênh tham khảo là gì, học gì.** `@thegioikiquai` (Thế Giới Kì Quái) đăng **truyện kinh dị / "quy tắc quái đàm" hoạt hình Trung Quốc được dịch + lồng tiếng Việt** (hình của xưởng gốc, chữ Hán trong hình). Ta **chỉ học nhịp kể, ngắt nghỉ, cách cắt cảnh và trộn âm** — đo được bằng số. **Không** học hình, nhân vật, nội dung, thể loại kinh dị. Phong cách hình (người que, tối giản) theo [`07-KENH-NGUOI-QUE-NUOC-NGOAI.md`](07-KENH-NGUOI-QUE-NUOC-NGOAI.md); khuôn nội dung (tâm lý học / tâm lý đầu tư, 8–15 phút, tiêu đề, thumbnail, 90 ngày đầu) theo [`08-CON-DUONG-PHAT-TRIEN.md`](08-CON-DUONG-PHAT-TRIEN.md) mục 9.

## 0. Số đo tổng hợp (trung vị 5 video) và giá trị mặc định trong code

### 0.1. Bảng trung vị

Video: #1 "Bài thuốc đẻ con trai", #2 "Thiên Đình mục rửa", #3 "Lừa đảo … Campuchia", #4 (22:23), #5 "Hậu duệ núi Ai Lao". Số tiếng Việt (âm tiết); quy đổi tiếng Anh ở cột cuối. "—" = video đó không đo được.

| Thông số | #1 | #2 | #3 | #4 | #5 | **Trung vị** | Dùng cho kênh mới |
|---|---|---|---|---|---|---|---|
| Thời lượng | 30:36 | 23:50 | 25:36 | 22:23 | 36:32 | **25:36** | 8–15 phút (docs/08) |
| Intro thương hiệu | 3,04 s | 3,0 s | 3,0 s | 3,5 s | 3,2 s | **3,0 s** | 2–3 s, đặt sau hook |
| Hook (phần lời) | ~27 s | ~10 s | 12,4 s | ~36 s | ~31 s | **27 s** | 15–30 s |
| Độ dài cảnh (trung vị) | 3,7 s | 4,8 s | 6,0 s | 4,5 s | 4,7 s | **4,7 s** | thân 3,5–5 s |
| Cảnh trong hook / 60 s đầu | — | ~3 s | — | 3,0 s (TB) | 3,1 s | **~3,0 s** | 2,5–3,5 s |
| Nhịp hoạt hình | 10–20 bước/s | ~12 | 24 | 24 | 14,8 | **~15 bước/s** | máy quay 30 fps mượt |
| Tốc độ đọc (âm tiết/phút, cả nghỉ) | 212 | 244 | 260 | 232 | 234,5 | **234,5** | ≈ 155–170 từ/phút |
| Nghỉ sau dấu phẩy | ~0,25 (p25) | ~0,26 (p25) | ~0,20 | 0,20–0,30 | ~0,20 | **~0,25 s** | `phay` 0,2 (+0,06 = 0,26) |
| Nghỉ sau dấu chấm | 0,42* | ~0,48 (ASR) | ~0,20 | 0,65–0,85 | 0,55–0,60 | **~0,48 s** | `cham` 0,42 (+0,06 = 0,48) |
| Nghỉ câu hỏi / trước ý bất ngờ (p75) | 0,64 | 0,60 | — | — | ~0,58 | **~0,60 s** | `hoi` 0,55 (+0,06 = 0,61) |
| Nghỉ hết đoạn | ~0,95 (max) | — | 0,74 | 1,05–1,26 | ≤ 0,70 (max) | **~0,85 s** | `doan` 0,8 (+0,06 = 0,86) |
| Hình đổi trước câu mới | cắt ở 86–100 % khoảng nghỉ | 30–95 % khoảng nghỉ | hình đến trước từ khoá 70–130 ms | 150–200 ms | 160 ms | **~0,16 s** | `dem_truoc` 0,15 |
| Cắt rơi vào chỗ nghỉ | ~60 % | ~2/3 | cắt giữa nghỉ đoạn | 13/16 | 11/11 | **~2/3 trở lên** | 1 câu (vế câu) = 1 cảnh |
| Nhạc nền dưới giọng | −24 dB | ≤ −35 dB (gần như không) | −31 dB | −20 dB | −31 dB | **−31 dB** | 0,07 (≈ −23) + sidechain −3…−6 dB ≈ −26…−29 |
| Ducking | không đo được | — | không thấy | không chứng minh | không đo được | **không rõ** | nhẹ, 3–6 dB |
| Nháy đen | 4 lần / 2 phút, 0,08–0,3 s | không (3 phút đầu) | khung đen 0,5 s ở cú sốc | 1 lần 0,3 s (hook) | — | **thưa, ở ranh giới / cú sốc** | `toi-den` ≤ 2 phút một lần |
| Kêu gọi đăng ký bằng lời | không | không | không | không | không | **không** | 1 câu CTA ≤ 6 s cuối video (đề xuất) |

\* #1 chỉ có trung vị chung mọi khoảng nghỉ (lẫn phẩy và chấm). #3 nghỉ đều ~0,2 s cả sau chấm — nhịp gấp hơn các video khác.

**"+0,06"**: giọng mỗi mẩu được cắt lặng nhưng giữ 0,03 s hai đầu (`giong.DEM_MANH`), nên khoảng lặng tai nghe = giá trị `nghi` + ~0,06 s. Các giá trị trong code đã trừ phần này để khoảng nghe được khớp trung vị.

Khoảng lặng nghe được ở ranh giới cảnh = `dem_sau` + `dem_truoc` + 0,06: giữa hai cảnh thường 0,35 + 0,15 + 0,06 ≈ **0,56 s** (giữa trung vị chấm 0,48 và cụm 0,55–0,85 của #4/#5 — cắt cảnh thường trùng chỗ đổi ý); đổi phần 0,9 + 0,15 + 0,06 ≈ **1,1 s** (≈ nghỉ đoạn dài của #4).

### 0.2. Giá trị mặc định trong code (khớp `config.yaml`)

| Khoá | Mặc định | Nơi đọc | Ý nghĩa |
|---|---|---|---|
| `tts.nghi.phay` | 0,2 | giong.py | lặng sau mẩu kết bằng `,` `;` `:` |
| `tts.nghi.cham` | 0,42 | giong.py | sau `.` |
| `tts.nghi.hoi` | 0,55 | giong.py | sau `?` `!` |
| `tts.nghi.ngat` | 0,5 | giong.py | sau `…` và gạch dài `—` |
| `tts.nghi.doan` | 0,8 | giong.py | xuống dòng trong `loi` |
| `canh.nghi` | — | giong.py | ghi đè từng khoá trên cho một cảnh |
| mẩu tối thiểu | 3 từ | chuan_hoa.py `TU_TOI_THIEU_MOT_MANH` | mẩu ngắn hơn gộp với mẩu kế (mất nghỉ ở đó) |
| `canh.toc_do` | — (0,8–1,3) | giong.py, kichban.py | ghi đè `tts.<động cơ>.toc_do`; nằm trong khoá băm |
| `am_thanh.dem_truoc` | 0,15 | dong_thoi_gian.py | hình đổi trước lời (cảnh có lời) |
| `am_thanh.nghi_giua_canh` | 0,35 | dong_thoi_gian.py | `dem_sau` mặc định |
| `am_thanh.nghi_cuoi_phan` | 0,9 | dong_thoi_gian.py | `dem_sau` khi cảnh kế có `phan` khác |
| `am_thanh.nhac_nen_am_luong` | 0,07 | am_thanh.py, kichban.py | nhạc nền (≈ −23 dB nếu nhạc và giọng cùng độ lớn) |
| sidechain | ngưỡng 0,05, tỉ lệ 2,5, attack 20 ms, release 300 ms | am_thanh.py (`SC_*`) | giảm thêm ~3 dB (giọng −21 dBFS) … ~6 dB (−16 dBFS) |
| phụ đề | giữ qua nghỉ < 0,3 s; tắt 0,09 s sau mẩu khi nghỉ dài | phu_de.py | khớp từng câu theo tệp mốc giọng |
| `video.zoom_cham_muc` | 0,05 | (chờ dung_hinh.py đọc) | biên độ `zoom-cham` mặc định |
| `kiem_nhip.*` | 8 s; 60 s / 3,5 s; 8–15 phút; 150–175 từ/phút; 120 s | kiem_nhip.py | ngưỡng `nq kiem-nhip` |

Kiểm sau khi có giọng: `nq kiem-nhip <du-an>` báo cảnh > 8 s không đổi hình, 60 s đầu > 3,5 s/cảnh, tổng ngoài 8–15 phút, tốc độ ngoài 150–175 từ/phút, quá 2 phút không có `toi-den`.

Ký hiệu nguồn của mỗi quy tắc:
- **(đo)** = lấy thẳng từ số đo kênh tham khảo.
- **(chỉnh)** = số đo đã quy đổi cho tiếng Anh / thể loại giải thích.
- **(đề xuất)** = kênh tham khảo không làm, thêm vì thể loại mới cần (giải thích khái niệm, người que).

## 0b. Nguyên tắc

1. **Học cấu trúc và nhịp, không sao chép.** Kênh tham khảo dùng hình của xưởng hoạt hình khác, giọng Việt, dải đỏ tên kênh, intro clapper. Kênh mới: nhân vật người que **của mình** (Max, chuyên gia…), bảng màu, logo, intro, nhạc **của mình**. Không dùng lại chữ, bố cục thumbnail, tên series, câu mở của họ.
2. **Kể chuyện trước, giải thích sau.** Kênh tham khảo thắng nhờ: câu 1 là xung đột, cược tăng ngay, có câu báo trước, kể ngôi thứ nhất liền mạch, không lời thừa. Kênh tâm lý mới phải là **một câu chuyện có nhân vật gặp thiên kiến**, khái niệm được gọi tên khi người xem đã "dính" vào chuyện.
3. **Hình luôn động, nhưng động chậm.** Máy quay không bao giờ đứng yên hẳn; đổi hình mỗi ~4 s; chuyển cảnh gần như toàn cắt thẳng.
4. **Nhận diện cố định suốt video**: một lớp thương hiệu (dải/ logo) + phụ đề cứng cùng một kiểu từ đầu đến cuối.

---

## 1. Cấu trúc video theo phần

Kênh tham khảo dài 30–50 phút (truyện). Kênh mới bắt đầu **8–12 phút** (khớp `05-VIET-KICH-BAN.md`); khi có ~30 video có thể thử dạng "Full story" 20–30 phút ghép 3–4 thiên kiến cùng một nhân vật (đề xuất, theo đà kênh tham khảo kéo dài dần).

| # | `phan` | Thời lượng (video 10 phút) | Việc | Nguồn |
|---|---|---|---|---|
| 0 | (intro thương hiệu) | 2–3 s | Logo kênh mới, không lời, 1 tiếng động. **Đặt sau hook**, không đặt đầu video | kênh đặt intro 3 s ở 0:00 (đo); chuyển ra sau hook (đề xuất — kênh mới chưa có khán giả quen) |
| 1 | `hook` | 0–15 s | Câu 1 = xung đột của nhân vật ("Max just watched $40,000 disappear in nine minutes."). Câu 2–3 = nâng cược ("And the worst part? He did it on purpose."). Không chào, không giới thiệu kênh | (đo) câu 1 là xung đột, cược nâng trong 10–20 s |
| 2 | `boi-canh` | 15–45 s | Lùi về: Max là ai, đang muốn gì. **Câu báo trước ở ~25–30 s**: "He didn't know it yet, but his brain had already made the decision for him." | (đo) câu báo trước ~0:28 |
| 3 | `vi-du` (diễn biến) | 0:45–3:30 | Chuỗi biến cố leo thang, mỗi 30–45 s một bước xấu hơn | (đo) chuỗi biến cố leo thang |
| 4 | `giai-thich` | 3:30–5:00 | Gọi tên khái niệm (chữ lớn), giải thích một ý mỗi câu | (đề xuất) |
| 5 | `nghien-cuu` | 5:00–6:30 | 1–2 nghiên cứu thật, chuyên gia dẫn | (đề xuất) |
| 6 | `vi-du` (quay lại Max) | 6:30–8:00 | Max gặp lại tình huống, lần này nhận ra | (đề xuất, giữ mạch truyện) |
| 7 | `cach-tranh` | 8:00–9:30 | 2–4 cách làm ngay | (đề xuất) |
| 8 | `ket` | 9:30–10:00 | **Một câu hình ảnh / đảo nghĩa** đọng lại; một câu CTA ngắn sau đó (≤ 6 s) + câu miễn trừ đầu tư | (đo) kết bằng câu đảo nghĩa; CTA (đề xuất — kênh tham khảo không có) |

- Bỏ `tom-tat` dài: kênh tham khảo không tóm tắt; nếu cần, gói trong 1–2 câu ở `cach-tranh`. (chỉnh)
- **Nhịp đọc tăng dần** về cao trào (kênh: +10…24 % từ đầu đến cuối) → đặt `"toc_do": 0.95` trong cảnh `boi-canh`/`giai-thich`, `1.05` ở cao trào `vi-du` (khoá `canh.toc_do`, 0,8–1,3). (đo → chỉnh)

## 2. Độ dài cảnh mục tiêu

| Đoạn | Độ dài 1 cảnh (giữa 2 lần cắt) | Nguồn |
|---|---|---|
| 60 s đầu | **2,5–3,5 s** (1 câu ngắn hoặc nửa câu) | (đo) trung vị ~3,0 s (#2, #4, #5) |
| Thân | **3,5–5 s**, trung vị 4–4,5 s | (đo) trung vị 5 video 4,7 s (3,7–6,0) → chỉnh ngắn hơn chút vì kênh giải thích |
| Đoạn giải thích / nghiên cứu | 4–7 s, nhưng **trong cảnh phải có ≥ 1 thay đổi** sau mỗi ~3 s (chữ bật, đổi biểu cảm, đẩy máy quay) | (chỉnh) kênh có cảnh 20–30 s nhưng đổi khung bên trong |
| Tối đa | 8 s một khung không đổi gì | (đo) p75 6 s |

Quy đổi lời: tiếng Anh ~160 từ/phút → 1 cảnh 4 s ≈ **10–12 từ**; câu > 18 từ tách 2 cảnh (khớp 05).

## 3. Quy tắc "mỗi câu một thay đổi hình"

1. **Mỗi câu = 1 cảnh** (`canh`), trừ câu > 18 từ (tách) và câu < 4 từ nối liền câu trước (gộp được).
2. Trong cảnh mới phải khác cảnh trước **ít nhất một** trong: khung máy quay (toàn ↔ cận), nhân vật / biểu cảm, đạo cụ, nền, chữ khoá.
3. **Cắt vào chỗ nghỉ, sát đầu câu mới**: kênh cắt ở 85–100 % khoảng nghỉ (đo). Với dòng thời gian của hợp đồng (cảnh = `dem_truoc` + giọng + `dem_sau`), `dem_sau` mặc định 0,35 s và `dem_truoc` mặc định 0,15 s → hình đổi ~0,16 s trước tiếng đầu câu (trung vị #4/#5). Thường không cần ghi hai khoá này trong kịch bản. (đo)
4. Cứ **3–5 cảnh liền một bối cảnh** thì đổi khung toàn → trung → cận như kênh (đo): cảnh 1 toàn (`zoom-cham`), cảnh 2 trung, cảnh 3 cận mặt, cảnh 4 cận đạo cụ.
5. Từ khoá xuất hiện trong lời → chữ / đạo cụ bật lên **đúng lúc từ đó được đọc** (đề xuất; kênh tham khảo không có chữ khoá). Khi chưa có mốc từng từ, đặt `tre` = (số từ đứng trước từ khoá ÷ tổng số từ câu) × thời lượng giọng − 0,1 s.
6. ~35–40 % lần cắt của kênh rơi giữa câu dài (đo) → câu 14–18 từ có thể tách đôi ở dấu phẩy thành 2 cảnh.

## 4. Ánh xạ thủ pháp → giá trị trong hợp đồng

### 4.1. Máy quay (`may_quay`)

| Thủ pháp kênh | Giá trị | Mức | Ghi chú |
|---|---|---|---|
| Đẩy vào chậm liên tục trong cảnh (mặc định) | `zoom-cham` | `muc` 0,04–0,06 | (đo hướng, biên độ chỉnh) — mặc định toàn video |
| Kéo ra chậm (mở bối cảnh, kết) | `zoom-ra` | 0,04–0,06 | cảnh đầu một bối cảnh mới, cảnh kết |
| Lia ngang đưa nhân vật thứ hai vào khung | `lia-trai` / `lia-phai` | 0,06–0,10 | (đo, video #2 40–41 s); đặt nhân vật thứ hai sát mép phía lia tới |
| Đẩy nhanh ở câu sốc / câu hỏi | `dam` | 0,10–0,15 | ≤ 1 lần / 30 s |
| Cảnh doạ / sụp đổ (chớp sét, cổ phiếu sập) | `rung` | nhẹ | ≤ 1 lần / phút, đi cùng `nhay-trang` |
| Cảnh chữ / biểu đồ cần đọc | `dung-yen` | — | chỉ cảnh có biểu đồ hoặc nhiều chữ |

Không để 2 cảnh liền nhau cùng `lia-*` cùng hướng.

### 4.2. Chuyển cảnh (`chuyen_canh` — chuyển VÀO cảnh)

| Thủ pháp | Giá trị | `thoi_luong` | Tần suất | Mức |
|---|---|---|---|---|
| Cắt thẳng (mặc định) | `cat` | 0 | ~90 % cảnh | (đo) |
| Nháy đen ngắn khi đổi bối cảnh / nhảy thời gian | `toi-den` | **0,15–0,3** | ~1–2 lần/phút, ở ranh giới phần | (đo) 4 lần/2 phút, mỗi lần 0,08–0,3 s |
| Chớp trắng (sét, cú sốc, "aha") | `nhay-trang` | 0,15–0,2 | ≤ 1 lần/phút | (đo, chớp sét trong hình) |
| Trộn mờ (cảnh nhớ lại, kết dịu) | `mo-dan` | 0,4–0,6 | cảnh kết, flashback | (đề xuất; kênh kết dịu bằng cảnh tĩnh) |
| `truot-trai`, `truot-len`, `zoom-vao` | — | — | **không dùng** thường xuyên — kênh không dùng | (đo: không thấy) |

### 4.3. Lớp nhân vật (`hieu_ung` vào, `lien_tuc`)

| Thủ pháp | Giá trị | Mức |
|---|---|---|
| Nhân vật có sẵn trong cảnh khi cắt vào (mặc định) | `hieu_ung: khong` | (đo) kênh không "bật" nhân vật |
| Nhân vật bước vào khung | `truot-trai` / `truot-phai`, `tre` 0–0,3 s | (chỉnh, thay cho lia) |
| Đạo cụ / biểu đồ / icon minh hoạ từ khoá | `bat-len` + `am_thanh` pop nhỏ | (đề xuất) — tối đa 1–2 lớp bật mỗi cảnh |
| Ý nghĩ, ký ức, bóng ma của quyết định cũ | `mo-dan` | (đề xuất) |
| Vật rơi (tiền, cổ phiếu sập) | `roi-xuong` | (đề xuất) |
| Phóng to đạo cụ chính | `phong-to` | (đề xuất) |
| Đứng yên | `lien_tuc: tho` (biên độ nhỏ) | (chỉnh) kênh không nhún; `tho` thay cho "sống" của cut-out |
| Sợ, lo | `lien_tuc: run` | (đề xuất, thay cho mồ hôi/ mắt đỏ) |
| Vui, phấn khích | `lien_tuc: nhun` | (đề xuất) — chỉ cảnh vui, không dùng mặc định |
| Lưỡng lự | `lien_tuc: lac` | (đề xuất) |
| Lớp hết vai trò giữa cảnh | `het: <giây>` | (đề xuất) |

### 4.4. Biểu cảm thay cho hoạt ảnh vẽ tay

Kênh đổi biểu cảm **giữa các cảnh** bằng hình khác (đo). Kênh mới: mỗi cảnh chọn tệp biểu cảm khác (`max__lo-lang__dung.png` → `max__hoang-so__dung.png`); 2 cảnh liền cùng nhân vật thì đổi biểu cảm hoặc khung, không lặp nguyên hình.

## 5. Bố cục và màu

| Quy tắc | Giá trị | Mức |
|---|---|---|
| Cảnh toàn: nhân vật chạm đáy (`neo: day`), cao | `co` 0,55–0,75 khung (người que mảnh, cần to hơn manhua để đọc ở điện thoại) | (đo 70–90 % → chỉnh) |
| Cảnh cận mặt | `co` 0,9–1,2, đầu ở 1/3 trên | (đo ~60 % khung là mặt) |
| Một nhân vật + chữ khoá | nhân vật 1/3 trái (`vi_tri` x ≈ 0,3), chữ 2/3 phải (x ≈ 0,68, y ≈ 0,3) | (khớp ví dụ hợp đồng) |
| Hai nhân vật | x ≈ 0,3 và 0,7, đối mặt (`lat` cho người bên phải) | (đo) |
| Nhóm 3–4 | xếp hàng ngang x = 0,2 / 0,4 / 0,6 / 0,8, cùng chân đáy | (đo) |
| Vùng an toàn | không đặt gì quan trọng ở 8 % trên (lớp thương hiệu) và 15 % dưới (phụ đề) | (đo: kênh giữ dải trên + phụ đề dưới) |
| Nền | màu đặc hoặc phòng nền đơn giản; tối giản hơn kênh (người que) | (chỉnh) |
| Bảng màu gợi ý (của kênh mới) | nền giấy ngà `#F5F1E8`; nét `#1A1A1A`; nhấn tiền/rủi ro đỏ `#D64545`; nhấn lời giải xanh `#2E7D5B`; phụ vàng `#F2B134` | (đề xuất; kênh tham khảo tối xám + đỏ, kênh mới sáng để khác biệt) |
| Cảnh doạ / thua lỗ | đổi nền tối `#202124` + nhấn đỏ (giữ "khoảnh khắc đáng sợ" của kênh tham khảo) | (đo → chỉnh) |

## 6. Chữ trên hình và phụ đề

**Phụ đề** (luôn bật, cứng vào hình) — (đo → chỉnh):
- Đáy giữa, `vi_tri_y` 0,90–0,92; 1 dòng, tối đa 7–8 từ (`so_tu_toi_da: 8`); đổi dòng theo cụm lời (~1,6 s).
- Chữ trắng `#FFFFFF`, đậm (Inter Bold); cỡ **44–48 px ở 1080p** (kênh ~38–43 px; tăng nhẹ vì xem trên điện thoại); viền đen `#111111` 5–6 px **hoặc** hộp đen 70–85 % độ đục (kênh video #1 dùng hộp — hợp đồng chưa có hộp, xem mục 11).

**Chữ khoá** (`chu`) — (đề xuất; kênh tham khảo không có):
- Chỉ tên khái niệm / con số: 1–4 từ IN HOA, `co` 80–110, màu nhấn (đỏ cho rủi ro, xanh cho lời giải).
- Hiệu ứng `go-chu` cho tên khái niệm lần đầu; `bat-len` cho con số; `tre` khớp lúc từ đó được đọc.
- Tối đa **1 chữ khoá / cảnh**, không quá 1 cảnh có chữ trong 3 cảnh liền (kênh tham khảo cho thấy người xem không cần chữ để theo truyện).
- Không chép nguyên câu lời lên hình.

**Lớp thương hiệu cố định** (đo → chỉnh): logo kênh mới nhỏ ở góc trên phải (cao ~6 % khung, độ đục 80 %) suốt video. Không làm dải ngang đỏ như kênh tham khảo (tránh giống).

## 7. Giọng đọc

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Tốc độ | **155–170 từ/phút** tiếng Anh; hook & cao trào 165–175, giải thích 150–160 | (đo 212–244 âm tiết/phút tiếng Việt → chỉnh: kể nhanh, liền) |
| Câu | trung vị 10–13 từ; tối đa 18 | (đo 13 âm tiết trung vị → chỉnh) |
| Nghỉ sau dấu phẩy | ~260 ms nghe được (`tts.nghi.phay` 0,2) | (đo trung vị 5 video ~250 ms) |
| Nghỉ sau dấu chấm trong cảnh | ~480 ms (`cham` 0,42) | (đo trung vị ~480 ms; #4/#5 dài hơn 0,55–0,85) |
| Nghỉ giữa 2 cảnh | ~560 ms (`dem_sau` 0,35 + `dem_truoc` 0,15) | (đo) |
| Nghỉ sau câu hỏi / `!` | ~610 ms (`hoi` 0,55) | (đo p75 ~600 ms) |
| Nghỉ sau `…` / gạch dài | ~560 ms (`ngat` 0,5) | (chỉnh, không đo riêng) |
| Nghỉ xuống dòng trong `loi` | ~860 ms (`doan` 0,8) | (đo trung vị ~850 ms) |
| Đổi phần (`phan` của cảnh kế khác) | ~1,1 s (`nghi_cuoi_phan` 0,9) | (đo #4 1,05–1,26 s) |
| Một giọng kể duy nhất, ngôi kể nhất quán | có | (đo: một mạch kể; giới tính/chất giọng: chưa kiểm bằng tai) |

Bộ giọng tự tách `loi` thành mẩu theo dấu câu và chèn lặng như bảng (mục 0.2) — **không cần chia cảnh chỉ để có nghỉ**. Muốn ngắt dài hơn trong một cảnh: dùng `…` hoặc `—`, xuống dòng, hoặc `"nghi": {"cham": 0.6}`. Mẩu < 3 từ bị gộp với mẩu kế ("No. I mean it." đọc liền) — muốn tách thì viết thành câu ≥ 3 từ. Kokoro: đo thử tốc độ thật của `am_michael` ở `toc_do` 1,0 trên 10 câu mẫu (`nq kiem-nhip` in từ/phút) rồi chỉnh để đạt ~160 từ/phút.

## 8. Nhạc nền và hiệu ứng âm

| Thông số | Giá trị | Nguồn |
|---|---|---|
| Nhạc nền | một bản nhẹ, liên tục, ít giai điệu (pad / piano thưa) | (đo: kênh có nền rất nhỏ hoặc không; loại nhạc chưa kiểm bằng tai) |
| Mức nhạc so với giọng | **−26 đến −30 dB** dưới giọng khi đang nói | (đo trung vị 5 video −31 dB; dải −20…−35) |
| `nhac_nen.am_luong` | **0,07** mặc định (≈ −23 dB nếu tệp nhạc và giọng cùng độ lớn); nhạc to / dày thì 0,05 | (đo → chỉnh) |
| Sidechain | đã bật trong code: ngưỡng 0,05, tỉ lệ 2,5 → giảm thêm ~3–6 dB khi nói, trả lại lúc nghỉ — không đo được kênh có hay không | (đề xuất) |
| Mức giọng | trung vị RMS ≈ −21…−24 dBFS, đỉnh ≈ −10…−13 dBFS → xuất ~−14 LUFS cho YouTube | (đo → chỉnh) |
| Đổi nhạc | theo phần: hook/diễn biến căng → giải thích trung tính → kết dịu; đổi ở cảnh `toi-den` | (đề xuất) |
| Hiệu ứng âm | **thưa**: pop nhỏ khi đạo cụ/chữ bật (−18…−24 dB dưới giọng), whoosh khi `lia`/`dam`, một "hit" trầm ở twist; không đặt tiếng động to trong khoảng nghỉ giữa câu | (đo: khoảng nghỉ của kênh không có tiếng động lớn, đỉnh ≤ −35 dBFS) |
| `am_thanh[].am_luong` | pop 0,3–0,5; whoosh 0,4–0,6; hit 0,6–0,8 | (đề xuất) |
| Intro thương hiệu | 1 âm hiệu 2–3 s của kênh mới | (đo: kênh có intro âm ngắn; loại âm chưa kiểm bằng tai) |

## 9. Tiêu đề, thumbnail, mô tả

**Tiêu đề** (đo cấu trúc → chỉnh cho tiếng Anh):
- Cụm 4–9 từ gây tò mò, có **đồ vật / con số cụ thể**, không in hoa toàn bộ, không emoji, ≤ 60 ký tự.
- Mẫu (theo các nhóm của kênh: quy tắc/điều cấm · bí mật/sự thật · cái giá · nghịch lý · ngôi thứ nhất):
  - Điều cấm: "Never Check Your Portfolio After 9 PM", "The One Rule Rich Investors Never Break"
  - Sự thật: "The Truth About Why You Sell Winners Too Early"
  - Cái giá: "The Hidden Cost of Being Right"
  - Nghịch lý: "Why Losing $100 Hurts More Than Winning $200"
  - Ngôi thứ nhất: "I Lost $40,000 Because of One Bias"
- Hậu tố tên kênh **không cần** (kênh mới chưa có thương hiệu); tiền tố dạng `(Full)` chỉ dùng nếu làm dạng truyện dài nhiều phần.

**Thumbnail** (đo bố cục → của kênh mới):
- 1–2 nhân vật người que **biểu cảm cực mạnh** (hoảng, cười méo), nền tương phản cao.
- 2–5 từ chữ đậm, viền dày; một màu nhấn đỏ cho rủi ro. Đặt chữ ở mép trên **hoặc** dải tối ở mép dưới (hai kiểu kênh dùng).
- Logo kênh nhỏ ở góc cố định (kênh tham khảo: góc trên phải — kênh mới chọn góc khác, vd. trên trái, để khác biệt).
- Chữ thumbnail **không lặp nguyên tiêu đề**.

**Mô tả** (kênh tham khảo tối giản; đề xuất thêm cho tiếng Anh/SEO):
1. 1–2 câu tóm tắt có từ khoá khái niệm ("loss aversion", "disposition effect").
2. Chương (timestamps) theo `phan`.
3. Nguồn nghiên cứu (bắt buộc theo 05).
4. Câu miễn trừ đầu tư.
5. 3–4 hashtag cố định của kênh + 1–2 theo chủ đề.

## 10. Thông số kỹ thuật cho bộ dựng

| Thông số | Giá trị đề xuất | Số đo kênh | Ghi chú |
|---|---|---|---|
| fps xuất | 30 | 30 (đo) | giữ `video.fps: 30` |
| fps hoạt hình bộ phận (nếu làm rig) | 12–15 bước/s (giật nhẹ kiểu vẽ tay) **hoặc** 30 mượt | 10–20 (đo) | cần khoá mới `buoc_hinh` (mục 11) |
| Máy quay | nội suy mỗi khung 30 fps (mượt hơn kênh) | 10–20 bước/s (đo) | chuyển động chậm nên 30 fps không lộ |
| Biên độ `zoom-cham` mỗi cảnh | 4–6 % (`muc` 0,04–0,06) | chưa đo chính xác (thấy ~đẩy rõ trong 4 s) | |
| Easing cử động tay / vào khung | 0,3–0,4 s vào khung; 0,6–0,8 s cử động bộ phận; **ease-out** (cubic) | 0,6–0,8 s, ease-out (thấy) | |
| Biên độ `tho` | co giãn 1–1,5 % chiều cao, chu kỳ 3–4 s | kênh không nhún (thấy) | |
| Biên độ `nhun` | 2–3 % chiều cao, chu kỳ 0,5–0,7 s | — | chỉ cảnh vui |
| Biên độ `run` | 1–2 px ở 1080p, 12–15 lần/s | — | |
| Độ dài cảnh | 2,5–3,5 s (60 s đầu); 3,5–5 s (thân); tối đa 8 s không đổi gì | trung vị 4,7 s; hook ~3,0 s (đo, 5 video) | `nq kiem-nhip` kiểm |
| Chuyển cảnh | `cat` ~90 %; `toi-den` 0,15–0,3 s ở ranh giới phần, ≤ 2 phút một lần | cắt thẳng + nháy đen thưa 0,08–0,5 s (đo) | `nq kiem-nhip` kiểm |
| `dem_truoc` | 0,15 s (`am_thanh.dem_truoc`) | hình đổi trước câu mới ~0,16 s (đo) | mặc định trong code |
| `dem_sau` (sau câu) | 0,35 s (`am_thanh.nghi_giua_canh`) | nghe ~0,56 s giữa 2 cảnh (đo chấm 0,48–0,75) | mặc định trong code |
| Nghỉ trong cảnh (TTS) | phẩy 0,2 · chấm 0,42 · hỏi 0,55 · ngắt 0,5 · đoạn 0,8 (`tts.nghi`) | trung vị 5 video (mục 0.1) | đã có trong giong.py |
| Nghỉ cuối phần | 0,9 s (`am_thanh.nghi_cuoi_phan`) | nghỉ đoạn dài 1,05–1,26 s (#4) | tự dùng khi `phan` cảnh kế khác |
| Độ trễ hình so với từ khoá | 0 đến −100 ms (hình hiện ngay hoặc trước từ một chút) | không đo được (kênh không có chữ khoá) | |
| Tốc độ đọc | 155–170 từ/phút | 212–244 âm tiết/phút tiếng Việt (đo) | |
| Mức giọng | ~−14 LUFS tích hợp toàn video | RMS trung vị −21…−24 dBFS (đo) | |
| Nhạc nền so với giọng | −22…−26 dB (`am_luong` 0,06–0,08) | −24 dB (video #1), không nhạc (video #2) (đo) | |
| Sidechain | có, giảm thêm 3–6 dB, attack 20 ms, release 300 ms | không đo được | |
| SFX so với giọng | −6…−18 dB tuỳ loại, không đặt trong khoảng nghỉ giữa câu | đỉnh trong nghỉ ≤ −35 dBFS (đo) | |
| Phụ đề | trắng, Inter Bold 44–48 px, viền 5–6 px hoặc hộp đen 75 %, y 0,91, ≤ 8 từ/dòng | ~38–43 px, hộp đen đặc / viền (thấy) | |
| Intro thương hiệu | 2–3 s, đặt sau hook | 3,0 s ở 0:00 (đo) | |

## 11. Hiệu ứng còn thiếu (đề xuất cho agent lõi — KHÔNG tự sửa code)

Xếp theo mức cần thiết.

1. **Lớp cố định toàn video** — logo / dải thương hiệu vẽ trên mọi cảnh. Đề xuất khoá gốc `"lop_co_dinh": [{"anh": "...", "vi_tri": [0.94, 0.06], "co": 0.06, "do_duc": 0.8}]`. (Kênh: dải đỏ + logo suốt video.)
2. **Hộp nền phụ đề** — `phu_de.hop_nen: "#000000"`, `phu_de.do_duc_hop: 0.75`, `phu_de.giu_hop_khi_lang: false`. (Kênh video #1.)
3. ~~Nghỉ theo dấu câu trong TTS~~ — **đã làm**: `tts.nghi` / `canh.nghi`, tệp mốc từng mẩu, phụ đề khớp từng câu.
4. ~~Tốc độ giọng từng cảnh~~ — **đã làm**: `canh.toc_do` 0,8–1,3.
5. **Máy quay theo mốc trong cảnh** (đổi khung toàn → cận không cắt, như kênh 36–56 s): `"may_quay": {"kieu": "khung", "diem": [{"t": 0, "tam": [0.5,0.5], "ty_le": 1.0}, {"t": 3.0, "tam": [0.35,0.4], "ty_le": 1.4}], "easing": "em"}`.
6. **Nhân vật nhiều bộ phận xoay khớp (rig cut-out)** — nhân vật = thư mục PNG `than`, `dau`, `tay_trai`, `tay_phai`, mỗi phần có `khop` (điểm xoay) và `goc` theo mốc + easing. Kênh: tay xoay quanh vai 0,6–0,8 s ease-out. Ảnh Gemini cần tách bộ phận (thêm hướng dẫn vào `04-TAO-ANH-GEMINI.md`).
7. **Thay hình theo mốc trong cảnh** (sprite swap: mắt liếc, biểu cảm đổi giữa câu) — `"doi_anh": [{"t": 1.2, "anh": "nhan-vat/max__hoang-so__dung.png"}]`.
8. **Chớp mắt tự động** — lớp có `mat_nham` (ảnh mắt nhắm), chớp 0,12–0,15 s, ngẫu nhiên mỗi 2,5–5 s. Kênh không thấy rõ, nhưng giúp người que "sống" khi máy quay chậm.
9. **Khớp miệng theo biên độ giọng** — cho nhân vật đang nói (chuyên gia): 2–3 hình miệng, chọn theo RMS giọng mỗi 1/12 s. Kênh không khớp miệng (người kể ngoài hình) → **ưu tiên thấp**.
10. **Bước hình kiểu vẽ tay** — `buoc_hinh: 12` làm lớp/bộ phận chỉ cập nhật 12 lần/s (kênh 10–20 bước/s). Máy quay giữ 30 fps.
11. **Đi bộ** — chu kỳ 2–4 hình chân + tịnh tiến ngang + nhún nhẹ theo bước; thay cho "lia máy quay đưa nhân vật vào khung" khi cần.
12. **Hiệu ứng vẽ chồng** — `duong-toc-do` (đường tốc độ toả từ mép, cảnh quát / sốc), `hao-quang` (vầng sáng + tia, cảnh "aha"), `phat-sang` (mắt / vật phát sáng), `mo-hoi` (giọt rơi). Có thể làm bằng ảnh PNG có sẵn + `lien_tuc`, nhưng hiệu ứng thủ tục thì tái dùng tốt hơn.
13. **Lệch cắt so với lời (J/L-cut)** — `lech_hinh: -0.15` cho phép hình đổi trước khi câu kết thúc (kênh ~35–40 % cắt giữa câu). Hợp đồng hiện cấm chồng tiếng; khoá này chỉ dời mốc hình, không chồng tiếng.
14. **Easing tuỳ chọn** cho `hieu_ung` vào: `"easing": "ra" | "vao" | "em"` (ease-out mặc định), và `"thoi_gian_vao"` (0,3–0,4 s).

## 12. Ví dụ 4 cảnh mở đầu theo khuôn

```jsonc
{
  "tieu_de": "Why Losing $100 Hurts More Than Winning $200",
  "ngon_ngu": "en",
  "nhac_nen": {"tep": "nhac-nen/tense-pad.mp3", "am_luong": 0.07},
  "canh": [
    {"id": "c01", "phan": "hook",
     "loi": "Max just watched forty thousand dollars disappear in nine minutes.",
     "nen": "#202124",
     "may_quay": {"kieu": "zoom-cham", "muc": 0.06},
     "chuyen_canh": {"kieu": "cat", "thoi_luong": 0},
     "lop": [{"anh": "nhan-vat/max__hoang-so__dung.png", "vi_tri": [0.35, 0.9], "neo": "day", "co": 0.7, "hieu_ung": "khong", "lien_tuc": "run"},
             {"anh": "bieu-do/gia-sap.png", "vi_tri": [0.72, 0.42], "co": 0.35, "hieu_ung": "bat-len", "tre": 0.9, "am_thanh": "am-thanh/hit-tram.wav"}]},
    {"id": "c02", "phan": "hook",
     "loi": "And the worst part? He did it on purpose.",
     "dem_sau": 0.6, "nen": "#202124",
     "may_quay": {"kieu": "dam", "muc": 0.12},
     "chuyen_canh": {"kieu": "cat", "thoi_luong": 0},
     "lop": [{"anh": "nhan-vat/max__boi-roi__can.png", "vi_tri": [0.5, 0.55], "co": 1.0, "hieu_ung": "khong", "lien_tuc": "tho"}]},
    {"id": "c03", "phan": "boi-canh",
     "loi": "Three months earlier, Max had a simple plan.",
     "nen": "#F5F1E8",
     "may_quay": {"kieu": "zoom-ra", "muc": 0.05},
     "chuyen_canh": {"kieu": "toi-den", "thoi_luong": 0.25},
     "lop": [{"anh": "nhan-vat/max__vui__dung.png", "vi_tri": [0.3, 0.9], "neo": "day", "co": 0.6, "hieu_ung": "khong", "lien_tuc": "tho"}]},
    {"id": "c04", "phan": "boi-canh",
     "loi": "He didn't know it yet, but his brain had already made the decision for him.",
     "dem_sau": 0.6, "nen": "#F5F1E8",
     "may_quay": {"kieu": "zoom-cham", "muc": 0.05},
     "chuyen_canh": {"kieu": "cat", "thoi_luong": 0},
     "lop": [{"anh": "nhan-vat/max__vui__dung.png", "vi_tri": [0.3, 0.9], "neo": "day", "co": 0.6, "lien_tuc": "tho"},
             {"anh": "dao-cu/nao-phat-sang.png", "vi_tri": [0.68, 0.4], "co": 0.25, "hieu_ung": "mo-dan", "tre": 2.2, "am_thanh": "am-thanh/pop.wav"}]}
  ]
}
```
(Cảnh c03 dùng `toi-den` 0,25 s vì nhảy thời gian — đúng chỗ kênh tham khảo dùng nháy đen.)
