"""Test nguoique/dong_thoi_gian.py: thời lượng cảnh, nối tiếp, tổng, số khung không trôi."""

import pytest

from nguoique.dong_thoi_gian import THOI_LUONG_TOI_THIEU, lap_dong_thoi_gian, so_khung
from nguoique.kichban import kiem_kich_ban


def _giong(tmp_path, cac: dict) -> dict:
    """{id: giây} -> {id: (tệp có thật, giây)} (lap_dong_thoi_gian kiểm tệp còn tồn tại)."""
    kq = {}
    for cid, giay in cac.items():
        tep = tmp_path / f"{cid}.wav"
        tep.write_bytes(b"RIFF")  # chỉ cần tồn tại
        kq[cid] = (tep, giay)
    return kq


def _kb(ch, canh):
    return kiem_kich_ban({"tieu_de": "T", "canh": canh}, ch)


def test_thoi_luong_bang_dem_truoc_giong_dem_sau(ch, tmp_path):
    kb = _kb(ch, [{"id": "c01", "loi": "Hello.", "dem_truoc": 0.2, "dem_sau": 0.3}])
    ds, tong = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 2.0}), ch)
    assert ds[0]["thoi_luong"] == pytest.approx(0.2 + 2.0 + 0.3)
    assert ds[0]["bat_dau"] == pytest.approx(0.0)
    assert ds[0]["bat_dau_giong"] == pytest.approx(0.2)
    assert tong == pytest.approx(2.5)


def test_mac_dinh_dem_truoc_va_nghi_giua_canh(ch, tmp_path):
    ch["am_thanh"]["nghi_giua_canh"] = 0.25
    ch["am_thanh"]["dem_truoc"] = 0.15
    kb = _kb(ch, [{"id": "c01", "loi": "Hello."}])
    ds, _ = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 1.5}), ch)
    assert ds[0]["thoi_luong"] == pytest.approx(0.15 + 1.5 + 0.25)
    assert ds[0]["dem_truoc"] == pytest.approx(0.15)


def test_mac_dinh_khi_kb_chua_qua_kiem(ch, tmp_path):
    """dem_truoc / dem_sau thiếu (None) trong dict thô cũng dùng mặc định; config thiếu khoá -> 0,15 / 0,35."""
    ch["am_thanh"].pop("dem_truoc", None)
    ch["am_thanh"].pop("nghi_giua_canh", None)
    kb = {"canh": [{"id": "c01", "loi": "Hello."}]}
    ds, _ = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 1.0}), ch)
    assert ds[0]["thoi_luong"] == pytest.approx(0.15 + 1.0 + 0.35)


def test_toi_thieu_thoi_luong(ch, tmp_path):
    kb = _kb(ch, [{"id": "c01", "loi": "Hi.", "thoi_luong": 4.0, "dem_truoc": 0.1, "dem_sau": 0.1}])
    ds, tong = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 1.0}), ch)
    assert ds[0]["thoi_luong"] == pytest.approx(4.0)
    assert tong == pytest.approx(4.0)


def test_toi_thieu_nua_giay(ch, tmp_path):
    assert THOI_LUONG_TOI_THIEU == pytest.approx(0.5)
    kb = _kb(ch, [{"id": "c01", "loi": "Hi.", "dem_truoc": 0.0, "dem_sau": 0.0}])
    ds, _ = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 0.2}), ch)
    assert ds[0]["thoi_luong"] == pytest.approx(0.5)


def test_canh_khong_loi_dung_thoi_luong(ch):
    kb = _kb(ch, [{"id": "c01", "loi": "", "thoi_luong": 1.7, "dem_sau": 0.0}])
    ds, tong = lap_dong_thoi_gian(kb, {}, ch)
    assert ds[0]["giong"] is None
    assert ds[0]["thoi_luong"] == pytest.approx(1.7)
    assert tong == pytest.approx(1.7)


def test_thieu_giong_thi_im_lang_khong_loi(ch):
    kb = _kb(ch, [{"id": "c01", "loi": "Hello.", "dem_truoc": 0.1, "dem_sau": 0.25}])
    ds, _ = lap_dong_thoi_gian(kb, None, ch)
    assert ds[0]["giong"] is None
    assert ds[0]["giong_giay"] == 0.0
    assert ds[0]["thoi_luong"] == pytest.approx(0.5)  # 0,35 < 0,5


def _ds_nhieu_canh(ch, tmp_path):
    giay = {"c01": 1.234, "c02": 2.071, "c03": 0.333, "c04": 3.917, "c05": 1.001}
    canh = [{"id": cid, "loi": f"Scene {cid}."} for cid in giay]
    canh.append({"id": "c06", "loi": "", "thoi_luong": 1.111})
    kb = _kb(ch, canh)
    return lap_dong_thoi_gian(kb, _giong(tmp_path, giay), ch)


