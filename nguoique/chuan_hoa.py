"""Chuẩn hoá chữ tiếng Anh trước khi đưa vào động cơ giọng đọc.

Chỉ ảnh hưởng tới giọng (phụ đề vẫn dùng chữ gốc trong kịch bản).

Nguyên tắc: chỉ sửa những gì động cơ hay đọc sai (ký hiệu tiền tệ, %, &, viết tắt).
Số thường / năm / số thứ tự để nguyên — Kokoro (misaki) và Piper (espeak-ng) tự đọc tốt,
viết thành chữ trước dễ làm sai ngữ điệu ("1990" là năm hay là số?).
"""

import re
from pathlib import Path

# ---------------------------------------------------------------- từ điển


def nap_tu_dien(path) -> dict:
    """Đọc tệp YAML `từ viết: cách đọc`. Thiếu tệp / tệp rỗng -> {}."""
    if path is None:
        return {}
    p = Path(path)
    if not p.is_file():
        return {}
    import yaml

    try:
        du_lieu = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as loi:
        raise ValueError(
            f"Tệp từ điển đọc '{p}' sai cú pháp YAML: {loi}\n"
            "Cách sửa: mỗi dòng dạng `ETF: E T F` (có dấu cách sau dấu hai chấm)."
        ) from loi
    if du_lieu is None:
        return {}
    if not isinstance(du_lieu, dict):
        raise ValueError(
            f"Tệp từ điển đọc '{p}' phải là bảng `từ: cách đọc`, không phải {type(du_lieu).__name__}."
        )
    return {str(k).strip(): str(v).strip() for k, v in du_lieu.items() if k is not None and v is not None and str(k).strip()}


def _ap_tu_dien(van_ban: str, tu_dien: dict) -> str:
    """Thay nguyên từ. Khoá viết thường -> khớp không phân biệt hoa thường; có chữ hoa -> khớp đúng."""
    if not tu_dien:
        return van_ban
    # khoá dài trước để "S&P 500" thắng "S&P"
    for khoa in sorted(tu_dien, key=len, reverse=True):
        co = 0 if any(c.isupper() for c in khoa) else re.IGNORECASE
        mau = re.compile(r"(?<![\w])" + re.escape(khoa) + r"(?![\w])", co)
        thay = tu_dien[khoa]
        van_ban = mau.sub(lambda _m, t=thay: t, van_ban)
    return van_ban


# ---------------------------------------------------------------- tiền tệ, %, ký hiệu

_DON_VI_LON = {
    "k": "thousand", "thousand": "thousand",
    "m": "million", "mn": "million", "million": "million",
    "b": "billion", "bn": "billion", "billion": "billion",
    "t": "trillion", "tn": "trillion", "trillion": "trillion",
}

_TIEN_TE = {
    "$": ("dollar", "dollars", "cent", "cents"),
    "€": ("euro", "euros", "cent", "cents"),
    "£": ("pound", "pounds", "penny", "pence"),
    "¥": ("yen", "yen", None, None),
}

_MAU_TIEN = re.compile(
    r"(?P<ky>[$€£¥])\s?(?P<so>\d[\d,]*(?:\.\d+)?)"
    r"(?:\s?(?P<lon>thousand|million|billion|trillion|bn|mn|tn|[kKmMbBtT])(?![\w]))?"
)


def _doc_tien(m: re.Match) -> str:
    mot, nhieu, xu_mot, xu_nhieu = _TIEN_TE[m.group("ky")]
    so = m.group("so")
    lon = m.group("lon")
    if lon:
        # "$2.5 million" -> "2.5 million dollars"
        return f"{so} {_DON_VI_LON[lon.lower()]} {nhieu}"
    nguyen, _, le = so.partition(".")
    so_nguyen = nguyen.replace(",", "")
    don_vi = mot if so_nguyen == "1" else nhieu
    if le and xu_mot and len(le) == 2:
        if le == "00":
            return f"{nguyen} {don_vi}"
        xu = int(le)
        ten_xu = xu_mot if xu == 1 else xu_nhieu
        if so_nguyen == "0":
            return f"{xu} {ten_xu}"
        return f"{nguyen} {don_vi} and {xu} {ten_xu}"
    if le:
        return f"{so} {nhieu}"
    return f"{nguyen} {don_vi}"


_THAY_DON_GIAN = [
    # (mẫu, thay) — áp theo thứ tự
    (re.compile(r"(\d)\s?%"), r"\1 percent"),
    (re.compile(r"(?<=\s)&(?=\s)"), "and"),
    (re.compile(r"\bvs\.?(?=\s)", re.IGNORECASE), "versus"),
    (re.compile(r"\be\.g\.,?", re.IGNORECASE), "for example,"),
    (re.compile(r"\bi\.e\.,?", re.IGNORECASE), "that is,"),
    (re.compile(r"\betc\.", re.IGNORECASE), "et cetera."),
    (re.compile(r"~\s?(?=\d)"), "about "),
    (re.compile(r"(\d)\s?x(?![\w])"), r"\1 times"),          # 10x -> 10 times
    (re.compile(r"(?<=\d)\s?[–—-]\s?(?=\d)"), " to "),         # 3-5 -> 3 to 5 (năm 2008-2009 cũng ổn)
    (re.compile(r"[“”]"), '"'),
    (re.compile(r"[‘’]"), "'"),
]
# gạch dài giữa câu: chế độ thường -> ", " (ngắt nhẹ); chế độ giu_ngat -> giữ " — " để tach_manh chèn nghỉ
_MAU_GACH_DAI = re.compile(r"[ \t]*(?:[—–]|(?<!-)--(?!-))[ \t]*")  # không nuốt xuống dòng


