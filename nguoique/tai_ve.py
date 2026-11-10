"""Tải mô hình giọng đọc và font.

- kokoro : gói `kokoro` tự tải Kokoro-82M từ Hugging Face (hexgrad/Kokoro-82M) lần đầu chạy, lưu ở
           bộ đệm HF (%USERPROFILE%\\.cache\\huggingface). Hàm này đọc thử một câu để tải trước.
- piper  : .onnx + .onnx.json từ rhasspy/piper-voices (đã kiểm: en/en_US/norman/medium/en_US-norman-medium.onnx ~63MB).
- font   : Inter Bold TTF tĩnh. Nguồn chính: Fontsource (jsDelivr, bộ chữ latin, Inter 4.x);
           dự phòng: tệp zip bản phát hành chính thức rsms/inter v4.1 (lấy extras/ttf/Inter-Bold.ttf).
"""

import os
import sys
import time
import zipfile
from pathlib import Path

from .cauhinh import GOC

PIPER_GOC = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
FONT_NGUON = "https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-700-normal.ttf"
FONT_ZIP = "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip"
FONT_MAC_DINH = "kho-mau/font/Inter-Bold.ttf"
_DAU_TTF = (b"\x00\x01\x00\x00", b"true", b"OTTO")


def _duong_dan(p) -> Path:
    p = Path(p)
    return p if p.is_absolute() else GOC / p


def _mb(n: float) -> str:
    return f"{n / 1048576:.1f} MB"


def _tai(url: str, dich: Path, ten: str = None) -> Path:
    """Tải theo luồng vào dich (qua tệp .part), có % tiến độ. Đã có thì bỏ qua."""
    import requests

    dich = Path(dich)
    ten = ten or dich.name
    if dich.is_file() and dich.stat().st_size > 0:
        print(f"  {ten}: đã có, bỏ qua.")
        return dich
    dich.parent.mkdir(parents=True, exist_ok=True)
    tam = dich.with_name(dich.name + ".part")
    try:
        with requests.get(url, stream=True, timeout=60, allow_redirects=True,
                          headers={"User-Agent": "nguoique-tai-ve"}) as r:
            r.raise_for_status()
            tong = int(r.headers.get("content-length") or 0)
            da, lan_in = 0, 0.0
            with open(tam, "wb") as f:
                for khoi in r.iter_content(chunk_size=1 << 20):
                    if not khoi:
                        continue
                    f.write(khoi)
                    da += len(khoi)
                    bay_gio = time.time()
                    if bay_gio - lan_in > 0.3:
                        lan_in = bay_gio
                        if tong:
                            sys.stdout.write(f"\r  {ten}: {100.0 * da / tong:5.1f}% ({_mb(da)}/{_mb(tong)})")
                        else:
                            sys.stdout.write(f"\r  {ten}: {_mb(da)}")
                        sys.stdout.flush()
        if tong and da != tong:
            raise RuntimeError(f"tải thiếu ({da}/{tong} byte)")
        os.replace(tam, dich)
        sys.stdout.write(f"\r  {ten}: 100.0% ({_mb(da)})          \n")
        return dich
    except Exception as loi:
        try:
            tam.unlink()
        except OSError:
            pass
        raise RuntimeError(
            f"Tải {ten} thất bại từ {url}: {loi}\n  Cách sửa: kiểm tra mạng rồi chạy lại lệnh (tệp đã tải xong sẽ được bỏ qua)."
        ) from loi


# ---------------------------------------------------------------- từng mục


def _tai_kokoro(ch: dict):
    print("Kokoro-82M: nạp và đọc thử một câu (lần đầu sẽ tải ~330MB mô hình + giọng từ Hugging Face)…")
    from .giong import Kokoro

    dc = Kokoro(ch)
    mau, sr = dc.doc("Hello! This is a quick voice test.")
    print(f"  Kokoro OK: {len(mau) / sr:.2f}s âm thanh, {sr} Hz, thiết bị {dc.thiet_bi}.")


def _url_piper(ten_tep: str) -> str:
    """en_US-norman-medium.onnx -> .../en/en_US/norman/medium/en_US-norman-medium.onnx"""
    goc = ten_tep[:-len(".onnx")] if ten_tep.endswith(".onnx") else ten_tep
    phan = goc.split("-")
    if len(phan) != 3 or "_" not in phan[0]:
        raise ValueError(
            f"Tên mô hình Piper '{ten_tep}' không đúng dạng <ngon_ngu_VUNG>-<ten>-<chat_luong>.onnx "
            "(vd. en_US-norman-medium.onnx). Cách sửa: sửa tts.piper.mo_hinh trong config.yaml."
        )
    vung, ten, chat_luong = phan
    ngon_ngu = vung.split("_")[0]
    return f"{PIPER_GOC}/{ngon_ngu}/{vung}/{ten}/{chat_luong}/{ten_tep}"


