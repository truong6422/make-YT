"""Test nguoique/chuan_hoa.py: từ điển khớp nguyên từ, $ và % đổi chữ, tach_doan."""

import pytest

from nguoique.chuan_hoa import chu_cho_dong_co, chuan_hoa, nap_tu_dien, tach_doan, tach_manh


# ------------------------------------------------------------ từ điển

def test_tu_dien_khop_nguyen_tu_co_chu_hoa():
    tu_dien = {"ETF": "E T F"}
    kq = chuan_hoa("An ETF is not ETFS or METF.", tu_dien)
    assert "An E T F is" in kq
    assert "ETFS" in kq  # không thay giữa từ
    assert "METF" in kq


def test_tu_dien_khoa_chu_hoa_phan_biet_hoa_thuong():
    kq = chuan_hoa("ETF and etf", {"ETF": "E T F"})
    assert kq == "E T F and etf"


def test_tu_dien_khoa_thuong_khong_phan_biet_hoa_thuong():
    kq = chuan_hoa("Ai said AI is ai.", {"ai": "A I"})
    # "said" chứa "ai" nhưng không phải nguyên từ -> giữ
    assert kq == "A I said A I is A I."


def test_tu_dien_khoa_dai_thang_khoa_ngan():
    kq = chuan_hoa("The S&P 500 rose.", {"S&P": "S and P", "S&P 500": "S and P five hundred"})
    assert kq == "The S and P five hundred rose."


def test_tu_dien_rong_hoac_none():
    assert chuan_hoa("Hello world.", {}) == "Hello world."
    assert chuan_hoa("Hello world.", None) == "Hello world."
    assert chuan_hoa("", {}) == ""


def test_nap_tu_dien_thieu_tep(tmp_path):
    assert nap_tu_dien(tmp_path / "khong-co.yaml") == {}
    assert nap_tu_dien(None) == {}


def test_nap_tu_dien_doc_yaml(tmp_path):
    tep = tmp_path / "td.yaml"
    tep.write_text("ETF: E T F\nP/E: P to E\n", encoding="utf-8")
    assert nap_tu_dien(tep) == {"ETF": "E T F", "P/E": "P to E"}


def test_nap_tu_dien_sai_cu_phap_bao_loi(tmp_path):
    tep = tmp_path / "td.yaml"
    tep.write_text("- a\n- b\n", encoding="utf-8")  # danh sách, không phải bảng
    with pytest.raises(ValueError):
        nap_tu_dien(tep)


# ------------------------------------------------------------ tiền, phần trăm

@pytest.mark.parametrize(
    "vao, ra",
    [
        ("It cost $5.", "It cost 5 dollars."),
        ("Only $1 left.", "Only 1 dollar left."),
        ("A $2.5 million deal.", "A 2.5 million dollars deal."),
        ("Pay $3.50 now.", "Pay 3 dollars and 50 cents now."),
        ("Just $0.99 today.", "Just 99 cents today."),
        ("Worth $1,000.", "Worth 1,000 dollars."),
        ("Raised $3B fast.", "Raised 3 billion dollars fast."),
    ],
)
def test_doi_tien_do_la(vao, ra):
    assert chuan_hoa(vao, {}) == ra


@pytest.mark.parametrize(
    "vao, ra",
    [
        ("Up 20% today.", "Up 20 percent today."),
        ("Down 3.5 % now.", "Down 3.5 percent now."),
    ],
)
def test_doi_phan_tram(vao, ra):
    assert chuan_hoa(vao, {}) == ra


def test_khong_con_ky_hieu_sau_chuan_hoa():
    kq = chuan_hoa("You lose $100 and feel 50% worse.", {})
    assert "$" not in kq
    assert "%" not in kq
    assert "100 dollars" in kq
    assert "50 percent" in kq


# ------------------------------------------------------------ tach_doan

_VAN_BAN_DAI = (
    "Imagine you bought two stocks last year. One went up a lot, the other went down. "
    "Which one would you sell first? Most people sell the winner, and they keep the loser, "
    "hoping it will come back. This is called the disposition effect; it is one of the most "
    "studied biases in behavioral finance, and it costs investors real money every single year. "
    "Short. "
    + "This sentence has no punctuation inside and it just keeps going on and on with many "
      "ordinary words so that it must be cut somewhere by the splitter without losing anything"
    + ". The end!"
)


