"""Test nguoique/kiem_nhip.py: các luật nhịp trên dòng thời gian dựng tay (không cần giọng thật)."""

import pytest

from nguoique.kiem_nhip import bao_cao_nhip, co_doi_hinh, kiem_nhip


def _ds(canh_dai, loi="one two three four five six seven eight nine ten", giong_ty_le=0.8):
    """[(canh dict, thời lượng)] -> (ds, tổng). Giọng chiếm giong_ty_le thời lượng cảnh."""
    ds, t = [], 0.0
    for canh, dai in canh_dai:
        canh = dict({"loi": loi}, **canh)
        ds.append({"id": canh["id"], "canh": canh, "bat_dau": t, "ket_thuc": t + dai, "thoi_luong": dai,
                   "giong_giay": dai * giong_ty_le if canh.get("loi") else 0.0})
        t += dai
    return ds, t


def _co(kq, chu):
    return any(chu in c for c in kq["canh_bao"])


def test_canh_dai_khong_doi_hinh(ch):
    ds, tong = _ds([({"id": "c01"}, 9.0),
                    ({"id": "c02", "lop": [{"anh": "a.png", "tre": 3.0}]}, 9.0),
                    ({"id": "c03", "may_quay": {"kieu": "khung", "moc": [{"t": 0}, {"t": 4}]}}, 9.0),
                    ({"id": "c04"}, 7.0)])
    kq = kiem_nhip({}, ds, tong, ch)
    assert _co(kq, "Cảnh c01")
    assert not _co(kq, "Cảnh c02") and not _co(kq, "Cảnh c03") and not _co(kq, "Cảnh c04")


def test_co_doi_hinh_bo_qua_tre_ngoai_canh():
    assert not co_doi_hinh({"lop": [{"tre": 0.0}], "chu": [{"tre": 12.0}]}, 9.0)
    assert co_doi_hinh({"lop": [{"het": 4.0}]}, 9.0)
    assert co_doi_hinh({"lop": [{"dong_tac": [{"t": 1}]}]}, 9.0)


def test_sau_muoi_giay_dau_cham_qua(ch):
    ds, tong = _ds([({"id": f"c{i:02d}"}, 5.0) for i in range(20)])
    kq = kiem_nhip({}, ds, tong, ch)
    assert kq["tb_dau_video"] == pytest.approx(5.0)
    assert _co(kq, "60s đầu")
    ds2, tong2 = _ds([({"id": f"c{i:02d}"}, 3.0) for i in range(20)])
    assert not _co(kiem_nhip({}, ds2, tong2, ch), "60s đầu")


def test_tong_thoi_luong_va_toi_den(ch):
    # 10 phút, cảnh 3s, toi-den mỗi 90s -> không báo tổng / toi-den
    canh = [({"id": f"c{i:03d}", "chuyen_canh": {"kieu": "toi-den" if i % 30 == 0 else "cat"}}, 3.0)
            for i in range(200)]
    ds, tong = _ds(canh)
    kq = kiem_nhip({}, ds, tong, ch)
    assert not _co(kq, "Tổng thời lượng")
    assert not _co(kq, "toi-den")
    # bỏ hết toi-den -> báo khoảng dài
    ds2, tong2 = _ds([({"id": f"c{i:03d}"}, 3.0) for i in range(200)])
    assert _co(kiem_nhip({}, ds2, tong2, ch), "toi-den")
    # 1 phút -> ngoài 8–15 phút
    ds3, tong3 = _ds([({"id": f"c{i:02d}"}, 3.0) for i in range(20)])
    assert _co(kiem_nhip({}, ds3, tong3, ch), "Tổng thời lượng")


def test_toc_do_doc(ch):
    # 10 từ trong 3,6s giọng -> ~167 từ/phút: đạt
    ds, tong = _ds([({"id": f"c{i:02d}"}, 4.5) for i in range(10)])
    kq = kiem_nhip({}, ds, tong, ch)
    assert kq["tu_moi_phut"] == pytest.approx(10 / 3.6 * 60)
    assert not _co(kq, "Tốc độ đọc")
    # 10 từ trong 6s -> 100 từ/phút: chậm
    ds2, tong2 = _ds([({"id": f"c{i:02d}"}, 7.5) for i in range(10)])
    assert _co(kiem_nhip({}, ds2, tong2, ch), "Tốc độ đọc")


def test_nguong_doc_tu_config_va_bao_cao(ch):
    ch["kiem_nhip"] = {"tong_phut": [0, 100]}
    ds, tong = _ds([({"id": "c01"}, 3.0)])
    kq = kiem_nhip({}, ds, tong, ch)
    assert not _co(kq, "Tổng thời lượng")
    chu = bao_cao_nhip(kq)
    assert "1 cảnh" in chu
