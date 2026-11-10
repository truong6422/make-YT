"""Test nguoique/nhan_vat_ghep.py + lớp nhân vật ghép trong dung_hinh / kichban / hinh_tam (không cần ffmpeg)."""

import json
import math
import time

import numpy as np
import pytest
from PIL import Image

from nguoique.dong_thoi_gian import lap_dong_thoi_gian
from nguoique.dung_hinh import BoDung
from nguoique.hinh_tam import BIEU_CAM, tao_nhan_vat_ghep_tam
from nguoique.kichban import LoiKichBan, kiem_kich_ban
from nguoique.nhan_vat_ghep import (
    BO_PHAN_CHUAN, TU_THE_GHEP, NhanVatGhep, LoiNhanVatGhep, buoc_hinh, bieu_cam_tai, chon_mieng, dang_nham,
    goc_di_bo, goc_tai, lich_chop_mat, mieng_chu_ky, tinh_bao_giong, trang_thai_mieng, vi_tri_tai, xoay_vec,
)

W, H = 640, 360


# ---------------- hàm thuần ----------------
def test_xoay_vec_nguoc_chieu_kim_dong_ho():
    x, y = xoay_vec(0.0, 40.0, 90)  # tay buông xuống, xoay +90° -> chỉ sang phải
    assert x == pytest.approx(40.0) and y == pytest.approx(0.0, abs=1e-9)


def test_buoc_hinh():
    assert buoc_hinh(0.07, 15) == pytest.approx(1 / 15)
    assert buoc_hinh(0.0, 15) == 0.0
    assert buoc_hinh(0.07, 0) == 0.07


def test_thu_vien_du_tu_the():
    for ten in ("dung", "chi-tay-phai", "chi-tay-trai", "om-dau", "gio-hai-tay", "nhun-vai", "khoanh-tay",
                "vay-tay", "suy-nghi-tay-cam", "di-bo-1", "di-bo-2", "di-bo-3", "di-bo-4"):
        assert ten in TU_THE_GHEP
        assert set(BO_PHAN_CHUAN) <= set(TU_THE_GHEP[ten])


def test_goc_noi_suy_ease_out():
    lop = {"tu_the": "dung", "dong_tac": [{"tu_the": "chi-tay-phai", "luc": 1.0, "thoi_luong": 0.7, "easing": "ra"}]}
    a, b = TU_THE_GHEP["dung"]["tay-phai-tren"], TU_THE_GHEP["chi-tay-phai"]["tay-phai-tren"]
    assert goc_tai(lop, 0.5)["tay-phai-tren"] == pytest.approx(a)
    assert goc_tai(lop, 1.7)["tay-phai-tren"] == pytest.approx(b)
    giua = goc_tai(lop, 1.35)["tay-phai-tren"]
    assert a + (b - a) * 0.5 < giua < b, "ease-out: nửa thời gian đã đi quá nửa đường"


def test_goc_lien_tuc_khi_doi_tu_the_giua_chung():
    lop = {"dong_tac": [{"tu_the": "om-dau", "luc": 0.0, "thoi_luong": 1.0},
                        {"tu_the": "gio-hai-tay", "luc": 0.5, "thoi_luong": 1.0}]}
    truoc = goc_tai(lop, 0.4999)["tay-trai-tren"]
    sau = goc_tai(lop, 0.5)["tay-trai-tren"]
    assert sau == pytest.approx(truoc, abs=0.1)


def test_vay_tay_dao_dong():
    lop = {"tu_the": "vay-tay"}
    vals = {round(goc_tai(lop, t)["tay-phai-duoi"], 3) for t in (0.0, 0.125, 0.375)}
    assert len(vals) == 3


def test_bieu_cam_doi_giua_canh():
    lop = {"bieu_cam": "lo-lang", "dong_tac": [{"bieu_cam": "soc", "luc": 2.0}]}
    assert bieu_cam_tai(lop, 1.9) == "lo-lang"
    assert bieu_cam_tai(lop, 2.0) == "soc"


