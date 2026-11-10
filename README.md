# Người Que — máy làm video YouTube hoạt hình người que

Bộ công cụ tự động dựng video YouTube **hoạt hình người que** về **tâm lý học con người** (tiền bạc chỉ là một mảng ví dụ, không phải kênh tư vấn tài chính), cho người xem nước ngoài (nội dung video bằng **tiếng Anh**). Người làm chỉ cần: chọn chủ đề → nhờ Claude viết kịch bản dạng JSON → máy tự đọc giọng, ghép hình, chuyển cảnh, phụ đề, nhạc nền → ra tệp MP4 + `.srt` để đăng.

Hình thức tham khảo kênh `@thegioikiquai` (học cấu trúc, nhịp, cách dựng) — **không** sao chép hình, nhân vật, lời, nhạc của họ. Nhân vật chính của mình tên **Max**.

## Dùng thế nào (chỉ 2 câu, Claude tự chạy hết)

Mở **Claude Code** trong thư mục repo trên máy Acer, gõ:

| Khi nào | Gõ |
|---|---|
| Lần đầu | `/cai-dat` |
| Mỗi video | `/video <chủ đề>` — vd. `/video why we procrastinate` |

Claude tự viết kịch bản, tách nền ảnh Gemini mới, bù hình tạm, đọc giọng, dựng nháp, sửa lỗi, dựng bản thật và báo đường dẫn MP4 + thumbnail + mô tả YouTube. Các lệnh `nq ...` bên dưới chỉ để tham khảo.

**Hoặc làm bằng giao diện trên trình duyệt:** bấm đúp `giao-dien.bat` ở gốc repo (hoặc nhờ Claude chạy `nq giao-dien`) → mở `http://127.0.0.1:8770`. Cần cài (`/cai-dat`) một lần trước; cửa sổ đen phải để mở trong lúc dùng. Giao diện không gọi Claude: viết kịch bản ở nơi khác (vd. chat với Claude theo `/kich-ban`) rồi **dán** JSON + mô tả vào tab Dự án.

### Giao diện quản trị (`nq giao-dien`)

| Tab | Làm được |
|---|---|
| Dự án | Danh sách dự án; **dán kịch bản** JSON (+ mô tả YouTube) để tạo / sửa dự án — máy kiểm JSON và lược đồ trước khi lưu, bản cũ giữ ở `kich-ban.json.bak`; xem lời từng cảnh; dựng nháp / bản thật, kiểm nhịp, thumbnail; xem MP4 + thumbnail, chép mô tả YouTube; đánh dấu danh sách kiểm chính sách ([docs/12](docs/12-CHINH-SACH-YOUTUBE.md) mục 5), lưu ở `du-an/<slug>/kiem-chinh-sach.json` |
| Kho hình | Kéo thả ảnh Gemini vào `kho-mau/_cho-xu-ly/`; tách nền, bù hình tạm, lập lại danh mục; xem ảnh theo nhóm |
| Việc đang chạy | Hàng việc chạy lần lượt từng việc (GPU / CPU dùng chung), xem nhật ký, dừng việc |
| Cài đặt | Kiểm tra máy (ffmpeg, GPU, giọng, font); sửa `config.yaml` (tự sao lưu `config.yaml.bak` trước khi ghi) |

Chỉ nghe `127.0.0.1` (không mở ra mạng ngoài), chỉ dùng thư viện chuẩn Python.

Hợp đồng kỹ thuật chung (lệnh, lược đồ JSON, cấu hình): [`docs/00-HOP-DONG.md`](docs/00-HOP-DONG.md).

## Chi phí

| Khoản | Giá |
|---|---|
| Tài khoản Claude (viết kịch bản bằng Claude Code) | khoản **duy nhất** phải trả |
| Ảnh nhân vật / đạo cụ / nền | 0 đ — tạo tay bằng Gemini bản web miễn phí ([docs/04](docs/04-TAO-ANH-GEMINI.md)) |
| Giọng đọc | 0 đ — Kokoro-82M chạy trên máy (Apache-2.0, dùng thương mại được) |
| Nhạc nền / hiệu ứng âm thanh | 0 đ — nguồn miễn bản quyền như YouTube Audio Library ([docs/03](docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md)) |
| Dựng hình | 0 đ — Pillow + ffmpeg trên máy |

Không gọi API trả phí nào (không OpenAI, không ElevenLabs, không Gemini API).

## Yêu cầu máy

Máy chạy thật: **Acer Aspire 7** — Ryzen 5 5500U, RAM 16GB, **GTX 1650 4GB**, Windows 10/11.

- Card GTX 1650 đủ cho Kokoro (giọng) và mã hoá `h264_nvenc`. Không có card NVIDIA vẫn chạy được: giọng trên CPU (chậm hơn), mã hoá `libx264`.
- Ổ cứng trống ~10GB (Python, mô hình giọng, tệp tạm khi dựng).
- Có mạng lúc cài đặt và lúc tải mô hình lần đầu; sau đó chạy offline được (trừ Claude).

