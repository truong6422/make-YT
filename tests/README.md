# Bộ test

Chạy trên máy Acer (có Python 3.11 + `.venv` đã cài gói), từ gốc repo:

```powershell
.\.venv\Scripts\Activate.ps1
pip install pytest          # nếu chưa có
python -m pytest            # chạy tất cả
python -m pytest -q tests/test_chuan_hoa.py   # chạy một tệp
python -m pytest -k bo_dem  # chạy theo tên
```

- Không cần mô hình giọng, GPU hay mạng: test dùng động cơ `gia-lap` (tiếng bíp), chế độ `truc-tiep`.
- `conftest.py` đọc `config.yaml` rồi ghi đè (giọng giả lập, kho mẫu / dự án trong thư mục tạm của pytest),
  nên không đụng `kho-mau/`, `du-an/` thật.
- `test_tich_hop.py` dựng MP4 thật (`nq dung --nhap`) nên cần `ffmpeg` + `ffprobe` trong PATH; thiếu thì tự bỏ qua (skip).