def test_canh_noi_tiep_va_tong_dung(ch, tmp_path):
    ds, tong = _ds_nhieu_canh(ch, tmp_path)
    assert [m["id"] for m in ds] == ["c01", "c02", "c03", "c04", "c05", "c06"]
    assert ds[0]["bat_dau"] == pytest.approx(0.0)
    for truoc, sau in zip(ds, ds[1:]):
        assert sau["bat_dau"] == pytest.approx(truoc["ket_thuc"])  # nối tiếp, không chồng
    for m in ds:
        assert m["ket_thuc"] - m["bat_dau"] == pytest.approx(m["thoi_luong"])
        assert m["bat_dau"] <= m["bat_dau_giong"] <= m["ket_thuc"]
        assert m["bat_dau_giong"] + m["giong_giay"] <= m["ket_thuc"] + 1e-9  # giọng nằm gọn trong cảnh
    assert tong == pytest.approx(ds[-1]["ket_thuc"])
    assert tong == pytest.approx(sum(m["thoi_luong"] for m in ds))


@pytest.mark.parametrize("fps", [15, 24, 25, 30, 60])
def test_so_khung_khong_troi(ch, tmp_path, fps):
    ds, tong = _ds_nhieu_canh(ch, tmp_path)
    tong_khung = 0
    f_cuoi = 0
    for m in ds:
        f0, f1 = so_khung(m["bat_dau"], m["ket_thuc"], fps)
        assert f0 == f_cuoi, "khung đầu cảnh phải tiếp đúng khung cuối cảnh trước"
        assert f1 >= f0
        tong_khung += f1 - f0
        f_cuoi = f1
    assert tong_khung == round(tong * fps)


def test_so_khung_cong_thuc():
    assert so_khung(0.0, 1.0, 30) == (0, 30)
    assert so_khung(1.02, 2.05, 30) == (round(1.02 * 30), round(2.05 * 30))


# ------------------------------------------------------------ nghỉ cuối phần, mốc giọng

def test_nghi_cuoi_phan_khi_canh_ke_doi_phan(ch, tmp_path):
    ch["am_thanh"]["nghi_giua_canh"] = 0.35
    ch["am_thanh"]["nghi_cuoi_phan"] = 0.9
    kb = _kb(ch, [
        {"id": "c01", "phan": "hook", "loi": "One."},
        {"id": "c02", "phan": "hook", "loi": "Two."},          # kế là boi-canh -> 0,9
        {"id": "c03", "phan": "boi-canh", "loi": "Three.", "dem_sau": 0.2},  # ghi tay thắng
        {"id": "c04", "phan": "ket", "loi": "Four."},          # cảnh cuối -> nghi_giua_canh
    ])
    ds, _ = lap_dong_thoi_gian(kb, _giong(tmp_path, {c: 1.0 for c in ("c01", "c02", "c03", "c04")}), ch)
    assert [m["dem_sau"] for m in ds] == [pytest.approx(0.35), pytest.approx(0.9), pytest.approx(0.2),
                                         pytest.approx(0.35)]


def test_khong_co_phan_thi_khong_doi_nghi(ch, tmp_path):
    ch["am_thanh"]["nghi_giua_canh"] = 0.35
    kb = _kb(ch, [{"id": "c01", "loi": "One."}, {"id": "c02", "phan": "hook", "loi": "Two."}])
    ds, _ = lap_dong_thoi_gian(kb, _giong(tmp_path, {"c01": 1.0, "c02": 1.0}), ch)
    assert ds[0]["dem_sau"] == pytest.approx(0.35)


def test_gan_moc_giong_giay_tuyet_doi(ch, tmp_path):
    import json

    giong = _giong(tmp_path, {"c01": 2.0, "c02": 1.0})
    moc = {"phien_ban": 1, "thoi_luong": 2.0, "manh": [
        {"chu": "Hello there friend,", "bat_dau": 0.0, "ket_thuc": 0.8},
        {"chu": "how are you?", "bat_dau": 1.0, "ket_thuc": 2.0}]}
    giong["c01"][0].with_suffix(".json").write_text(json.dumps(moc), encoding="utf-8")
    # mốc cũ (lệch thời lượng) của c02 -> bỏ qua
    giong["c02"][0].with_suffix(".json").write_text(json.dumps(dict(moc, thoi_luong=5.0)), encoding="utf-8")
    kb = _kb(ch, [{"id": "c01", "loi": "Hello there friend, how are you?", "dem_truoc": 0.2},
                  {"id": "c02", "loi": "Fine."}])
    ds, _ = lap_dong_thoi_gian(kb, giong, ch)
    m = ds[0]["moc"]
    assert [x["bat_dau"] for x in m] == [pytest.approx(0.2), pytest.approx(1.2)]
    assert m[-1]["ket_thuc"] == pytest.approx(2.2)
    assert ds[1]["moc"] is None
