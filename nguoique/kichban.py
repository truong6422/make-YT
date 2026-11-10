"""Nạp kich-ban.json: kiểm giá trị theo hợp đồng, gom mọi lỗi vào một thông báo, điền mặc định."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

# ---- Tập giá trị (docs/00-HOP-DONG.md) ----
PHAN = ("hook", "boi-canh", "giai-thich", "vi-du", "nghien-cuu", "cach-tranh", "tom-tat", "ket")
HIEU_UNG_VAO = ("khong", "bat-len", "mo-dan", "truot-trai", "truot-phai", "truot-len", "roi-xuong", "go-chu", "phong-to",
                "bay-luon")  # bay-luon: lướt vào theo đường cong (docs/10)
HIEU_UNG_ANH = tuple(h for h in HIEU_UNG_VAO if h != "go-chu")  # go-chu chỉ dùng cho chữ
LIEN_TUC = ("khong", "nhun", "lac", "tho", "run")
NEO = ("giua", "day")
MAY_QUAY = ("dung-yen", "zoom-cham", "zoom-ra", "lia-trai", "lia-phai", "dam", "rung", "lac-tay")
EASING = ("ra", "vao-ra", "nay")  # nhân vật ghép / mốc máy quay (docs/10)
CHUYEN_CANH = ("cat", "mo-dan", "toi-den", "nhay-trang", "truot-trai", "truot-len", "zoom-vao")

# Mức mặc định của từng kiểu máy quay (zoom: +6%; lia: zoom 6% rồi lia; dam: đẩy 10%; rung: biên độ)
MUC_MAY_QUAY = {"dung-yen": 0.0, "zoom-cham": 0.06, "zoom-ra": 0.06, "lia-trai": 0.06, "lia-phai": 0.06,
                "dam": 0.10, "rung": 0.006, "lac-tay": 0.006}

_KHOA_CANH = {"id", "phan", "loi", "loi_doc", "thoi_luong", "dem_truoc", "dem_sau", "nen", "may_quay",
              "chuyen_canh", "lop", "chu", "am_thanh",
              "toc_do", "nghi"}  # toc_do / nghi: giọng từng cảnh (giong.py)
LOAI_NGHI = ("phay", "cham", "hoi", "ngat", "doan")  # khoá của canh.nghi (= tts.nghi)
_KHOA_LOP = {"anh", "vi_tri", "neo", "co", "hieu_ung", "tre", "lien_tuc", "het", "lat", "am_thanh",
             # nhân vật ghép bộ phận (docs/10-NHAN-VAT-GHEP.md)
             "nhan_vat", "bieu_cam", "tu_the", "dong_tac", "chop_mat", "noi", "di", "nhip_hinh"}
_KHOA_DONG_TAC = {"luc", "tu_the", "thoi_luong", "easing", "bieu_cam"}
_KHOA_DI = {"tu", "den", "luc", "thoi_luong", "chu_ky"}
_KHOA_MOC = {"luc", "zoom", "tam", "thoi_luong", "easing"}
_KHOA_THUONG_HIEU = {"anh", "vi_tri", "co", "do_mo"}
_KHOA_CHU = {"noi_dung", "vi_tri", "co", "mau", "vien", "mau_vien", "nen", "hieu_ung", "tre", "am_thanh",
             "lien_tuc", "het", "rong_toi_da", "font"}
_KHOA_GOC = {"tieu_de", "ngon_ngu", "nhac_nen", "canh"}
_KHOA_GOC_THEM = {"thumbnail"}  # khoá thêm hợp lệ, lõi giữ nguyên không kiểm (nq thumbnail đọc)
_KHOA_GOC_THEM |= {"thuong_hieu", "nhip_hinh"}  # có kiểm (docs/10)


class LoiKichBan(ValueError):
    """Kịch bản sai: thông điệp liệt kê mọi lỗi (cảnh nào, khoá nào, cách sửa)."""


def doc_mau(gia_tri) -> tuple[int, int, int, int]:
    """'#RGB' | '#RRGGBB' | '#RRGGBBAA' | [r,g,b(,a)] -> (r,g,b,a). Sai -> ValueError."""
    if isinstance(gia_tri, (list, tuple)) and len(gia_tri) in (3, 4):
        so = [int(v) for v in gia_tri] + ([255] if len(gia_tri) == 3 else [])
        if all(0 <= v <= 255 for v in so):
            return tuple(so)  # type: ignore[return-value]
        raise ValueError(f"màu {gia_tri!r} có thành phần ngoài 0..255")
    if not isinstance(gia_tri, str):
        raise ValueError(f"màu phải là chuỗi '#RRGGBB', nhận {gia_tri!r}")
    s = gia_tri.strip().lstrip("#")
    if len(s) in (3, 4):
        s = "".join(c * 2 for c in s)
    if len(s) == 6:
        s += "FF"
    if len(s) != 8:
        raise ValueError(f"màu {gia_tri!r} không đúng dạng '#RRGGBB'")
    try:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4, 6))  # type: ignore[return-value]
    except ValueError:
        raise ValueError(f"màu {gia_tri!r} có ký tự không phải hệ 16") from None


def la_mau(gia_tri) -> bool:
    """Chuỗi bắt đầu bằng '#' (hoặc danh sách số) được coi là mã màu; còn lại là đường dẫn ảnh."""
    return isinstance(gia_tri, (list, tuple)) or (isinstance(gia_tri, str) and gia_tri.strip().startswith("#"))


def _la_so(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class _Kiem:
    def __init__(self) -> None:
        self.loi: list[str] = []
        self.canh_bao: list[str] = []

    def them(self, cho: str, thong_diep: str) -> None:
        self.loi.append(f"- {cho}: {thong_diep}")

    def so(self, d: dict, khoa: str, cho: str, mac_dinh, nho_nhat=None, lon_nhat=None, cho_phep_none=False):
        v = d.get(khoa, mac_dinh)
        if v is None:
            if cho_phep_none or mac_dinh is None:
                return None
            v = mac_dinh
        if not _la_so(v):
            self.them(cho, f"'{khoa}' phải là số, nhận {v!r}")
            return mac_dinh
        if nho_nhat is not None and v < nho_nhat:
            self.them(cho, f"'{khoa}' = {v} nhỏ hơn {nho_nhat}")
            return mac_dinh
        if lon_nhat is not None and v > lon_nhat:
            self.them(cho, f"'{khoa}' = {v} lớn hơn {lon_nhat}")
            return mac_dinh
        return float(v)

    def chon(self, d: dict, khoa: str, cho: str, tap: tuple, mac_dinh: str, goi_y: str = ""):
        v = d.get(khoa, mac_dinh)
        if v is None:
            v = mac_dinh
        if not isinstance(v, str) or v not in tap:
            self.them(cho, f"'{khoa}' = {v!r} không hợp lệ; chọn một trong: {', '.join(tap)}{goi_y}")
            return mac_dinh
        return v

    def mau(self, d: dict, khoa: str, cho: str, mac_dinh, cho_phep_none=False):
        v = d.get(khoa, mac_dinh)
        if v is None:
            if cho_phep_none:
                return None
            v = mac_dinh
        try:
            doc_mau(v)
        except ValueError as e:
            self.them(cho, f"'{khoa}': {e}")
            return mac_dinh
        return v

    def vi_tri(self, d: dict, cho: str, mac_dinh=(0.5, 0.5)):
        v = d.get("vi_tri", list(mac_dinh))
        if v is None:
            v = list(mac_dinh)
        if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(_la_so(x) for x in v)):
            self.them(cho, f"'vi_tri' phải là [x, y] (số 0..1 theo khung), nhận {v!r}")
            return list(mac_dinh)
        if not all(-1.0 <= x <= 2.0 for x in v):
            self.them(cho, f"'vi_tri' = {v} quá xa khung (cho phép -1..2)")
            return list(mac_dinh)
        return [float(v[0]), float(v[1])]

    def khoa_la(self, d: dict, hop_le: set, cho: str) -> None:
        for k in d:
            if k not in hop_le and not str(k).startswith("_") and k != "ghi_chu":
                self.canh_bao.append(f"{cho}: khoá lạ '{k}' (bỏ qua — gõ nhầm?)")

    def am_thanh_don(self, v, cho: str, khoa="am_thanh"):
        """Âm thanh gắn vào lớp / chữ: None | 'tep' | {'tep','am_luong'}."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return {"tep": v, "am_luong": 1.0}
        if isinstance(v, dict) and isinstance(v.get("tep"), str) and v["tep"]:
            al = self.so(v, "am_luong", f"{cho}.{khoa}", 1.0, 0.0, 4.0)
            return {"tep": v["tep"], "am_luong": al}
        self.them(cho, f"'{khoa}' phải là đường dẫn chuỗi hoặc {{\"tep\": ..., \"am_luong\": ...}}, nhận {v!r}")
        return None


