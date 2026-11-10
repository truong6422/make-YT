# Hợp đồng chung giữa các phần (mọi agent / người sửa code phải theo)

## Mục tiêu
Repo tự động hoá video YouTube hoạt hình **người que** về tâm lý học con người và tâm lý đầu tư / tài chính, cho **người xem nước ngoài (tiếng Anh)**. Hình thức tham khảo kênh `https://www.youtube.com/@thegioikiquai` (học cấu trúc, nhịp, cách dựng — KHÔNG sao chép hình, nhân vật, lời, nhạc của họ).

Chi phí: chỉ tài khoản Claude. Ảnh nhân vật / bố cục tạo tay bằng Gemini bản web (miễn phí) rồi bỏ vào `kho-mau/`. Giọng đọc chạy local. Nhạc / hiệu ứng âm thanh miễn bản quyền (YouTube Audio Library…).

Máy chạy thật: Acer Aspire 7, Ryzen 5 5500U, RAM 16GB, **GTX 1650 4GB**, Windows. Máy đang viết code KHÔNG chạy pipeline (không cài Python ở đây).

## Ngôn ngữ
- Tài liệu, thông báo CLI, tên lệnh: **tiếng Việt** (người dùng là người Việt).
- Nội dung video (lời đọc, chữ trên hình, phụ đề): **tiếng Anh** (mặc định `ngon_ngu: en` trong kịch bản; để mở sau cho ngôn ngữ khác).
- Định danh trong code: tiếng Việt không dấu, snake_case (vd. `dung_video`, `thoi_luong`).

## Công nghệ
- Python 3.11, gói `nguoique/`, lệnh `nq` (pyproject `[project.scripts] nq = "nguoique.cli:main"`), chạy được `python -m nguoique`.
- Phụ thuộc lõi: `pillow>=10.1`, `numpy`, `pyyaml`, `requests`. Tuỳ chọn (extras): `may-chu` (fastapi, uvicorn), `kokoro` (kokoro, soundfile), `piper` (piper-tts), `phan-tich` (yt-dlp, faster-whisper).
- Dựng hình: **Pillow vẽ từng khung → đẩy rawvideo rgb24 vào ffmpeg qua stdin** (không dùng Remotion / MoviePy). Mã hoá `h264_nvenc` nếu có, không thì `libx264`.
- Âm thanh: numpy ghép giọng + hiệu ứng theo dòng thời gian, ffmpeg trộn nhạc nền có `sidechaincompress` (nhạc nhỏ lại khi có lời).
- Giọng đọc: lớp động cơ chung, mặc định **Kokoro-82M** (Apache-2.0, dùng thương mại được), dự phòng **Piper**, và `gia-lap` (tiếng bíp — để thử luồng không cần mô hình). Không dùng mô hình giấy phép phi thương mại (XTTS-v2 / CPML, F5-TTS CC-BY-NC) làm mặc định vì kênh sẽ bật kiếm tiền.

## Cấu trúc repo
```
config.yaml              cấu hình chung (xem dưới)
tu-dien-doc.yaml         từ viết -> cách đọc (chỉ ảnh hưởng giọng)
setup.ps1                cài trên máy Acer (ASCII-only, PowerShell 5.1)
pyproject.toml
nguoique/
  __init__.py  __main__.py
  cli.py          (agent "lõi") argparse, các lệnh bên dưới
  cauhinh.py      (lõi) GOC, doc_cau_hinh(), kho_mau(ch), thu_muc_du_an(ch, ten)
  kichban.py      (lõi) nap_kich_ban(path) -> dict đã kiểm + mặc định; hằng tập hiệu ứng
  dong_thoi_gian.py (lõi) lap_dong_thoi_gian(kb, giong, ch) -> (ds, tong)
  dung_hinh.py    (lõi) vẽ khung, máy quay, chuyển cảnh, phụ đề, đẩy ffmpeg
  am_thanh.py     (lõi) tron_am_thanh(...)
  am_thanh_io.py  (lõi) ghi_wav, doc_wav(bytes)->(np.float32, sr), giai_ma(path, sr), thoi_luong_wav, can_ffmpeg()
  phu_de.py       (lõi) chia cụm phụ đề, xuất .srt
  kho.py          (lõi) lap_danh_muc(kho), tach_nen(...)
  giong.py        (agent "giọng") động cơ + tạo giọng cho dự án
  chuan_hoa.py    (giọng) chuẩn hoá chữ trước khi đọc (tiếng Anh: số, %, $, từ điển)
  may_chu.py      (giọng) máy chủ FastAPI
  tai_ve.py       (giọng) tải mô hình / font
  phan_tich.py    (giọng) phân tích video mẫu
templates/kich-ban-mau.json  (lõi)
du-an/<ten>/kich-ban.json    dự án video; build/ và .mp4 bị gitignore
kho-mau/  nhan-vat/ phong-nen/ dao-cu/ bieu-do/ nhac-nen/ am-thanh/ font/ _cho-xu-ly/
docs/     tài liệu (agent "tài liệu" + "phân tích kênh")
.claude/commands/        lệnh Claude Code: /kich-ban, /phan-tich-kenh
```