def test_di_bo_vi_tri_va_huong():
    lop = {"di": {"tu": [0.2, 0.85], "den": [0.6, 0.85], "luc": 0.5, "thoi_luong": 2.0}}
    x, y, w, _, trai = vi_tri_tai(lop, 0.0)
    assert (x, y, w) == (0.2, 0.85, 0.0) and trai is False
    x, _, w, _, _ = vi_tri_tai(lop, 1.5)
    assert x == pytest.approx(0.4) and w == 1.0
    assert vi_tri_tai(lop, 5.0)[0] == pytest.approx(0.6)
    assert vi_tri_tai({"di": {"tu": [0.8, 0.8], "den": [0.2, 0.8]}}, 0.5)[4] is True
    a, b = goc_di_bo(0.0), goc_di_bo(0.5)
    assert a["chan-phai-tren"] == pytest.approx(TU_THE_GHEP["di-bo-1"]["chan-phai-tren"])
    assert b["chan-trai-tren"] == pytest.approx(TU_THE_GHEP["di-bo-3"]["chan-trai-tren"])


def test_chop_mat_co_dinh_theo_hat_giong():
    a, b = lich_chop_mat("c01|0", 30.0), lich_chop_mat("c01|0", 30.0)
    assert a == b and a
    assert all(2.5 <= y - x <= 5.0 for x, y in zip(a, a[1:]))
    assert lich_chop_mat("c02|0", 30.0) != a
    assert dang_nham(a, a[0] + 0.05) and not dang_nham(a, a[0] + 0.2)


def test_bao_giong_va_mieng():
    sr = 16000
    t = np.arange(sr, dtype=np.float32) / sr
    mau = np.where(t < 0.5, 0.5 * np.sin(2 * np.pi * 220 * t), 0.0).astype(np.float32)
    bao = tinh_bao_giong(mau, sr)
    assert len(bao) == 15
    assert bao[2] > 0.3 and bao[12] == 0.0
    assert chon_mieng(bao, 0.2) == "ha-to"
    assert chon_mieng(bao, 0.9) == "dong"
    assert chon_mieng(None, 0.2) == "dong"
    ds = trang_thai_mieng(np.array([0, 1, 0, 1, 0, 1, 0, 0], dtype=np.float32))
    # giữ tối thiểu 0,15 s = 3 ô 1/15 s: không có trạng thái nào ngắn hơn 3 ô (trừ đoạn cuối)
    doan, dem = [], 1
    for x, y in zip(ds, ds[1:]):
        if x == y:
            dem += 1
        else:
            doan.append(dem)
            dem = 1
    assert all(d >= 3 for d in doan)


def test_mieng_chu_ky_056():
    assert mieng_chu_ky(0.1) != "dong"
    assert mieng_chu_ky(0.4) == "dong"
    assert mieng_chu_ky(0.56 + 0.1) != "dong"


# ---------------- rig đồ chơi: kiểm hình học khớp ----------------
def _rig_do_choi(thu_muc):
    thu_muc.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (10, 50), (255, 0, 0, 255)).save(thu_muc / "cha.png")
    Image.new("RGBA", (10, 30), (0, 0, 255, 255)).save(thu_muc / "con.png")
    khung = {"kich_thuoc": [200, 200], "bo_phan": [
        {"ten": "cha", "tep": "cha.png", "cha": None, "khop": [5, 5], "gan": [100, 50], "lop": 1, "goc": 0},
        {"ten": "con", "tep": "con.png", "cha": "cha", "khop": [5, 5], "gan": [5, 45], "lop": 2, "goc": 0,
         "dau_mut": [5, 30]}]}
    (thu_muc / "khung.json").write_text(json.dumps(khung), encoding="utf-8")
    return NhanVatGhep(thu_muc)


def test_cay_khop_con_theo_cha_xoay(tmp_path):
    nv = _rig_do_choi(tmp_path / "r")
    tg = nv.cay({"cha": 0, "con": 0}, 1.0)
    assert (tg["con"].px, tg["con"].py) == pytest.approx((100, 90))
    tg = nv.cay({"cha": 90, "con": 0}, 1.0)
    assert (tg["con"].px, tg["con"].py) == pytest.approx((140, 50))
    tg = nv.cay({"cha": 90, "con": 0}, 1.0, lat=True)  # lật gương: sang trái
    assert (tg["con"].px, tg["con"].py) == pytest.approx((60, 50))


