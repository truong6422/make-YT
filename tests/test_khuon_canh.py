"""Test nguoique/khuon_canh.py: điền tham số, ghi đè, báo lỗi, mọi khuôn trong templates/khuon-canh triển khai được."""

import json

import pytest

from nguoique.khuon_canh import (
    THU_MUC_KHUON, LoiKhuonCanh, danh_sach_khuon, doc_khuon, tham_so_mau, trien_khai,
)
from nguoique.kichban import LoiKichBan, kiem_kich_ban

KHUON_THU = {
    "_mo_ta": "khuôn thử",
    "_tham_so": {
        "loi": {"bat_buoc": True, "mo_ta": "lời", "vi_du": "Hello there, this is a test."},
        "chu": {"mac_dinh": "HELLO", "mo_ta": "chữ"},
        "tre": {"mac_dinh": 0.8, "mo_ta": "trễ"},
        "dao_cu": {"mac_dinh": "dao-cu/tien.png", "mo_ta": "đạo cụ"},
        "bieu_cam": {"mac_dinh": "vui", "mo_ta": "biểu cảm"},
    },
    "canh": {
        "phan": "hook",
        "loi": "{{loi}}",
        "nen": "#F5F1E8",
        "may_quay": "zoom-cham",
        "lop": [
            {"anh": "nhan-vat/max__{{bieu_cam}}__dung.png", "vi_tri": [0.3, 0.9], "neo": "day", "co": 0.6},
            {"anh": "{{dao_cu}}", "vi_tri": [0.7, 0.4], "co": 0.2, "hieu_ung": "bat-len", "tre": "{{tre}}"},
        ],
        "chu": [{"noi_dung": "{{chu}}!", "vi_tri": [0.7, 0.2], "co": 90, "tre": "{{tre}}"}],
    },
}


@pytest.fixture
def tm(tmp_path):
    d = tmp_path / "khuon"
    d.mkdir()
    (d / "thu.json").write_text(json.dumps(KHUON_THU, ensure_ascii=False), encoding="utf-8")
    return d


def _kb(*canh, **goc):
    return {"tieu_de": "T", "ngon_ngu": "en", "nhac_nen": None, "canh": list(canh), **goc}


def test_trien_khai_dien_tham_so(tm):
    kb = _kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "Max opens the app.", "tre": 1.5, "bieu_cam": "soc"}})
    ra = trien_khai(kb, tm)
    c = ra["canh"][0]
    assert c["id"] == "c01" and c["loi"] == "Max opens the app."
    assert "khuon" not in c and "tham_so" not in c
    assert c["lop"][0]["anh"] == "nhan-vat/max__soc__dung.png"  # chỗ trống giữa chuỗi
    assert c["lop"][1]["tre"] == 1.5 and isinstance(c["lop"][1]["tre"], float)  # chỗ trống một mình giữ kiểu số
    assert c["chu"][0]["noi_dung"] == "HELLO!"  # mặc định
    assert kb["canh"][0]["khuon"] == "thu", "không được sửa kịch bản gốc"


def test_ghi_de_thang_khuon(tm):
    lop_moi = [{"anh": "dao-cu/bong-den.png", "vi_tri": [0.5, 0.5]}]
    kb = _kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "Hi there friend."},
              "may_quay": "dam", "lop": lop_moi, "chu_them": [{"noi_dung": "EXTRA"}], "dem_sau": 0.6})
    c = trien_khai(kb, tm)["canh"][0]
    assert c["may_quay"] == "dam"
    assert c["lop"] == lop_moi  # thay nguyên, không trộn
    assert [x["noi_dung"] for x in c["chu"]] == ["HELLO!", "EXTRA"]
    assert c["dem_sau"] == 0.6 and c["phan"] == "hook"


def test_tham_so_rong_bo_lop(tm):
    kb = _kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "No prop here.", "dao_cu": ""}})
    c = trien_khai(kb, tm)["canh"][0]
    assert [l["anh"] for l in c["lop"]] == ["nhan-vat/max__vui__dung.png"]


