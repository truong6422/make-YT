"""Test nguoique/dung_hinh.py ở 640x360 (không cần ffmpeg): vẽ khung, dán ảnh, chuyển cảnh, máy quay."""

import pytest
from PIL import Image

from nguoique.dong_thoi_gian import lap_dong_thoi_gian
from nguoique.dung_hinh import BoDung, dan
from nguoique.kichban import CHUYEN_CANH, HIEU_UNG_ANH, HIEU_UNG_VAO, LIEN_TUC, MAY_QUAY, LoiKichBan, kiem_kich_ban

from conftest import kb_toi_gian

W, H = 640, 360


def _bo_dung(ch, tmp_path, kb_vao=None, phu_de=None):
    kb = kiem_kich_ban(kb_vao or kb_toi_gian(so_canh=2, loi=False), ch)
    ds, tong = lap_dong_thoi_gian(kb, {}, ch)
    bd = BoDung(kb, ds, ch, tmp_path / "du-an" / "thu", nhap=True, phu_de=phu_de)
    return bd, kb, ds, tong


def test_kich_thuoc_nhap(ch, tmp_path):
    bd, *_ = _bo_dung(ch, tmp_path)
    assert (bd.W, bd.H, bd.fps) == (W, H, 15)


@pytest.mark.parametrize("t", [0.0, 0.1, 0.3, 0.9])
def test_ve_mot_khung_anh_thieu_dung_o_giu_cho(ch, tmp_path, t):
    bd, kb, ds, _ = _bo_dung(ch, tmp_path)
    canh = kb["canh"][0]
    khung = bd.ve_canh(canh, t, ds[0]["thoi_luong"])
    assert isinstance(khung, Image.Image)
    assert khung.size == (W, H)
    assert khung.mode == "RGB"