def test_bo_tri_khop_trung_diem_ve(tmp_path):
    """Điểm khớp của con trong ảnh đã xoay phải rơi đúng vị trí tính được (không hở khớp)."""
    nv = _rig_do_choi(tmp_path / "r")
    for g in (0, 37, 90, 180, 233):
        ds = nv.bo_tri({"cha": g, "con": 0}, 1.0, False, 0, 0, cham_dat=False)
        tg = nv.cay({"cha": g, "con": 0}, 1.0)
        im, x, y = ds[0]
        # khớp cha (5,5) sau xoay: tâm ảnh xoay + vector
        rx, ry = xoay_vec(5 - 5, 5 - 25, g)
        assert x + im.width / 2 + rx == pytest.approx(tg["cha"].px, abs=1e-6)
        assert y + im.height / 2 + ry == pytest.approx(tg["cha"].py, abs=1e-6)
        assert im.getpixel((int(im.width / 2 + rx), int(im.height / 2 + ry)))[3] > 0


def test_khung_json_sai_bao_loi(tmp_path):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "khung.json").write_text('{"bo_phan": [{"ten": "a", "tep": "a.png", "cha": "b"}]}',
                                                encoding="utf-8")
    with pytest.raises(LoiNhanVatGhep, match="cha"):
        NhanVatGhep(tmp_path / "x")
    with pytest.raises(LoiNhanVatGhep, match="hinh-tam"):
        NhanVatGhep(tmp_path / "khong-co")


# ---------------- bộ tạm từ hinh_tam ----------------
def test_tao_nhan_vat_ghep_tam_du_tep(tmp_path):
    da = tao_nhan_vat_ghep_tam(tmp_path, "max")
    goc = tmp_path / "nhan-vat-ghep" / "max"
    assert (goc / "khung.json").is_file() and da
    for bp in BO_PHAN_CHUAN:
        assert (goc / f"{bp}.png").is_file(), bp
    for bc in BIEU_CAM:
        assert (goc / "mat" / f"{bc}.png").is_file()
    for m in ("dong", "ha-nho", "ha-to"):
        assert (goc / "mieng" / f"{m}.png").is_file()
    assert (goc / "mat" / "nham.png").is_file()
    assert tao_nhan_vat_ghep_tam(tmp_path, "max") == [], "chạy lại không ghi đè"
    nv = NhanVatGhep(goc)
    assert set(nv.thu_tu) == set(BO_PHAN_CHUAN)
    # đứng: bàn chân ở gần đáy khung tham chiếu, đầu ở trên
    assert 900 < nv.nen_dat() < 1024
    tg = nv.cay(nv.goc_tu_the("dung"), 1.0)
    assert tg["dau"].py == pytest.approx(380, abs=1)
    assert tg["tay-phai-tren"].py == pytest.approx(440, abs=1)


def test_om_dau_tay_cham_dau(tmp_path):
    tao_nhan_vat_ghep_tam(tmp_path, "max")
    nv = NhanVatGhep(tmp_path / "nhan-vat-ghep" / "max")
    tg = nv.cay(nv.goc_tu_the("om-dau"), 1.0)
    for ben in ("trai", "phai"):
        c = tg[f"tay-{ben}-duoi"]
        hx, hy = nv._diem(c, (19, 129), False)  # bàn tay = điểm cuối cẳng tay
        assert math.hypot(hx - 512, hy - 270) < 140, "bàn tay phải ở sát đầu"


# ---------------- dựng trong BoDung ----------------
def _kb_ghep(lop: dict, thoi_luong=3.0, **goc):
    return {"tieu_de": "T", "canh": [{"id": "c01", "loi": "", "thoi_luong": thoi_luong, "nen": "#FFFFFF",
                                      "may_quay": "dung-yen", "lop": [lop]}], **goc}


def _bo_dung_ghep(ch, tmp_path, lop, nhap=True, **goc):
    tao_nhan_vat_ghep_tam(tmp_path / "kho-mau", "max")
    kb = kiem_kich_ban(_kb_ghep(lop, **goc), ch)
    ds, _ = lap_dong_thoi_gian(kb, {}, ch)
    return BoDung(kb, ds, ch, tmp_path / "du-an" / "thu", nhap=nhap), kb