def test_tham_so_chung(tm):
    kb = _kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "One."}},
             {"id": "c02", "khuon": "thu", "tham_so": {"loi": "Two.", "chu": "OWN"}},
             tham_so_chung={"chu": "SHARED", "khong_ai_dung": 1})
    ra = trien_khai(kb, tm)
    assert "tham_so_chung" not in ra
    assert [c["chu"][0]["noi_dung"] for c in ra["canh"]] == ["SHARED!", "OWN!"]


def test_thieu_tham_so_bat_buoc(tm):
    kb = _kb({"id": "c07", "khuon": "thu", "tham_so": {"chu": "X"}})
    with pytest.raises(LoiKhuonCanh, match=r"c07.*loi"):
        trien_khai(kb, tm)


def test_tham_so_la_bao_loi(tm):
    kb = _kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "Hi.", "chuu": "typo"}})
    with pytest.raises(LoiKhuonCanh, match="chuu"):
        trien_khai(kb, tm)


def test_khuon_khong_ton_tai(tm):
    kb = _kb({"id": "c03", "khuon": "khong-co", "tham_so": {}})
    with pytest.raises(LoiKhuonCanh, match="khong-co") as e:
        trien_khai(kb, tm)
    assert "thu" in str(e.value)  # liệt kê khuôn có
    assert isinstance(e.value, LoiKichBan)  # CLI bắt chung với lỗi kịch bản


def test_canh_thuong_giu_nguyen(tm):
    thuong = {"id": "c01", "loi": "Plain scene.", "nen": "#FFFFFF"}
    assert trien_khai(_kb(thuong), tm)["canh"][0] == thuong


def test_thu_muc_dau_uu_tien(tm, tmp_path):
    rieng = tmp_path / "rieng"
    rieng.mkdir()
    k = json.loads(json.dumps(KHUON_THU))
    k["canh"]["nen"] = "#000000"
    (rieng / "thu.json").write_text(json.dumps(k), encoding="utf-8")
    c = trien_khai(_kb({"id": "c01", "khuon": "thu", "tham_so": {"loi": "Hi."}}), [rieng, tm])["canh"][0]
    assert c["nen"] == "#000000"


DS_KHUON = danh_sach_khuon(THU_MUC_KHUON)


def test_du_bo_khuon():
    can = {"mo-bai-cau-hoi", "dat-van-de", "hai-lua-chon", "so-sanh-truoc-sau", "bieu-do-tang", "bieu-do-giam",
           "ten-khai-niem", "trich-nghien-cuu", "con-so-lon", "danh-sach-3-y", "vi-du-doi-thuong", "dam-dong",
           "noi-tam", "meo-tranh", "tom-tat", "mien-tru", "ket-keu-goi"}
    assert can <= set(DS_KHUON), f"thiếu khuôn: {sorted(can - set(DS_KHUON))}"


@pytest.mark.parametrize("ten", DS_KHUON)
def test_moi_khuon_trien_khai_duoc(ten, ch, capsys):
    khuon = doc_khuon(ten)
    assert khuon.get("_mo_ta"), f"{ten}: thiếu _mo_ta"
    for t, dt in khuon["_tham_so"].items():
        assert dt.get("mo_ta"), f"{ten}.{t}: thiếu mo_ta"
    kb = _kb({"id": "c01", "khuon": ten, "tham_so": tham_so_mau(khuon)})
    ra = trien_khai(kb)
    assert "{{" not in json.dumps(ra, ensure_ascii=False), f"{ten}: còn chỗ trống chưa điền"
    kiem_kich_ban(ra, ch, nguon=f"khuôn {ten}")  # đúng lược đồ, giá trị trong tập hợp lệ
    assert "khoá lạ" not in capsys.readouterr().err


def test_kich_ban_khung_trien_khai_duoc(goc_repo, ch, capsys):
    kb = json.loads((goc_repo / "templates" / "kich-ban-khung.json").read_text(encoding="utf-8"))
    ra = kiem_kich_ban(trien_khai(kb), ch, nguon="kich-ban-khung.json")
    assert "khoá lạ" not in capsys.readouterr().err
    phan = [c["phan"] for c in ra["canh"]]
    for p in ("hook", "boi-canh", "vi-du", "giai-thich", "nghien-cuu", "cach-tranh", "tom-tat", "ket"):
        assert p in phan
    assert len({c["id"] for c in ra["canh"]}) == len(ra["canh"])