## Giao diện giữa module (chữ ký cố định)
```python
# am_thanh_io.py
can_ffmpeg() -> str                         # đường dẫn ffmpeg, lỗi tiếng Việt nếu thiếu
ghi_wav(path, mau: np.ndarray, tan_so: int) # float32 [-1,1] -> wav 16-bit mono
doc_wav(du_lieu: bytes) -> tuple[np.ndarray, int]
giai_ma(path, tan_so: int) -> np.ndarray    # mọi định dạng -> float32 mono qua ffmpeg
thoi_luong_wav(path) -> float

# giong.py
tao_giong_du_an(kb: dict, thu_muc_build: Path, ch: dict) -> dict[str, tuple[Path, float]]
    # id cảnh -> (tệp wav, số giây). Lời tách mẩu theo dấu câu (chuan_hoa.tach_manh), đọc từng mẩu,
    # chèn lặng tts.nghi / canh.nghi. Bộ đệm 2 tầng: mẩu build/giong/manh/<băm>.wav (động cơ|giọng|tốc độ|chữ mẩu)
    # và cảnh build/giong/<id>-<băm>.wav + tệp mốc <id>-<băm>.json {"manh": [{"chu","loai","bat_dau","ket_thuc","nghi_sau"}]}.
    # Chỉ nạp động cơ khi có mẩu cần đọc. Cắt lặng mỗi mẩu (giữ 0,03s).
tao_dong_co(ch: dict)  # theo ch["tts"]["che_do"]: máy chủ -> client HTTP; trực tiếp -> động cơ local
# động cơ: thuộc tính ten, tan_so; phương thức doc(van_ban, toc_do=None) -> (np.float32, sr)

# may_chu.py
chay_may_chu(ch: dict, host="127.0.0.1", port=8765)
    # GET /trang-thai -> {"dong_co","tan_so","dinh_danh","ho_tro": ["toc_do"]} ; POST /doc {"van_ban", "toc_do"?} -> audio/wav
    # dinh_danh = "động cơ|giọng|tốc độ" của máy chủ; client khác config của mình -> lỗi, bảo khởi động lại máy chủ

# tai_ve.py
tai_mo_hinh(ch: dict, muc: str)   # muc: kokoro | piper | font | tat-ca

# phan_tich.py
phan_tich(nguon: str, ch: dict, nguong_canh=0.3, chep_loi=True) -> Path  # trả thư mục kết quả
```