@pytest.mark.parametrize("lop", [
    {"nhan_vat": "max", "vi_tri": [0.5, 0.9], "neo": "day", "co": 0.4, "bieu_cam": "lo-lang",
     "dong_tac": [{"tu_the": "chi-tay-phai", "luc": 0.5}, {"bieu_cam": "soc", "luc": 1.0}], "noi": True},
    {"nhan_vat": "max", "co": 0.4, "lat": True, "tu_the": "om-dau", "lien_tuc": "run", "hieu_ung": "mo-dan"},
    {"nhan_vat": "max", "co": 0.3, "neo": "day", "di": {"tu": [0.8, 0.9], "den": [0.2, 0.9], "thoi_luong": 2.0},
     "lien_tuc": "tho", "hieu_ung": "bat-len", "het": 2.5},
    {"nhan_vat": "khong-co-nhan-vat", "co": 0.3},
])
def test_ve_nhan_vat_ghep(ch, tmp_path, lop):
    bd, kb = _bo_dung_ghep(ch, tmp_path, lop)
    for t in (0.0, 0.1, 0.3, 0.8, 1.2, 2.0, 2.7):
        khung = bd.ve_canh(kb["canh"][0], t, 3.0)
        assert khung.size == (W, H) and khung.mode == "RGB"
    khung = bd.ve_canh(kb["canh"][0], 1.2, 3.0)
    assert khung.getextrema() != ((255, 255), (255, 255), (255, 255)), "phải vẽ ra nhân vật"


def test_nhip_hinh_giu_hinh_trong_buoc(ch, tmp_path):
    lop = {"nhan_vat": "max", "co": 0.4, "chop_mat": False,
           "dong_tac": [{"tu_the": "gio-hai-tay", "luc": 0.0, "thoi_luong": 1.0}]}
    bd, kb = _bo_dung_ghep(ch, tmp_path, lop)
    a = bd.ve_canh(kb["canh"][0], 0.401, 3.0).tobytes()
    b = bd.ve_canh(kb["canh"][0], 0.43, 3.0).tobytes()  # cùng ô 1/15 s (0,4 .. 0,4667)
    c = bd.ve_canh(kb["canh"][0], 0.47, 3.0).tobytes()
    assert a == b and a != c


def test_kich_ban_ghep_kiem_loi(ch):
    lop = {"nhan_vat": "max", "dong_tac": [{"tu_the": "dung", "luc": 0.5, "easing": "bay"}],
           "di": {"tu": [0.1, 0.9]}}
    with pytest.raises(LoiKichBan) as loi:
        kiem_kich_ban(_kb_ghep(lop), ch)
    tb = str(loi.value)
    assert "dong_tac[0]" in tb and "'easing'" in tb and "'den'" in tb


def test_kich_ban_ghep_mac_dinh(ch):
    kb = kiem_kich_ban(_kb_ghep({"nhan_vat": "max"}, nhip_hinh=12), ch)
    lop = kb["canh"][0]["lop"][0]
    assert lop["tu_the"] == "dung" and lop["chop_mat"] is True and lop["noi"] is False
    assert lop["dong_tac"] == [] and lop["di"] is None and lop["hieu_ung"] == "khong"
    assert kb["nhip_hinh"] == 12


def test_hieu_nang_1080p_hai_nhan_vat(ch, tmp_path):
    """Mục tiêu ≤ 60 ms/khung ở Ryzen 5500U; ở đây chỉ chặn trên lỏng (máy test khác nhau)."""
    tao_nhan_vat_ghep_tam(tmp_path / "kho-mau", "max")
    kb = kiem_kich_ban({"canh": [{"id": "c01", "loi": "", "thoi_luong": 4.0, "may_quay": "zoom-cham", "lop": [
        {"nhan_vat": "max", "vi_tri": [0.3, 0.9], "neo": "day", "co": 0.3, "noi": True,
         "dong_tac": [{"tu_the": "chi-tay-phai", "luc": 0.5}]},
        {"nhan_vat": "max", "vi_tri": [0.7, 0.9], "neo": "day", "co": 0.3, "lat": True,
         "di": {"tu": [0.9, 0.9], "den": [0.7, 0.9], "thoi_luong": 3.0}}]}]}, ch)
    ds, _ = lap_dong_thoi_gian(kb, {}, ch)
    bd = BoDung(kb, ds, ch, tmp_path / "du-an" / "thu", nhap=False)
    for f in range(30):  # làm nóng bộ đệm ảnh xoay
        bd.ve_canh(kb["canh"][0], f / 30, 4.0)
    bat_dau = time.perf_counter()
    for f in range(30, 90):
        bd.ve_canh(kb["canh"][0], f / 30, 4.0)
    ms = (time.perf_counter() - bat_dau) / 60 * 1000
    assert ms < 400, f"{ms:.0f} ms/khung"