def chuan_hoa(van_ban: str, tu_dien: dict, giu_ngat: bool = False) -> str:
    """Chuẩn hoá một đoạn lời tiếng Anh để máy đọc. Từ điển áp trước (khớp nguyên từ).

    giu_ngat=False (mặc định, như cũ): xuống dòng -> dấu cách, gạch dài -> ", ".
    giu_ngat=True: giữ xuống dòng ("\\n"), gạch dài (" — ") và "..." (thành "…") để `tach_manh`
    biết chỗ chèn nghỉ (giong.py dùng chế độ này).
    """
    if not van_ban:
        return ""
    s = str(van_ban).replace("\r\n", "\n").replace("\r", "\n")
    s = _ap_tu_dien(s, tu_dien or {})
    s = _MAU_TIEN.sub(_doc_tien, s)
    for mau, thay in _THAY_DON_GIAN:
        s = mau.sub(thay, s)
    s = _MAU_GACH_DAI.sub(" — " if giu_ngat else ", ", s)
    s = re.sub(r"[ \t\f\v]+", " ", s)
    if giu_ngat:
        s = re.sub(r"\.{3,}", "…", s)
        s = re.sub(r" *\n\s*", "\n", s)            # nhiều dòng trống -> một "\n"
        s = re.sub(r"[ \t]+([,.;:!?])", r"\1", s)
        s = re.sub(r"^[ —]+|[ —]+$", "", s, flags=re.MULTILINE)  # gạch thừa đầu / cuối dòng
    else:
        # gom khoảng trắng (giữ xuống dòng đơn thành dấu cách — động cơ tự ngắt theo câu)
        s = re.sub(r"\s*\n\s*", " ", s)
        s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r",\s*,", ",", s)
    return s.strip()


# ---------------------------------------------------------------- mẩu theo dấu câu (nghỉ trong giọng)

# Loại nghỉ sau mỗi mẩu -> khoá trong tts.nghi / canh.nghi. Giá trị = trung vị số đo 5 video (docs/02 mục 0)
# trừ ~0,06s lặng mà giong.py giữ lại hai đầu mẩu (DEM_MANH 0,03s × 2): chấm 0,42 -> nghe ~0,48s.
LOAI_NGHI = ("phay", "cham", "hoi", "ngat", "doan")
NGHI_MAC_DINH = {"phay": 0.2, "cham": 0.42, "hoi": 0.55, "ngat": 0.5, "doan": 0.8}
_HANG_NGHI = {"phay": 1, "cham": 2, "ngat": 3, "hoi": 4, "doan": 5}  # hai ranh giới dồn nhau -> lấy loại mạnh hơn
TU_TOI_THIEU_MOT_MANH = 3  # mẩu < 3 từ gộp với mẩu kế (Kokoro đọc mẩu quá ngắn dễ méo ngữ điệu)

# ranh giới: dấu câu (kèm nháy / ngoặc đóng) rồi khoảng trắng hoặc hết dòng; hoặc gạch dài
_MAU_RANH = re.compile(
    r"(?P<dau>[.!?…]+|[,;:])[\"'”’)\]]*(?=\s|$)"
    r"|(?P<gach>\s*(?:—|–|(?<!-)--(?!-))\s*)"
)
_MAU_GACH_CUOI = re.compile(r"\s*(?:—|–|--)\s*$")
_MAU_GACH_GIUA = re.compile(r"\s*(?:—|–|(?<!-)--(?!-))\s*")


def _loai_dau(dau: str) -> str:
    if "?" in dau or "!" in dau:
        return "hoi"
    if "…" in dau or ".." in dau:
        return "ngat"
    if "." in dau:
        return "cham"
    return "phay"


