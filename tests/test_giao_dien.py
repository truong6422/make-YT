"""Giao diện quản trị: dữ liệu dự án, chặn đường dẫn, tải ảnh, máy chủ HTTP thật trên cổng ngẫu nhiên."""

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from nguoique import giao_dien as gd

PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


@pytest.fixture()
def ch(tmp_path):
    (tmp_path / "du-an").mkdir()
    (tmp_path / "kho").mkdir()
    return {"du_an": str(tmp_path / "du-an"), "kho_mau": str(tmp_path / "kho")}


def _tao_du_an(ch, slug="loss-aversion", kb=None):
    from pathlib import Path

    d = Path(ch["du_an"]) / slug
    d.mkdir()
    kb = kb or {"tieu_de": "Why losing hurts", "canh": [
        {"id": "c001", "phan": "hook", "loi": "Max just lost twenty dollars."},
        {"id": "c002", "khuon": "ten-khai-niem", "tham_so": {"loi": "This is called loss aversion."}},
    ]}
    (d / "kich-ban.json").write_text(json.dumps(kb), encoding="utf-8")
    return d


def test_kiem_slug():
    assert gd.kiem_slug("loss-aversion") == "loss-aversion"
    for xau in ("", "../x", "A", "a/b", "a b", "-a"):
        with pytest.raises(gd.LoiGiaoDien):
            gd.kiem_slug(xau)


def test_trong_thu_muc_chan_thoat(tmp_path):
    assert gd.trong_thu_muc(tmp_path, "a/b.png") == (tmp_path / "a" / "b.png").resolve()
    for xau in ("../x.png", "a/../../x.png", "%2e%2e/x.png"):
        with pytest.raises(gd.LoiGiaoDien):
            gd.trong_thu_muc(tmp_path, xau)


def test_ds_va_chi_tiet_du_an(ch):
    _tao_du_an(ch)
    ds = gd.ds_du_an(ch)
    assert [a["slug"] for a in ds] == ["loss-aversion"]
    assert ds[0]["so_canh"] == 2 and ds[0]["kich_ban_hop_le"] and not ds[0]["co_mp4"]
    ct = gd.chi_tiet_du_an(ch, "loss-aversion")
    assert ct["tom_tat"]["so_tu"] == 10
    assert ct["canh"][1]["loi"] == "This is called loss aversion." and ct["canh"][1]["phan"] == "hook"
    with pytest.raises(gd.LoiGiaoDien):
        gd.chi_tiet_du_an(ch, "khong-co")


def test_kich_ban_json_loi(ch):
    d = _tao_du_an(ch)
    (d / "kich-ban.json").write_text("{sai", encoding="utf-8")
    ct = gd.chi_tiet_du_an(ch, "loss-aversion")
    assert ct["loi_json"] and not ct["tom_tat"]["hop_le"]


def test_luu_chinh_sach(ch):
    d = _tao_du_an(ch)
    gd.luu_chinh_sach(ch, "loss-aversion", {"muc": {"y-rieng": True, "khong-logo": 0}, "ghi_chu": "ok"})
    luu = json.loads((d / "kiem-chinh-sach.json").read_text(encoding="utf-8"))
    assert luu["muc"] == {"y-rieng": True, "khong-logo": False} and luu["ghi_chu"] == "ok"
    assert gd.ds_du_an(ch)[0]["chinh_sach_xong"] == 1


def test_tai_anh(ch):
    p = gd.luu_anh_tai_len(ch, "Max__vui__dung.png", PNG_1x1)
    assert p.name == "max__vui__dung.png" and p.parent.name == "_cho-xu-ly"
    assert gd.ds_kho(ch)["_cho-xu-ly"][0]["ten"] == "max__vui__dung.png"
    with pytest.raises(gd.LoiGiaoDien):
        gd.luu_anh_tai_len(ch, "../x.png", PNG_1x1)
    with pytest.raises(gd.LoiGiaoDien):
        gd.luu_anh_tai_len(ch, "x.png", b"khong phai anh")


def test_lenh_cho_viec():
    ten, lenh = gd.lenh_cho_viec("nhap", "loss-aversion", None, None)
    assert lenh[-3:] == ["lam", "loss-aversion", "--nhap"]
    with pytest.raises(gd.LoiGiaoDien):
        gd.lenh_cho_viec("nhap", "../x", None, None)
    with pytest.raises(gd.LoiGiaoDien):
        gd.lenh_cho_viec("xoa-het", None, None, None)
    with pytest.raises(gd.LoiGiaoDien):
        gd.lenh_cho_viec("kich-ban", None, 'x" && rm', None)


def test_hang_viec_chay_lan_luot():
    import sys

    h = gd.HangViec()
    v1 = h.them("in 1", [sys.executable, "-c", "print('một')"])
    v2 = h.them("lỗi", [sys.executable, "-c", "import sys; sys.exit(3)"])
    han = time.time() + 30
    while time.time() < han and v2.trang_thai in ("cho", "chay"):
        time.sleep(0.05)
    assert v1.trang_thai == "xong" and "một" in v1.dong
    assert v2.trang_thai == "loi" and v2.ma_thoat == 3


