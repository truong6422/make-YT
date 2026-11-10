"""Thumbnail YouTube 1280x720 từ khoá `thumbnail` trong kich-ban.json (chỉ cần Pillow).

Định dạng (mọi khoá đều tuỳ chọn trừ `chu`):
{
  "nen": "#FFD54F",                    # mã màu hoặc ảnh (phong-nen/...; tìm trong kho rồi thư mục dự án)
  "chu": "YOU SELL *TOO EARLY*",       # 2-5 từ; *...* = chữ nhấn
  "mau_chu": "#111111", "mau_nhan": "#E53935",
  "mau_vien": "#FFFFFF", "vien": null, # viền chữ (px ở 1280x720), null = tự tính theo cỡ chữ
  "bong": true,                        # bóng đổ dưới chữ
  "vi_tri_chu": [0.32, 0.5], "rong_chu": 0.58, "can_le": "giua",   # giua | trai
  "so_dong_toi_da": 3,
  "nhan_vat": [{"anh": "nhan-vat/max__soc__dung.png", "vi_tri": [0.75, 0.6], "co": 0.5, "lat": false}],
  "mui_ten": {"tu": [0.5, 0.5], "den": [0.7, 0.4], "mau": "#E53935", "day": 0.022},
  "khoanh_tron": {"tam": [0.75, 0.4], "ban_kinh": 0.15, "mau": "#E53935", "day": 0.012}
}
Toạ độ chuẩn hoá 0..1 theo khung. `co` = chiều cao nhân vật / chiều cao khung (đã cắt sát phần trong suốt).
`mui_ten` / `khoanh_tron` nhận một dict hoặc danh sách dict.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps

RONG, CAO = 1280, 720
HS = 2                                   # vẽ 2x rồi thu nhỏ để khử răng cưa
RV, CV = RONG * HS, CAO * HS
FONT_DU_PHONG = "C:/Windows/Fonts/arialbd.ttf"
NEN_MAC_DINH = "#FFD54F"

# ---------------------------------------------------------------- tiện ích


def _mau(gia_tri, mac_dinh: str) -> tuple[int, int, int]:
    if gia_tri is None:
        return ImageColor.getrgb(mac_dinh)[:3]
    try:
        return ImageColor.getrgb(str(gia_tri))[:3]
    except ValueError:
        print(f"[thumbnail] Cảnh báo: mã màu '{gia_tri}' không hợp lệ, dùng {mac_dinh}. "
              "Cách sửa: viết dạng #RRGGBB, vd. #E53935.")
        return ImageColor.getrgb(mac_dinh)[:3]


def _diem(gia_tri, mac_dinh=(0.5, 0.5)) -> tuple[float, float]:
    try:
        x, y = float(gia_tri[0]), float(gia_tri[1])
    except (TypeError, ValueError, IndexError):
        x, y = mac_dinh
    return x * RV, y * CV


def _tim_tep(ten, kho: Path, ra: Path) -> Path | None:
    if not ten:
        return None
    p = Path(str(ten))
    ung_vien = [p] if p.is_absolute() else [kho / p, ra.parent / p, p]
    for u in ung_vien:
        if u.is_file():
            return u
    return None


def _chon_font(font_path, kho: Path) -> str | None:
    ung_vien: list[Path] = []
    if font_path:
        p = Path(str(font_path))
        ung_vien += [p] if p.is_absolute() else [p, kho / p, kho.parent / p]
    ung_vien.append(Path(FONT_DU_PHONG))
    for u in ung_vien:
        if u.is_file():
            try:
                ImageFont.truetype(str(u), 20)
                return str(u)
            except OSError:
                continue
    print("[thumbnail] Cảnh báo: không tìm thấy font .ttf, dùng font mặc định của Pillow. "
          "Cách sửa: chạy `nq tai-mo-hinh font` hoặc truyền đường dẫn font.")
    return None


def _font(duong: str | None, co: int):
    if duong:
        return ImageFont.truetype(duong, co)
    try:
        return ImageFont.load_default(co)       # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def _danh_sach(gia_tri) -> list[dict]:
    if isinstance(gia_tri, dict):
        return [gia_tri]
    if isinstance(gia_tri, list):
        return [x for x in gia_tri if isinstance(x, dict)]
    return []


# ---------------------------------------------------------------- nền + nhân vật


def _ve_nen(cfg: dict, kho: Path, ra: Path) -> Image.Image:
    nen = cfg.get("nen", NEN_MAC_DINH) or NEN_MAC_DINH
    nen = str(nen)
    if nen.startswith("#"):
        return Image.new("RGB", (RV, CV), _mau(nen, NEN_MAC_DINH))
    tep = _tim_tep(nen, kho, ra)
    if tep is None:
        print(f"[thumbnail] Cảnh báo: không thấy ảnh nền '{nen}' (tìm trong {kho} và {ra.parent}), "
              f"dùng màu {NEN_MAC_DINH}.")
        return Image.new("RGB", (RV, CV), _mau(NEN_MAC_DINH, NEN_MAC_DINH))
    anh = Image.open(tep).convert("RGB")
    ti_le = max(RV / anh.width, CV / anh.height)
    anh = anh.resize((max(RV, round(anh.width * ti_le)), max(CV, round(anh.height * ti_le))),
                     Image.Resampling.LANCZOS)
    x = (anh.width - RV) // 2
    y = (anh.height - CV) // 2
    return anh.crop((x, y, x + RV, y + CV))


def _dan_nhan_vat(nen: Image.Image, nv: dict, kho: Path, ra: Path) -> None:
    tep = _tim_tep(nv.get("anh"), kho, ra)
    if tep is None:
        print(f"[thumbnail] Bỏ qua nhân vật: không thấy '{nv.get('anh')}' trong {kho}.")
        return
    anh = Image.open(tep).convert("RGBA")
    hop = anh.getchannel("A").getbbox()
    if hop:
        anh = anh.crop(hop)
    if nv.get("lat"):
        anh = ImageOps.mirror(anh)
    try:
        co = float(nv.get("co", 0.8))
    except (TypeError, ValueError):
        co = 0.8
    cao = max(1, round(co * CV))
    rong = max(1, round(anh.width * cao / anh.height))
    anh = anh.resize((rong, cao), Image.Resampling.LANCZOS)
    cx, cy = _diem(nv.get("vi_tri"), (0.75, 0.6))
    nen.paste(anh, (round(cx - rong / 2), round(cy - cao / 2)), anh)


# ---------------------------------------------------------------- chữ


def _tach_tu(chu: str) -> list[tuple[str, bool]]:
    """'YOU SELL *TOO EARLY*' -> [(YOU,F),(SELL,F),(TOO,T),(EARLY,T)]."""
    ds: list[tuple[str, bool]] = []
    for doan in re.split(r"(\*[^*]+\*)", chu):
        if not doan:
            continue
        nhan = len(doan) >= 2 and doan.startswith("*") and doan.endswith("*")
        if nhan:
            doan = doan[1:-1]
        for tu in doan.replace("*", "").split():
            ds.append((tu, nhan))
    return ds


def _bo_cuc_chu(tu_ds, duong_font, d, rong_toi_da, cao_toi_da, so_dong_toi_da, vien_cd):
    """Tìm cỡ chữ lớn nhất mà khối chữ vừa vùng. Trả (font, vien, dong, cach, cao_dong, lech_tren, gian, tong_cao)."""
    ket_qua = None
    for co in range(int(CV * 0.26), int(CV * 0.06) - 1, -4):
        font = _font(duong_font, co)
        vien = vien_cd if vien_cd is not None else max(4, round(co * 0.09))
        cach = d.textlength(" ", font=font)
        dong: list[tuple[list[tuple[str, bool, float]], float]] = []
        hien_tai: list[tuple[str, bool, float]] = []
        rong_ht = 0.0
        vua = True
        for tu, nhan in tu_ds:
            w = d.textlength(tu, font=font)
            if w + 2 * vien > rong_toi_da:
                vua = False
                break
            moi = w if not hien_tai else rong_ht + cach + w
            if hien_tai and moi + 2 * vien > rong_toi_da:
                dong.append((hien_tai, rong_ht))
                hien_tai, rong_ht = [(tu, nhan, w)], w
            else:
                hien_tai.append((tu, nhan, w))
                rong_ht = moi
        if hien_tai:
            dong.append((hien_tai, rong_ht))
        hop = font.getbbox("HÁgy", stroke_width=vien)
        cao_dong = hop[3] - hop[1]
        gian = co * 0.06
        tong_cao = len(dong) * cao_dong + (len(dong) - 1) * gian
        ket_qua = (font, vien, dong, cach, cao_dong, hop[1], gian, tong_cao)
        if vua and len(dong) <= so_dong_toi_da and tong_cao <= cao_toi_da:
            return ket_qua
    return ket_qua  # cỡ nhỏ nhất nếu không cỡ nào vừa


def _ve_chu(nen: Image.Image, cfg: dict, duong_font: str | None) -> None:
    chu = str(cfg.get("chu") or "").strip()
    tu_ds = _tach_tu(chu)
    if not tu_ds:
        return
    if len(tu_ds) > 5:
        print(f"[thumbnail] Cảnh báo: chữ có {len(tu_ds)} từ — nên 2-5 từ để đọc kịp trên điện thoại.")

    # Vùng chữ: tránh phía có nhân vật
    xs = []
    for nv in _danh_sach(cfg.get("nhan_vat")):
        try:
            xs.append(float(nv.get("vi_tri", [0.75, 0.6])[0]))
        except (TypeError, ValueError, IndexError):
            pass
    if xs:
        tb = sum(xs) / len(xs)
        mac_dinh_tam, mac_dinh_rong = ((0.32, 0.5), 0.58) if tb >= 0.5 else ((0.68, 0.5), 0.58)
    else:
        mac_dinh_tam, mac_dinh_rong = (0.5, 0.5), 0.9
    cx, cy = _diem(cfg.get("vi_tri_chu"), mac_dinh_tam)
    try:
        rong_vung = float(cfg.get("rong_chu", mac_dinh_rong)) * RV
    except (TypeError, ValueError):
        rong_vung = mac_dinh_rong * RV
    try:
        so_dong_toi_da = int(cfg.get("so_dong_toi_da", 3))
    except (TypeError, ValueError):
        so_dong_toi_da = 3
    vien_cd = cfg.get("vien")
    try:
        vien_cd = None if vien_cd is None else max(0, round(float(vien_cd) * HS))
    except (TypeError, ValueError):
        vien_cd = None

    mau_chu = _mau(cfg.get("mau_chu"), "#111111")
    mau_nhan = _mau(cfg.get("mau_nhan"), "#E53935")
    mau_vien = _mau(cfg.get("mau_vien"), "#FFFFFF")
    co_bong = cfg.get("bong", True) is not False

    d = ImageDraw.Draw(nen)
    font, vien, dong, cach, cao_dong, lech_tren, gian, tong_cao = _bo_cuc_chu(
        tu_ds, duong_font, d, rong_vung, CV * 0.82, so_dong_toi_da, vien_cd
    )
    can_trai = str(cfg.get("can_le", "giua")) == "trai"
    lech_bong = max(3, round(cao_dong * 0.05))

    y = cy - tong_cao / 2
    for tu_dong, rong_dong in dong:
        x = (cx - rong_vung / 2 + vien) if can_trai else (cx - rong_dong / 2)
        for tu, nhan, w in tu_dong:
            vt = (x, y - lech_tren)
            if co_bong:
                d.text((vt[0] + lech_bong, vt[1] + lech_bong), tu, font=font, fill=(0, 0, 0),
                       stroke_width=vien, stroke_fill=(0, 0, 0))
            d.text(vt, tu, font=font, fill=mau_nhan if nhan else mau_chu,
                   stroke_width=vien, stroke_fill=mau_vien)
            x += w + cach
        y += cao_dong + gian


# ---------------------------------------------------------------- mũi tên / khoanh tròn


def _ve_mui_ten(d: ImageDraw.ImageDraw, cfg: dict) -> None:
    tu = _diem(cfg.get("tu"), (0.5, 0.5))
    den = _diem(cfg.get("den"), (0.7, 0.4))
    if math.hypot(den[0] - tu[0], den[1] - tu[1]) < 1:
        return
    mau = _mau(cfg.get("mau"), "#E53935")
    mau_vien = _mau(cfg.get("mau_vien"), "#FFFFFF")
    try:
        day = float(cfg.get("day", 0.022)) * CV
    except (TypeError, ValueError):
        day = 0.022 * CV
    them = day * 0.35
    goc = math.atan2(den[1] - tu[1], den[0] - tu[0])
    ux, uy = math.cos(goc), math.sin(goc)
    nx, ny = -uy, ux
    dai_dau, rong_dau = day * 2.6, day * 1.7
    bx, by = den[0] - ux * dai_dau, den[1] - uy * dai_dau
    cuoi_than = (bx + ux * dai_dau * 0.3, by + uy * dai_dau * 0.3)
    tam_giac = [den, (bx + nx * rong_dau, by + ny * rong_dau), (bx - nx * rong_dau, by - ny * rong_dau)]
    gx = sum(p[0] for p in tam_giac) / 3
    gy = sum(p[1] for p in tam_giac) / 3
    k = 1 + 2.2 * them / rong_dau

    for mau_ve, cong in ((mau_vien, them), (mau, 0.0)):
        rong_net = day + 2 * cong
        d.line([tu, cuoi_than], fill=mau_ve, width=max(1, round(rong_net)))
        r = rong_net / 2
        d.ellipse((tu[0] - r, tu[1] - r, tu[0] + r, tu[1] + r), fill=mau_ve)
        if cong:
            d.polygon([(gx + (p[0] - gx) * k, gy + (p[1] - gy) * k) for p in tam_giac], fill=mau_ve)
        else:
            d.polygon(tam_giac, fill=mau_ve)


def _ve_khoanh(d: ImageDraw.ImageDraw, cfg: dict) -> None:
    cx, cy = _diem(cfg.get("tam"), (0.75, 0.4))
    bk = cfg.get("ban_kinh", 0.15)
    try:
        if isinstance(bk, (list, tuple)):
            rx, ry = float(bk[0]) * CV, float(bk[1]) * CV
        else:
            rx = ry = float(bk) * CV
    except (TypeError, ValueError, IndexError):
        rx = ry = 0.15 * CV
    mau = _mau(cfg.get("mau"), "#E53935")
    mau_vien = _mau(cfg.get("mau_vien"), "#FFFFFF")
    try:
        day = float(cfg.get("day", 0.012)) * CV
    except (TypeError, ValueError):
        day = 0.012 * CV
    them = day * 0.4
    # Pillow vẽ viền vào trong khung: khung lớp trắng nới thêm `them` để hai nét cùng tâm
    d.ellipse((cx - rx - them, cy - ry - them, cx + rx + them, cy + ry + them),
              outline=mau_vien, width=max(1, round(day + 2 * them)))
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=mau, width=max(1, round(day)))


# ---------------------------------------------------------------- hàm chính


def tao_thumbnail(cau_hinh_thumb: dict, ra: Path, kho: Path, font_path: str | None = None) -> Path:
    """Vẽ thumbnail PNG 1280x720 theo `cau_hinh_thumb`, ghi ra `ra`. Trả đường dẫn tệp."""
    if not isinstance(cau_hinh_thumb, dict):
        raise ValueError(
            "Khoá 'thumbnail' trong kich-ban.json phải là một object, vd. "
            '{"nen": "#FFD54F", "chu": "YOU SELL *TOO EARLY*"}. '
            "Cách sửa: xem docs/06-HINH-TAM-VA-THUMBNAIL.md."
        )
    ra, kho = Path(ra), Path(kho)
    cfg = cau_hinh_thumb

    nen = _ve_nen(cfg, kho, ra)
    for nv in _danh_sach(cfg.get("nhan_vat"))[:2]:
        _dan_nhan_vat(nen, nv, kho, ra)

    _ve_chu(nen, cfg, _chon_font(font_path or cfg.get("font"), kho))

    d = ImageDraw.Draw(nen)
    for k in _danh_sach(cfg.get("khoanh_tron")):
        _ve_khoanh(d, k)
    for m in _danh_sach(cfg.get("mui_ten")):
        _ve_mui_ten(d, m)

    ra.parent.mkdir(parents=True, exist_ok=True)
    nen.resize((RONG, CAO), Image.Resampling.LANCZOS).save(ra, "PNG")
    return ra