def _manh_hon(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return a if _HANG_NGHI.get(a, 0) >= _HANG_NGHI.get(b, 0) else b


def so_tu(chu: str) -> int:
    """Số từ có chữ / số (gạch, dấu câu đứng riêng không tính)."""
    return sum(1 for t in (chu or "").split() if any(c.isalnum() for c in t))


def tach_manh(van_ban: str, tu_toi_thieu: int = TU_TOI_THIEU_MOT_MANH) -> list:
    """Tách lời thành mẩu theo dấu câu -> [(chữ, loại nghỉ sau)].

    Loại: "phay" (, ; :), "cham" (.), "hoi" (? !), "ngat" (… và gạch dài —), "doan" (xuống dòng);
    mẩu cuối có loại None (nghỉ cuối cảnh do dem_sau lo). Giữ nguyên chữ và dấu câu của mẩu
    (nối các mẩu bằng dấu cách ra lại đủ các từ). "10,000", "3.5", "9:30" không bị tách.
    Mẩu < tu_toi_thieu từ gộp vào mẩu kế (mẩu cuối ngắn gộp vào mẩu trước) — mất nghỉ ở chỗ gộp.
    Dùng chung cho giọng (chữ đã chuẩn hoá) và phụ đề (chữ gốc) để hai bên ra cùng số mẩu.
    """
    s = (van_ban or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not s:
        return []
    tho: list[list] = []  # [chữ, loại]
    for doan in re.split(r"\n\s*", s):
        doan = doan.strip()
        if not doan:
            continue
        so_truoc = len(tho)
        dau = 0
        for m in _MAU_RANH.finditer(doan):
            if m.group("gach") is not None:
                a, b = m.start(), m.end()
                if a > 0 and b < len(doan) and doan[a - 1].isdigit() and doan[b].isdigit():
                    continue  # 2008–2009: khoảng số, không phải ngắt
                loai = "ngat"
            else:
                loai = _loai_dau(m.group("dau"))
            manh = doan[dau:m.end()].strip()
            dau = m.end()
            if not manh:
                continue
            if so_tu(manh) == 0 and len(tho) > so_truoc:
                # chỉ toàn dấu (vd. ", —"): dồn vào mẩu trước, lấy loại nghỉ mạnh hơn
                tho[-1][0] = f"{tho[-1][0]} {manh}"
                tho[-1][1] = _manh_hon(tho[-1][1], loai)
                continue
            tho.append([manh, loai])
        con = doan[dau:].strip()
        if con:
            if so_tu(con) == 0 and len(tho) > so_truoc:
                tho[-1][0] = f"{tho[-1][0]} {con}"
            else:
                tho.append([con, None])
        if len(tho) > so_truoc:
            tho[-1][1] = "doan"  # hết đoạn (xuống dòng) là nghỉ mạnh nhất
    if not tho:
        return []
    tho[-1][1] = None

    kq: list[list] = []
    cho = ""
    for chu, loai in tho:
        if cho:
            chu = f"{cho} {chu}"
            cho = ""
        if so_tu(chu) < max(1, int(tu_toi_thieu)):
            cho = chu
            continue
        kq.append([chu, loai])
    if cho:
        if kq:
            kq[-1][0] = f"{kq[-1][0]} {cho}"
            kq[-1][1] = None
        else:
            kq.append([cho, None])
    return [(c, l) for c, l in kq]


def chu_cho_dong_co(manh: str) -> str:
    """Chữ của một mẩu đưa vào động cơ: gạch cuối mẩu -> ',' (giữ ngữ điệu chưa dứt), gạch giữa -> ', '."""
    s = _MAU_GACH_CUOI.sub(",", (manh or "").strip())
    s = _MAU_GACH_GIUA.sub(", ", s)
    s = re.sub(r",\s*,", ",", s)
    s = re.sub(r"^[\s,]+", "", s)
    return s.strip()


# ---------------------------------------------------------------- cắt đoạn

# ranh giới câu: sau . ! ? … (có thể kèm một dấu đóng ngoặc / nháy), rồi khoảng trắng
_MAU_CAU = re.compile(r"(?:(?<=[.!?…])|(?<=[.!?…][\"')\]]))\s+")


def _cat_cung(cau: str, toi_da: int) -> list:
    """Câu quá dài: cắt ở dấu phẩy / chấm phẩy, cùng lắm cắt theo từ."""
    if len(cau) <= toi_da:
        return [cau]
    manh = re.split(r"(?<=[,;:])\s+", cau)
    ket_qua, hien = [], ""
    for m in manh:
        if len(m) > toi_da:
            if hien:
                ket_qua.append(hien)
                hien = ""
            tu_hien = ""
            for tu in m.split():
                if tu_hien and len(tu_hien) + 1 + len(tu) > toi_da:
                    ket_qua.append(tu_hien)
                    tu_hien = tu
                else:
                    tu_hien = f"{tu_hien} {tu}" if tu_hien else tu
            if tu_hien:
                ket_qua.append(tu_hien)
            continue
        if hien and len(hien) + 1 + len(m) > toi_da:
            ket_qua.append(hien)
            hien = m
        else:
            hien = f"{hien} {m}" if hien else m
    if hien:
        ket_qua.append(hien)
    return ket_qua


def tach_doan(van_ban: str, toi_da: int = 300) -> list:
    """Cắt văn bản thành các đoạn ≤ toi_da ký tự, ưu tiên ranh giới câu."""
    s = (van_ban or "").strip()
    if not s:
        return []
    toi_da = max(20, int(toi_da))
    cac_cau = [c.strip() for c in _MAU_CAU.split(s) if c and c.strip()]
    doan, hien = [], ""
    for cau in cac_cau:
        for phan in _cat_cung(cau, toi_da):
            if hien and len(hien) + 1 + len(phan) > toi_da:
                doan.append(hien)
                hien = phan
            else:
                hien = f"{hien} {phan}" if hien else phan
    if hien:
        doan.append(hien)
    return doan