def _diem(k: _Kiem, d: dict, khoa: str, cho: str, mac_dinh, lo: float = -1.0, hi: float = 2.0) -> list:
    """[x, y] chuẩn hoá theo khung (như vi_tri) ở khoá bất kỳ."""
    v = d.get(khoa)
    if v is None:
        return list(mac_dinh)
    if not (isinstance(v, (list, tuple)) and len(v) == 2 and all(_la_so(x) for x in v)):
        k.them(cho, f"'{khoa}' phải là [x, y] (số theo khung), nhận {v!r}")
        return list(mac_dinh)
    if not all(lo <= x <= hi for x in v):
        k.them(cho, f"'{khoa}' = {v} ngoài khoảng {lo}..{hi}")
        return list(mac_dinh)
    return [float(v[0]), float(v[1])]


def _dung_sai(k: _Kiem, d: dict, khoa: str, cho: str, mac_dinh: bool) -> bool:
    v = d.get(khoa, mac_dinh)
    if v is None:
        return mac_dinh
    if not isinstance(v, bool):
        k.them(cho, f"'{khoa}' phải là true/false, nhận {v!r}")
        return mac_dinh
    return v


def _chuan_nhan_vat(k: _Kiem, lop: dict, cho: str) -> dict:
    """Lớp nhân vật ghép bộ phận: {"nhan_vat": "max", "bieu_cam", "tu_the", "dong_tac", "chop_mat", "noi", "di", ...}."""
    from .nhan_vat_ghep import TU_THE_GHEP

    k.khoa_la(lop, _KHOA_LOP, cho)
    ten = lop.get("nhan_vat")
    if not isinstance(ten, str) or not ten.strip():
        k.them(cho, "'nhan_vat' phải là tên thư mục trong kho-mau/nhan-vat-ghep/ (vd. \"max\")")
        ten = ""

    def tu_the(v, c):
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            k.them(c, f"'tu_the' phải là tên tư thế (vd. \"chi-tay-phai\"), nhận {v!r}")
            return None
        v = v.strip()
        if v not in TU_THE_GHEP:
            k.canh_bao.append(f"{c}: tư thế '{v}' không có trong thư viện ({', '.join(TU_THE_GHEP)}) — phải khai "
                              "trong khung.json của nhân vật, không thì vẽ 'dung'")
        return v

    def bieu_cam(v, c):
        if v is None:
            return None
        if not isinstance(v, str) or not v.strip():
            k.them(c, f"'bieu_cam' phải là mã biểu cảm (vd. \"lo-lang\"), nhận {v!r}")
            return None
        return v.strip()

    dong_tac = []
    ds = lop.get("dong_tac") or []
    if not isinstance(ds, list):
        k.them(cho, "'dong_tac' phải là danh sách [{\"luc\", \"tu_the\" | \"bieu_cam\", \"thoi_luong\", \"easing\"}]")
        ds = []
    for i, m in enumerate(ds):
        c = f"{cho}.dong_tac[{i}]"
        if not isinstance(m, dict):
            k.them(c, "mỗi động tác phải là đối tượng {\"luc\": giây, \"tu_the\": ...}")
            continue
        k.khoa_la(m, _KHOA_DONG_TAC, c)
        tt, bc = tu_the(m.get("tu_the"), c), bieu_cam(m.get("bieu_cam"), c)
        if tt is None and bc is None and "tu_the" not in m and "bieu_cam" not in m:
            k.them(c, "cần 'tu_the' hoặc 'bieu_cam'")
        dong_tac.append({"luc": k.so(m, "luc", c, 0.0, 0.0), "tu_the": tt, "bieu_cam": bc,
                         "thoi_luong": k.so(m, "thoi_luong", c, 0.7, 0.0, 30.0),
                         "easing": k.chon(m, "easing", c, EASING, "ra")})
    dong_tac.sort(key=lambda m: m["luc"])

    di = lop.get("di")
    if di is not None:
        if not isinstance(di, dict):
            k.them(cho, "'di' phải là {\"tu\": [x, y], \"den\": [x, y], \"luc\": giây, \"thoi_luong\": giây}")
            di = None
        else:
            c = f"{cho}.di"
            k.khoa_la(di, _KHOA_DI, c)
            if "tu" not in di or "den" not in di:
                k.them(c, "cần cả 'tu' và 'den' ([x, y] theo khung)")
            vt = k.vi_tri(lop, cho) if "vi_tri" in lop else [0.5, 0.85]
            di = {"tu": _diem(k, di, "tu", c, vt), "den": _diem(k, di, "den", c, vt),
                  "luc": k.so(di, "luc", c, 0.0, 0.0), "thoi_luong": k.so(di, "thoi_luong", c, 2.0, 0.05, 600.0),
                  "chu_ky": k.so(di, "chu_ky", c, 1.0, 0.2, 5.0)}
    hieu_ung = k.chon(lop, "hieu_ung", cho, HIEU_UNG_ANH, "khong",
                      " ('go-chu' chỉ dùng cho chữ)" if lop.get("hieu_ung") == "go-chu" else "")
    return {
        "nhan_vat": ten.strip() if isinstance(ten, str) else "",
        "vi_tri": di["tu"] if di and "vi_tri" not in lop else k.vi_tri(lop, cho),
        "neo": k.chon(lop, "neo", cho, NEO, "giua"),
        "co": k.so(lop, "co", cho, 0.3, 0.005, 5.0),
        "hieu_ung": hieu_ung,
        "tre": k.so(lop, "tre", cho, 0.0, 0.0),
        "lien_tuc": k.chon(lop, "lien_tuc", cho, LIEN_TUC, "khong"),
        "het": k.so(lop, "het", cho, None, 0.0, cho_phep_none=True),
        "lat": _dung_sai(k, lop, "lat", cho, False),
        "am_thanh": k.am_thanh_don(lop.get("am_thanh"), cho),
        "bieu_cam": bieu_cam(lop.get("bieu_cam"), cho),
        "tu_the": tu_the(lop.get("tu_the"), cho) or "dung",
        "dong_tac": dong_tac,
        "chop_mat": _dung_sai(k, lop, "chop_mat", cho, True),
        "noi": _dung_sai(k, lop, "noi", cho, False),
        "di": di,
        "nhip_hinh": k.so(lop, "nhip_hinh", cho, None, 0.0, 60.0, cho_phep_none=True),
    }