@pytest.mark.parametrize("toi_da", [20, 40, 80, 150, 300])
def test_tach_doan_khong_vuot_toi_da(toi_da):
    doan = tach_doan(_VAN_BAN_DAI, toi_da)
    assert doan, "phải có ít nhất một đoạn"
    for d in doan:
        assert len(d) <= toi_da, f"đoạn dài {len(d)} > {toi_da}: {d!r}"
        assert d == d.strip() and d


@pytest.mark.parametrize("toi_da", [20, 40, 80, 150, 300])
def test_tach_doan_khong_mat_chu(toi_da):
    doan = tach_doan(_VAN_BAN_DAI, toi_da)
    assert " ".join(doan).split() == _VAN_BAN_DAI.split()


def test_tach_doan_ngan_giu_nguyen():
    assert tach_doan("Hello there. How are you?", 300) == ["Hello there. How are you?"]


def test_tach_doan_rong():
    assert tach_doan("", 300) == []
    assert tach_doan("   ", 300) == []
    assert tach_doan(None, 300) == []


def test_tach_doan_uu_tien_ranh_gioi_cau():
    doan = tach_doan("First sentence is here. Second sentence is here.", 30)
    assert doan == ["First sentence is here.", "Second sentence is here."]


# ------------------------------------------------------------ giu_ngat + tach_manh (nghỉ trong giọng)

def test_che_do_thuong_khong_doi():
    assert chuan_hoa("Wait — what?\nNext line.", {}) == "Wait, what? Next line."


def test_giu_ngat_giu_xuong_dong_gach_va_ba_cham():
    kq = chuan_hoa("He paused — then ran...\n\n  It cost $5.", {}, giu_ngat=True)
    assert kq == "He paused — then ran…\nIt cost 5 dollars."


def test_giu_ngat_khoang_so_van_thanh_to():
    assert chuan_hoa("From 2008–2009 it fell.", {}, giu_ngat=True) == "From 2008 to 2009 it fell."


def test_tach_manh_loai_nghi():
    manh = tach_manh("We bought two stocks today, and we waited. Was it smart? Maybe not… "
                     "We sold one — too early.\nThe end came fast.")
    assert manh == [
        ("We bought two stocks today,", "phay"),
        ("and we waited.", "cham"),
        ("Was it smart?", "hoi"),
        ("Maybe not… We sold one —", "ngat"),          # "Maybe not…" 2 từ -> gộp với mẩu kế
        ("too early. The end came fast.", None),        # "too early." 2 từ -> gộp, mất nghỉ đoạn
    ]


def test_tach_manh_xuong_dong_la_nghi_doan():
    manh = tach_manh("He waited for the market.\nThen everything changed at once.")
    assert manh == [("He waited for the market.", "doan"), ("Then everything changed at once.", None)]


def test_tach_manh_khong_tach_so_va_khong_mat_chu():
    loi = "You paid $3.50 at 9:30, then 10,000 dollars more. Ouch! That really hurt a lot."
    manh = tach_manh(loi)
    assert " ".join(c for c, _ in manh).split() == loi.split()
    assert manh[0] == ("You paid $3.50 at 9:30,", "phay")
    assert manh[-1][1] is None


def test_tach_manh_gop_manh_ngan():
    # "Ouch!" (1 từ) gộp vào mẩu kế; mẩu cuối ngắn gộp vào mẩu trước
    assert tach_manh("Ouch! That really hurt a lot. Bad.") == [("Ouch! That really hurt a lot. Bad.", None)]
    assert tach_manh("One two three. Four five six. Yes.") == [("One two three.", "cham"), ("Four five six. Yes.", None)]


def test_tach_manh_rong():
    assert tach_manh("") == []
    assert tach_manh(None) == []
    assert tach_manh("Hi.") == [("Hi.", None)]


def test_chu_cho_dong_co_bo_gach():
    assert chu_cho_dong_co("We sold one —") == "We sold one,"
    assert chu_cho_dong_co("Wait — no, stop.") == "Wait, no, stop."