def test_o_giu_cho_co_ve_gi_do(ch, tmp_path):
    """Ảnh thiếu -> ô giữ chỗ xám, khác hẳn nền trắng trơn."""
    kb_vao = kb_toi_gian(so_canh=1, loi=False)
    kb_vao["canh"][0]["lop"][0].update({"hieu_ung": "khong", "co": 0.3, "vi_tri": [0.5, 0.5], "neo": "giua"})
    kb_vao["canh"][0]["chu"] = []
    kb_vao["canh"][0]["may_quay"] = "dung-yen"
    bd, kb, ds, _ = _bo_dung(ch, tmp_path, kb_vao)
    khung = bd.ve_canh(kb["canh"][0], 0.5, ds[0]["thoi_luong"])
    assert khung.getpixel((W // 2, H // 2)) != (255, 255, 255)
    assert khung.getpixel((2, 2)) == (255, 255, 255)


def test_moi_hieu_ung_va_lien_tuc_ve_duoc(ch, tmp_path):
    lop = [{"anh": f"nhan-vat/thieu-{i}.png", "vi_tri": [0.1 + 0.1 * i, 0.8], "co": 0.1,
            "hieu_ung": hu, "lien_tuc": LIEN_TUC[i % len(LIEN_TUC)], "het": 0.5, "lat": i % 2 == 0}
           for i, hu in enumerate(HIEU_UNG_ANH)]
    chu = [{"noi_dung": f"TEXT {i}", "vi_tri": [0.5, 0.1 + 0.08 * i], "co": 40, "hieu_ung": hu,
            "vien": 3, "nen": "#FFEE00" if i % 2 else None}
           for i, hu in enumerate(HIEU_UNG_VAO)]
    kb_vao = {"canh": [{"id": "c01", "loi": "", "thoi_luong": 2.0, "lop": lop, "chu": chu,
                        "nen": "phong-nen/thieu.png"}]}
    bd, kb, ds, _ = _bo_dung(ch, tmp_path, kb_vao)
    for t in (0.0, 0.05, 0.2, 0.45, 0.6, 1.5):
        assert bd.ve_canh(kb["canh"][0], t, 2.0).size == (W, H)


@pytest.mark.parametrize(
    "x, y",
    [(-500, -500), (-100, 50), (600, 300), (5000, 5000), (-5000, 10), (0, 0), (320.4, 180.6)],
)
def test_dan_tran_va_am_toa_do(x, y):
    khung = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    anh = Image.new("RGBA", (300, 200), (255, 0, 0, 255))
    dan(khung, anh, x, y)
    dan(khung, anh, x, y, alpha=0.5)
    dan(khung, anh, x, y, alpha=0.0)
    assert khung.size == (W, H)
    assert anh.size == (300, 200)


def test_dan_anh_lon_hon_khung():
    khung = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    anh = Image.new("RGBA", (2000, 1500), (0, 0, 255, 255))
    dan(khung, anh, -700, -600)
    assert khung.size == (W, H)
    assert khung.getpixel((10, 10))[:3] == (0, 0, 255)


def test_dan_dung_vi_tri():
    khung = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    anh = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    dan(khung, anh, -5, -5)
    assert khung.getpixel((0, 0))[:3] == (255, 0, 0)
    assert khung.getpixel((4, 4))[:3] == (255, 0, 0)
    assert khung.getpixel((5, 5))[:3] == (255, 255, 255)


@pytest.mark.parametrize("kieu", CHUYEN_CANH)
@pytest.mark.parametrize("p", [0.0, 0.2, 0.5, 0.8, 1.0])
def test_moi_kieu_chuyen_canh_dung_kich_thuoc(ch, tmp_path, kieu, p):
    bd, *_ = _bo_dung(ch, tmp_path)
    truoc = Image.new("RGB", (W, H), (10, 20, 30))
    hien = Image.new("RGB", (W, H), (200, 100, 50))
    ra = bd.chuyen_canh(truoc, hien, kieu, p)
    assert ra.size == (W, H)
    assert ra.mode == "RGB"


@pytest.mark.parametrize("kieu", MAY_QUAY)
@pytest.mark.parametrize("t", [0.0, 0.15, 1.0, 2.0])
def test_moi_kieu_may_quay_dung_kich_thuoc(ch, tmp_path, kieu, t):
    bd, *_ = _bo_dung(ch, tmp_path)
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    ra = bd.may_quay(khung, {"kieu": kieu, "muc": 0.1}, t, 2.0)
    assert ra.size == (W, H)


def test_cac_khung_dung_so_khung_va_so_byte(ch, tmp_path):
    kb_vao = kb_toi_gian(so_canh=2, loi=False)  # mỗi cảnh 1,0s, cảnh 2 chuyển mo-dan
    kb_vao["canh"][1]["loi"] = "Hello there, subtitle test."
    kb_vao["canh"][1]["thoi_luong"] = 1.0
    phu_de = [(1.1, 1.6, "Hello there,"), (1.6, 2.0, "subtitle test.")]
    bd, kb, ds, tong = _bo_dung(ch, tmp_path, kb_vao, phu_de=phu_de)
    so = 0
    for du_lieu in bd.cac_khung():
        assert len(du_lieu) == W * H * 3
        so += 1
    assert so == round(tong * 15)


def test_ve_phu_de_khong_loi(ch, tmp_path):
    bd, *_ = _bo_dung(ch, tmp_path, phu_de=[(0.0, 1.0, "A subtitle line that is quite long indeed")])
    khung = Image.new("RGB", (W, H), (0, 0, 0))
    bd.ve_phu_de(khung, 0.5)
    assert khung.size == (W, H)
    assert khung.getbbox() is not None, "phụ đề phải vẽ ra gì đó"


# ---------------- máy quay theo mốc, cầm tay, thương hiệu, hộp phụ đề (docs/10) ----------------
def test_may_quay_moc_doi_khung_toan_sang_can(ch, tmp_path):
    kb_vao = kb_toi_gian(so_canh=1, loi=False)
    kb_vao["canh"][0]["may_quay"] = {"moc": [{"luc": 0, "zoom": 1.0, "tam": [0.5, 0.5]},
                                             {"luc": 0.4, "zoom": 2.0, "tam": [0.25, 0.25], "thoi_luong": 0.4}]}
    bd, kb, ds, _ = _bo_dung(ch, tmp_path, kb_vao)
    mq = kb["canh"][0]["may_quay"]
    assert mq["kieu"] == "dung-yen" and len(mq["moc"]) == 2
    assert bd._moc_may_quay(mq["moc"], 0.2) == (1.0, 0.5, 0.5)
    z, x, y = bd._moc_may_quay(mq["moc"], 0.6)
    assert 1.0 < z < 2.0 and 0.25 < x < 0.5
    assert bd._moc_may_quay(mq["moc"], 0.9) == pytest.approx((2.0, 0.25, 0.25))
    # khung: nửa trên-trái đỏ -> zoom vào góc đó thì cả khung đỏ
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    khung.paste((255, 0, 0), (0, 0, W // 2, H // 2))
    ra = bd.may_quay(khung, mq, 0.9, 1.0)
    assert ra.size == (W, H)
    assert ra.getpixel((W - 5, H - 5))[0] > 200 and ra.getpixel((W - 5, H - 5))[1] < 60


def test_may_quay_moc_sai_bao_loi(ch):
    kb_vao = kb_toi_gian(so_canh=1, loi=False)
    kb_vao["canh"][0]["may_quay"] = {"moc": [{"luc": 0, "zoom": 0.5}]}
    with pytest.raises(LoiKichBan, match="zoom"):
        kiem_kich_ban(kb_vao, ch)


@pytest.mark.parametrize("t", [0.0, 0.6, 1.2, 2.4])
def test_lac_tay_cong_don(ch, tmp_path, t):
    bd, *_ = _bo_dung(ch, tmp_path)
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    assert bd.may_quay(khung, {"kieu": "zoom-cham", "muc": 0.05, "lac_tay": True}, t, 2.4).size == (W, H)
    assert bd.may_quay(khung, {"kieu": "lac-tay", "muc": 0.006}, t, 2.4).size == (W, H)


def test_thuong_hieu_ve_moi_khung(ch, tmp_path):
    kb_vao = kb_toi_gian(so_canh=1, loi=False)
    kb_vao["thuong_hieu"] = {"anh": "logo/khong-co.png", "vi_tri": [0.9, 0.1], "co": 0.1, "do_mo": 1.0}
    bd, kb, ds, _ = _bo_dung(ch, tmp_path, kb_vao)
    assert kb["thuong_hieu"][0]["co"] == pytest.approx(0.1)
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    bd.ve_thuong_hieu(khung)
    assert khung.getpixel((int(0.9 * W), int(0.1 * H))) != (255, 255, 255)
    assert khung.getpixel((5, H - 5)) == (255, 255, 255)


def test_kich_ban_cu_khong_co_thuong_hieu(ch, tmp_path):
    bd, kb, *_ = _bo_dung(ch, tmp_path)
    assert "thuong_hieu" not in kb and bd.anh_thuong_hieu() == []


def test_hop_nen_phu_de(ch, tmp_path):
    ch = dict(ch)
    ch["phu_de"] = dict(ch["phu_de"], hop_nen="#000000", do_duc_hop=1.0, giu_hop_khi_lang=True, vien=0)
    bd, *_ = _bo_dung(ch, tmp_path, phu_de=[(0.0, 1.0, "Hi")])
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    bd.ve_phu_de(khung, 0.5)
    y = int(float(ch["phu_de"]["vi_tri_y"]) * H)
    assert khung.getpixel((int(W * 0.15), y)) == (0, 0, 0), "hộp rộng ≥ 80% khung khi giu_hop_khi_lang"
    khung2 = Image.new("RGB", (W, H), (255, 255, 255))
    bd.ve_phu_de(khung2, 5.0)  # lặng: hộp vẫn còn
    assert khung2.getpixel((W // 2, y)) == (0, 0, 0)


def test_khong_co_hop_khi_khong_khai(ch, tmp_path):
    ch = dict(ch)
    ch["phu_de"] = {k: v for k, v in ch["phu_de"].items() if k != "hop_nen"}
    bd, *_ = _bo_dung(ch, tmp_path, phu_de=[(0.0, 1.0, "Hi")])
    assert bd._mau_hop is None
    khung = Image.new("RGB", (W, H), (255, 255, 255))
    bd.ve_phu_de(khung, 5.0)
    assert khung.getpixel((W // 2, H - 20)) == (255, 255, 255)


def test_dung_theo_doan_giong_het_tuan_tu(ch, tmp_path):
    """Dựng song song: ghép khung của từng đoạn (có chuyển cảnh mờ dần ở đầu đoạn) phải trùng khung tuần tự."""
    kb_vao = kb_toi_gian(so_canh=5, loi=False)
    for i, c in enumerate(kb_vao["canh"]):
        c["chuyen_canh"] = {"kieu": "mo-dan" if i % 2 else "toi-den", "thoi_luong": 0.3}
    bd, kb, ds, _ = _bo_dung(ch, tmp_path, kb_vao)
    tuan_tu = list(bd.cac_khung())
    for so_doan in (2, 3, 5):
        doan = bd.chia_doan(so_doan)
        assert doan[0][0] == 0 and doan[-1][1] == len(ds)
        assert all(a[1] == b[0] for a, b in zip(doan, doan[1:]))
        ghep = [k for i0, i1 in doan for k in bd.cac_khung(i0, i1)]
        assert ghep == tuan_tu