def _chuan_thuong_hieu(k: _Kiem, v) -> list | None:
    """Gốc 'thuong_hieu': {anh, vi_tri (tâm), co (= chiều cao / khung cao), do_mo (độ hiện 0..1)} hoặc danh sách."""
    if v is None:
        return None
    ds = v if isinstance(v, list) else [v]
    kq = []
    for i, m in enumerate(ds):
        c = f"thuong_hieu[{i}]" if isinstance(v, list) else "thuong_hieu"
        if not isinstance(m, dict) or not isinstance(m.get("anh"), str) or not m["anh"].strip():
            k.them(c, "cần {\"anh\": \"logo/kenh.png\", \"vi_tri\": [0.94, 0.06], \"co\": 0.06, \"do_mo\": 0.8}")
            continue
        k.khoa_la(m, _KHOA_THUONG_HIEU, c)
        kq.append({"anh": m["anh"].strip(), "vi_tri": _diem(k, m, "vi_tri", c, (0.94, 0.06), 0.0, 1.0),
                   "co": k.so(m, "co", c, 0.06, 0.005, 1.0), "do_mo": k.so(m, "do_mo", c, 0.8, 0.0, 1.0)})
    return kq or None


def _chuan_lop(k: _Kiem, lop, cho: str) -> dict | None:
    if not isinstance(lop, dict):
        k.them(cho, "mỗi lớp phải là đối tượng {\"anh\": ...}")
        return None
    if "nhan_vat" in lop:
        return _chuan_nhan_vat(k, lop, cho)
    k.khoa_la(lop, _KHOA_LOP, cho)
    anh = lop.get("anh")
    if not isinstance(anh, str) or not anh.strip():
        k.them(cho, "thiếu 'anh' (đường dẫn ảnh, vd. nhan-vat/max__vui__dung.png)")
        anh = ""
    tre = k.so(lop, "tre", cho, 0.0, 0.0)
    hieu_ung = k.chon(lop, "hieu_ung", cho, HIEU_UNG_ANH, "khong",
                      " ('go-chu' chỉ dùng cho chữ)" if lop.get("hieu_ung") == "go-chu" else "")
    het = k.so(lop, "het", cho, None, 0.0, cho_phep_none=True)
    lat = lop.get("lat", False)
    if lat is None:
        lat = False
    if not isinstance(lat, bool):
        k.them(cho, f"'lat' phải là true/false, nhận {lat!r}")
        lat = False
    return {
        "anh": anh.strip(),
        "vi_tri": k.vi_tri(lop, cho),
        "neo": k.chon(lop, "neo", cho, NEO, "giua"),
        "co": k.so(lop, "co", cho, 0.3, 0.005, 5.0),
        "hieu_ung": hieu_ung,
        "tre": tre,
        "lien_tuc": k.chon(lop, "lien_tuc", cho, LIEN_TUC, "khong"),
        "het": het,
        "lat": lat,
        "am_thanh": k.am_thanh_don(lop.get("am_thanh"), cho),
    }


