"""Dựng hình: Pillow vẽ từng khung -> rawvideo rgb24 qua stdin vào ffmpeg (kèm tron.wav).

Quy ước hiệu ứng (hướng = hướng chuyển động):
- truot-trai: trượt sang trái (vào từ bên phải); truot-phai: sang phải (vào từ bên trái);
  truot-len: đi lên (vào từ dưới); roi-xuong: rơi từ trên xuống, nảy nhẹ.
- bat-len: phóng từ 0 lên, vượt nhẹ rồi về (ease_out_back ~0,35s); phong-to: 55% -> 100%.
- go-chu: hiện từng ký tự ~0,045s/ký tự, bố cục cố định theo cả câu nên chữ không giật.
- Máy quay áp lên cả khung (trừ phụ đề); chuyển cảnh trộn khung cuối của cảnh trước với cảnh hiện tại.
- Kích thước lớp ảnh: 'co' = bề rộng ảnh / bề rộng khung. Chữ: 'co' = cỡ chữ theo khung cao 1080.
"""

from __future__ import annotations

import bisect
import math
import os
import subprocess
import sys
import tempfile
import time
from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .am_thanh_io import can_ffmpeg
from .cauhinh import duong_dan, kho_mau, tim_tep
from .kichban import doc_mau, la_mau
from .nhan_vat_ghep import (
    NHIP_BAO, NHIP_HINH_MAC_DINH, LoiNhanVatGhep, NhanVatGhep, bao_giong_tu_tep, bieu_cam_tai, buoc_hinh,
    dang_nham, goc_di_bo, goc_tai, lam_muot, lich_chop_mat, mieng_chu_ky, tron_goc, trang_thai_mieng, vi_tri_tai,
)

LANCZOS = Image.Resampling.LANCZOS
BILINEAR = Image.Resampling.BILINEAR
BICUBIC = Image.Resampling.BICUBIC

# truot-*: 0,4 s ease-out không vượt đích (đo video 03/04/05: 270–600 ms)
THOI_GIAN_VAO = {"khong": 0.0, "bat-len": 0.35, "mo-dan": 0.4, "truot-trai": 0.4, "truot-phai": 0.4,
                 "truot-len": 0.4, "roi-xuong": 0.6, "phong-to": 0.45, "bay-luon": 0.6}
LAC_TAY = (0.006, 2.4)  # máy quay cầm tay: lệch ngang ±0,6% khung, chu kỳ 2,4 s (video 03/04)
GIAY_MOI_KY_TU = 0.045
THOI_GIAN_HET = 0.25

_da_bao: set[str] = set()


def _bao_mot_lan(khoa: str, thong_diep: str) -> None:
    if khoa not in _da_bao:
        _da_bao.add(khoa)
        print(f"\nCẢNH BÁO: {thong_diep}", file=sys.stderr)


# ---------------- easing ----------------
def kep(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def ease_out_cubic(p: float) -> float:
    p = kep(p)
    return 1.0 - (1.0 - p) ** 3


def ease_in_out(p: float) -> float:
    p = kep(p)
    return p * p * (3.0 - 2.0 * p)


def ease_out_back(p: float, s: float = 1.70158) -> float:
    p = kep(p)
    q = p - 1.0
    return 1.0 + (s + 1.0) * q ** 3 + s * q ** 2


def ease_out_bounce(p: float) -> float:
    p = kep(p)
    n, d = 7.5625, 2.75
    if p < 1 / d:
        return n * p * p
    if p < 2 / d:
        p -= 1.5 / d
        return n * p * p + 0.75
    if p < 2.5 / d:
        p -= 2.25 / d
        return n * p * p + 0.9375
    p -= 2.625 / d
    return n * p * p + 0.984375


# ---------------- tiện ích ----------------
class BoDem:
    """Bộ đệm LRU nhỏ."""

    def __init__(self, toi_da: int) -> None:
        self.d: OrderedDict = OrderedDict()
        self.toi_da = toi_da

    def lay(self, khoa):
        v = self.d.get(khoa)
        if v is not None:
            self.d.move_to_end(khoa)
        return v

    def dat(self, khoa, v):
        self.d[khoa] = v
        self.d.move_to_end(khoa)
        while len(self.d) > self.toi_da:
            self.d.popitem(last=False)
        return v


def dan(khung: Image.Image, anh: Image.Image, x: float, y: float, alpha: float = 1.0) -> None:
    """Dán ảnh RGBA lên khung RGBA tại (x, y) — toạ độ âm / tràn khung được cắt phần thấy được."""
    if alpha <= 0.004:
        return
    x, y = int(round(x)), int(round(y))
    W, H = khung.size
    w, h = anh.size
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) == (x, y, x + w, y + h):
        phan = anh
    else:
        phan = anh.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    if alpha < 0.996:
        if phan is anh:
            phan = anh.copy()
        k = float(alpha)
        phan.putalpha(phan.getchannel("A").point(lambda v: int(v * k + 0.5)))
    khung.alpha_composite(phan, dest=(x0, y0))


def _do_dong(font) -> tuple[int, int]:
    try:
        asc, desc = font.getmetrics()
        return int(asc), int(desc)
    except AttributeError:
        b = font.getbbox("Ag")
        return int(b[3]), 0


def _rong(font, s: str) -> float:
    try:
        return float(font.getlength(s))
    except AttributeError:
        b = font.getbbox(s)
        return float(b[2] - b[0])


def xuong_dong(chu: str, font, rong_toi_da: float) -> list[str]:
    """Ngắt dòng theo bề rộng tối đa (giữ '\\n' do người viết đặt)."""
    dong: list[str] = []
    for doan in str(chu).split("\n"):
        tu = doan.split()
        if not tu:
            dong.append("")
            continue
        hien = tu[0]
        for w in tu[1:]:
            thu = f"{hien} {w}"
            if _rong(font, thu) <= rong_toi_da:
                hien = thu
            else:
                dong.append(hien)
                hien = w
        dong.append(hien)
    return dong