def test_may_chu_http(ch, tmp_path, monkeypatch):
    _tao_du_an(ch)
    (tmp_path / "du-an" / "loss-aversion" / "thumbnail.png").write_bytes(PNG_1x1)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(f"du_an: '{ch['du_an']}'\nkho_mau: '{ch['kho_mau']}'\n", encoding="utf-8")
    httpd = gd.tao_may_chu(0, str(cfg))
    cong = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    goc = f"http://127.0.0.1:{cong}"
    try:
        def lay(duong, **kw):
            with urllib.request.urlopen(urllib.request.Request(goc + duong, **kw), timeout=10) as r:
                return r.status, r.headers, r.read()

        st, _, b = lay("/")
        assert st == 200 and b"Max" in b
        st, _, b = lay("/api/tong-quan")
        assert json.loads(b)["du_an"][0]["slug"] == "loss-aversion"
        st, h, b = lay("/tep/du-an/loss-aversion/thumbnail.png", headers={"Range": "bytes=0-7"})
        assert st == 206 and b == PNG_1x1[:8] and h["Content-Range"].endswith(f"/{len(PNG_1x1)}")
        for xau in ("/tep/du-an/loss-aversion/..%2f..%2fconfig.yaml", "/tep/du-an/loss-aversion/kich-ban.py"):
            with pytest.raises(urllib.error.HTTPError) as e:
                lay(xau)
            assert e.value.code in (403, 404)
        # trang lạ không được gửi lệnh
        with pytest.raises(urllib.error.HTTPError) as e:
            lay("/api/viec", data=b'{"loai":"kho"}', method="POST",
                headers={"Origin": "http://evil.example", "Content-Type": "application/json"})
        assert e.value.code == 403
        st, _, b = lay("/api/kho/tai-len?ten=dao-cu__x.png", data=PNG_1x1, method="POST")
        assert json.loads(b)["tep"] == "dao-cu__x.png"
        with pytest.raises(urllib.error.HTTPError) as e:
            lay("/api/cau-hinh", data=json.dumps({"noi_dung": "- khong la bang"}).encode(), method="POST",
                headers={"Content-Type": "application/json"})
        assert e.value.code == 400
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_tach_dong_tien_do_va_crlf():
    dong, td = [], []
    con = gd.tach_dong("a\r\nb\nDựng 10%\rDựng 20%\rc\r", dong.append, td.append)
    assert dong == ["a", "b"] and td == ["Dựng 10%", "Dựng 20%"] and con == "c\r"
    con = gd.tach_dong(con + "\nd\n", dong.append, td.append)
    assert dong == ["a", "b", "c", "d"] and con == ""


def test_nhat_ky_cat_bot_giu_chi_so_tuyet_doi():
    v = gd.Viec(1, "x", [], gd.GOC)
    for i in range(gd.Viec.TOI_DA_DONG + 5):
        v.them_dong(str(i))
    tt = v.thong_tin(gd.Viec.TOI_DA_DONG + 3)
    assert tt["so_dong"] == gd.Viec.TOI_DA_DONG + 5 and tt["dong"] == [str(gd.Viec.TOI_DA_DONG + 3), str(gd.Viec.TOI_DA_DONG + 4)]


def test_tach_nen_theo_kho_cau_hinh(ch):
    _, lenh = gd.lenh_cho_viec("tach-nen", None, None, None, ch)
    assert lenh[-3].endswith("_cho-xu-ly") and lenh[-1] == str(gd.kho_mau(ch))


@pytest.fixture()
def ch_day_du(ch):
    from nguoique.cauhinh import doc_cau_hinh

    return {**doc_cau_hinh(), **ch}


def test_dan_kich_ban_mau_hop_le(ch_day_du):
    from pathlib import Path

    mau = (gd.GOC / "templates" / "kich-ban-mau.json").read_text(encoding="utf-8")
    kq = gd.luu_kich_ban_dan(ch_day_du, "thu-dan", "```json\n" + mau + "\n```", "Title\nDescription")
    d = Path(ch_day_du["du_an"]) / "thu-dan"
    assert kq["so_canh"] > 0 and (d / "kich-ban.json").is_file() and (d / "mo-ta-youtube.md").is_file()
    assert not (d / ".kich-ban-dang-kiem.json").exists()
    with pytest.raises(gd.LoiGiaoDien) as e:  # đã có, không tick ghi đè
        gd.luu_kich_ban_dan(ch_day_du, "thu-dan", mau)
    assert e.value.ma == 409
    gd.luu_kich_ban_dan(ch_day_du, "thu-dan", mau, ghi_de=True)
    assert (d / "kich-ban.json.bak").is_file()
    assert gd.chi_tiet_du_an(ch_day_du, "thu-dan")["kich_ban_tho"].strip().startswith("{")


@pytest.mark.parametrize("xau, chu", [("{sai", "JSON sai"), ('{"tieu_de": "x", "canh": "khong-phai-ds"}', "chưa hợp lệ"), ("", "Chưa dán")])
def test_dan_kich_ban_sai_khong_ghi_gi(ch_day_du, xau, chu):
    from pathlib import Path

    with pytest.raises(gd.LoiGiaoDien) as e:
        gd.luu_kich_ban_dan(ch_day_du, "hong", xau)
    assert chu in str(e.value)
    assert not (Path(ch_day_du["du_an"]) / "hong").exists()
