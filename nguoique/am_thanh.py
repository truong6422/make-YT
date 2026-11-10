"""Âm thanh: ghép giọng + hiệu ứng theo dòng thời gian (numpy), trộn nhạc nền bằng ffmpeg."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np

from .am_thanh_io import can_ffmpeg, doc_wav, ghi_wav, giai_ma
from .cauhinh import kho_mau, tim_tep

_da_bao: set[str] = set()

# Nhạc nền mặc định 0,07 (≈ −23 dB so với giọng khi tệp nhạc và giọng cùng độ lớn); trung vị kênh tham khảo
# ≈ −27 dB dưới giọng (docs/02 mục 0) -> sidechain chỉ cần giảm THÊM 3–6 dB khi đang nói.
NHAC_NEN_AM_LUONG_MAC_DINH = 0.07
# sidechaincompress (dò RMS giọng): giọng Kokoro trung vị ~−21 dBFS, đoạn to ~−16 dBFS.
#   ngưỡng 0,05 (≈ −26 dBFS), tỉ lệ 2,5 -> giảm (vượt ngưỡng × (1 − 1/2,5)):
#   −21 dBFS: 5 dB × 0,6 ≈ 3 dB ; −16 dBFS: 10 dB × 0,6 ≈ 6 dB. Lúc nghỉ giữa câu nhạc trở lại mức gốc.
#   (Bản cũ 0,02 / 6 giảm ~11 dB — nhạc "thở" rõ, kênh tham khảo không có kiểu đó.)
SC_NGUONG = 0.05
SC_TI_LE = 2.5
SC_ATTACK_MS = 20
SC_RELEASE_MS = 300


def _bao_mot_lan(khoa: str, thong_diep: str) -> None:
    if khoa not in _da_bao:
        _da_bao.add(khoa)
        print(f"CẢNH BÁO: {thong_diep}", file=sys.stderr)


def _cong(dich: np.ndarray, mau: np.ndarray, vi_tri_mau: float) -> None:
    i = int(round(vi_tri_mau))
    if mau.size == 0 or i >= dich.size:
        return
    if i < 0:
        mau = mau[-i:]
        i = 0
    j = min(dich.size, i + mau.size)
    dich[i:j] += mau[: j - i]


def _nap(path: Path, tan_so: int) -> np.ndarray:
    """WAV đúng tần số đọc thẳng; còn lại (mp3, wav khác tần số...) qua ffmpeg."""
    if path.suffix.lower() == ".wav":
        try:
            x, sr = doc_wav(path.read_bytes())
            if sr == tan_so:
                return x
        except ValueError:
            pass
    return giai_ma(path, tan_so)


def _hieu_ung_cua_canh(canh: dict) -> list[tuple[str, float, float]]:
    """[(tệp, trễ trong cảnh, âm lượng)] từ am_thanh của cảnh + khoá am_thanh của lớp / chữ."""
    kq = [(m["tep"], float(m.get("tre") or 0.0), float(m.get("am_luong", 1.0))) for m in canh.get("am_thanh") or []]
    for muc in list(canh.get("lop") or []) + list(canh.get("chu") or []):
        at = muc.get("am_thanh")
        if not at:
            continue
        if isinstance(at, str):
            at = {"tep": at, "am_luong": 1.0}
        kq.append((at["tep"], float(muc.get("tre") or 0.0), float(at.get("am_luong", 1.0))))
    return kq


def _chay_ffmpeg(lenh: list[str]) -> tuple[int, str]:
    kq = subprocess.run(lenh, capture_output=True)
    return kq.returncode, kq.stderr.decode("utf-8", "replace").strip()


def tron_am_thanh(kb: dict, ds: list[dict], tong: float, thu_muc_du_an: Path, thu_muc_build: Path,
                  ch: dict) -> Path:
    """Ghép build/giong.wav + build/hieu-ung.wav rồi trộn với nhạc nền -> build/tron.wav (stereo). Trả đường dẫn."""
    am = ch.get("am_thanh") or {}
    sr = int(am.get("tan_so", 48000))
    build = Path(thu_muc_build)
    build.mkdir(parents=True, exist_ok=True)
    kho = kho_mau(ch)
    n = max(1, int(math.ceil(tong * sr)))

    giong = np.zeros(n, dtype=np.float32)
    hieu_ung = np.zeros(n, dtype=np.float32)
    bo_dem: dict[Path, np.ndarray] = {}

    for muc in ds:
        if muc.get("giong"):
            _cong(giong, _nap(Path(muc["giong"]), sr), float(muc["bat_dau_giong"]) * sr)
        for tep, tre, al in _hieu_ung_cua_canh(muc["canh"]):
            p = tim_tep(tep, thu_muc_du_an, kho)
            if p is None:
                _bao_mot_lan(f"am:{tep}", f"thiếu âm thanh '{tep}' — bỏ qua. Thêm tệp vào kho-mau/{tep} hoặc thư mục dự án.")
                continue
            if p not in bo_dem:
                try:
                    bo_dem[p] = _nap(p, sr)
                except (RuntimeError, ValueError) as e:
                    _bao_mot_lan(f"am:{tep}", f"không đọc được '{p}' — bỏ qua. ({e})")
                    bo_dem[p] = np.zeros(0, dtype=np.float32)
            _cong(hieu_ung, bo_dem[p] * al, (float(muc["bat_dau"]) + tre) * sr)

    dinh = float(np.max(np.abs(hieu_ung))) if hieu_ung.size else 0.0
    if dinh > 0.98:
        hieu_ung *= 0.98 / dinh  # tránh vỡ tiếng khi nhiều hiệu ứng chồng nhau
    dinh = float(np.max(np.abs(giong))) if giong.size else 0.0
    if dinh > 0.99:
        giong *= 0.99 / dinh

    tep_giong = build / "giong.wav"
    tep_hu = build / "hieu-ung.wav"
    tep_tron = build / "tron.wav"
    ghi_wav(tep_giong, giong, sr)
    ghi_wav(tep_hu, hieu_ung, sr)

    nhac = None
    al_nhac = float(am.get("nhac_nen_am_luong", NHAC_NEN_AM_LUONG_MAC_DINH))
    nn = kb.get("nhac_nen")
    if nn:
        p = tim_tep(nn["tep"], thu_muc_du_an, kho)
        if p is None:
            _bao_mot_lan(f"nhac:{nn['tep']}", f"thiếu nhạc nền '{nn['tep']}' — dựng không nhạc. Thêm tệp vào kho-mau/{nn['tep']}.")
        else:
            nhac = p
            al_nhac = float(nn.get("am_luong", al_nhac))
    giam = bool(am.get("giam_nhac_khi_noi", True))

    ff = can_ffmpeg()
    for gioi_han in ("alimiter=limit=0.95:level=disabled", "alimiter=limit=0.95"):
        lenh = _lenh_tron(ff, tep_giong, tep_hu, nhac, tep_tron, tong, sr, al_nhac, giam, gioi_han)
        ma, loi = _chay_ffmpeg(lenh)
        if ma == 0:
            return tep_tron
    raise RuntimeError(
        f"ffmpeg trộn âm thanh thất bại:\n{loi}\n"
        "Cách sửa: cập nhật ffmpeg (cần bản ≥ 5: `winget upgrade Gyan.FFmpeg`), kiểm tệp nhạc nền mở được không."
    )


def _lenh_tron(ff: str, tep_giong: Path, tep_hu: Path, nhac: Path | None, tep_ra: Path, tong: float, sr: int,
               al_nhac: float, giam: bool, gioi_han: str) -> list[str]:
    dinh_dang = f"aformat=sample_fmts=fltp:sample_rates={sr}:channel_layouts=stereo"
    lenh = [ff, "-y", "-hide_banner", "-loglevel", "error", "-nostdin", "-i", str(tep_giong), "-i", str(tep_hu)]
    if nhac is not None:
        lenh += ["-stream_loop", "-1", "-i", str(nhac)]
        fade_ra = max(0.0, tong - 3.0)
        loc = f"[0:a]{dinh_dang},asplit=2[g][sc];" if giam else f"[0:a]{dinh_dang}[g];"
        loc += f"[1:a]{dinh_dang}[h];"
        loc += (f"[2:a]{dinh_dang},atrim=0:{tong:.3f},asetpts=PTS-STARTPTS,volume={al_nhac:.4f},"
                f"afade=t=in:st=0:d=1.5,afade=t=out:st={fade_ra:.3f}:d=3[n0];")
        if giam:
            loc += (f"[n0][sc]sidechaincompress=threshold={SC_NGUONG}:ratio={SC_TI_LE}:"
                    f"attack={SC_ATTACK_MS}:release={SC_RELEASE_MS}[n];")
        else:
            loc += "[n0]anull[n];"
        loc += f"[g][h][n]amix=inputs=3:duration=first:normalize=0,{gioi_han}[ra]"
    else:
        loc = (f"[0:a]{dinh_dang}[g];[1:a]{dinh_dang}[h];"
               f"[g][h]amix=inputs=2:duration=first:normalize=0,{gioi_han}[ra]")
    lenh += ["-filter_complex", loc, "-map", "[ra]", "-ac", "2", "-ar", str(sr), "-t", f"{tong:.3f}",
             "-c:a", "pcm_s16le", str(tep_ra)]
    return lenh
