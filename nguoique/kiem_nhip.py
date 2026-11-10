"""Kiểm nhịp kịch bản sau khi có giọng (`nq kiem-nhip <du-an>`): so dòng thời gian với khuôn docs/02.

Báo (chỉ khuyên, không chặn dựng):
1. cảnh dài > 8s mà không đổi gì bên trong (không lớp / chữ có `tre` hoặc `het` giữa cảnh, không `dong_tac`,
   `doi_anh`, không mốc máy quay `moc` / `diem`);
2. 60s đầu: độ dài cảnh trung bình > 3,5s;
3. tổng thời lượng ngoài 8–15 phút;
4. tốc độ đọc ước tính (số từ của `loi` / giây giọng, tính cả nghỉ trong cảnh) ngoài 150–175 từ/phút;
5. quá 2 phút liền không có chuyển cảnh `toi-den` (kênh tham khảo nháy đen ở ranh giới phần).
Ngưỡng đổi được trong config `kiem_nhip` (xem config.yaml).
"""

from __future__ import annotations

MAC_DINH = {
    "canh_khong_doi_toi_da": 8.0,
    "dau_video_giay": 60.0,
    "dau_video_tb_toi_da": 3.5,
    "tong_phut": [8.0, 15.0],
    "tu_moi_phut": [150.0, 175.0],
    "toi_den_cach_toi_da": 120.0,
}


def _nguong(ch: dict) -> dict:
    kq = dict(MAC_DINH)
    kq.update({k: v for k, v in ((ch or {}).get("kiem_nhip") or {}).items() if k in MAC_DINH and v is not None})
    return kq


def _so(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _mm_ss(giay: float) -> str:
    giay = max(0.0, float(giay))
    return f"{int(giay // 60)}:{giay % 60:04.1f}"


def co_doi_hinh(canh: dict, dai: float) -> bool:
    """Trong cảnh có gì đổi giữa chừng (sau 0s, trước khi hết cảnh) không."""
    for muc in list(canh.get("lop") or []) + list(canh.get("chu") or []):
        if not isinstance(muc, dict):
            continue
        for khoa in ("tre", "het"):
            v = _so(muc.get(khoa))
            if v is not None and 0.0 < v < dai:
                return True
        if muc.get("dong_tac") or muc.get("doi_anh"):
            return True
    mq = canh.get("may_quay")
    if isinstance(mq, dict) and (mq.get("moc") or mq.get("diem")):
        return True
    return bool(canh.get("dong_tac") or canh.get("doi_anh"))


def _kieu_chuyen(canh: dict) -> str:
    cc = canh.get("chuyen_canh")
    if isinstance(cc, dict):
        return str(cc.get("kieu") or "")
    return str(cc or "")


def kiem_nhip(kb: dict, ds: list[dict], tong: float, ch: dict) -> dict:
    """-> {"tong", "so_canh", "tu_moi_phut" (None nếu chưa có giọng), "tb_dau_video", "canh_bao": [chuỗi]}."""
    ng = _nguong(ch)
    canh_bao: list[str] = []

    # 1. cảnh dài không đổi hình
    for m in ds:
        dai = float(m["thoi_luong"])
        if dai > float(ng["canh_khong_doi_toi_da"]) and not co_doi_hinh(m["canh"], dai):
            canh_bao.append(
                f"Cảnh {m['id']} ({_mm_ss(m['bat_dau'])}) dài {dai:.1f}s mà không đổi hình. "
                "Cách sửa: tách cảnh, hoặc thêm lớp / chữ có 'tre' giữa cảnh (đổi biểu cảm, bật đạo cụ).")

    # 2. 60s đầu
    dau_giay = float(ng["dau_video_giay"])
    dau = [m for m in ds if float(m["bat_dau"]) < dau_giay]
    tb_dau = None
    if dau:
        het = min(dau_giay, float(dau[-1]["ket_thuc"]))
        tb_dau = het / len(dau)
        if tb_dau > float(ng["dau_video_tb_toi_da"]):
            canh_bao.append(
                f"{dau_giay:.0f}s đầu: cảnh trung bình {tb_dau:.1f}s (> {float(ng['dau_video_tb_toi_da']):g}s). "
                "Cách sửa: hook mỗi câu (hoặc nửa câu) một cảnh, ~3s/cảnh.")

    # 3. tổng thời lượng
    lo, hi = (float(x) for x in ng["tong_phut"])
    if not lo * 60 <= tong <= hi * 60:
        canh_bao.append(f"Tổng thời lượng {_mm_ss(tong)} nằm ngoài {lo:g}–{hi:g} phút.")

    # 4. tốc độ đọc
    so_tu = 0
    giay = 0.0
    for m in ds:
        g = float(m.get("giong_giay") or 0.0)
        if g > 0:
            so_tu += len(str(m["canh"].get("loi") or "").split())
            giay += g
    tu_phut = so_tu / giay * 60.0 if giay > 0 else None
    lo, hi = (float(x) for x in ng["tu_moi_phut"])
    if tu_phut is not None and not lo <= tu_phut <= hi:
        canh_bao.append(
            f"Tốc độ đọc ước tính {tu_phut:.0f} từ/phút, ngoài {lo:g}–{hi:g}. "
            "Cách sửa: chỉnh tts.<động cơ>.toc_do (hoặc canh.toc_do 0,8–1,3), hoặc tts.nghi.")

    # 5. toi-den
    moc = [0.0] + [float(m["bat_dau"]) for m in ds if _kieu_chuyen(m["canh"]) == "toi-den"] + [float(tong)]
    cach = float(ng["toi_den_cach_toi_da"])
    for a, b in zip(moc, moc[1:]):
        if b - a > cach:
            canh_bao.append(
                f"{_mm_ss(a)}–{_mm_ss(b)}: {(b - a) / 60:.1f} phút không có chuyển cảnh toi-den. "
                "Cách sửa: đặt chuyen_canh toi-den (0,15–0,3s) ở cảnh đầu phần / nhảy thời gian.")

    return {"tong": float(tong), "so_canh": len(ds), "tu_moi_phut": tu_phut, "tb_dau_video": tb_dau,
            "canh_bao": canh_bao}


def bao_cao_nhip(kq: dict) -> str:
    """Chuỗi in ra màn hình cho `nq kiem-nhip`."""
    dong = [f"Nhịp: {kq['so_canh']} cảnh, tổng {_mm_ss(kq['tong'])}"
            + (f", ~{kq['tu_moi_phut']:.0f} từ/phút" if kq.get("tu_moi_phut") else ", chưa có giọng")
            + (f", 60s đầu {kq['tb_dau_video']:.1f}s/cảnh" if kq.get("tb_dau_video") else "") + "."]
    if kq["canh_bao"]:
        dong.append(f"{len(kq['canh_bao'])} điểm cần xem:")
        dong += [f"  - {c}" for c in kq["canh_bao"]]
    else:
        dong.append("Không có gì lệch khuôn docs/02.")
    return "\n".join(dong)
