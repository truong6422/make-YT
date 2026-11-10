"""Test nguoique/kichban.py: nạp mẫu, báo lỗi rõ cảnh / khoá, id trùng, điền mặc định."""

import copy
import json

import pytest

from nguoique.kichban import (
    CHUYEN_CANH, HIEU_UNG_VAO, LIEN_TUC, MAY_QUAY, NEO, LoiKichBan, kiem_kich_ban, nap_kich_ban,
)

from conftest import ghi_kich_ban, kb_toi_gian


def test_mau_nap_duoc(kb_mau_path, ch):
    assert kb_mau_path.is_file(), "thiếu templates/kich-ban-mau.json"
    kb = nap_kich_ban(kb_mau_path, ch)
    assert kb["canh"], "mẫu phải có cảnh"
    assert kb["ngon_ngu"] == "en"
    ids = [c["id"] for c in kb["canh"]]
    assert len(ids) == len(set(ids))
    assert kb["_thu_muc"]
    for c in kb["canh"]:
        assert c["may_quay"]["kieu"] in MAY_QUAY
        assert c["chuyen_canh"]["kieu"] in CHUYEN_CANH
        for lop in c["lop"]:
            assert lop["hieu_ung"] in HIEU_UNG_VAO and lop["hieu_ung"] != "go-chu"
            assert lop["lien_tuc"] in LIEN_TUC
            assert lop["neo"] in NEO
        for chu in c["chu"]:
            assert chu["hieu_ung"] in HIEU_UNG_VAO


def test_nap_thu_muc_du_an(tmp_path, ch):
    ghi_kich_ban(tmp_path / "da", kb_toi_gian())
    kb = nap_kich_ban(tmp_path / "da", ch)  # truyền thư mục -> tự tìm kich-ban.json
    assert [c["id"] for c in kb["canh"]] == ["c01", "c02"]


def test_thieu_tep_bao_loi(tmp_path, ch):
    with pytest.raises(LoiKichBan):
        nap_kich_ban(tmp_path / "khong-co" / "kich-ban.json", ch)


def test_json_sai_bao_loi_dong_cot(tmp_path, ch):
    tep = tmp_path / "kich-ban.json"
    tep.write_text('{"canh": [ {"id": "c01",} ]}', encoding="utf-8")
    with pytest.raises(LoiKichBan, match="dòng"):
        nap_kich_ban(tep, ch)


@pytest.mark.parametrize(
    "sua, cho, khoa",
    [
        (lambda kb: kb["canh"][1]["lop"][0].__setitem__("hieu_ung", "bay-vong"), "cảnh c02.lop[0]", "hieu_ung"),
        (lambda kb: kb["canh"][0]["lop"][0].__setitem__("hieu_ung", "go-chu"), "cảnh c01.lop[0]", "hieu_ung"),
        (lambda kb: kb["canh"][0]["lop"][0].__setitem__("lien_tuc", "nhay"), "cảnh c01.lop[0]", "lien_tuc"),
        (lambda kb: kb["canh"][0]["lop"][0].__setitem__("neo", "tren"), "cảnh c01.lop[0]", "neo"),
        (lambda kb: kb["canh"][1]["chu"][0].__setitem__("hieu_ung", "lap-lanh"), "cảnh c02.chu[0]", "hieu_ung"),
        (lambda kb: kb["canh"][1].__setitem__("may_quay", "bay"), "cảnh c02.may_quay", "kieu"),
        (lambda kb: kb["canh"][1].__setitem__("chuyen_canh", {"kieu": "xoay", "thoi_luong": 0.3}),
         "cảnh c02.chuyen_canh", "kieu"),
    ],
)
def test_gia_tri_sai_chi_ro_canh_va_khoa(ch, sua, cho, khoa):
    kb = kb_toi_gian()
    sua(kb)
    with pytest.raises(LoiKichBan) as loi:
        kiem_kich_ban(kb, ch)
    tb = str(loi.value)
    assert cho in tb, tb
    assert f"'{khoa}'" in tb, tb


def test_gom_nhieu_loi_mot_lan(ch):
    kb = kb_toi_gian()
    kb["canh"][0]["lop"][0]["hieu_ung"] = "sai-1"
    kb["canh"][1]["chu"][0]["hieu_ung"] = "sai-2"
    with pytest.raises(LoiKichBan) as loi:
        kiem_kich_ban(kb, ch)
    tb = str(loi.value)
    assert "sai-1" in tb and "sai-2" in tb
    assert "cảnh c01" in tb and "cảnh c02" in tb


def test_id_trung_bao_loi(ch):
    kb = kb_toi_gian()
    kb["canh"][1]["id"] = "c01"
    with pytest.raises(LoiKichBan) as loi:
        kiem_kich_ban(kb, ch)
    tb = str(loi.value)
    assert "cảnh c01" in tb and "'id'" in tb and "trùng" in tb


def test_id_trung_qua_tep(tmp_path, ch):
    kb = kb_toi_gian()
    kb["canh"][1]["id"] = "c01"
    tep = ghi_kich_ban(tmp_path / "da", kb)
    with pytest.raises(LoiKichBan, match="trùng"):
        nap_kich_ban(tep, ch)