## Cài đặt trên máy Acer

Mở PowerShell:

```powershell
git clone <địa chỉ repo> nguoi-que
cd nguoi-que
powershell -ExecutionPolicy Bypass -File setup.ps1
```

`setup.ps1` lo phần cài Python 3.11, ffmpeg, các gói (`nq` và phần mở rộng `may-chu`, `kokoro`…), tải mô hình giọng và font. Xong thì kiểm tra:

```powershell
nq kiem-tra
```

Lệnh này báo từng mục: ffmpeg, NVENC, torch CUDA, gói đã cài, font, mô hình, máy chủ giọng. Mục nào đỏ → xem [Xử lý sự cố](#xử-lý-sự-cố-thường-gặp).

Cài thêm [Claude Code](https://claude.com/claude-code) để dùng lệnh `/kich-ban`.

## Video đầu tiên trong 15 phút (chưa cần ảnh Gemini)

Thử trọn luồng bằng hình + âm thanh TẠM do máy tự vẽ, với kịch bản mẫu (~1 phút, 12 cảnh):

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1   # 1. cài (lần đầu; mở lại PowerShell nếu nó bảo)
.\.venv\Scripts\Activate.ps1
nq hinh-tam                                          # 2. vẽ bộ hình / SFX tạm vào kho-mau/ + lập danh mục
nq moi thu-nghiem                                    # 3. chép kịch bản mẫu -> du-an/thu-nghiem/kich-ban.json
nq may-chu                                           # 4. Ở CỬA SỔ PowerShell KHÁC, để nguyên
nq dung thu-nghiem --nhap                            # 5. quay lại cửa sổ đầu: dựng nháp 640x360
```

Kết quả: `du-an/thu-nghiem/thu-nghiem.mp4` + `.srt`. Thiếu nhạc nền `nhac-nen/curious-light.mp3` thì chỉ cảnh báo và dựng không nhạc. Chưa có GPU / mô hình: đặt `tts.dong_co: gia-lap` trong `config.yaml` (tiếng bíp) để thử luồng. Thêm `nq thumbnail thu-nghiem` để ra `thumbnail.png`. Ảnh tạm chỉ để thử — thay dần bằng ảnh Gemini cùng tên ([docs/06](docs/06-HINH-TAM-VA-THUMBNAIL.md)).

## Quy trình làm 1 video từ đầu đến cuối

1. **Chọn chủ đề.** Lấy từ danh sách 30 chủ đề trong [docs/05](docs/05-VIET-KICH-BAN.md) (vd. *loss aversion*, *sunk cost*…).
2. **Kiểm tra kho hình.** Chạy `nq kho` để cập nhật `kho-mau/danh-muc.md`. Kho còn trống thì làm bộ tối thiểu ~25 ảnh theo [docs/04](docs/04-TAO-ANH-GEMINI.md) (trong lúc chờ: `nq hinh-tam` vẽ hình tạm cùng tên).
3. **Viết kịch bản.** Mở Claude Code trong thư mục repo, gõ:
   ```
   /kich-ban loss aversion
   ```
   Claude tạo `du-an/<slug>/kich-ban.json` + `du-an/<slug>/mo-ta-youtube.md`, và liệt kê ảnh còn thiếu kèm prompt Gemini.
4. **Kiểm tra / sửa JSON.** Đọc lại lời (`loi`), kiểm nguồn nghiên cứu, chỉnh vị trí lớp ảnh. Tạo nốt ảnh thiếu (Gemini → `nq tach-nen` → `nq kho`). Ảnh chưa có thì máy vẽ khung giữ chỗ ghi tên tệp — vẫn dựng thử được.
5. **Bật máy chủ giọng** ở một cửa sổ PowerShell riêng (để nguyên, không tắt):
   ```powershell
   nq may-chu
   ```
   Máy chủ giữ mô hình Kokoro trong bộ nhớ, các lần dựng sau không phải nạp lại.
6. **Dựng nháp** ở cửa sổ khác để xem nhịp, vị trí, phát âm:
   ```powershell
   nq dung <slug> --nhap
   ```
   Bản nháp 640×360, 15fps, nhanh. Chỉ sửa vài cảnh thì dựng riêng: `nq dung <slug> --nhap --canh c03,c04`.
7. **Dựng bản thật:**
   ```powershell
   nq dung <slug>
   ```
   Ra MP4 1920×1080 30fps + tệp `.srt` trong `du-an/<slug>/`. Giọng đã đọc được lưu đệm theo nội dung → chạy lại chỉ đọc cảnh đã sửa.
8. **Đăng.** Tải MP4 lên YouTube, dán tiêu đề / mô tả / chương / tag từ `mo-ta-youtube.md`, tải `.srt` làm phụ đề tiếng Anh. Thumbnail: ghi khoá `thumbnail` trong `kich-ban.json` theo ý tưởng gợi ý rồi `nq thumbnail <slug>`.

### Thời gian ước tính

Độ dài video chốt **8–15 phút, mặc định ~10 phút** (~1.500–1.600 từ lời, ~150 cảnh; xem [docs/05](docs/05-VIET-KICH-BAN.md)). Số dưới đây cho **video 10 phút** trên Acer Aspire 7 (Ryzen 5 5500U, GTX 1650) — **ước tính, chưa đo thật**; video 15 phút nhân ~1,5.

| Bước | Thời gian |
|---|---|
| Claude viết kịch bản + mô tả | 5–10 phút |
| Đọc lại, kiểm nguồn, sửa JSON | 20–40 phút |
| Tạo ảnh thiếu bằng Gemini (khi kho đã có bộ cơ bản) | 0–30 phút |
| Giọng đọc lần đầu (Kokoro, GPU; nạp mô hình ~20–40s) | ~1–3 phút (CPU: ~3–6 phút); lần sau chỉ đọc cảnh sửa |
| Dựng nháp 640×360, 15fps (~9.000 khung) | ~2–5 phút |
| Dựng bản thật 1920×1080, 30fps (~18.000 khung, Pillow vẽ trên CPU, NVENC mã hoá) | ~10–20 phút (libx264 thay NVENC: thêm ~5–10 phút) |
| Đăng bài | 10–15 phút |

Video đầu tiên lâu hơn nhiều vì phải làm kho hình (~2–3 giờ cho bộ tối thiểu).

## Bảng lệnh `nq`

| Lệnh | Việc |
|---|---|
| `nq kiem-tra` | Kiểm ffmpeg, NVENC, torch CUDA, gói đã cài, font, mô hình, máy chủ giọng |
| `nq tai-mo-hinh <kokoro\|piper\|font\|tat-ca>` | Tải mô hình giọng / font |
| `nq may-chu [--host] [--port]` | Bật máy chủ giọng (mặc định `127.0.0.1:8765`) |
| `nq moi <ten>` | Tạo dự án mới từ `templates/kich-ban-mau.json` |
| `nq giong <du-an>` | Chỉ tạo giọng đọc |
| `nq dung <du-an> [--nhap] [--canh c01,c02] [--khong-phu-de]` | Giọng → trộn âm → dựng MP4 + `.srt` |
| `nq kho` | Quét `kho-mau/` → `danh-muc.json` + `danh-muc.md` |
| `nq hinh-tam [--ghi-de]` | Vẽ bộ hình người que + SFX TẠM vào `kho-mau/` (giữ tệp đã có), rồi tự lập danh mục ([docs/06](docs/06-HINH-TAM-VA-THUMBNAIL.md)) |
| `nq thumbnail <du-an> [--ra <tep.png>]` | Thumbnail 1280×720 từ khoá `thumbnail` trong `kich-ban.json` → `du-an/<ten>/thumbnail.png` |
| `nq tach-nen <tep\|thu-muc> --ra <thu-muc>` | Ảnh nền trắng → PNG nền trong, tự cắt sát, xoá dấu ngôi sao Gemini ở góc. `--ra kho-mau` thì tự xếp theo tiền tố tên (`dao-cu__tien` → `dao-cu/tien.png`, ảnh nhân vật → `nhan-vat/`) |
| `nq phan-tich <url\|tep>` | Phân tích video mẫu (cảnh, nhịp, lời) |
| `nq giao-dien [--cong 8770] [--khong-mo]` | Mở giao diện quản trị `http://127.0.0.1:8770` (dự án, kho hình, hàng việc, cài đặt); `--khong-mo` = không tự mở trình duyệt. Bấm đúp `giao-dien.bat` cũng được |

Lệnh Claude Code: `/kich-ban <chủ đề>`, `/phan-tich-kenh <thư mục phan-tich/...>`.

## Cấu trúc thư mục

```
config.yaml            cấu hình chung (độ phân giải, giọng, phụ đề, âm thanh)
tu-dien-doc.yaml       từ viết -> cách đọc (chỉ ảnh hưởng giọng)
setup.ps1              cài đặt trên máy Acer
giao-dien.bat          bấm đúp để mở giao diện quản trị (nq giao-dien)
nguoique/              mã nguồn lệnh nq
templates/             kịch bản mẫu
du-an/<ten>/           mỗi video một thư mục: kich-ban.json, mo-ta-youtube.md, build/, .mp4
kho-mau/               kho hình / âm thanh dùng chung (xem kho-mau/README.md)
  nhan-vat/ phong-nen/ dao-cu/ bieu-do/ nhac-nen/ am-thanh/ font/ _cho-xu-ly/
giong-mau/             để dành cho giọng mẫu (hiện chưa cần)
docs/                  tài liệu
.claude/commands/      lệnh /kich-ban, /phan-tich-kenh cho Claude Code
```

## Tài liệu

| Tệp | Nội dung |
|---|---|
| [docs/00-HOP-DONG.md](docs/00-HOP-DONG.md) | Hợp đồng kỹ thuật: lệnh, lược đồ `kich-ban.json`, cấu hình, hiệu ứng |
| [docs/01-PHAN-TICH-KENH.md](docs/01-PHAN-TICH-KENH.md) | Kết quả phân tích kênh tham khảo |
| [docs/02-KHUON-PHONG-CACH.md](docs/02-KHUON-PHONG-CACH.md) | Khuôn phong cách: nhịp cảnh, bố cục, màu, hiệu ứng |
| [docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md](docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md) | Giọng đọc, nhạc nền, hiệu ứng âm thanh |
| [docs/04-TAO-ANH-GEMINI.md](docs/04-TAO-ANH-GEMINI.md) | Tạo kho hình bằng Gemini web + bộ prompt |
| [docs/05-VIET-KICH-BAN.md](docs/05-VIET-KICH-BAN.md) | Cách viết kịch bản, 30 chủ đề khởi đầu, checklist |
| [docs/06-HINH-TAM-VA-THUMBNAIL.md](docs/06-HINH-TAM-VA-THUMBNAIL.md) | Bộ hình tạm (`nq hinh-tam`), thumbnail (`nq thumbnail`) |
| [docs/12-CHINH-SACH-YOUTUBE.md](docs/12-CHINH-SACH-YOUTUBE.md) | Chính sách kiếm tiền YouTube, chủ đề cần tránh, danh sách kiểm cho mọi kịch bản |
| [kho-mau/README.md](kho-mau/README.md) | Quy ước kho mẫu |
| [giong-mau/README.md](giong-mau/README.md) | Ghi chú về giọng mẫu |

## Xử lý sự cố thường gặp

**`ffmpeg` không có trong PATH** (`nq kiem-tra` báo thiếu ffmpeg, hoặc lỗi "không tìm thấy ffmpeg")
- Chạy lại `setup.ps1`, hoặc cài tay: `winget install Gyan.FFmpeg`.
- **Đóng và mở lại** PowerShell (PATH chỉ cập nhật ở cửa sổ mới). Thử `ffmpeg -version`.

**CUDA không nhận** (`nq kiem-tra` báo `torch cuda: không`)
- Cập nhật driver NVIDIA mới (GeForce Experience hoặc trang NVIDIA). Kiểm bằng `nvidia-smi`.
- Có thể torch bản CPU đã được cài; chạy lại `setup.ps1` để cài torch bản CUDA.
- Tạm thời: đặt `tts.thiet_bi: cpu` trong `config.yaml` — vẫn chạy, chỉ chậm hơn.
- Laptop 2 card: cắm sạc, chọn chế độ hiệu năng cao.

**NVENC lỗi** (ffmpeg báo `h264_nvenc` / "No NVENC capable devices" / "OpenEncodeSessionEx failed")
- Cập nhật driver NVIDIA; đóng ứng dụng khác đang dùng card (OBS, game).
- Nếu vẫn lỗi: sửa `config.yaml` → `video.ma_hoa: libx264`. Chậm hơn nhưng chắc chạy.

**Giọng đọc sai từ** (đọc sai tên riêng, viết tắt, ký hiệu)
- Sai ở nhiều video → thêm vào `tu-dien-doc.yaml` (vd. `FOMO: foh-moh`, `Kahneman: KAH-nuh-muhn`). Chỉ ảnh hưởng giọng, phụ đề vẫn giữ chữ gốc.
- Sai ở một câu → đặt trường `loi_doc` của cảnh đó, vd. `"loi": "The S&P 500 fell 20%."`, `"loi_doc": "The S and P five hundred fell twenty percent."`.
- Dựng lại cảnh đó cho nhanh: `nq dung <slug> --nhap --canh c07`.

**Máy chủ giọng không chạy** (`nq dung` báo không kết nối được `127.0.0.1:8765`)
- Mở cửa sổ khác chạy `nq may-chu` và để nguyên; hoặc đặt `tts.che_do: truc-tiep` trong `config.yaml`.

**Ảnh hiện khung giữ chỗ ghi tên tệp** — tệp ảnh chưa có hoặc sai tên. Xem `kho-mau/danh-muc.md`, sửa đường dẫn trong JSON hoặc tạo ảnh còn thiếu.

**Lỗi kịch bản** — `nq dung` báo rõ cảnh nào, khoá nào sai; đối chiếu tập giá trị ở [docs/00-HOP-DONG.md](docs/00-HOP-DONG.md).
