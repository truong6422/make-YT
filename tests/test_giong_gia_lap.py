"""Test nguoique/giong.py với động cơ gia-lap (không cần mô hình / mạng)."""

import wave

import numpy as np
import pytest

from nguoique import giong


def _kb(loi1="Hello there, this is the first scene.", loi2="And this is the second one."):
    return {
        "tieu_de": "T",
        "ngon_ngu": "en",
        "canh": [
            {"id": "c01", "loi": loi1},
            {"id": "c02", "loi": loi2},
            {"id": "c03", "loi": "", "thoi_luong": 1.0},  # cảnh không lời: không có giọng
        ],
    }


def _doc_so_giay(tep):
    with wave.open(str(tep), "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
        return wf.getnframes() / float(wf.getframerate())


def test_tao_dong_co_gia_lap(ch):
    dc = giong.tao_dong_co(ch)
    assert dc.ten == "gia-lap"
    mau, sr = dc.doc("Hello world, testing.")
    assert sr == dc.tan_so
    assert isinstance(mau, np.ndarray) and mau.dtype == np.float32
    assert mau.size > 0
    assert float(np.max(np.abs(mau))) <= 1.0


def test_tao_giong_du_an_tao_wav(ch, tmp_path):
    build = tmp_path / "build"
    kq = giong.tao_giong_du_an(_kb(), build, ch)
    assert set(kq) == {"c01", "c02"}
    for cid, (tep, giay) in kq.items():
        assert tep.is_file(), cid
        assert tep.suffix == ".wav"
        assert giay > 0
        assert _doc_so_giay(tep) == pytest.approx(giay, abs=0.01)


def test_tao_giong_du_an_lan_hai_dung_bo_dem(ch, tmp_path, monkeypatch):
    build = tmp_path / "build"
    kq1 = giong.tao_giong_du_an(_kb(), build, ch)
    mtime = {cid: tep.stat().st_mtime_ns for cid, (tep, _) in kq1.items()}

    def _cam_nap(*_a, **_k):
        raise AssertionError("lần 2 không được nạp động cơ (phải dùng bộ đệm)")

    monkeypatch.setattr(giong, "tao_dong_co", _cam_nap)
    kq2 = giong.tao_giong_du_an(_kb(), build, ch)

    assert set(kq2) == set(kq1)
    for cid in kq1:
        assert kq2[cid][0] == kq1[cid][0]
        assert kq2[cid][1] == pytest.approx(kq1[cid][1], abs=0.01)
        assert kq2[cid][0].stat().st_mtime_ns == mtime[cid], f"{cid} bị ghi lại"


def test_doi_loi_chi_doc_lai_canh_do(ch, tmp_path):
    build = tmp_path / "build"
    kq1 = giong.tao_giong_du_an(_kb(), build, ch)
    kq2 = giong.tao_giong_du_an(_kb(loi2="The second scene now says something else."), build, ch)
    assert kq2["c01"][0] == kq1["c01"][0]
    assert kq2["c02"][0] != kq1["c02"][0]
    assert not kq1["c02"][0].exists(), "tệp cũ của cảnh đã đổi lời phải bị xoá"
    assert kq2["c02"][0].is_file()


def test_khong_co_canh_can_doc_thi_khong_nap_dong_co(ch, tmp_path, monkeypatch):
    def _cam_nap(*_a, **_k):
        raise AssertionError("không có lời thì không được nạp động cơ")

    monkeypatch.setattr(giong, "tao_dong_co", _cam_nap)
    kb = {"canh": [{"id": "c01", "loi": "", "thoi_luong": 1.0}]}
    assert giong.tao_giong_du_an(kb, tmp_path / "build", ch) == {}


# ------------------------------------------------------------ nghỉ theo dấu câu, mốc, bộ đệm mẩu

import json

LOI_BA_CAU = "We bought two stocks today. One of them went up fast? The other one went down."


def _kb_mot(loi=LOI_BA_CAU, **them):
    return {"canh": [dict({"id": "c01", "loi": loi}, **them)]}


def _moc(tep):
    return json.loads(tep.with_suffix(".json").read_text(encoding="utf-8"))


def test_chen_nghi_theo_dau_cau_va_ghi_moc(ch, tmp_path):
    ch["tts"]["nghi"] = {"phay": 0.2, "cham": 0.42, "hoi": 0.55, "ngat": 0.5, "doan": 0.8}
    tep, giay = giong.tao_giong_du_an(_kb_mot(), tmp_path / "build", ch)["c01"]
    moc = _moc(tep)
    assert moc["id"] == "c01"
    assert moc["thoi_luong"] == pytest.approx(giay, abs=0.01)
    manh = moc["manh"]
    assert [m["loai"] for m in manh] == ["cham", "hoi", None]
    assert manh[0]["bat_dau"] == pytest.approx(0.0)
    assert manh[-1]["ket_thuc"] == pytest.approx(giay, abs=0.01)
    # khoảng lặng giữa hai mẩu = nghỉ của dấu câu
    assert manh[1]["bat_dau"] - manh[0]["ket_thuc"] == pytest.approx(0.42, abs=0.002)
    assert manh[2]["bat_dau"] - manh[1]["ket_thuc"] == pytest.approx(0.55, abs=0.002)
    # lặng thật trong tệp wav
    wav, sr = giong.doc_wav(tep.read_bytes())
    a, b = int(manh[0]["ket_thuc"] * sr) + 5, int(manh[1]["bat_dau"] * sr) - 5
    assert float(np.max(np.abs(wav[a:b]))) < 1e-3


def test_canh_nghi_ghi_de_va_dung_lai_bo_dem_manh(ch, tmp_path, monkeypatch):
    build = tmp_path / "build"
    giong.tao_giong_du_an(_kb_mot(), build, ch)

    def _cam_nap(*_a, **_k):
        raise AssertionError("chỉ đổi nghỉ thì không được đọc lại (mẩu đã có trong bộ đệm)")

    monkeypatch.setattr(giong, "tao_dong_co", _cam_nap)
    tep, _ = giong.tao_giong_du_an(_kb_mot(nghi={"cham": 1.0}), build, ch)["c01"]
    manh = _moc(tep)["manh"]
    assert manh[1]["bat_dau"] - manh[0]["ket_thuc"] == pytest.approx(1.0, abs=0.002)


def test_sua_mot_cau_chi_doc_lai_mau_do(ch, tmp_path, monkeypatch):
    build = tmp_path / "build"
    giong.tao_giong_du_an(_kb_mot(), build, ch)
    da_doc = []
    goc = giong.GiaLap.doc

    def _dem(self, van_ban, toc_do=None):
        da_doc.append(van_ban)
        return goc(self, van_ban, toc_do)

    monkeypatch.setattr(giong.GiaLap, "doc", _dem)
    loi_moi = LOI_BA_CAU.replace("went down.", "went down hard.")
    giong.tao_giong_du_an(_kb_mot(loi_moi), build, ch)
    assert da_doc == ["The other one went down hard."]


def test_manh_ngan_gop_voi_manh_ke(ch, tmp_path):
    tep, _ = giong.tao_giong_du_an(_kb_mot("No. I mean it, really. Stop now please."), tmp_path / "build", ch)["c01"]
    chu = [m["chu"] for m in _moc(tep)["manh"]]
    # "No." (1 từ) gộp vào mẩu kế; "really." (1 từ) gộp vào mẩu kế
    assert chu == ["No. I mean it,", "really. Stop now please."]


def test_toc_do_canh_doi_do_dai_va_bam(ch, tmp_path):
    build = tmp_path / "build"
    noi = lambda tep: sum(m["ket_thuc"] - m["bat_dau"] for m in _moc(tep)["manh"])  # noqa: E731
    t1, g1 = giong.tao_giong_du_an(_kb_mot(), build, ch)["c01"]
    n1 = noi(t1)  # đọc trước: lần sau xoá tệp cũ của cảnh
    t2, g2 = giong.tao_giong_du_an(_kb_mot(toc_do=1.25), build, ch)["c01"]
    assert t1 != t2
    assert noi(t2) < n1
    assert g2 < g1


def test_toc_do_canh_ngoai_khoang_bao_loi(ch, tmp_path):
    with pytest.raises(ValueError, match="toc_do"):
        giong.tao_giong_du_an(_kb_mot(toc_do=2.0), tmp_path / "build", ch)
