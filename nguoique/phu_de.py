"""Phụ đề: chia lời thành cụm ngắn theo dấu câu, xuất .srt.

Thời gian: nếu dòng thời gian có mốc từng mẩu giọng ("moc", từ tệp mốc giong.py ghi) và lời tách ra
cùng số mẩu (chuan_hoa.tach_manh) -> mỗi mẩu lời khớp đúng mẩu giọng của nó, cụm trong mẩu chia theo
ký tự; tắt trong khoảng nghỉ dài (kênh tham khảo: phụ đề tắt ~0,09s sau câu, trống lúc nghỉ).
Không có mốc / lệch số mẩu -> cách cũ: chia cả khoảng giọng của cảnh theo số ký tự.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .chuan_hoa import tach_manh

NOI_KHI_NGHI_DUOI = 0.3  # nghỉ ngắn hơn (dấu phẩy): giữ cụm đến mẩu kế cho khỏi nháy
TAT_SAU_MANH = 0.09      # nghỉ dài: cụm tắt sau khi hết tiếng bấy nhiêu giây

# Tách SAU dấu câu có khoảng trắng theo sau ("10,000" không bị tách).
_TACH = re.compile(r"(?<=[.!?;:,—–…])\s+")


def chia_cum(loi: str, so_tu_toi_da: int = 8) -> list[str]:
    """Chia lời thành các cụm ≤ so_tu_toi_da từ; ưu tiên ngắt ở dấu câu, cụm dài chia đều."""
    so_tu_toi_da = max(1, int(so_tu_toi_da))
    cum: list[str] = []
    for doan in _TACH.split((loi or "").strip()):
        tu = doan.split()
        if not tu:
            continue
        n = len(tu)
        so_phan = math.ceil(n / so_tu_toi_da)
        moi_phan = math.ceil(n / so_phan)
        for i in range(0, n, moi_phan):
            cum.append(" ".join(tu[i:i + moi_phan]))
    return cum


def _chia_theo_ky_tu(cum: list[str], dau: float, giay: float) -> list[tuple[float, float, str]]:
    trong_so = [max(1, len(c)) for c in cum]
    tong = float(sum(trong_so))
    kq, t = [], dau
    for c, w in zip(cum, trong_so):
        d = giay * w / tong
        kq.append((t, t + d, c))
        t += d
    return kq


def _theo_moc(loi: str, moc: list[dict], so_tu: int, het_canh: float) -> list[tuple[float, float, str]] | None:
    """Khớp từng mẩu lời với mẩu giọng. Lệch số mẩu -> None (dùng cách cũ)."""
    manh = [c for c, _ in tach_manh(loi)]
    if not manh or len(manh) != len(moc):
        return None
    kq: list[tuple[float, float, str]] = []
    for i, (chu, m) in enumerate(zip(manh, moc)):
        a, b = float(m["bat_dau"]), float(m["ket_thuc"])
        if b - a <= 0.02:
            return None
        cum = chia_cum(chu, so_tu)
        if not cum:
            return None
        phan = _chia_theo_ky_tu(cum, a, b - a)
        ke = float(moc[i + 1]["bat_dau"]) if i + 1 < len(moc) else het_canh
        nghi = max(0.0, ke - b)
        keo = nghi if nghi < NOI_KHI_NGHI_DUOI else min(TAT_SAU_MANH, nghi)
        bd, kt, c = phan[-1]
        phan[-1] = (bd, kt + keo, c)
        kq.extend(phan)
    return kq


def lap_phu_de(ds: list[dict], ch: dict) -> list[tuple[float, float, str]]:
    """Từ dòng thời gian -> [(bắt đầu, kết thúc, chữ)] (giây tuyệt đối). Ưu tiên mốc từng mẩu giọng."""
    so_tu = int((ch.get("phu_de") or {}).get("so_tu_toi_da", 8))
    kq: list[tuple[float, float, str]] = []
    for muc in ds:
        loi = (muc["canh"].get("loi") or "").strip()
        if not loi:
            continue
        moc = muc.get("moc")
        if moc and float(muc.get("giong_giay") or 0.0) > 0.05:
            theo_moc = _theo_moc(loi, moc, so_tu, float(muc["ket_thuc"]))
            if theo_moc is not None:
                kq.extend(theo_moc)
                continue
        cum = chia_cum(loi, so_tu)
        if not cum:
            continue
        dau = float(muc["bat_dau_giong"])
        giay = float(muc.get("giong_giay") or 0.0)
        if giay <= 0.05:  # chưa có giọng: trải hết phần còn lại của cảnh
            giay = max(0.3, float(muc["ket_thuc"]) - dau)
        trong_so = [max(1, len(c)) for c in cum]
        tong = float(sum(trong_so))
        t = dau
        for c, w in zip(cum, trong_so):
            d = giay * w / tong
            kq.append((t, t + d, c))
            t += d
    return kq


def _tg(s: float) -> str:
    ms = max(0, int(round(s * 1000)))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    giay, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{giay:02d},{ms:03d}"


def ghi_srt(cum: list[tuple[float, float, str]], path) -> Path:
    """Ghi tệp .srt (UTF-8)."""
    dong: list[str] = []
    for i, (bd, kt, chu) in enumerate(cum, 1):
        dong += [str(i), f"{_tg(bd)} --> {_tg(kt)}", chu, ""]
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(dong), encoding="utf-8")
    return p
