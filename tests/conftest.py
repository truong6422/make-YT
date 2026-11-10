"""Cấu hình chung cho bộ test.

- Thêm gốc repo vào sys.path để `import nguoique` chạy được cả khi chưa `pip install -e .`.
- Fixture `ch`: đọc `config.yaml` của repo rồi ghi đè cho test (giọng giả lập, chạy trực tiếp,
  kho mẫu / dự án trỏ vào thư mục tạm) — không cần mô hình, GPU hay mạng.
"""

import copy
import json
import sys
from pathlib import Path

import pytest

GOC_REPO = Path(__file__).resolve().parent.parent
if str(GOC_REPO) not in sys.path:
    sys.path.insert(0, str(GOC_REPO))

# Cấu hình dự phòng (khớp docs/00-HOP-DONG.md) khi config.yaml chưa có.
_CAU_HINH_DU_PHONG = {
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
        "bat": True, "co_chu": 52, "mau": "#FFFFFF", "mau_vien": "#111111", "vien": 6,
        "so_tu_toi_da": 8, "vi_tri_y": 0.92, "font": "kho-mau/font/Inter-Bold.ttf",
        "font_du_phong": "C:/Windows/Fonts/arialbd.ttf",
    },
    "chuyen_canh_mac_dinh": {"kieu": "cat", "thoi_luong": 0.3},
    "may_quay_mac_dinh": "zoom-cham",
}


def _tron(goc: dict, de: dict) -> dict:
    """Trộn sâu `de` vào `goc` (trả bản mới)."""
    kq = copy.deepcopy(goc)
    for k, v in de.items():
        if isinstance(v, dict) and isinstance(kq.get(k), dict):
            kq[k] = _tron(kq[k], v)
        else:
            kq[k] = copy.deepcopy(v)
    return kq


def doc_cau_hinh_repo() -> dict:
    tep = GOC_REPO / "config.yaml"
    if tep.is_file():
        import yaml

        du_lieu = yaml.safe_load(tep.read_text(encoding="utf-8")) or {}
        return _tron(_CAU_HINH_DU_PHONG, du_lieu)
    return copy.deepcopy(_CAU_HINH_DU_PHONG)


@pytest.fixture
def goc_repo() -> Path:
    return GOC_REPO


@pytest.fixture
def ch(tmp_path) -> dict:
    """Cấu hình tạm: giọng gia-lap chạy trực tiếp, kho mẫu / dự án rỗng trong tmp_path."""
    kho = tmp_path / "kho-mau"
    du_an = tmp_path / "du-an"
    kho.mkdir(parents=True, exist_ok=True)
    du_an.mkdir(parents=True, exist_ok=True)
    tu_dien = GOC_REPO / "tu-dien-doc.yaml"
    de = {
        "kho_mau": str(kho),
        "du_an": str(du_an),
        "tts": {
            "che_do": "truc-tiep",
            "dong_co": "gia-lap",
            "thiet_bi": "cpu",
            "tu_dien": str(tu_dien),
        },
        # font không có trong tmp -> code phải tự dùng font dự phòng / mặc định của Pillow
        "phu_de": {"font": str(kho / "font" / "khong-co.ttf")},
    }
    return _tron(doc_cau_hinh_repo(), de)


@pytest.fixture
def kb_mau_path(goc_repo) -> Path:
    return goc_repo / "templates" / "kich-ban-mau.json"


def ghi_kich_ban(thu_muc: Path, kb: dict) -> Path:
    thu_muc.mkdir(parents=True, exist_ok=True)
    tep = thu_muc / "kich-ban.json"
    tep.write_text(json.dumps(kb, ensure_ascii=False, indent=2), encoding="utf-8")
    return tep


def kb_toi_gian(so_canh: int = 2, loi: bool = True) -> dict:
    """Kịch bản nhỏ hợp lệ theo lược đồ trong hợp đồng."""
    canh = []
    for i in range(so_canh):
        c = {
            "id": f"c{i + 1:02d}",
            "phan": "hook" if i == 0 else "giai-thich",
            "loi": f"This is scene number {i + 1}. It has a few words." if loi else "",
            "nen": "#FFFFFF",
            "lop": [
                {"anh": "nhan-vat/khong-co-anh.png", "vi_tri": [0.3, 0.85], "neo": "day",
                 "co": 0.22, "hieu_ung": "bat-len"}
            ],
            "chu": [{"noi_dung": "HELLO", "vi_tri": [0.7, 0.3], "co": 96, "mau": "#E53935",
                     "hieu_ung": "go-chu", "tre": 0.2}],
        }
        if not loi:
            c["thoi_luong"] = 1.0
        if i > 0:
            c["chuyen_canh"] = {"kieu": "mo-dan", "thoi_luong": 0.3}
        canh.append(c)
    return {"tieu_de": "Test Video", "ngon_ngu": "en", "nhac_nen": None, "canh": canh}


@pytest.fixture
def kb_tep(tmp_path) -> Path:
    return ghi_kich_ban(tmp_path / "du-an" / "thu", kb_toi_gian())