def _chuan_chu(k: _Kiem, chu, cho: str) -> dict | None:
    if not isinstance(chu, dict):
        k.them(cho, "mỗi chữ phải là đối tượng {\"noi_dung\": ...}")
        return None
    k.khoa_la(chu, _KHOA_CHU, cho)
    nd = chu.get("noi_dung")
    if _la_so(nd):
        nd = str(nd)
    if not isinstance(nd, str) or not nd.strip():
        k.them(cho, "thiếu 'noi_dung' (chữ hiện trên hình)")
        nd = ""
    font = chu.get("font")
    if font is not None and not isinstance(font, str):
        k.them(cho, f"'font' phải là đường dẫn chuỗi, nhận {font!r}")
        font = None
    return {
        "noi_dung": nd,
        "vi_tri": k.vi_tri(chu, cho),
        "co": k.so(chu, "co", cho, 72.0, 4.0, 1000.0),
        "mau": k.mau(chu, "mau", cho, "#111111"),
        "vien": k.so(chu, "vien", cho, 0.0, 0.0, 100.0),
        "mau_vien": k.mau(chu, "mau_vien", cho, "#000000"),
        "nen": k.mau(chu, "nen", cho, None, cho_phep_none=True),
        "hieu_ung": k.chon(chu, "hieu_ung", cho, HIEU_UNG_VAO, "khong"),
        "tre": k.so(chu, "tre", cho, 0.0, 0.0),
        "lien_tuc": k.chon(chu, "lien_tuc", cho, LIEN_TUC, "khong"),
        "het": k.so(chu, "het", cho, None, 0.0, cho_phep_none=True),
        "rong_toi_da": k.so(chu, "rong_toi_da", cho, 0.8, 0.05, 1.0),
        "font": font,
        "am_thanh": k.am_thanh_don(chu.get("am_thanh"), cho),
    }


