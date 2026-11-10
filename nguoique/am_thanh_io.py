"""Đọc / ghi âm thanh: WAV 16-bit mono, giải mã mọi định dạng qua ffmpeg."""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import wave
from pathlib import Path

import numpy as np

_FFMPEG: str | None = None


def can_ffmpeg() -> str:
    """Đường dẫn ffmpeg (biến môi trường NQ_FFMPEG hoặc PATH). Thiếu -> RuntimeError tiếng Việt."""
    global _FFMPEG
    if _FFMPEG:
        return _FFMPEG
    ung_vien = []
    if os.environ.get("NQ_FFMPEG"):
        ung_vien.append(os.environ["NQ_FFMPEG"])
    tim = shutil.which("ffmpeg")
    if tim:
        ung_vien.append(tim)
    for p in ung_vien:
        if p and Path(p).is_file():
            _FFMPEG = str(p)
            return _FFMPEG
    raise RuntimeError(
        "Không tìm thấy ffmpeg.\n"
        "Cách sửa: chạy `winget install Gyan.FFmpeg` (hoặc setup.ps1), đóng rồi mở lại terminal;\n"
        "hoặc đặt biến môi trường NQ_FFMPEG trỏ tới ffmpeg.exe."
    )


def ghi_wav(path, mau: np.ndarray, tan_so: int) -> None:
    """float32 [-1, 1] -> WAV PCM 16-bit mono. Mảng nhiều kênh được trộn về mono."""
    x = np.asarray(mau, dtype=np.float32)
    if x.ndim > 1:
        # (n, kenh) hoặc (kenh, n): lấy trục dài hơn làm thời gian
        x = x.mean(axis=1) if x.shape[0] >= x.shape[1] else x.mean(axis=0)
    x = np.nan_to_num(x.reshape(-1), nan=0.0, posinf=1.0, neginf=-1.0)
    pcm = (np.clip(x, -1.0, 1.0) * 32767.0).round().astype("<i2")
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(tan_so))
        w.writeframes(pcm.tobytes())


def doc_wav(du_lieu: bytes) -> tuple[np.ndarray, int]:
    """Bytes WAV (PCM 8/16/24/32-bit hoặc float 32/64, mọi số kênh) -> (float32 mono, tần số)."""
    if len(du_lieu) < 12 or du_lieu[:4] not in (b"RIFF", b"RF64") or du_lieu[8:12] != b"WAVE":
        raise ValueError("Dữ liệu không phải tệp WAV (thiếu đầu RIFF/WAVE).")
    vt = 12
    fmt = None
    kieu_con = None
    data = None
    n = len(du_lieu)
    while vt + 8 <= n:
        ma = du_lieu[vt:vt + 4]
        co = struct.unpack_from("<I", du_lieu, vt + 4)[0]
        than = vt + 8
        if ma == b"fmt ":
            fmt = struct.unpack_from("<HHIIHH", du_lieu, than)
            if fmt[0] == 0xFFFE and co >= 26:
                kieu_con = struct.unpack_from("<H", du_lieu, than + 24)[0]
        elif ma == b"data":
            if co == 0xFFFFFFFF or than + co > n:
                co = n - than  # tệp ghi dạng luồng / RF64: lấy đến hết
            data = du_lieu[than:than + co]
            if fmt is not None:
                break
        vt = than + co + (co & 1)
    if fmt is None or data is None:
        raise ValueError("Tệp WAV thiếu khối 'fmt ' hoặc 'data'.")
    kieu, kenh, tan_so, _, _, bit = fmt
    if kieu == 0xFFFE:
        kieu = kieu_con if kieu_con is not None else 1
    kenh = max(1, int(kenh))
    byte_mau = max(1, bit // 8)
    du = len(data) % (byte_mau * kenh)
    if du:
        data = data[: len(data) - du]
    if kieu == 1:
        if bit == 8:
            x = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        elif bit == 16:
            x = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768.0
        elif bit == 24:
            b = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
            v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)
            v = np.where(v >= (1 << 23), v - (1 << 24), v)
            x = v.astype(np.float32) / float(1 << 23)
        elif bit == 32:
            x = np.frombuffer(data, dtype="<i4").astype(np.float32) / float(1 << 31)
        else:
            raise ValueError(f"WAV PCM {bit}-bit chưa hỗ trợ.")
    elif kieu == 3:
        if bit == 32:
            x = np.frombuffer(data, dtype="<f4").astype(np.float32)
        elif bit == 64:
            x = np.frombuffer(data, dtype="<f8").astype(np.float32)
        else:
            raise ValueError(f"WAV float {bit}-bit chưa hỗ trợ.")
    else:
        raise ValueError(f"WAV mã định dạng {kieu} chưa hỗ trợ (chỉ PCM / float).")
    if kenh > 1:
        x = x.reshape(-1, kenh).mean(axis=1)
    return np.ascontiguousarray(x, dtype=np.float32), int(tan_so)


def giai_ma(path, tan_so: int) -> np.ndarray:
    """Mọi định dạng (wav, mp3, ogg...) -> float32 mono ở tần số `tan_so`, qua ffmpeg."""
    ff = can_ffmpeg()
    lenh = [ff, "-v", "error", "-nostdin", "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le",
            "-ac", "1", "-ar", str(int(tan_so)), "-"]
    kq = subprocess.run(lenh, capture_output=True)
    if kq.returncode != 0:
        loi = kq.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"ffmpeg không giải mã được '{path}':\n{loi}\nCách sửa: kiểm tệp có mở được không, hoặc đổi sang .wav / .mp3.")
    return np.frombuffer(kq.stdout, dtype="<f4").astype(np.float32)


def thoi_luong_wav(path) -> float:
    """Số giây của tệp WAV."""
    x, sr = doc_wav(Path(path).read_bytes())
    return float(x.size) / float(sr) if sr else 0.0