def ve_khoi_chu(dong: list[str], font, mau, vien: int, mau_vien, nen=None, so_ky_tu: int | None = None) -> Image.Image:
    """Vẽ khối chữ căn giữa từng dòng. so_ky_tu: chỉ vẽ chừng ấy ký tự đầu (gõ chữ) nhưng giữ nguyên bố cục."""
    asc, desc = _do_dong(font)
    cao_dong = max(1, asc + desc)
    gian = int(round(cao_dong * 0.12))
    sw = max(0, int(round(vien)))
    rong_dong = [_rong(font, d) for d in dong]
    rong_max = max(rong_dong, default=0.0)
    dem = sw + (int(round(cao_dong * 0.3)) if nen else 0) + 2
    W = int(math.ceil(rong_max)) + 2 * dem
    H = len(dong) * cao_dong + max(0, len(dong) - 1) * gian + 2 * dem
    im = Image.new("RGBA", (max(1, W), max(1, H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if nen:
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(cao_dong * 0.3), fill=nen)
    con_lai = so_ky_tu
    for i, (s, rw) in enumerate(zip(dong, rong_dong)):
        ve = s
        if con_lai is not None:
            if con_lai <= 0:
                break
            ve = s[:con_lai]
            con_lai -= len(s) + 1  # +1: khoảng trắng / xuống dòng giữa các dòng
        if not ve:
            continue
        x = dem + (rong_max - rw) / 2.0  # neo trái của dòng cố định theo cả dòng
        y = dem + i * (cao_dong + gian)
        if sw > 0:
            d.text((x, y), ve, font=font, fill=mau, stroke_width=sw, stroke_fill=mau_vien)
        else:
            d.text((x, y), ve, font=font, fill=mau)
    return im


class BoFont:
    """Font theo thứ tự: riêng (chu.font) -> config phu_de.font -> font_du_phong -> load_default(size)."""

    def __init__(self, ch: dict) -> None:
        pd = ch.get("phu_de") or {}
        self.ds = [pd.get("font"), pd.get("font_du_phong")]
        self.dem: dict = {}

    def lay(self, co: float, rieng: str | None = None):
        co = max(6, int(round(co)))
        khoa = (rieng, co)
        if khoa in self.dem:
            return self.dem[khoa]
        font = None
        for p in [rieng] + self.ds:
            if not p:
                continue
            q = duong_dan(p)
            if q.is_file():
                try:
                    font = ImageFont.truetype(str(q), co)
                    break
                except OSError:
                    _bao_mot_lan(f"font:{q}", f"không mở được font '{q}' — thử font kế tiếp.")
        if font is None:
            _bao_mot_lan("font:mac-dinh", "không thấy font trong config (phu_de.font / font_du_phong) — dùng font mặc định "
                         "của Pillow. Cách sửa: `nq tai-mo-hinh font`.")
            try:
                font = ImageFont.load_default(size=co)
            except TypeError:
                font = ImageFont.load_default()
        self.dem[khoa] = font
        return font


def _o_giu_cho(ten: str, nhom: str, bo_font: BoFont) -> Image.Image:
    kich = {"nhan-vat": (520, 900), "phong-nen": (1600, 900), "bieu-do": (1000, 700)}.get(nhom, (700, 700))
    im = Image.new("RGBA", kich, (200, 200, 200, 235))
    d = ImageDraw.Draw(im)
    w, h = kich
    d.rectangle([0, 0, w - 1, h - 1], outline=(110, 110, 110, 255), width=8)
    d.line([0, 0, w, h], fill=(160, 160, 160, 255), width=4)
    d.line([0, h, w, 0], fill=(160, 160, 160, 255), width=4)
    font = bo_font.lay(max(24, w // 14))
    khoi = ve_khoi_chu(xuong_dong(ten.replace("/", "/ ").replace("__", " __"), font, w * 0.85), font,
                       (40, 40, 40, 255), 4, (230, 230, 230, 255))
    im.alpha_composite(khoi, dest=(max(0, (w - khoi.width) // 2), max(0, (h - khoi.height) // 2)))
    return im


# ---------------- bộ dựng ----------------
class BoDung:
    def __init__(self, kb: dict, ds: list[dict], ch: dict, thu_muc_du_an: Path, nhap: bool = False,
                 phu_de: list | None = None, bao_giong: dict | None = None) -> None:
        v = ch.get("video") or {}
        self.nhap = nhap
        if nhap:
            self.W, self.H, self.fps = 640, 360, 15
        else:
            self.W, self.H, self.fps = int(v.get("rong", 1920)), int(v.get("cao", 1080)), int(v.get("fps", 30))
        self.W -= self.W % 2
        self.H -= self.H % 2
        self.k = self.H / 1080.0
        self.ch = ch
        self.kb = kb
        self.ds = ds
        self.thu_muc_du_an = Path(thu_muc_du_an)
        self.kho = kho_mau(ch)
        self.font = BoFont(ch)
        self._goc: dict[str, Image.Image] = {}
        self._theo_rong = BoDem(300)
        self._chu = BoDem(400)
        self._dong = BoDem(400)
        self._nen = BoDem(16)
        self._den = Image.new("RGB", (self.W, self.H), (0, 0, 0))
        self._trang = Image.new("RGB", (self.W, self.H), (255, 255, 255))
        pd = ch.get("phu_de") or {}
        self.pd = pd
        self.cum = sorted(phu_de or [], key=lambda c: c[0])
        self._bd_cum = [c[0] for c in self.cum]
        # nhân vật ghép: id cảnh -> mục dòng thời gian; bao giọng (RMS mỗi 1/15 s) theo id cảnh
        self._muc = {m.get("id"): m for m in ds}
        self.bao_giong = dict(bao_giong or {})
        self._mieng_canh: dict = {}
        self._ghep: dict = {}
        self._lich_chop: dict = {}
        nhip = kb.get("nhip_hinh")
        self.nhip_hinh = NHIP_HINH_MAC_DINH if nhip is None else float(nhip)
        self._th: list | None = None
        # hộp nền phụ đề (config phu_de.hop_nen, chỉ đọc; mặc định không có hộp)
        self._mau_hop = None
        if pd.get("hop_nen"):
            try:
                r, g, b, _ = doc_mau(pd["hop_nen"])
                self._mau_hop = (r, g, b, int(round(255 * kep(float(pd.get("do_duc_hop", 0.75))))))
            except (ValueError, TypeError):
                _bao_mot_lan("hop_nen", f"phu_de.hop_nen = {pd.get('hop_nen')!r} không phải mã màu — bỏ hộp nền.")
        self._giu_hop = bool(pd.get("giu_hop_khi_lang", False))
        self._hop_rong: Image.Image | None = None

    # ---- tài nguyên ----
    def anh_goc(self, rel: str) -> Image.Image:
        im = self._goc.get(rel)
        if im is not None:
            return im
        p = tim_tep(rel, self.thu_muc_du_an, self.kho)
        if p is not None:
            try:
                with Image.open(p) as f:
                    f.load()
                    im = f.convert("RGBA")
            except OSError as e:
                _bao_mot_lan(f"anh:{rel}", f"không mở được ảnh '{p}' ({e}) — vẽ ô giữ chỗ.")
        else:
            _bao_mot_lan(f"anh:{rel}", f"thiếu ảnh '{rel}' — vẽ ô giữ chỗ. Thêm tệp vào kho-mau/{rel} "
                                       "hoặc thư mục dự án (xem `nq kho`).")
        if im is None:
            nhom = Path(rel).parts[0] if Path(rel).parts else ""
            im = _o_giu_cho(rel, nhom, self.font)
        self._goc[rel] = im
        return im

    def anh_theo_rong(self, rel: str, rong: float, lat: bool = False, goc: float = 0.0) -> Image.Image:
        rong_q = max(2, int(round(rong / 2.0)) * 2)  # lượng tử 2px để bộ đệm trúng nhiều
        khoa = (rel, rong_q, lat, goc)
        im = self._theo_rong.lay(khoa)
        if im is None:
            g = self.anh_goc(rel)
            cao = max(1, int(round(g.height * rong_q / g.width)))
            im = g.resize((rong_q, cao), LANCZOS if rong_q < g.width else BICUBIC)
            if lat:
                im = ImageOps.mirror(im)
            if goc:
                im = im.rotate(goc, resample=BICUBIC, expand=True)
            self._theo_rong.dat(khoa, im)
        return im

    def anh_nen(self, nen: str) -> Image.Image:
        im = self._nen.lay(nen)
        if im is None:
            if la_mau(nen):
                im = Image.new("RGBA", (self.W, self.H), doc_mau(nen))
            else:
                g = self.anh_goc(nen)
                tl = max(self.W / g.width, self.H / g.height)
                w, h = max(self.W, int(math.ceil(g.width * tl))), max(self.H, int(math.ceil(g.height * tl)))
                r = g.resize((w, h), LANCZOS)
                x, y = (w - self.W) // 2, (h - self.H) // 2
                im = Image.new("RGBA", (self.W, self.H), (255, 255, 255, 255))
                im.alpha_composite(r.crop((x, y, x + self.W, y + self.H)))
            self._nen.dat(nen, im)
        return im

    def _cac_dong(self, noi_dung: str, font, co: int, rieng, rong_px: float) -> list[str]:
        khoa = (noi_dung, co, rieng, int(rong_px))
        dong = self._dong.lay(khoa)
        if dong is None:
            dong = self._dong.dat(khoa, xuong_dong(noi_dung, font, rong_px))
        return dong

    def anh_chu(self, chu: dict, so_ky_tu: int | None) -> tuple[Image.Image, int]:
        """-> (ảnh khối chữ, tổng số ký tự để gõ)."""
        co = max(6, int(round(chu["co"] * self.k)))
        font = self.font.lay(co, chu.get("font"))
        rong_px = chu.get("rong_toi_da", 0.8) * self.W
        dong = self._cac_dong(chu["noi_dung"], font, co, chu.get("font"), rong_px)
        tong = sum(len(d) for d in dong) + max(0, len(dong) - 1)
        if so_ky_tu is not None and so_ky_tu >= tong:
            so_ky_tu = None
        vien = int(round((chu.get("vien") or 0) * self.k))
        if chu.get("vien") and vien < 1:
            vien = 1
        khoa = (chu["noi_dung"], co, chu.get("font"), str(chu["mau"]), vien, str(chu["mau_vien"]),
                str(chu.get("nen")), int(rong_px), so_ky_tu)
        im = self._chu.lay(khoa)
        if im is None:
            nen = doc_mau(chu["nen"]) if chu.get("nen") else None
            im = ve_khoi_chu(dong, font, doc_mau(chu["mau"]), vien, doc_mau(chu["mau_vien"]), nen, so_ky_tu)
            self._chu.dat(khoa, im)
        return im, tong

    def anh_phu_de(self, chu: str) -> Image.Image:
        khoa = ("__phu_de__", chu)
        im = self._chu.lay(khoa)
        if im is None:
            pd = self.pd
            co = max(6, int(round(float(pd.get("co_chu", 52)) * self.k)))
            font = self.font.lay(co)
            vien = max(1, int(round(float(pd.get("vien", 6)) * self.k))) if pd.get("vien") else 0
            dong = xuong_dong(chu, font, self.W * 0.86)
            im = ve_khoi_chu(dong, font, doc_mau(pd.get("mau", "#FFFFFF")), vien, doc_mau(pd.get("mau_vien", "#111111")))
            if self._mau_hop:
                w, h = self._kich_hop(im.width, im.height, font, vien)
                hop = self._ve_hop(w, h, font)
                hop.alpha_composite(im, dest=((w - im.width) // 2, (h - im.height) // 2))
                im = hop
            self._chu.dat(khoa, im)
        return im

    # ---- hộp nền phụ đề ----
    def _kich_hop(self, w_chu: int, h_chu: int, font, vien: int) -> tuple[int, int]:
        asc, desc = _do_dong(font)
        cao_dong = max(1, asc + desc)
        px, py = int(round(cao_dong * 0.5)), int(round(cao_dong * 0.18))
        w, h = w_chu + 2 * px, h_chu + 2 * py
        if self._giu_hop:  # hộp cố định khi lặng -> lúc có chữ cũng tối thiểu cùng cỡ để hộp không nhảy
            w = max(w, int(self.W * 0.8))
            h = max(h, cao_dong + 2 * (max(0, vien) + 2) + 2 * py)
        return min(w, self.W), min(h, self.H)

    def _ve_hop(self, w: int, h: int, font) -> Image.Image:
        asc, desc = _do_dong(font)
        hop = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0))
        ImageDraw.Draw(hop).rounded_rectangle([0, 0, w - 1, h - 1], radius=max(0, int((asc + desc) * 0.2)),
                                              fill=self._mau_hop)
        return hop

    def anh_hop_rong(self) -> Image.Image:
        if self._hop_rong is None:
            pd = self.pd
            font = self.font.lay(max(6, int(round(float(pd.get("co_chu", 52)) * self.k))))
            vien = max(1, int(round(float(pd.get("vien", 6)) * self.k))) if pd.get("vien") else 0
            w, h = self._kich_hop(0, 0, font, vien)
            self._hop_rong = self._ve_hop(w, h, font)
        return self._hop_rong

    # ---- biến đổi theo thời gian ----
    def _vao(self, kieu: str, t: float, tre: float, dai_vao: float):
        """-> (hiện?, tỉ lệ, alpha, dx, dy)."""
        if t < tre:
            return False, 1.0, 0.0, 0.0, 0.0
        if kieu == "khong" or dai_vao <= 0:
            return True, 1.0, 1.0, 0.0, 0.0
        p = (t - tre) / dai_vao
        if p >= 1.0:
            return True, 1.0, 1.0, 0.0, 0.0
        W, H = self.W, self.H
        if kieu == "bat-len":
            return True, max(0.02, ease_out_back(p)), kep(p * 3.0), 0.0, 0.0
        if kieu == "mo-dan":
            return True, 1.0, ease_in_out(p), 0.0, 0.0
        if kieu == "truot-trai":
            return True, 1.0, kep(p * 2.5), (1.0 - ease_out_cubic(p)) * 0.35 * W, 0.0
        if kieu == "truot-phai":
            return True, 1.0, kep(p * 2.5), -(1.0 - ease_out_cubic(p)) * 0.35 * W, 0.0
        if kieu == "truot-len":
            return True, 1.0, kep(p * 2.5), 0.0, (1.0 - ease_out_cubic(p)) * 0.3 * H
        if kieu == "roi-xuong":
            return True, 1.0, kep(p * 4.0), 0.0, -(1.0 - ease_out_bounce(p)) * 0.6 * H
        if kieu == "phong-to":
            return True, 0.55 + 0.45 * ease_out_cubic(p), kep(p * 2.0), 0.0, 0.0
        if kieu == "bay-luon":  # lướt vào theo cung Bezier bậc 2 từ dưới phải, ease-out không vượt đích
            e = ease_out_cubic(p)
            u = 1.0 - e
            dx = u * u * 0.40 * W + 2.0 * u * e * 0.18 * W
            dy = u * u * 0.25 * H - 2.0 * u * e * 0.20 * H
            return True, 0.85 + 0.15 * e, kep(p * 3.0), dx, dy
        return True, 1.0, 1.0, 0.0, 0.0

    def _lien_tuc(self, kieu: str, t: float):
        """-> (tỉ lệ, dx, dy, góc xoay). t = giây kể từ lúc lớp hiện."""
        if kieu == "nhun":
            return 1.0, 0.0, -abs(math.sin(math.pi * t / 0.55)) * 0.012 * self.H, 0.0
        if kieu == "lac":
            return 1.0, 0.0, 0.0, round(3.0 * math.sin(2 * math.pi * t / 1.4) * 2) / 2.0  # lượng tử 0,5°
        if kieu == "tho":
            return 1.0 + 0.025 * math.sin(2 * math.pi * t / 2.6), 0.0, 0.0, 0.0
        if kieu == "run":
            dx = (math.sin(t * 61.0) + math.sin(t * 37.0)) * 0.0016 * self.W
            dy = (math.cos(t * 53.0) + math.sin(t * 29.0)) * 0.0016 * self.H
            return 1.0, dx, dy, 0.0
        return 1.0, 0.0, 0.0, 0.0

    @staticmethod
    def _het(het, t: float) -> float:
        if het is None or t < het:
            return 1.0
        return 1.0 - kep((t - het) / THOI_GIAN_HET)

    # ---- vẽ ----
    def ve_lop(self, khung: Image.Image, lop: dict, t: float, canh: dict | None = None, j: int = 0) -> None:
        if lop.get("nhan_vat"):
            self.ve_nhan_vat_ghep(khung, lop, t, canh, j)
            return
        kieu = lop["hieu_ung"]
        hien, s, a, dx, dy = self._vao(kieu, t, lop["tre"], THOI_GIAN_VAO.get(kieu, 0.4))
        if not hien:
            return
        a *= self._het(lop.get("het"), t)
        if a <= 0.004:
            return
        s2, dx2, dy2, goc = self._lien_tuc(lop["lien_tuc"], t - lop["tre"])
        s *= s2
        rong = lop["co"] * self.W * s
        if rong < 2:
            return
        im = self.anh_theo_rong(lop["anh"], rong, bool(lop.get("lat")), goc)
        cx = lop["vi_tri"][0] * self.W + dx + dx2
        cy = lop["vi_tri"][1] * self.H + dy + dy2
        x = cx - im.width / 2.0
        y = cy - im.height if lop["neo"] == "day" else cy - im.height / 2.0
        dan(khung, im, x, y, a)

    # ---- nhân vật ghép bộ phận (nhan_vat_ghep.py, docs/10) ----
    def nhan_vat_ghep(self, ten: str) -> NhanVatGhep | None:
        if ten in self._ghep:
            return self._ghep[ten]
        nv = None
        p = tim_tep(f"nhan-vat-ghep/{ten}/khung.json", self.thu_muc_du_an, self.kho)
        if p is None:
            _bao_mot_lan(f"ghep:{ten}", f"thiếu nhân vật ghép '{ten}' (kho-mau/nhan-vat-ghep/{ten}/khung.json) — vẽ ô "
                                        "giữ chỗ. Cách sửa: `nq hinh-tam` tạo bộ tạm, hoặc xem docs/10-NHAN-VAT-GHEP.md.")
        else:
            try:
                nv = NhanVatGhep(p.parent)
            except LoiNhanVatGhep as e:
                _bao_mot_lan(f"ghep:{ten}", f"{e} — vẽ ô giữ chỗ.")
        self._ghep[ten] = nv
        return nv

    def _mieng(self, cid: str, t: float) -> str:
        """Hình miệng của nhân vật đang nói: theo bao giọng (giữ ≥ 0,15 s), không có thì mở-đóng chu kỳ 0,56 s."""
        muc = self._muc.get(cid) or {}
        tg = t - float(muc.get("dem_truoc") or 0.0)
        if cid not in self._mieng_canh:
            self._mieng_canh[cid] = trang_thai_mieng(self.bao_giong.get(cid))
        ds = self._mieng_canh[cid]
        if ds:
            i = int(tg * NHIP_BAO)
            return ds[i] if 0 <= i < len(ds) else "dong"
        if 0.0 <= tg < float(muc.get("giong_giay") or 0.0):
            return mieng_chu_ky(tg)
        return "dong"

    def ve_nhan_vat_ghep(self, khung: Image.Image, lop: dict, t: float, canh: dict | None, j: int) -> None:
        kieu = lop.get("hieu_ung", "khong")
        tre = float(lop.get("tre") or 0.0)
        hien, m, a, dx, dy = self._vao(kieu, t, tre, THOI_GIAN_VAO.get(kieu, 0.4))
        if not hien:
            return
        a *= self._het(lop.get("het"), t)
        if a <= 0.004:
            return
        nhip = lop.get("nhip_hinh")
        ta = buoc_hinh(t, self.nhip_hinh if nhip is None else float(nhip))  # nhịp vẽ tay, máy quay vẫn mượt
        x_c, y_c, w_di, pha, trai = vi_tri_tai(lop, ta)
        co = float(lop.get("co", 0.3))
        neo = lop.get("neo", "giua")
        nv = self.nhan_vat_ghep(str(lop["nhan_vat"]))
        if nv is None:
            rong = co * self.W * m
            if rong < 2:
                return
            im = self.anh_theo_rong(f"nhan-vat/{lop['nhan_vat']}__ghep.png", rong, bool(lop.get("lat")))
            cx, cy = x_c * self.W + dx, y_c * self.H + dy
            dan(khung, im, cx - im.width / 2.0, cy - im.height if neo == "day" else cy - im.height / 2.0, a)
            return
        cid = canh.get("id", "") if canh else ""

        goc = goc_tai(lop, ta, nv.thu_vien, nv.goc_mac_dinh)
        lat = bool(lop.get("lat"))
        if w_di > 0:
            goc = tron_goc(goc, goc_di_bo(pha, nv.thu_vien, nv.goc_mac_dinh), w_di)
            lat = bool(trai)  # đi sang trái -> lật gương chu kỳ đi (thiết kế cho hướng sang phải)
        tl = ta - tre
        lt = lop.get("lien_tuc", "khong")
        dx2 = dy2 = 0.0
        if lt == "nhun":
            dy2 = -abs(math.sin(math.pi * tl / 0.55)) * 0.012 * self.H
        elif lt == "run":
            dx2 = (math.sin(tl * 61.0) + math.sin(tl * 37.0)) * 0.0016 * self.W
            dy2 = (math.cos(tl * 53.0) + math.sin(tl * 29.0)) * 0.0016 * self.H
        elif lt == "lac":
            goc["dau"] = goc.get("dau", 0.0) + 4.0 * math.sin(2 * math.pi * tl / 1.4)
        elif lt == "tho":  # thở: đầu và vai nhích rất nhẹ thay cho co giãn ảnh
            sv = math.sin(2 * math.pi * tl / 3.2)
            goc["dau"] = goc.get("dau", 0.0) + 1.2 * sv
            goc["tay-trai-tren"] = goc.get("tay-trai-tren", 0.0) - 1.5 * sv
            goc["tay-phai-tren"] = goc.get("tay-phai-tren", 0.0) + 1.5 * sv

        bc = bieu_cam_tai(lop, ta, nv.bieu_cam_mac_dinh)
        nham = False
        if lop.get("chop_mat", True):
            lich = self._lich_chop.get((cid, j))
            if lich is None:
                dai = float((self._muc.get(cid) or {}).get("thoi_luong") or 60.0)
                lich = self._lich_chop[(cid, j)] = lich_chop_mat(f"{cid}|{j}", dai)
            nham = dang_nham(lich, ta)
        mat = nv.tep_mat(bc, nham)
        mieng = nv.tep_mieng(bc, self._mieng(cid, ta) if lop.get("noi") else "dong")

        m_q = 1.0 if abs(m - 1.0) < 1e-3 else max(0.04, round(m / 0.04) * 0.04)  # đệm trúng khi bat-len / phong-to
        w0, h0 = nv.kich_thuoc
        s = co * self.W / w0 * m_q
        if s * w0 < 2:
            return
        cx = x_c * self.W + dx + dx2
        cy = y_c * self.H + dy + dy2
        x0 = cx - w0 * s / 2.0
        y0 = cy - nv.nen_dat() * s if neo == "day" else cy - h0 * s / 2.0
        ds = nv.bo_tri(goc, s, lat, x0, y0, mat, mieng)
        if not ds:
            return
        if a >= 0.996:
            for im, x, y in ds:
                dan(khung, im, x, y)
            return
        # mờ dần: ghép vào một ảnh rồi mới dán, để chỗ chồng khớp không đậm hơn
        vt = [(im, int(round(x)), int(round(y))) for im, x, y in ds]
        bx, by = min(v[1] for v in vt), min(v[2] for v in vt)
        ex, ey = max(v[1] + v[0].width for v in vt), max(v[2] + v[0].height for v in vt)
        gop = Image.new("RGBA", (max(1, ex - bx), max(1, ey - by)), (0, 0, 0, 0))
        for im, x, y in vt:
            gop.alpha_composite(im, dest=(x - bx, y - by))
        dan(khung, gop, bx, by, a)

    def ve_chu(self, khung: Image.Image, chu: dict, t: float) -> None:
        kieu = chu["hieu_ung"]
        tre = chu["tre"]
        if t < tre:
            return
        a = self._het(chu.get("het"), t)
        if a <= 0.004:
            return
        if kieu == "go-chu":
            n = int((t - tre) / GIAY_MOI_KY_TU) + 1
            im, _ = self.anh_chu(chu, n)
            s, dx, dy = 1.0, 0.0, 0.0
        else:
            _, s, a0, dx, dy = self._vao(kieu, t, tre, THOI_GIAN_VAO.get(kieu, 0.4))
            a *= a0
            im, _ = self.anh_chu(chu, None)
        s2, dx2, dy2, goc = self._lien_tuc(chu.get("lien_tuc", "khong"), t - tre)
        s *= s2
        if abs(s - 1.0) > 0.003:
            w, h = max(1, int(round(im.width * s))), max(1, int(round(im.height * s)))
            im = im.resize((w, h), BILINEAR)
        if goc:
            im = im.rotate(goc, resample=BICUBIC, expand=True)
        cx = chu["vi_tri"][0] * self.W + dx + dx2
        cy = chu["vi_tri"][1] * self.H + dy + dy2
        dan(khung, im, cx - im.width / 2.0, cy - im.height / 2.0, a)

    def may_quay(self, khung: Image.Image, mq: dict, t: float, dai: float) -> Image.Image:
        kieu, muc = mq.get("kieu", "dung-yen"), float(mq.get("muc", 0.0))
        p = kep(t / dai) if dai > 0 else 1.0
        z, cx, cy = 1.0, 0.5, 0.5
        if kieu == "zoom-cham":
            z = 1.0 + muc * ease_in_out(p)
        elif kieu == "zoom-ra":
            z = 1.0 + muc * (1.0 - ease_in_out(p))
        elif kieu in ("lia-trai", "lia-phai"):
            z = 1.0 + muc
            lech = (1.0 - 1.0 / z) / 2.0
            e = ease_in_out(p)
            cx = 0.5 + lech * (1.0 - 2.0 * e) * (1.0 if kieu == "lia-trai" else -1.0)
        elif kieu == "dam":
            z = 1.0 + muc * ease_out_cubic(t / 0.3)
        elif kieu == "rung":
            z = 1.0 + muc * 2.5
            lech = (1.0 - 1.0 / z) / 2.0
            cx = 0.5 + lech * 0.85 * math.sin(t * 41.0)
            cy = 0.5 + lech * 0.85 * math.cos(t * 33.0)
        elif kieu == "lac-tay":
            z = 1.0 + max(muc, LAC_TAY[0]) * 2.5
        if kieu == "lac-tay" or mq.get("lac_tay"):  # cầm tay: lệch ngang ±0,6% khung, chu kỳ 2,4 s (cộng dồn)
            bien = (muc if kieu == "lac-tay" and muc > 0 else LAC_TAY[0])
            z = max(z, 1.0 + 2.5 * bien)
            cx += bien * math.sin(2 * math.pi * t / LAC_TAY[1])
            cy += 0.35 * bien * math.sin(2 * math.pi * t / (LAC_TAY[1] * 1.7))
        moc = mq.get("moc")
        if moc:  # mốc trong cảnh (đổi khung toàn -> cận không cắt), nhân lên hiệu ứng kiểu
            zm, xm, ym = self._moc_may_quay(moc, t)
            cx = xm + (cx - 0.5) / zm
            cy = ym + (cy - 0.5) / zm
            z *= zm
        if z <= 1.0005 and cx == 0.5 and cy == 0.5:
            return khung
        W, H = self.W, self.H
        bw, bh = W / z, H / z
        l = kep(cx * W - bw / 2.0, 0.0, W - bw)
        tp = kep(cy * H - bh / 2.0, 0.0, H - bh)
        return khung.resize((W, H), BILINEAR, box=(l, tp, l + bw, tp + bh))

    @staticmethod
    def _moc_may_quay(moc: list, t: float) -> tuple[float, float, float]:
        """Trạng thái (zoom, tâm x, tâm y) ở giây t: từ (1, giữa) lần lượt nội suy tới từng mốc đã bắt đầu."""
        z, x, y = 1.0, 0.5, 0.5
        for i, m in enumerate(moc):
            luc = float(m.get("luc") or 0.0)
            if t < luc:
                break
            tl = m.get("thoi_luong")
            tl = (0.0 if i == 0 else 0.8) if tl is None else float(tl)
            e = 1.0 if tl <= 0 else lam_muot(m.get("easing") or "vao-ra", (t - luc) / tl)
            tam = m.get("tam") or [0.5, 0.5]
            z += (max(1.0, float(m.get("zoom", 1.0))) - z) * e
            x += (float(tam[0]) - x) * e
            y += (float(tam[1]) - y) * e
        return max(1.0, z), x, y

    def chuyen_canh(self, truoc: Image.Image, hien: Image.Image, kieu: str, p: float) -> Image.Image:
        W, H = self.W, self.H
        e = ease_in_out(p)
        if kieu == "mo-dan":
            return Image.blend(truoc, hien, e)
        if kieu == "toi-den":
            if p < 0.5:
                return Image.blend(truoc, self._den, ease_in_out(p * 2.0))
            return Image.blend(self._den, hien, ease_in_out((p - 0.5) * 2.0))
        if kieu == "nhay-trang":
            if p < 0.25:
                return Image.blend(truoc, self._trang, p / 0.25)
            return Image.blend(self._trang, hien, ease_in_out((p - 0.25) / 0.75))
        if kieu == "truot-trai":
            lech = int(round(e * W))
            ra = Image.new("RGB", (W, H))
            ra.paste(truoc, (-lech, 0))
            ra.paste(hien, (W - lech, 0))
            return ra
        if kieu == "truot-len":
            lech = int(round(e * H))
            ra = Image.new("RGB", (W, H))
            ra.paste(truoc, (0, -lech))
            ra.paste(hien, (0, H - lech))
            return ra
        if kieu == "zoom-vao":
            z = 1.0 + 0.6 * e
            bw, bh = W / z, H / z
            l, tp = (W - bw) / 2.0, (H - bh) / 2.0
            phong = truoc.resize((W, H), BILINEAR, box=(l, tp, l + bw, tp + bh))
            return Image.blend(phong, hien, e)
        return hien

    def ve_canh(self, canh: dict, t: float, dai: float) -> Image.Image:
        khung = self.anh_nen(canh["nen"]).copy()
        for j, lop in enumerate(canh["lop"]):
            self.ve_lop(khung, lop, t, canh, j)
        for chu in canh["chu"]:
            self.ve_chu(khung, chu, t)
        return self.may_quay(khung.convert("RGB"), canh["may_quay"], t, dai)

    def ve_phu_de(self, khung: Image.Image, tg: float) -> None:
        i = bisect.bisect_right(self._bd_cum, tg) - 1
        chu = None
        if i >= 0:
            bd, kt, c = self.cum[i]
            if tg < kt and c:
                chu = c
        if chu is None:
            if not (self._mau_hop and self._giu_hop):
                return
            im = self.anh_hop_rong()  # phu_de.giu_hop_khi_lang: hộp vẫn hiện khi không có lời
        else:
            im = self.anh_phu_de(chu)
        x = (self.W - im.width) // 2
        y = int(round(float(self.pd.get("vi_tri_y", 0.92)) * self.H - im.height / 2.0))
        y = max(0, min(self.H - im.height, y))
        khung.paste(im, (x, y), im)

    def anh_thuong_hieu(self) -> list:
        """kb['thuong_hieu']: [{anh, vi_tri (tâm), co (= chiều cao / khung cao), do_mo (độ hiện 0..1)}] -> [(ảnh, x, y)]."""
        if self._th is None:
            ds = self.kb.get("thuong_hieu") or []
            if isinstance(ds, dict):
                ds = [ds]
            self._th = []
            for m in ds:
                if not isinstance(m, dict) or not m.get("anh"):
                    continue
                g = self.anh_goc(str(m["anh"]))
                cao = max(2, int(round(float(m.get("co", 0.06)) * self.H)))
                rong = max(1, int(round(g.width * cao / max(1, g.height))))
                im = g.resize((rong, cao), LANCZOS if cao < g.height else BICUBIC)
                k = kep(float(m.get("do_mo", 0.8)))
                if k < 0.996:
                    im.putalpha(im.getchannel("A").point(lambda v, k=k: int(v * k + 0.5)))
                vt = m.get("vi_tri") or [0.94, 0.06]
                x = int(round(float(vt[0]) * self.W - rong / 2.0))
                y = int(round(float(vt[1]) * self.H - cao / 2.0))
                self._th.append((im, max(0, min(self.W - rong, x)), max(0, min(self.H - cao, y))))
        return self._th

    def ve_thuong_hieu(self, khung: Image.Image) -> None:
        """Lớp thương hiệu cố định cả video: vẽ sau máy quay + chuyển cảnh (không zoom, không mờ theo cảnh)."""
        for im, x, y in self.anh_thuong_hieu():
            khung.paste(im, (x, y), im)

    def _khung_cuoi(self, muc: dict) -> Image.Image | None:
        """Khung cuối (chưa logo / phụ đề) của một cảnh — để cảnh sau chuyển cảnh từ đó."""
        bd, kt = float(muc["bat_dau"]), float(muc["ket_thuc"])
        f0, f1 = int(round(bd * self.fps)), int(round(kt * self.fps))
        if f1 <= f0:
            return None
        return self.ve_canh(muc["canh"], (f1 - 1) / self.fps - bd, kt - bd).copy()

    def cac_khung(self, i0: int = 0, i1: int | None = None):
        """Sinh bytes rgb24 từng khung theo dòng thời gian (cảnh ds[i0:i1]; mặc định cả video)."""
        fps = self.fps
        truoc: Image.Image | None = None
        if i0 > 0:  # đoạn giữa video (dựng song song): tự vẽ lại khung cuối của cảnh liền trước
            for j in range(i0 - 1, -1, -1):
                truoc = self._khung_cuoi(self.ds[j])
                if truoc is not None:
                    break
        for muc in self.ds[i0:i1]:
            canh = muc["canh"]
            bd, kt = float(muc["bat_dau"]), float(muc["ket_thuc"])
            dai = kt - bd
            f0, f1 = int(round(bd * fps)), int(round(kt * fps))
            cc = canh.get("chuyen_canh") or {"kieu": "cat", "thoi_luong": 0.0}
            kieu_cc = cc.get("kieu", "cat")
            tc = min(float(cc.get("thoi_luong") or 0.0), dai * 0.8)
            for f in range(f0, f1):
                tg = f / fps
                t = tg - bd
                khung = self.ve_canh(canh, t, dai)
                if f == f1 - 1:
                    cuoi = khung.copy()
                if kieu_cc != "cat" and tc > 0 and t < tc:
                    khung = self.chuyen_canh(truoc if truoc is not None else self._den, khung, kieu_cc, t / tc)
                if self.kb.get("thuong_hieu"):
                    self.ve_thuong_hieu(khung)  # 'cuoi' đã chép trước nên khung chuyển cảnh không có logo chồng
                if self.cum:
                    self.ve_phu_de(khung, tg)  # 'cuoi' đã được chép ở trên nên vẽ thẳng không ảnh hưởng
                yield khung.tobytes()
            if f1 > f0:
                truoc = cuoi

    # ---- mã hoá ----
    def _bo_ma(self, ffmpeg: str) -> str:
        if self.nhap:
            return "libx264"
        muon = str((self.ch.get("video") or {}).get("ma_hoa", "h264_nvenc")).lower()
        if muon != "h264_nvenc":
            return "libx264"
        try:
            kq = subprocess.run([ffmpeg, "-hide_banner", "-encoders"], capture_output=True, timeout=30)
            if b"h264_nvenc" in kq.stdout:
                return "h264_nvenc"
        except (OSError, subprocess.SubprocessError):
            pass
        _bao_mot_lan("nvenc", "ffmpeg không có h264_nvenc — dùng libx264 (chậm hơn).")
        return "libx264"

    def _lenh(self, ffmpeg: str, tep_am: Path, tep_ra: Path, bo_ma: str) -> list[str]:
        q = str(int((self.ch.get("video") or {}).get("chat_luong", 21)))
        lenh = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{self.W}x{self.H}", "-r", str(self.fps), "-i", "-",
                "-i", str(tep_am), "-map", "0:v", "-map", "1:a"]
        if bo_ma == "h264_nvenc":
            lenh += ["-c:v", "h264_nvenc", "-preset", "p5", "-cq", q, "-b:v", "0"]
        elif self.nhap:
            lenh += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"]
        else:
            lenh += ["-c:v", "libx264", "-preset", "medium", "-crf", q]
        lenh += ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tep_ra)]
        return lenh

    def _ma_hoa(self, lenh: list[str], tong_khung: int, khoang: tuple = (0, None), dem=None) -> None:
        """Đẩy khung vào ffmpeg. dem: multiprocessing.Value chung (dựng song song) — khi có thì không in tiến độ."""
        with tempfile.TemporaryFile() as tep_loi:
            proc = subprocess.Popen(lenh, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=tep_loi)
            bat_dau = time.time()
            pt_cu = -1
            i = 0
            try:
                for i, du_lieu in enumerate(self.cac_khung(*khoang), 1):
                    proc.stdin.write(du_lieu)
                    if dem is not None:
                        with dem.get_lock():
                            dem.value += 1
                        continue
                    pt = int(i * 100 / max(1, tong_khung))
                    if pt != pt_cu:
                        pt_cu = pt
                        toc = i / max(1e-6, time.time() - bat_dau)
                        sys.stdout.write(f"\r  Dựng hình: {pt:3d}% ({i}/{tong_khung} khung, {toc:.1f} khung/s)   ")
                        sys.stdout.flush()
                proc.stdin.close()
            except (BrokenPipeError, OSError) as e:
                try:
                    proc.kill()
                except OSError:
                    pass
                proc.wait()
                tep_loi.seek(0)
                loi = tep_loi.read().decode("utf-8", "replace").strip()
                raise LoiMaHoa(f"ffmpeg dừng giữa chừng ở khung {i} ({e}).\n{loi}") from None
            except BaseException:
                try:
                    proc.kill()
                except OSError:
                    pass
                proc.wait()
                raise
            ma = proc.wait()
            if dem is None:
                sys.stdout.write("\n")
            if ma != 0:
                tep_loi.seek(0)
                loi = tep_loi.read().decode("utf-8", "replace").strip()
                raise LoiMaHoa(f"ffmpeg kết thúc với mã {ma}.\n{loi}")

    # ---- dựng song song: chia cảnh thành đoạn, mỗi tiến trình vẽ + mã hoá một đoạn, rồi ghép (-c copy) ----
    def so_tien_trinh(self, tong_khung: int) -> int:
        """video.song_song: "tu-dong" (mặc định) = máy mạnh (>= 16 luồng CPU và >= 24 GB RAM) thì song song,
        mỗi tiến trình tính ~2 GB RAM, tối đa 8; máy yếu hơn (vd. laptop Aspire 7) chạy tuần tự như cũ.
        Số >= 1 = ép đúng bấy nhiêu tiến trình (1 = tuần tự)."""
        muon = (self.ch.get("video") or {}).get("song_song", "tu-dong")
        try:
            n = int(muon)
        except (TypeError, ValueError):
            n = 0
        if n <= 0:
            luong, ram = os.cpu_count() or 2, _ram_gb()
            n = min(8, luong - 2, int(ram // 3)) if luong >= 16 and ram >= 24 else 1
        if self.nhap or len(self.ds) < 2 or tong_khung < self.fps * 20:
            return 1
        return max(1, min(n, len(self.ds)))

    def chia_doan(self, so_doan: int) -> list[tuple[int, int]]:
        """Chia ds thành `so_doan` khoảng cảnh liền nhau [i0, i1), số khung gần bằng nhau."""
        fps = self.fps
        moc = [int(round(float(m["ket_thuc"]) * fps)) for m in self.ds]
        tong = moc[-1] if moc else 0
        doan, i0 = [], 0
        for k in range(1, so_doan):
            dich = tong * k / so_doan
            i1 = max(i0 + 1, bisect.bisect_left(moc, dich) + 1)
            if i1 >= len(self.ds):
                break
            doan.append((i0, i1))
            i0 = i1
        doan.append((i0, len(self.ds)))
        return doan

    def _lenh_doan(self, ffmpeg: str, tep_ra: Path) -> list[str]:
        """Đoạn hình không tiếng, libx264 (NVENC giới hạn số phiên cùng lúc trên card thường)."""
        q = str(int((self.ch.get("video") or {}).get("chat_luong", 21)))
        return [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{self.W}x{self.H}", "-r", str(self.fps), "-i", "-",
                "-c:v", "libx264", "-preset", "medium", "-crf", q, "-threads", "2", "-pix_fmt", "yuv420p",
                str(tep_ra)]

    def _chay_song_song(self, ffmpeg: str, tep_am: Path, tep_ra: Path, tong_khung: int, n: int) -> None:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor

        doan = self.chia_doan(n * 2)
        thu_muc_tam = Path(tempfile.mkdtemp(prefix="nq-doan-", dir=str(tep_ra.parent)))
        print(f"  Dựng song song: {n} tiến trình, {len(doan)} đoạn.")
        try:
            ctx = mp.get_context("spawn")
            dem = ctx.Value("q", 0)
            viec = []
            for k, (i0, i1) in enumerate(doan):
                tep = thu_muc_tam / f"doan-{k:03d}.mp4"
                viec.append((self.kb, self.ds, self.ch, str(self.thu_muc_du_an), self.nhap, self.cum,
                             self.bao_giong, i0, i1, self._lenh_doan(ffmpeg, tep)))
            bat_dau = time.time()
            with ProcessPoolExecutor(max_workers=n, mp_context=ctx, initializer=_khoi_tao_doan,
                                     initargs=(dem,)) as pool:
                cho = [pool.submit(_dung_doan, v) for v in viec]
                pt_cu = -1
                while not all(f.done() for f in cho):
                    time.sleep(0.5)
                    i = dem.value
                    pt = int(i * 100 / max(1, tong_khung))
                    if pt != pt_cu:
                        pt_cu = pt
                        toc = i / max(1e-6, time.time() - bat_dau)
                        sys.stdout.write(f"\r  Dựng hình: {pt:3d}% ({i}/{tong_khung} khung, {toc:.1f} khung/s)   ")
                        sys.stdout.flush()
                for f in cho:
                    f.result()  # ném lỗi của tiến trình con (nếu có)
            sys.stdout.write("\n")
            ds_tep = thu_muc_tam / "ds.txt"
            ds_tep.write_text("".join(f"file '{(thu_muc_tam / f'doan-{k:03d}.mp4').as_posix()}'\n"
                                      for k in range(len(doan))), encoding="utf-8")
            lenh = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(ds_tep), "-i", str(tep_am), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tep_ra)]
            kq = subprocess.run(lenh, capture_output=True)
            if kq.returncode != 0:
                raise LoiMaHoa("ghép đoạn thất bại.\n" + kq.stderr.decode("utf-8", "replace").strip())
        finally:
            for p in thu_muc_tam.glob("*"):
                try:
                    p.unlink()
                except OSError:
                    pass
            try:
                thu_muc_tam.rmdir()
            except OSError:
                pass

    def chay(self, tep_am: Path, tep_ra: Path) -> Path:
        ffmpeg = can_ffmpeg()
        tep_ra = Path(tep_ra)
        tep_ra.parent.mkdir(parents=True, exist_ok=True)
        tong_khung = int(round(float(self.ds[-1]["ket_thuc"]) * self.fps)) if self.ds else 0
        n = self.so_tien_trinh(tong_khung)
        if n > 1:
            print(f"  Khung {self.W}x{self.H} @ {self.fps}fps, {tong_khung} khung, mã hoá libx264 theo đoạn.")
            try:
                self._chay_song_song(ffmpeg, tep_am, tep_ra, tong_khung, n)
                return tep_ra
            except LoiMaHoa as e:
                raise RuntimeError(f"Mã hoá video thất bại: {e}\nCách sửa: đặt video.song_song: 1 trong config.yaml "
                                   "để dựng tuần tự; cập nhật ffmpeg; kiểm dung lượng ổ đĩa.") from None
        bo_ma = self._bo_ma(ffmpeg)
        print(f"  Khung {self.W}x{self.H} @ {self.fps}fps, {tong_khung} khung, mã hoá {bo_ma}.")
        try:
            self._ma_hoa(self._lenh(ffmpeg, tep_am, tep_ra, bo_ma), tong_khung)
        except LoiMaHoa as e:
            if bo_ma != "h264_nvenc":
                raise RuntimeError(f"Mã hoá video thất bại: {e}\nCách sửa: cập nhật ffmpeg, kiểm dung lượng ổ đĩa.") from None
            print(f"\nCẢNH BÁO: NVENC lỗi — thử lại bằng libx264.\n{e}", file=sys.stderr)
            try:
                self._ma_hoa(self._lenh(ffmpeg, tep_am, tep_ra, "libx264"), tong_khung)
            except LoiMaHoa as e2:
                raise RuntimeError(f"Mã hoá video thất bại: {e2}\nCách sửa: cập nhật ffmpeg, kiểm dung lượng ổ đĩa.") from None
        return tep_ra


class LoiMaHoa(RuntimeError):
    pass


def _ram_gb() -> float:
    """Tổng RAM máy (GB), không cần thư viện ngoài; không đọc được thì 0 (-> dựng tuần tự)."""
    try:
        if os.name == "nt":
            import ctypes

            class _Mem(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            m = _Mem()
            m.dwLength = ctypes.sizeof(_Mem)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return m.ullTotalPhys / 1024 ** 3
            return 0.0
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3
    except (OSError, ValueError, AttributeError):
        return 0.0


_DEM_KHUNG = None  # multiprocessing.Value chung, gán trong tiến trình con


def _khoi_tao_doan(dem) -> None:
    global _DEM_KHUNG
    _DEM_KHUNG = dem


def _dung_doan(tham: tuple) -> None:
    """Tiến trình con: vẽ cảnh ds[i0:i1] và mã hoá ra một đoạn hình không tiếng."""
    kb, ds, ch, thu_muc, nhap, cum, bao_giong, i0, i1, lenh = tham
    bd = BoDung(kb, ds, ch, Path(thu_muc), nhap=nhap, phu_de=None, bao_giong=bao_giong)
    bd.cum = cum  # phụ đề đã sắp xếp sẵn ở tiến trình chính
    bd._bd_cum = [c[0] for c in cum]
    tong = int(round((float(ds[i1 - 1]["ket_thuc"]) - float(ds[i0]["bat_dau"])) * bd.fps))
    bd._ma_hoa(lenh, tong, (i0, i1), _DEM_KHUNG)


def dung_video(kb: dict, ds: list[dict], tep_am_thanh: Path, tep_ra: Path, thu_muc_du_an: Path, ch: dict,
               nhap: bool = False, phu_de: list | None = None, bao_giong: dict | None = None) -> Path:
    """Dựng MP4 từ dòng thời gian + bản trộn âm thanh. phu_de: [(bd, kt, chữ)] để đốt vào hình, None = không.

    bao_giong: {id cảnh: RMS mỗi 1/15 s} cho nhân vật ghép `noi: true`; None = tự tính từ ds[i]["giong"].
    """
    if bao_giong is None:
        bao_giong = {}
        for muc in ds:
            lop = (muc.get("canh") or {}).get("lop") or []
            if muc.get("giong") and any(l.get("nhan_vat") and l.get("noi") for l in lop):
                try:
                    bao_giong[muc["id"]] = bao_giong_tu_tep(muc["giong"])
                except (RuntimeError, ValueError, OSError) as e:
                    _bao_mot_lan(f"bao:{muc['id']}", f"không đọc được giọng cảnh {muc['id']} để khớp miệng ({e}) — "
                                                     "miệng mở-đóng theo nhịp 0,56 s.")
    return BoDung(kb, ds, ch, thu_muc_du_an, nhap=nhap, phu_de=phu_de, bao_giong=bao_giong).chay(tep_am_thanh, tep_ra)
