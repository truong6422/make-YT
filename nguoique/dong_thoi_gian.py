"""Lập dòng thời gian: mỗi cảnh = dem_truoc + giây giọng + dem_sau (tối thiểu thoi_luong và 0,5s).

Mặc định (config `am_thanh`, số đo ở docs/02):
- dem_truoc = `dem_truoc` (0,15s) nếu cảnh có lời, 0 nếu không — hình đổi sớm hơn lời ~0,16s như kênh tham khảo.
- dem_sau   = `nghi_giua_canh` (0,35s); nếu cảnh kế có `phan` khác cảnh này -> `nghi_cuoi_phan` (0,9s).
  dem_sau / dem_truoc ghi trong cảnh luôn thắng.
Nếu tệp giọng có tệp mốc cạnh nó (<id>-<băm>.json, giong.py ghi), gắn mốc từng mẩu (giây tuyệt đối) vào "moc".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THOI_LUONG_TOI_THIEU = 0.5
DEM_TRUOC_MAC_DINH = 0.15
NGHI_GIUA_CANH_MAC_DINH = 0.35
NGHI_CUOI_PHAN_MAC_DINH = 0.9


def doc_moc(tep_giong, giay: float | None = None) -> list[dict] | None:
    """Đọc tệp mốc cạnh tệp giọng -> [{"bat_dau", "ket_thuc", "chu", "loai"}] (giây tính từ đầu tệp giọng).
    Không có / hỏng / lệch thời lượng tệp giọng quá 0,05s (mốc cũ) -> None."""
    p = Path(tep_giong).with_suffix(".json")
    if not p.is_file():
        return None
    try:
        du_lieu = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    manh = du_lieu.get("manh") if isinstance(du_lieu, dict) else None
    if not isinstance(manh, list) or not manh:
        return None
    try:
        if giay is not None and abs(float(du_lieu.get("thoi_luong", giay)) - float(giay)) > 0.05:
            return None
        kq = []
        truoc = 0.0
        for m in manh:
            a, b = float(m["bat_dau"]), float(m["ket_thuc"])
            if b < a or a < truoc - 1e-6:
                return None
            kq.append({"bat_dau": a, "ket_thuc": b, "chu": str(m.get("chu", "")), "loai": m.get("loai")})
            truoc = b
    except (KeyError, TypeError, ValueError):
        return None
    return kq


def lap_dong_thoi_gian(kb: dict, giong: dict | None, ch: dict) -> tuple[list[dict], float]:
    """-> (ds, tong). Mỗi phần tử ds:
    {"id", "canh", "bat_dau", "ket_thuc", "thoi_luong", "giong" (Path|None), "giong_giay",
     "bat_dau_giong" (giây tuyệt đối khi lời bắt đầu), "dem_truoc", "dem_sau",
     "moc" (list mốc từng mẩu, giây tuyệt đối | None)}.
    Cảnh nối tiếp nhau, không chồng tiếng.
    """
    giong = giong or {}
    am = ch.get("am_thanh") or {}
    nghi = float(am.get("nghi_giua_canh", NGHI_GIUA_CANH_MAC_DINH))
    nghi_phan = float(am.get("nghi_cuoi_phan", NGHI_CUOI_PHAN_MAC_DINH))
    dem_truoc_md = float(am.get("dem_truoc", DEM_TRUOC_MAC_DINH))
    ds_canh = list(kb.get("canh") or [])
    ds: list[dict] = []
    t = 0.0
    for i, canh in enumerate(ds_canh):
        cid = canh["id"]
        co_loi = bool((canh.get("loi") or "").strip())
        tep, giay = None, 0.0
        g = giong.get(cid)
        if g:
            tep = Path(g[0])
            giay = max(0.0, float(g[1]))
            if not tep.is_file():
                print(f"CẢNH BÁO: tệp giọng của cảnh {cid} không còn ({tep}) — cảnh này im lặng.", file=sys.stderr)
                tep, giay = None, 0.0
        elif co_loi:
            print(f"CẢNH BÁO: cảnh {cid} có lời nhưng chưa có giọng — cảnh này im lặng.", file=sys.stderr)

        dem_truoc = canh.get("dem_truoc")
        if dem_truoc is None:
            dem_truoc = dem_truoc_md if co_loi else 0.0
        dem_sau = canh.get("dem_sau")
        if dem_sau is None:
            dem_sau = nghi
            ke = ds_canh[i + 1] if i + 1 < len(ds_canh) else None
            if ke is not None and canh.get("phan") and ke.get("phan") and ke.get("phan") != canh.get("phan"):
                dem_sau = nghi_phan  # đổi phần: nghỉ dài hơn (docs/02 mục 0)
        dai = float(dem_truoc) + giay + float(dem_sau)
        dai = max(dai, float(canh.get("thoi_luong") or 0.0), THOI_LUONG_TOI_THIEU)
        bat_dau_giong = t + float(dem_truoc)
        moc = None
        if tep is not None:
            tho = doc_moc(tep, giay)
            if tho:
                moc = [dict(m, bat_dau=bat_dau_giong + m["bat_dau"], ket_thuc=bat_dau_giong + m["ket_thuc"]) for m in tho]
        ds.append({
            "id": cid,
            "canh": canh,
            "bat_dau": t,
            "ket_thuc": t + dai,
            "thoi_luong": dai,
            "giong": tep,
            "giong_giay": giay,
            "bat_dau_giong": bat_dau_giong,
            "dem_truoc": float(dem_truoc),
            "dem_sau": float(dem_sau),
            "moc": moc,
        })
        t += dai
    return ds, t


def so_khung(bat_dau: float, ket_thuc: float, fps: float) -> tuple[int, int]:
    """(khung đầu, khung cuối không gồm) = (round(đầu·fps), round(cuối·fps)) — không trôi khi cộng dồn."""
    return int(round(bat_dau * fps)), int(round(ket_thuc * fps))