def _chuan_am_thanh_canh(k: _Kiem, ds, cho: str) -> list:
    if ds is None:
        return []
    if isinstance(ds, (str, dict)):
        ds = [ds]
    if not isinstance(ds, list):
        k.them(cho, "'am_thanh' phải là danh sách [{\"tep\", \"tre\", \"am_luong\"}]")
        return []
    kq = []
    for i, m in enumerate(ds):
        c = f"{cho}.am_thanh[{i}]"
        if isinstance(m, str):
            m = {"tep": m}
        if not isinstance(m, dict) or not isinstance(m.get("tep"), str) or not m["tep"]:
            k.them(c, "cần {\"tep\": \"am-thanh/...\", \"tre\": giây, \"am_luong\": 0..1}")
            continue
        kq.append({"tep": m["tep"], "tre": k.so(m, "tre", c, 0.0, 0.0), "am_luong": k.so(m, "am_luong", c, 1.0, 0.0, 4.0)})
    return kq


def _chuan_may_quay(k: _Kiem, v, cho: str, mac_dinh) -> dict:
    if v is None:
        v = mac_dinh
    if isinstance(v, str):
        v = {"kieu": v}
    if not isinstance(v, dict):
        k.them(cho, f"'may_quay' phải là chuỗi hoặc {{\"kieu\", \"muc\"}}, nhận {v!r}")
        return {"kieu": "dung-yen", "muc": 0.0}
    kieu = k.chon(v, "kieu", f"{cho}.may_quay", MAY_QUAY, "dung-yen")
    muc = k.so(v, "muc", f"{cho}.may_quay", MUC_MAY_QUAY.get(kieu, 0.0), 0.0, 1.0)
    kq = {"kieu": kieu, "muc": muc}
    if v.get("lac_tay") is not None:  # cầm tay cộng dồn lên kiểu khác (docs/10)
        kq["lac_tay"] = _dung_sai(k, v, "lac_tay", f"{cho}.may_quay", False)
    moc = v.get("moc")
    if moc is not None:  # mốc trong cảnh: [{"luc", "zoom", "tam", "thoi_luong", "easing"}]
        if not isinstance(moc, list) or not moc:
            k.them(f"{cho}.may_quay", "'moc' phải là danh sách [{\"luc\": 0, \"zoom\": 1.0, \"tam\": [0.5, 0.5]}, ...]")
        else:
            ra = []
            for i, m in enumerate(moc):
                c = f"{cho}.may_quay.moc[{i}]"
                if not isinstance(m, dict):
                    k.them(c, "mỗi mốc phải là {\"luc\", \"zoom\", \"tam\", \"thoi_luong\"}")
                    continue
                k.khoa_la(m, _KHOA_MOC, c)
                ra.append({"luc": k.so(m, "luc", c, 0.0, 0.0), "zoom": k.so(m, "zoom", c, 1.0, 1.0, 4.0),
                           "tam": _diem(k, m, "tam", c, (0.5, 0.5), 0.0, 1.0),
                           "thoi_luong": k.so(m, "thoi_luong", c, 0.0 if i == 0 else 0.8, 0.0, 30.0),
                           "easing": k.chon(m, "easing", c, EASING, "vao-ra")})
            ra.sort(key=lambda m: m["luc"])
            kq["moc"] = ra
    return kq