def test_canh_khong_loi_thieu_thoi_luong(ch):
    kb = kb_toi_gian()
    kb["canh"][0]["loi"] = ""
    kb["canh"][0].pop("thoi_luong", None)
    with pytest.raises(LoiKichBan, match="thoi_luong"):
        kiem_kich_ban(kb, ch)


def test_mac_dinh_duoc_dien(ch):
    ch = copy.deepcopy(ch)
    ch["am_thanh"]["nghi_giua_canh"] = 0.4
    ch["may_quay_mac_dinh"] = "zoom-cham"
    ch["chuyen_canh_mac_dinh"] = {"kieu": "cat", "thoi_luong": 0.3}
    kb_vao = {
        "tieu_de": "T",
        "canh": [
            {"id": "c01", "loi": "Hello there.",
             "lop": [{"anh": "nhan-vat/a.png"}],
             "chu": [{"noi_dung": "HI"}]},
            {"id": "c02", "loi": "", "thoi_luong": 2.0},
        ],
    }
    goc = copy.deepcopy(kb_vao)
    kb = kiem_kich_ban(kb_vao, ch)
    assert kb_vao == goc, "không được sửa dict đầu vào"

    assert kb["ngon_ngu"] == "en"
    assert kb["nhac_nen"] is None
    c1, c2 = kb["canh"]
    # dem_truoc / dem_sau thiếu -> None; dong_thoi_gian điền mặc định (test_dong_thoi_gian.py)
    assert c1["dem_truoc"] is None and c1["dem_sau"] is None
    assert c2["dem_truoc"] is None
    assert c1["toc_do"] is None and c1["nghi"] is None
    assert c1["thoi_luong"] is None
    assert c2["thoi_luong"] == pytest.approx(2.0)
    assert c1["loi_doc"] is None
    assert c1["nen"] == "#FFFFFF"
    assert c1["may_quay"]["kieu"] == "zoom-cham"
    assert c1["may_quay"]["muc"] > 0
    assert c1["chuyen_canh"] == {"kieu": "cat", "thoi_luong": pytest.approx(0.3)}
    assert c1["am_thanh"] == []

    lop = c1["lop"][0]
    assert lop["neo"] == "giua"
    assert lop["hieu_ung"] == "khong"
    assert lop["lien_tuc"] == "khong"
    assert lop["tre"] == 0.0
    assert lop["het"] is None
    assert lop["lat"] is False
    assert lop["am_thanh"] is None
    assert lop["vi_tri"] == [0.5, 0.5]

    chu = c1["chu"][0]
    assert chu["hieu_ung"] == "khong"
    assert chu["tre"] == 0.0
    assert chu["nen"] is None
    assert chu["vien"] == 0.0


def test_may_quay_chuoi_va_doi_tuong(ch):
    kb = kb_toi_gian()
    kb["canh"][0]["may_quay"] = "dam"
    kb["canh"][1]["may_quay"] = {"kieu": "zoom-ra", "muc": 0.2}
    kq = kiem_kich_ban(kb, ch)
    assert kq["canh"][0]["may_quay"]["kieu"] == "dam"
    assert kq["canh"][1]["may_quay"] == {"kieu": "zoom-ra", "muc": pytest.approx(0.2)}


def test_am_thanh_lop_chuoi_thanh_doi_tuong(ch):
    kb = kb_toi_gian()
    kb["canh"][0]["lop"][0]["am_thanh"] = "am-thanh/pop.wav"
    kq = kiem_kich_ban(kb, ch)
    assert kq["canh"][0]["lop"][0]["am_thanh"] == {"tep": "am-thanh/pop.wav", "am_luong": 1.0}


def test_mau_hop_le_qua_json(tmp_path, ch, kb_mau_path):
    """Mẫu chép sang dự án mới (như `nq moi`) vẫn nạp được."""
    du_lieu = json.loads(kb_mau_path.read_text(encoding="utf-8-sig"))
    tep = ghi_kich_ban(tmp_path / "moi", du_lieu)
    kb = nap_kich_ban(tep, ch)
    assert len(kb["canh"]) == len(du_lieu["canh"])


def test_toc_do_va_nghi_cua_canh(ch):
    kb = kb_toi_gian()
    kb["canh"][0]["toc_do"] = 1.05
    kb["canh"][0]["nghi"] = {"cham": 0.6, "phay": 0.15}
    kq = kiem_kich_ban(kb, ch)
    assert kq["canh"][0]["toc_do"] == pytest.approx(1.05)
    assert kq["canh"][0]["nghi"] == {"cham": pytest.approx(0.6), "phay": pytest.approx(0.15)}
    assert kq["canh"][1]["toc_do"] is None


@pytest.mark.parametrize("sai", [{"toc_do": 1.5}, {"toc_do": 0.5}, {"nghi": {"dau": 0.3}}, {"nghi": {"cham": -1}},
                                 {"nghi": 0.4}])
def test_toc_do_nghi_sai_bao_loi(ch, sai):
    kb = kb_toi_gian()
    kb["canh"][0].update(sai)
    with pytest.raises(LoiKichBan):
        kiem_kich_ban(kb, ch)