## Lệnh CLI (cli.py, agent lõi nối tất cả)
| Lệnh | Việc |
|---|---|
| `nq kiem-tra` | ffmpeg, nvenc, torch cuda, gói đã cài, font, mô hình, máy chủ giọng |
| `nq tai-mo-hinh <kokoro\|piper\|font\|tat-ca>` | gọi `tai_ve.tai_mo_hinh` |
| `nq may-chu [--host] [--port]` | gọi `may_chu.chay_may_chu` |
| `nq moi <ten>` | chép `templates/kich-ban-mau.json` -> `du-an/<ten>/kich-ban.json` |
| `nq giong <du-an>` | chỉ tạo giọng |
| `nq dung <du-an> [--nhap] [--canh c01,c02] [--khong-phu-de]` | giọng -> trộn âm -> dựng MP4 + .srt; `--nhap` = 640x360, 15fps, nhanh |
| `nq kho` | quét `kho-mau/` -> `kho-mau/danh-muc.json` + `danh-muc.md` (bỏ thư mục bắt đầu bằng `_`) |
| `nq tach-nen <tep\|thu-muc> --ra <thu-muc>` | ảnh Gemini nền trắng -> PNG nền trong (loang từ viền, giữ phần trắng bên trong nhân vật), tự cắt sát |
| `nq phan-tich <url\|tep>` | gọi `phan_tich.phan_tich` |
| `nq hinh-tam [--ghi-de]` | `hinh_tam.tao_bo_hinh_tam(kho_mau(ch), ghi_de)` rồi `kho.lap_danh_muc` (docs/06) |
| `nq thumbnail <du-an> [--ra]` | `thumbnail.tao_thumbnail(...)` từ khoá gốc `thumbnail` của kich-ban.json (lõi giữ nguyên, không kiểm) -> `du-an/<ten>/thumbnail.png` |

## config.yaml (khoá dùng chung)
```yaml
kho_mau: kho-mau
du_an: du-an
video: {rong: 1920, cao: 1080, fps: 30, ma_hoa: h264_nvenc, chat_luong: 21}
tts:
  che_do: may-chu            # may-chu | truc-tiep
  dia_chi: http://127.0.0.1:8765
  dong_co: kokoro            # kokoro | piper | gia-lap
  thiet_bi: cuda             # cuda | cpu
  tu_dien: tu-dien-doc.yaml
  kokoro: {giong: am_michael, toc_do: 1.0, ma_ngon_ngu: a}   # a = American English
  piper: {mo_hinh: mo-hinh/piper/en_US-norman-medium.onnx, toc_do: 1.0}
  nghi: {phay: 0.2, cham: 0.42, hoi: 0.55, ngat: 0.5, doan: 0.8}   # giây lặng sau mẩu theo dấu câu
am_thanh: {tan_so: 48000, nhac_nen_am_luong: 0.07, giam_nhac_khi_noi: true, dem_truoc: 0.15,
           nghi_giua_canh: 0.35, nghi_cuoi_phan: 0.9}
# video.zoom_cham_muc: 0.05 (biên độ zoom-cham mặc định); kiem_nhip: {...} ngưỡng `nq kiem-nhip`
phu_de: {bat: true, co_chu: 52, mau: "#FFFFFF", mau_vien: "#111111", vien: 6, so_tu_toi_da: 8,
         vi_tri_y: 0.92, font: kho-mau/font/Inter-Bold.ttf, font_du_phong: C:/Windows/Fonts/arialbd.ttf}
chuyen_canh_mac_dinh: {kieu: cat, thoi_luong: 0.3}
may_quay_mac_dinh: zoom-cham
```