def _chuan_chuyen_canh(k: _Kiem, v, cho: str, mac_dinh: dict) -> dict:
    tl_md = float(mac_dinh.get("thoi_luong", 0.3) or 0.0)
    if v is None:
        v = dict(mac_dinh)
    if isinstance(v, str):
        v = {"kieu": v}
    if not isinstance(v, dict):
        k.them(cho, f"'chuyen_canh' phải là chuỗi hoặc {{\"kieu\", \"thoi_luong\"}}, nhận {v!r}")
        return {"kieu": "cat", "thoi_luong": 0.0}
    kieu = k.chon(v, "kieu", f"{cho}.chuyen_canh", CHUYEN_CANH, "cat")
    tl = k.so(v, "thoi_luong", f"{cho}.chuyen_canh", tl_md, 0.0, 5.0)
    return {"kieu": kieu, "thoi_luong": tl}


def _chuan_nghi(k: _Kiem, v, cho: str) -> dict | None:
    """canh.nghi: null | {"phay"|"cham"|"hoi"|"ngat"|"doan": giây 0..5} (ghi đè tts.nghi từng khoá)."""
    if v is None:
        return None
    if not isinstance(v, dict):
        k.them(cho, f"'nghi' phải là {{\"cham\": 0.5, ...}} (khoá: {', '.join(LOAI_NGHI)}), nhận {v!r}")
        return None
    kq = {}
    for khoa in v:
        if khoa not in LOAI_NGHI:
            k.them(f"{cho}.nghi", f"khoá lạ '{khoa}'; chọn trong: {', '.join(LOAI_NGHI)}")
            continue
        gt = k.so(v, khoa, f"{cho}.nghi", None, 0.0, 5.0, cho_phep_none=True)
        if gt is not None:
            kq[khoa] = gt
    return kq or None


