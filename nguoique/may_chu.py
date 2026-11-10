"""Máy chủ giọng đọc (FastAPI + uvicorn): nạp mô hình MỘT lần, các lệnh `nq dung` / `nq giong` gọi qua HTTP.

GET  /trang-thai -> {"dong_co": "...", "tan_so": 24000, "dinh_danh": "...", "ho_tro": ["toc_do"]}
POST /doc  {"van_ban": "...", "toc_do": 1.05 (tuỳ chọn, 0,5–2)} -> audio/wav (16-bit mono)

Lưu ý: KHÔNG dùng `from __future__ import annotations` ở tệp này — FastAPI / pydantic cần
kiểu thật của mô hình khai báo ở cấp module.
"""

import io
import threading
import wave
from typing import Optional

import numpy as np

try:
    from pydantic import BaseModel
except ImportError:  # chưa cài extras may-chu; chay_may_chu sẽ báo lỗi rõ
    BaseModel = None


if BaseModel is not None:

    class YeuCauDoc(BaseModel):
        van_ban: str
        toc_do: Optional[float] = None  # canh.toc_do; None = tốc độ trong config của máy chủ

else:
    YeuCauDoc = None


def _wav_bytes(mau: np.ndarray, tan_so: int) -> bytes:
    mau = np.clip(np.asarray(mau, dtype=np.float32).reshape(-1), -1.0, 1.0)
    pcm = (mau * 32767.0).astype("<i2")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(tan_so))
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


def chay_may_chu(ch: dict, host: str = "127.0.0.1", port: int = 8765):
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import Response
    except ImportError as loi:
        raise RuntimeError(
            "Chưa cài fastapi / uvicorn.\n  Cách sửa: `pip install -e \".[may-chu]\"` trong .venv (hoặc chạy lại setup.ps1)."
        ) from loi
    if YeuCauDoc is None:
        raise RuntimeError("Chưa cài pydantic (đi kèm fastapi). Cách sửa: `pip install -e \".[may-chu]\"`.")

    from .giong import _dinh_danh_giong, tao_dong_co_truc_tiep

    if host not in ("127.0.0.1", "localhost", "::1"):
        print(
            f"CẢNH BÁO: máy chủ giọng mở ở {host}:{port} và KHÔNG có xác thực — "
            "máy khác trong mạng gọi được. Chỉ dùng trong mạng tin cậy; bình thường để 127.0.0.1."
        )

    dong_co = tao_dong_co_truc_tiep(ch)  # nạp một lần
    khoa = threading.Lock()  # GPU / mô hình không an toàn khi chạy song song
    print(f"Động cơ {dong_co.ten} sẵn sàng ({dong_co.tan_so} Hz).")

    app = FastAPI(title="nguoique - may chu giong")

    dinh_danh = "|".join(str(x) for x in _dinh_danh_giong(ch))  # client so với config của mình

    @app.get("/trang-thai")
    def trang_thai():
        return {"dong_co": dong_co.ten, "tan_so": int(dong_co.tan_so), "dinh_danh": dinh_danh, "ho_tro": ["toc_do"]}

    @app.post("/doc")
    def doc(yeu_cau: YeuCauDoc):
        van_ban = (yeu_cau.van_ban or "").strip()
        if not van_ban:
            raise HTTPException(status_code=400, detail="van_ban rỗng")
        toc_do = yeu_cau.toc_do
        if toc_do is not None and not 0.5 <= float(toc_do) <= 2.0:
            raise HTTPException(status_code=400, detail="toc_do phải trong 0.5..2")
        try:
            with khoa:
                mau, sr = dong_co.doc(van_ban, toc_do=toc_do) if toc_do else dong_co.doc(van_ban)
        except Exception as loi:  # trả lỗi cho client thay vì sập máy chủ
            raise HTTPException(status_code=500, detail=f"Lỗi đọc: {type(loi).__name__}: {loi}")
        return Response(content=_wav_bytes(mau, sr), media_type="audio/wav")

    print(f"Máy chủ giọng: http://{host}:{port}  (Ctrl+C để dừng)")
    uvicorn.run(app, host=host, port=int(port), log_level="info")