## Lược đồ kich-ban.json
Toạ độ chuẩn hoá 0..1 theo khung; cỡ chữ tính theo khung cao 1080 rồi nhân tỉ lệ. Đường dẫn ảnh / âm thanh tương đối với thư mục dự án trước, rồi `kho-mau/`. Tệp thiếu: ảnh vẽ khung giữ chỗ ghi tên tệp, âm thanh bỏ qua + cảnh báo (để luồng vẫn chạy khi kho còn trống).
```jsonc
{
  "tieu_de": "Why You Sell Winners Too Early",
  "ngon_ngu": "en",
  "nhac_nen": {"tep": "nhac-nen/curious-light.mp3", "am_luong": 0.07},   // hoặc null
  "canh": [
    {
      "id": "c01",                       // duy nhất
      "phan": "hook",                    // hook | boi-canh | giai-thich | vi-du | nghien-cuu | cach-tranh | tom-tat | ket (chỉ để tổ chức)
      "loi": "Imagine you bought two stocks...",  // lời đọc + phụ đề
      "loi_doc": null,                   // tuỳ chọn: thay chữ để máy đọc đúng hơn
      "thoi_luong": null,                // tuỳ chọn: tối thiểu (giây), cảnh không lời bắt buộc có
      "dem_truoc": null, "dem_sau": null,  // null = mặc định (xem Dòng thời gian)
      "toc_do": null,                    // tuỳ chọn 0,8–1,3: tốc độ giọng riêng cảnh này (ghi đè tts.<động cơ>.toc_do)
      "nghi": null,                      // tuỳ chọn {"cham": 0.6, ...}: ghi đè tts.nghi cho cảnh này
      "nen": "#FFFFFF",                  // mã màu hoặc ảnh (phong-nen/...)
      "may_quay": "zoom-cham",           // hoặc {"kieu": "...", "muc": 0.06}
      "chuyen_canh": {"kieu": "mo-dan", "thoi_luong": 0.3},   // chuyển VÀO cảnh này
      "lop": [
        {"anh": "nhan-vat/max__lo-lang__dung.png", "vi_tri": [0.3, 0.85], "neo": "day",
         "co": 0.22, "hieu_ung": "bat-len", "tre": 0.0, "lien_tuc": "nhun", "het": null,
         "lat": false, "am_thanh": "am-thanh/pop.wav"}
      ],
      "chu": [
        {"noi_dung": "LOSS AVERSION", "vi_tri": [0.68, 0.3], "co": 96, "mau": "#E53935",
         "vien": 0, "mau_vien": "#000000", "nen": null, "hieu_ung": "go-chu", "tre": 0.6,
         "am_thanh": "am-thanh/tick.wav"}
      ],
      "am_thanh": [{"tep": "am-thanh/whoosh.wav", "tre": 0.0, "am_luong": 0.8}]
    }
  ]
}
```
Tập giá trị (kichban.py kiểm, sai thì báo lỗi rõ cảnh nào, khoá nào):
- `hieu_ung` (vào): `khong`, `bat-len`, `mo-dan`, `truot-trai`, `truot-phai`, `truot-len`, `roi-xuong`, `go-chu` (chỉ chữ), `phong-to`.
- `lien_tuc` (lặp khi đang hiện): `khong`, `nhun`, `lac`, `tho`, `run`.
- `neo`: `giua` (mặc định), `day`.
- `may_quay`: `dung-yen`, `zoom-cham`, `zoom-ra`, `lia-trai`, `lia-phai`, `dam` (đẩy nhanh vào đầu cảnh), `rung`.
- `chuyen_canh.kieu`: `cat`, `mo-dan`, `toi-den`, `nhay-trang`, `truot-trai`, `truot-len`, `zoom-vao`.
- `het`: giây (tính trong cảnh) để lớp mờ đi trong 0,25s.
Agent phân tích kênh có thể đề xuất thêm hiệu ứng → ghi vào docs, KHÔNG tự sửa code lõi.

## Dòng thời gian
Thời lượng cảnh = `dem_truoc` (mặc định `am_thanh.dem_truoc` 0,15 nếu có lời, 0 nếu không) + giây giọng + `dem_sau` (mặc định `nghi_giua_canh`; cảnh kế có `phan` khác -> `nghi_cuoi_phan`), tối thiểu `thoi_luong` và 0,5s. Cảnh nối tiếp, không chồng tiếng. Chuyển cảnh = trộn khung cuối (đứng yên) của cảnh trước với cảnh hiện tại trong `thoi_luong` đầu cảnh. Số khung mỗi cảnh = round(cuối·fps) − round(đầu·fps) để không trôi.

## Quy tắc chung
- Không thêm thư viện ngoài danh sách trên nếu không ghi rõ lý do trong báo cáo.
- Không commit / push. Không tạo tệp ngoài `D:\Project\Truonglb\project_02`.
- Python không có trên máy viết code: tự soát kỹ (cú pháp, import, chữ ký), không cài gì.
- Thông báo lỗi tiếng Việt, kèm cách sửa.