def kiem_kich_ban(kb, ch: dict, nguon: str = "kich-ban.json") -> dict:
    """Kiểm + điền mặc định; trả bản mới. Sai -> LoiKichBan liệt kê mọi lỗi."""
    k = _Kiem()
    if not isinstance(kb, dict):
        raise LoiKichBan(f"{nguon}: gốc phải là đối tượng JSON {{\"tieu_de\", \"canh\": [...]}}.")
    kb = copy.deepcopy(kb)
    k.khoa_la(kb, _KHOA_GOC | _KHOA_GOC_THEM, "gốc")

    am = ch.get("am_thanh") or {}
    al_nhac = float(am.get("nhac_nen_am_luong", 0.07))
    cc_md = ch.get("chuyen_canh_mac_dinh") or {"kieu": "cat", "thoi_luong": 0.3}
    if isinstance(cc_md, str):
        cc_md = {"kieu": cc_md, "thoi_luong": 0.3}
    mq_md = ch.get("may_quay_mac_dinh") or "dung-yen"

    tieu_de = kb.get("tieu_de", "")
    if tieu_de is None:
        tieu_de = ""
    if not isinstance(tieu_de, str):
        k.them("gốc", f"'tieu_de' phải là chuỗi, nhận {tieu_de!r}")
        tieu_de = str(tieu_de)
    ngon_ngu = kb.get("ngon_ngu") or "en"
    if not isinstance(ngon_ngu, str):
        k.them("gốc", f"'ngon_ngu' phải là mã chuỗi như 'en', nhận {ngon_ngu!r}")
        ngon_ngu = "en"

    nhac = kb.get("nhac_nen")
    if isinstance(nhac, str):
        nhac = {"tep": nhac} if nhac.strip() else None
    if nhac is not None:
        if not isinstance(nhac, dict) or not isinstance(nhac.get("tep"), str) or not nhac["tep"]:
            k.them("gốc", "'nhac_nen' phải là null hoặc {\"tep\": \"nhac-nen/...\", \"am_luong\": 0.15}")
            nhac = None
        else:
            nhac = {"tep": nhac["tep"], "am_luong": k.so(nhac, "am_luong", "nhac_nen", al_nhac, 0.0, 2.0)}

    ds_canh = kb.get("canh")
    if not isinstance(ds_canh, list) or not ds_canh:
        k.them("gốc", "'canh' phải là danh sách có ít nhất một cảnh")
        ds_canh = []

    da_co: set[str] = set()
    ra_canh = []
    for i, canh in enumerate(ds_canh):
        if not isinstance(canh, dict):
            k.them(f"cảnh #{i + 1}", "mỗi cảnh phải là đối tượng JSON")
            continue
        cid = canh.get("id")
        if _la_so(cid):
            cid = str(cid)
        if not isinstance(cid, str) or not cid.strip():
            k.them(f"cảnh #{i + 1}", "thiếu 'id' (vd. \"c01\")")
            cid = f"#{i + 1}"
        cid = cid.strip()
        cho = f"cảnh {cid}"
        if cid in da_co:
            k.them(cho, "'id' bị trùng — mỗi cảnh một id riêng")
        da_co.add(cid)
        k.khoa_la(canh, _KHOA_CANH, cho)

        phan = canh.get("phan")
        if phan is not None and phan not in PHAN:
            k.them(cho, f"'phan' = {phan!r} không hợp lệ; chọn một trong: {', '.join(PHAN)}")
            phan = None

        loi = canh.get("loi")
        if loi is None:
            loi = ""
        if not isinstance(loi, str):
            k.them(cho, f"'loi' phải là chuỗi, nhận {loi!r}")
            loi = ""
        loi = loi.strip()
        loi_doc = canh.get("loi_doc")
        if loi_doc is not None and not isinstance(loi_doc, str):
            k.them(cho, f"'loi_doc' phải là chuỗi hoặc null, nhận {loi_doc!r}")
            loi_doc = None
        if isinstance(loi_doc, str):
            loi_doc = loi_doc.strip() or None

        thoi_luong = k.so(canh, "thoi_luong", cho, None, 0.05, 600.0, cho_phep_none=True)
        if not loi and thoi_luong is None:
            k.them(cho, "cảnh không có 'loi' thì bắt buộc ghi 'thoi_luong' (giây)")

        # thiếu -> None: dong_thoi_gian điền mặc định (am_thanh.dem_truoc / nghi_giua_canh / nghi_cuoi_phan)
        dem_truoc = k.so(canh, "dem_truoc", cho, None, 0.0, 30.0, cho_phep_none=True)
        dem_sau = k.so(canh, "dem_sau", cho, None, 0.0, 30.0, cho_phep_none=True)
        toc_do = k.so(canh, "toc_do", cho, None, 0.8, 1.3, cho_phep_none=True)

        nen = canh.get("nen", "#FFFFFF")
        if nen is None or nen == "":
            nen = "#FFFFFF"
        if la_mau(nen):
            nen = k.mau(canh, "nen", cho, "#FFFFFF") if "nen" in canh and canh["nen"] else "#FFFFFF"
        elif not isinstance(nen, str):
            k.them(cho, f"'nen' phải là mã màu '#RRGGBB' hoặc đường dẫn ảnh, nhận {nen!r}")
            nen = "#FFFFFF"

        lop_vao = canh.get("lop") or []
        if not isinstance(lop_vao, list):
            k.them(cho, "'lop' phải là danh sách")
            lop_vao = []
        lop = [x for j, l in enumerate(lop_vao) if (x := _chuan_lop(k, l, f"{cho}.lop[{j}]")) is not None]

        chu_vao = canh.get("chu") or []
        if not isinstance(chu_vao, list):
            k.them(cho, "'chu' phải là danh sách")
            chu_vao = []
        chu = [x for j, c in enumerate(chu_vao) if (x := _chuan_chu(k, c, f"{cho}.chu[{j}]")) is not None]

        ra_canh.append({
            "id": cid,
            "phan": phan,
            "loi": loi,
            "loi_doc": loi_doc,
            "thoi_luong": thoi_luong,
            "dem_truoc": dem_truoc,
            "dem_sau": dem_sau,
            "toc_do": toc_do,
            "nghi": _chuan_nghi(k, canh.get("nghi"), cho),
            "nen": nen,
            "may_quay": _chuan_may_quay(k, canh.get("may_quay"), cho, mq_md),
            "chuyen_canh": _chuan_chuyen_canh(k, canh.get("chuyen_canh"), cho, cc_md),
            "lop": lop,
            "chu": chu,
            "am_thanh": _chuan_am_thanh_canh(k, canh.get("am_thanh"), cho),
        })

    thuong_hieu = _chuan_thuong_hieu(k, kb.get("thuong_hieu"))
    nhip_hinh = k.so(kb, "nhip_hinh", "gốc", None, 0.0, 60.0, cho_phep_none=True)

    for cb in k.canh_bao:
        print(f"CẢNH BÁO kịch bản: {cb}", file=sys.stderr)
    if k.loi:
        raise LoiKichBan(
            f"{nguon} có {len(k.loi)} lỗi:\n" + "\n".join(k.loi)
            + "\nCách sửa: mở tệp kịch bản, sửa đúng cảnh / khoá trên (tập giá trị ở docs/00-HOP-DONG.md)."
        )
    kq = {k2: v for k2, v in kb.items() if k2 not in _KHOA_GOC}
    kq.update({"tieu_de": tieu_de, "ngon_ngu": ngon_ngu, "nhac_nen": nhac, "canh": ra_canh})
    if "thuong_hieu" in kb:
        kq["thuong_hieu"] = thuong_hieu
    if "nhip_hinh" in kb:
        kq["nhip_hinh"] = nhip_hinh
    return kq


