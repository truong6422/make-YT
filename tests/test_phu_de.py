"""Test nguoique/phu_de.py: chia cụm, mốc thời gian, định dạng .srt."""

import re

import pytest

from nguoique.phu_de import chia_cum, ghi_srt, lap_phu_de

LOI = ("Imagine you own two stocks. One is up, one is down, and you need cash today because "
       "the rent is due and the landlord does not care about your portfolio at all. Which one do you sell?")


@pytest.mark.parametrize("toi_da", [1, 3, 5, 8, 12])
def test_chia_cum_khong_vuot_so_tu(toi_da):
    cum = chia_cum(LOI, toi_da)
    assert cum
    for c in cum:
        assert 1 <= len(c.split()) <= toi_da, c


@pytest.mark.parametrize("toi_da", [1, 3, 5, 8, 12])
def test_chia_cum_khong_mat_tu(toi_da):
    assert " ".join(chia_cum(LOI, toi_da)).split() == LOI.split()


def test_chia_cum_khong_tach_so_co_dau_phay():
    cum = chia_cum("You pay 10,000 dollars.", 8)
    assert cum == ["You pay 10,000 dollars."]


def test_chia_cum_rong():
    assert chia_cum("", 8) == []
    assert chia_cum("   ", 8) == []


def _ds(canh_giong):
    """[(bat_dau, ket_thuc, bat_dau_giong, giong_giay, loi)] -> ds kiểu dòng thời gian."""
    return [
        {"id": f"c{i}", "canh": {"id": f"c{i}", "loi": loi}, "bat_dau": bd, "ket_thuc": kt,
         "thoi_luong": kt - bd, "bat_dau_giong": bdg, "giong_giay": gg}
        for i, (bd, kt, bdg, gg, loi) in enumerate(canh_giong, 1)
    ]


def test_lap_phu_de_moc_tang_dan_va_nam_trong_giong(ch):
    ch["phu_de"]["so_tu_toi_da"] = 5
    ds = _ds([
        (0.0, 6.0, 0.1, 5.6, LOI),
        (6.0, 7.0, 6.1, 0.0, ""),                     # không lời -> không có phụ đề
        (7.0, 10.0, 7.1, 2.5, "Most people sell the winner. And that choice has a name."),
    ])
    cum = lap_phu_de(ds, ch)
    assert cum
    for bd, kt, chu in cum:
        assert kt > bd
        assert len(chu.split()) <= 5
    # mốc tăng dần, không chồng nhau
    for (bd1, kt1, _), (bd2, _kt2, _) in zip(cum, cum[1:]):
        assert bd2 >= bd1
        assert bd2 >= kt1 - 1e-6
    # mỗi cụm nằm trong khoảng giọng của cảnh nó thuộc về
    khoang = [(0.1, 0.1 + 5.6), (7.1, 7.1 + 2.5)]
    for bd, kt, _ in cum:
        assert any(a - 1e-6 <= bd and kt <= b + 1e-6 for a, b in khoang), (bd, kt)
    # cụm đầu bắt đầu đúng lúc giọng, cụm cuối của cảnh kết thúc đúng lúc hết giọng
    assert cum[0][0] == pytest.approx(0.1)
    cum_c1 = [c for c in cum if c[1] <= 5.7 + 1e-6]
    assert cum_c1[-1][1] == pytest.approx(5.7)
    assert cum[-1][1] == pytest.approx(9.6)
    # không mất chữ
    assert " ".join(c[2] for c in cum).split() == (LOI + " Most people sell the winner. And that choice has a name.").split()


def test_lap_phu_de_chua_co_giong_trai_het_canh(ch):
    ds = _ds([(0.0, 3.0, 0.1, 0.0, "Hello there friend.")])
    cum = lap_phu_de(ds, ch)
    assert cum[0][0] == pytest.approx(0.1)
    assert cum[-1][1] == pytest.approx(3.0)


_MAU_TG = r"\d{2}:\d{2}:\d{2},\d{3}"