def _tai_piper(ch: dict):
    cfg = ((ch or {}).get("tts") or {}).get("piper") or {}
    mo_hinh = _duong_dan(cfg.get("mo_hinh", "mo-hinh/piper/en_US-norman-medium.onnx"))
    print(f"Piper: {mo_hinh.name}")
    url = _url_piper(mo_hinh.name)
    _tai(url, mo_hinh)
    _tai(url + ".json", Path(str(mo_hinh) + ".json"))
    # MODEL_CARD (giấy phép / dữ liệu huấn luyện) lưu cạnh mô hình để tự kiểm — docs/03 mục 1.3
    the = mo_hinh.with_name(mo_hinh.stem + ".MODEL_CARD.txt")
    try:
        _tai(url.rsplit("/", 1)[0] + "/MODEL_CARD", the, "MODEL_CARD")
        noi_dung = the.read_text(encoding="utf-8", errors="replace").lower()
        if "lessac" in noi_dung or "non-commercial" in noi_dung or "noncommercial" in noi_dung:
            print(f"  CẢNH BÁO: MODEL_CARD của {mo_hinh.name} nhắc 'lessac' / 'non-commercial' — "
                  "kiểm giấy phép trước khi dùng cho kênh kiếm tiền (docs/03).")
    except RuntimeError as loi:
        print(f"  Không tải được MODEL_CARD (không bắt buộc): {loi.__cause__ or loi}")


def _la_ttf(du_lieu: bytes) -> bool:
    return len(du_lieu) > 1000 and du_lieu[:4] in _DAU_TTF


def _tai_font(ch: dict):
    pd = (ch or {}).get("phu_de") or {}
    dich = _duong_dan(pd.get("font") or FONT_MAC_DINH)
    print(f"Font: {dich}")
    if dich.is_file() and dich.stat().st_size > 0:
        print(f"  {dich.name}: đã có, bỏ qua.")
        return
    try:
        _tai(FONT_NGUON, dich)
        if _la_ttf(dich.read_bytes()):
            return
        dich.unlink()
        print("  Tệp tải về không phải TTF, thử nguồn dự phòng…")
    except RuntimeError as loi:
        print(f"  Nguồn chính lỗi ({loi.__cause__ or loi}); thử nguồn dự phòng…")
    # dự phòng: zip bản phát hành (~34MB), giữ ngoài kho-mau rồi xoá
    zip_tam = GOC / "mo-hinh" / "_tam" / "Inter-4.1.zip"
    _tai(FONT_ZIP, zip_tam)
    with zipfile.ZipFile(zip_tam) as z:
        ung_vien = [n for n in z.namelist() if n.replace("\\", "/").split("/")[-1] == "Inter-Bold.ttf"]
        if not ung_vien:
            raise RuntimeError("Không thấy Inter-Bold.ttf trong zip. Cách sửa: tải tay từ rsms.me/inter và chép vào " + str(dich))
        ung_vien.sort(key=lambda n: (0 if "extras/ttf" in n else 1, len(n)))
        du_lieu = z.read(ung_vien[0])
    if not _la_ttf(du_lieu):
        raise RuntimeError("Tệp trong zip không phải TTF hợp lệ.")
    dich.parent.mkdir(parents=True, exist_ok=True)
    dich.write_bytes(du_lieu)
    try:
        zip_tam.unlink()
    except OSError:
        pass
    print(f"  {dich.name}: OK (từ zip).")


def tai_mo_hinh(ch: dict, muc: str):
    muc = (muc or "").strip().lower()
    if muc == "kokoro":
        _tai_kokoro(ch)
    elif muc == "piper":
        _tai_piper(ch)
    elif muc == "font":
        _tai_font(ch)
    elif muc in ("tat-ca", "tat_ca", "all"):
        loi_gap = []
        for ten, ham in (("font", _tai_font), ("piper", _tai_piper), ("kokoro", _tai_kokoro)):
            try:
                ham(ch)
            except Exception as loi:
                print(f"LỖI {ten}: {loi}")
                loi_gap.append(ten)
        if loi_gap:
            raise RuntimeError(f"Chưa tải xong: {', '.join(loi_gap)} (xem lỗi ở trên). Có thể chạy riêng `nq tai-mo-hinh <muc>`.")
    else:
        raise ValueError(f"Mục tải không hợp lệ: '{muc}'. Chọn: kokoro, piper, font, tat-ca.")
    print("Xong.")