def nap_kich_ban(path, ch: dict | None = None) -> dict:
    """Đọc tệp kich-ban.json -> dict đã kiểm + mặc định. Khoá thêm: '_thu_muc' (thư mục dự án)."""
    p = Path(path)
    if p.is_dir():
        p = p / "kich-ban.json"
    if not p.is_file():
        raise LoiKichBan(f"Không thấy kịch bản '{p}'. Cách sửa: tạo dự án bằng `nq moi <ten>`.")
    try:
        du_lieu = json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise LoiKichBan(
            f"{p}: JSON sai ở dòng {e.lineno}, cột {e.colno}: {e.msg}.\n"
            "Cách sửa: kiểm dấu phẩy thừa / thiếu, ngoặc kép; JSON không cho phép chú thích //."
        ) from None
    # Cảnh dạng {"khuon": ..., "tham_so": {...}} -> triển khai từ khuôn (khuôn riêng dự án ưu tiên hơn khuôn chung)
    from .khuon_canh import THU_MUC_KHUON, trien_khai

    du_lieu = trien_khai(du_lieu, [p.parent / "khuon-canh", THU_MUC_KHUON])
    if ch is None:
        from .cauhinh import doc_cau_hinh

        ch = doc_cau_hinh()
    kb = kiem_kich_ban(du_lieu, ch, nguon=str(p))
    kb["_thu_muc"] = str(p.parent.resolve())
    return kb