def test_ghi_srt_dung_dinh_dang(tmp_path):
    cum = [(0.1, 1.5, "Hello there."), (1.5, 62.25, "Second line"), (3661.007, 3662.0, "Late")]
    tep = ghi_srt(cum, tmp_path / "sub" / "x.srt")
    assert tep.is_file()
    noi_dung = tep.read_text(encoding="utf-8")
    khoi = [k for k in noi_dung.strip().split("\n\n") if k.strip()]
    assert len(khoi) == 3
    for i, k in enumerate(khoi, 1):
        dong = k.split("\n")
        assert dong[0] == str(i)
        assert re.fullmatch(_MAU_TG + " --> " + _MAU_TG, dong[1]), dong[1]
        assert dong[2] == cum[i - 1][2]
    assert "00:00:00,100 --> 00:00:01,500" in noi_dung
    assert "00:00:01,500 --> 00:01:02,250" in noi_dung
    assert "01:01:01,007 --> 01:01:02,000" in noi_dung


# ------------------------------------------------------------ khớp theo mốc từng mẩu giọng

def _ds_moc(loi, moc, bd=0.0, kt=4.0, bdg=0.1, gg=3.0):
    ds = _ds([(bd, kt, bdg, gg, loi)])
    ds[0]["moc"] = moc
    return ds


def test_lap_phu_de_theo_moc_moi_cau_mot_khoang(ch):
    ch["phu_de"]["so_tu_toi_da"] = 8
    loi = "We bought two stocks today, and we waited. One of them went up fast?"
    moc = [{"bat_dau": 0.1, "ket_thuc": 1.2}, {"bat_dau": 1.4, "ket_thuc": 2.0},   # nghỉ phẩy 0,2s
           {"bat_dau": 2.5, "ket_thuc": 3.1}]                                     # nghỉ chấm 0,5s
    cum = lap_phu_de(_ds_moc(loi, moc), ch)
    assert [c[2] for c in cum] == ["We bought two stocks today,", "and we waited.", "One of them went up fast?"]
    assert cum[0][0] == pytest.approx(0.1)
    assert cum[0][1] == pytest.approx(1.4)          # nghỉ ngắn: giữ đến mẩu kế, không nháy
    assert cum[1][1] == pytest.approx(2.0 + 0.09)   # nghỉ dài: tắt sau 0,09s, trống lúc nghỉ
    assert cum[2][0] == pytest.approx(2.5)          # câu sau bật đúng lúc tiếng
    for (bd1, kt1, _), (bd2, _kt2, _) in zip(cum, cum[1:]):
        assert bd2 >= kt1 - 1e-6


def test_lap_phu_de_lech_so_manh_thi_dung_cach_cu(ch):
    loi = "We bought two stocks today, and we waited."
    cum = lap_phu_de(_ds_moc(loi, [{"bat_dau": 0.1, "ket_thuc": 3.1}]), ch)  # 1 mốc, lời có 2 mẩu
    assert cum[0][0] == pytest.approx(0.1)
    assert cum[-1][1] == pytest.approx(3.1)          # trải đều cả khoảng giọng như cũ
    assert " ".join(c[2] for c in cum).split() == loi.split()


def test_lap_phu_de_cum_dai_trong_mot_manh_chia_nho(ch):
    ch["phu_de"]["so_tu_toi_da"] = 3
    loi = "Most people sell the winner first. And that choice has a name."
    moc = [{"bat_dau": 0.1, "ket_thuc": 1.6}, {"bat_dau": 2.1, "ket_thuc": 3.1}]
    cum = lap_phu_de(_ds_moc(loi, moc), ch)
    assert all(len(c[2].split()) <= 3 for c in cum)
    cau1 = [c for c in cum if c[1] <= 1.6 + 0.09 + 1e-6]
    assert " ".join(c[2] for c in cau1) == "Most people sell the winner first."
    assert " ".join(c[2] for c in cum).split() == loi.split()
