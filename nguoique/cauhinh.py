"""Cấu hình chung: thư mục gốc, đọc config.yaml (trộn với mặc định), đường dẫn kho / dự án."""

from __future__ import annotations

import copy
import os
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent

# Mặc định khớp docs/00-HOP-DONG.md; config.yaml chỉ cần ghi khoá muốn đổi.
MAC_DINH: dict = {
    "kho_mau": "kho-mau",
    "du_an": "du-an",
    "video": {"rong": 1920, "cao": 1080, "fps": 30, "ma_hoa": "h264_nvenc", "chat_luong": 21},
    "tts": {
        "che_do": "may-chu",
        "dia_chi": "http://127.0.0.1:8765",
        "dong_co": "kokoro",
        "thiet_bi": "cuda",
        "tu_dien": "tu-dien-doc.yaml",
        "kokoro": {"giong": "am_michael", "toc_do": 1.0, "ma_ngon_ngu": "a"},
        "piper": {"mo_hinh": "mo-hinh/piper/en_US-norman-medium.onnx", "toc_do": 1.0},
        "nghi": {"phay": 0.2, "cham": 0.42, "hoi": 0.55, "ngat": 0.5, "doan": 0.8},
    },
    "am_thanh": {"tan_so": 48000, "nhac_nen_am_luong": 0.07, "giam_nhac_khi_noi": True, "dem_truoc": 0.15,
                 "nghi_giua_canh": 0.35, "nghi_cuoi_phan": 0.9},
    "phu_de": {
        "bat": True,
        "co_chu": 52,
        "mau": "#FFFFFF",
        "mau_vien": "#111111",
        "vien": 6,
        "so_tu_toi_da": 8,
        "vi_tri_y": 0.92,
        "font": "kho-mau/font/Inter-Bold.ttf",
        "font_du_phong": "C:/Windows/Fonts/arialbd.ttf",
    },
    "chuyen_canh_mac_dinh": {"kieu": "cat", "thoi_luong": 0.3},
    "may_quay_mac_dinh": "zoom-cham",
}


def _tron(goc: dict, moi: dict) -> dict:
    """Trộn sâu `moi` vào bản sao của `goc`."""
    kq = copy.deepcopy(goc)
    for k, v in moi.items():
        if isinstance(v, dict) and isinstance(kq.get(k), dict):
            kq[k] = _tron(kq[k], v)
        else:
            kq[k] = copy.deepcopy(v)
    return kq


def tep_cau_hinh(duong: str | os.PathLike | None = None) -> Path:
    """Tệp cấu hình sẽ dùng: tham số -> biến môi trường NQ_CAU_HINH -> <gốc>/config.yaml."""
    if duong:
        return Path(duong)
    if os.environ.get("NQ_CAU_HINH"):
        return Path(os.environ["NQ_CAU_HINH"])
    return GOC / "config.yaml"


def doc_cau_hinh(duong: str | os.PathLike | None = None) -> dict:
    """Đọc config.yaml rồi trộn vào MAC_DINH. Thiếu tệp -> dùng mặc định (có cảnh báo)."""
    p = tep_cau_hinh(duong)
    if not p.is_file():
        if duong:
            raise FileNotFoundError(f"Không thấy tệp cấu hình '{p}'. Kiểm lại đường dẫn --cau-hinh.")
        import sys

        print(f"CẢNH BÁO: không thấy {p}, dùng cấu hình mặc định.", file=sys.stderr)
        return copy.deepcopy(MAC_DINH)
    import yaml

    try:
        du_lieu = yaml.safe_load(p.read_text(encoding="utf-8-sig")) or {}
    except yaml.YAMLError as loi:
        raise ValueError(
            f"Tệp cấu hình '{p}' sai cú pháp YAML: {loi}\n"
            "Cách sửa: kiểm thụt lề (dùng dấu cách, không dùng Tab) và dấu ':' sau mỗi khoá."
        ) from loi
    if not isinstance(du_lieu, dict):
        raise ValueError(f"Tệp cấu hình '{p}' phải là bảng khoá: giá trị.")
    return _tron(MAC_DINH, du_lieu)


def duong_dan(p: str | os.PathLike) -> Path:
    """Đường dẫn tuyệt đối: tương đối thì tính từ gốc repo."""
    q = Path(os.path.expandvars(os.path.expanduser(str(p))))
    return q if q.is_absolute() else GOC / q


def kho_mau(ch: dict) -> Path:
    """Thư mục kho mẫu (kho-mau/)."""
    return duong_dan(ch.get("kho_mau") or "kho-mau")


def thu_muc_du_an(ch: dict, ten: str | os.PathLike) -> Path:
    """Thư mục của dự án. `ten` có thể là tên (du-an/<ten>), đường dẫn thư mục, hoặc đường dẫn kich-ban.json."""
    p = Path(str(ten))
    if p.suffix.lower() == ".json":
        return p.resolve().parent
    if p.is_absolute() or (p / "kich-ban.json").is_file():
        return p.resolve()
    return duong_dan(ch.get("du_an") or "du-an") / p


def tim_tep(ten: str | os.PathLike | None, thu_muc_du_an: Path | None, kho: Path | None) -> Path | None:
    """Tìm tệp ảnh / âm thanh: tuyệt đối -> thư mục dự án -> kho mẫu. Không có -> None."""
    if not ten:
        return None
    p = Path(str(ten))
    if p.is_absolute():
        return p if p.is_file() else None
    for goc in (thu_muc_du_an, kho):
        if goc is None:
            continue
        q = Path(goc) / p
        if q.is_file():
            return q
    return None
