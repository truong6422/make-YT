"""Bộ hình người que TẠM + hiệu ứng âm thanh TẠM cho `kho-mau/`.

Dùng để làm video đầu tiên khi chưa có ảnh Gemini: chỉ cần Pillow + numpy.
Tên tệp theo đúng mã ở docs/04-TAO-ANH-GEMINI.md (biểu cảm / tư thế tiếng Việt không dấu), nên mọi
tệp `templates/kich-ban-mau.json` tham chiếu đều có, và ảnh Gemini cùng tên thay thế được về sau.
- Ảnh: PNG nền trong suốt 1024x1024 (đám đông 1024x576, nền cảnh 1920x1080 không trong suốt),
  vẽ ở 2x rồi thu nhỏ để khử răng cưa.
- Âm thanh: wav 16-bit mono 48 kHz, ghi bằng module `wave` chuẩn.

Tệp đã có thì giữ nguyên (trừ khi `ghi_de=True`) để không đè ảnh thật người dùng đã bỏ vào.
"""

from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- hằng

CO = 1024                 # cỡ ảnh xuất
HE_SO = 2                 # vẽ ở 2x rồi thu nhỏ
CO_VE = CO * HE_SO        # 2048
NET = 36                  # độ dày nét ở khung 2x (= 18px ở ảnh xuất)

DEN = (17, 17, 17, 255)
TRANG = (255, 255, 255, 255)
XANH_NUOC = (79, 195, 247, 255)
DO = (229, 57, 53, 255)
XANH_LA = (67, 160, 71, 255)
HONG_NAO = (248, 160, 190, 255)  # màu đầu Brainy (bộ não hồng)

TAN_SO_SFX = 48000

# Đầu nhân vật (toạ độ khung 2x)
HX, HY, HR = 1024, 540, 230
VAI = (1024, 880)
HONG_Y = 1360

# Mã biểu cảm / tư thế = tiếng Việt không dấu, ĐÚNG bảng 3 và 4 của docs/04-TAO-ANH-GEMINI.md
# (để ảnh Gemini cùng tên thay thế được ảnh tạm, và /kich-ban tìm đúng tệp).
# mat: cham | to | cong | nham | nua | do-la ; nhin: lệch con ngươi (x, y)
# may: ((dy_trong, dy_ngoai) trái, (dy_trong, dy_ngoai) phải) ; None = không vẽ ; dy âm = nhướn lên
# mieng: cuoi | cuoi-to | meu | o | ha-to | luon-song | nhech | xien | thang | thang-lech | nghien
# them: mo-hoi | mot-giot | nuoc-mat | hoi | None
BIEU_CAM: dict[str, dict] = {
    "vui": {"mat": "cong", "nhin": (0, 0), "may": ((-20, -5), (-20, -5)), "mieng": "cuoi-to", "them": None},
    "tham-lam": {"mat": "do-la", "nhin": (0, 0), "may": ((22, -18), (22, -18)), "mieng": "cuoi-to", "them": None},
    "so-hai": {"mat": "to", "nhin": (0, 10), "may": ((-30, 10), (-30, 10)), "mieng": "luon-song", "them": None},
    "hoang-loan": {"mat": "to", "nhin": (0, 0), "may": ((-38, 10), (-38, 10)), "mieng": "ha-to", "them": "mo-hoi"},
    "hoi-han": {"mat": "cham", "nhin": (0, 18), "may": ((-25, 10), (-25, 10)), "mieng": "meu", "them": None},
    "tu-tin": {"mat": "nua", "nhin": (0, 0), "may": ((0, -5), (-30, -38)), "mieng": "nhech", "them": None},
    "boi-roi": {"mat": "cham", "nhin": (8, -6), "may": ((-35, -42), (12, 12)), "mieng": "xien", "them": None},
    "soc": {"mat": "to", "nhin": (0, 0), "may": ((-48, -48), (-48, -48)), "mieng": "o", "them": None},
    "suy-nghi": {"mat": "cham", "nhin": (14, -14), "may": ((0, 0), (-32, -32)), "mieng": "thang-lech", "them": None},
    "buon": {"mat": "cham", "nhin": (0, 12), "may": ((-25, 10), (-25, 10)), "mieng": "meu", "them": "nuoc-mat"},
    "gian": {"mat": "cham", "nhin": (0, 4), "may": ((32, -28), (32, -28)), "mieng": "nghien", "them": "hoi"},
    "nhe-nhom": {"mat": "nham", "nhin": (0, 0), "may": ((-12, -4), (-12, -4)), "mieng": "cuoi", "them": None},
    "dac-y": {"mat": "nua", "nhin": (0, 0), "may": ((-4, -22), (-4, -22)), "mieng": "nhech", "them": None},
    "lo-lang": {"mat": "cham", "nhin": (0, 4), "may": ((-34, 8), (-34, 8)), "mieng": "luon-song", "them": "mot-giot"},
    "hao-hung": {"mat": "to", "nhin": (0, -8), "may": ((-42, -42), (-42, -42)), "mieng": "cuoi-to", "them": None},
    "chan": {"mat": "nua", "nhin": (0, 0), "may": None, "mieng": "thang", "them": None},
}

TU_THE = ("dung", "chi-tay", "om-dau", "ngoi", "ngoi-may-tinh", "cam-dien-thoai", "di-bo")

# Mỗi tay: vai -> khuỷu -> bàn tay
TAY: dict[str, list[list[tuple[int, int]]]] = {
    "dung": [[VAI, (880, 1090), (820, 1290)], [VAI, (1168, 1090), (1228, 1290)]],
    "chi-tay": [[VAI, (880, 1090), (820, 1290)], [VAI, (1330, 830), (1640, 760)]],
    "om-dau": [[VAI, (700, 800), (800, 600)], [VAI, (1348, 800), (1248, 600)]],
    "ngoi": [[VAI, (930, 1120), (1120, 1300)], [VAI, (1150, 1110), (1290, 1300)]],
    "ngoi-may-tinh": [[VAI, (1150, 1100), (1340, 1215)], [VAI, (1210, 1050), (1400, 1180)]],
    "cam-dien-thoai": [[VAI, (880, 1090), (820, 1290)], [VAI, (1260, 1060), (1340, 900)]],
    "di-bo": [[VAI, (1140, 1080), (1250, 1240)], [VAI, (910, 1090), (820, 1240)]],
}

# Chân: hông -> (gối) -> bàn chân ; tư thế ngồi vẽ riêng (có ghế)
CHAN: dict[str, list[list[tuple[int, int]]]] = {
    "di-bo": [[(HX, HONG_Y), (1130, 1620), (1235, 1870)], [(HX, HONG_Y), (960, 1620), (835, 1850)]],
}
CHAN_THANG = [[(HX, HONG_Y), (870, 1880)], [(HX, HONG_Y), (1178, 1880)]]
TU_THE_NGOI = ("ngoi", "ngoi-may-tinh")

# Nhân vật phụ (docs/04 mục 5): chỉ tạo các tổ hợp hay dùng; cần thêm thì sửa ở đây.
NHAN_VAT_PHU: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "brainy": (("tu-tin", "vui", "suy-nghi", "boi-roi", "soc", "lo-lang"), ("dung", "chi-tay")),
    "ban": (("vui", "tham-lam", "so-hai", "buon", "hoi-han"), ("dung", "chi-tay")),
}
# Đám đông 16:9: tên tệp -> (biểu cảm, tư thế từng người, lật trái?, hướng nhìn đè)
DAM_DONG: dict[str, tuple[str, str, bool, tuple[int, int] | None]] = {
    "dam-dong__hao-hung__chay": ("hao-hung", "di-bo", False, None),
    "dam-dong__hoang-loan__bo-chay": ("hoang-loan", "di-bo", True, None),
    "dam-dong__soc__nhin-len": ("soc", "dung", False, (0, -18)),
}

# ---------------------------------------------------------------- tiện ích vẽ


def _anh_moi() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    anh = Image.new("RGBA", (CO_VE, CO_VE), (0, 0, 0, 0))
    return anh, ImageDraw.Draw(anh)


def _luu_anh(anh: Image.Image, duong_dan: Path) -> None:
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    anh.resize((CO, CO), Image.Resampling.LANCZOS).save(duong_dan, "PNG")


def _net(d: ImageDraw.ImageDraw, diem, rong: int = NET, mau=DEN) -> None:
    """Đường gấp khúc nét tròn đầu (vẽ thêm chấm tròn ở mỗi điểm)."""
    diem = [(float(x), float(y)) for x, y in diem]
    if len(diem) >= 2:
        d.line(diem, fill=mau, width=int(rong), joint="curve")
    r = rong / 2
    for x, y in diem:
        d.ellipse((x - r, y - r, x + r, y + r), fill=mau)


def _do_la(d: ImageDraw.ImageDraw, x: float, y: float, ti_le: float, rong: int, mau=DEN) -> None:
    """Ký hiệu $ vẽ bằng cung tròn (không cần font)."""
    r = 22 * ti_le
    tren = (x - r, y - 2 * r, x + r, y)
    duoi = (x - r, y, x + r, y + 2 * r)
    rong = int(rong)
    d.arc(tren, 90, 330, fill=mau, width=rong)
    d.arc(duoi, 270, 360, fill=mau, width=rong)
    d.arc(duoi, 0, 150, fill=mau, width=rong)
    d.line((x, y - 2.6 * r, x, y + 2.6 * r), fill=mau, width=max(2, int(rong * 0.7)))


def _giot(d: ImageDraw.ImageDraw, x: float, y: float, r: float) -> None:
    """Giọt nước (mồ hôi / nước mắt): vẽ bóng đen to hơn rồi phủ màu xanh."""
    for mau, them in ((DEN, 7), (XANH_NUOC, 0)):
        rr = r + them
        d.polygon(
            [(x, y - 2.2 * r - them * 1.5), (x - rr * 0.95, y - 0.3 * r), (x + rr * 0.95, y - 0.3 * r)],
            fill=mau,
        )
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=mau)


def _dau_mui_ten(d: ImageDraw.ImageDraw, tu, den, dai: float, rong: float, mau) -> None:
    """Tam giác mũi tên, đỉnh tại `den`, hướng từ `tu` sang `den`."""
    goc = math.atan2(den[1] - tu[1], den[0] - tu[0])
    ux, uy = math.cos(goc), math.sin(goc)
    nx, ny = -uy, ux
    bx, by = den[0] - ux * dai, den[1] - uy * dai
    d.polygon([den, (bx + nx * rong, by + ny * rong), (bx - nx * rong, by - ny * rong)], fill=mau)


# ---------------------------------------------------------------- khuôn mặt


def _mat(d: ImageDraw.ImageDraw, x: float, y: float, kieu: str, nhin) -> None:
    nx, ny = nhin
    if kieu == "to":
        r = 56
        d.ellipse((x - r, y - r, x + r, y + r), fill=TRANG, outline=DEN, width=12)
        rp = 20
        d.ellipse((x + nx - rp, y + ny - rp, x + nx + rp, y + ny + rp), fill=DEN)
    elif kieu == "cong":
        d.arc((x - 42, y - 26, x + 42, y + 40), 200, 340, fill=DEN, width=16)
    elif kieu == "nham":  # nhắm thư thái: cung võng xuống
        d.arc((x - 42, y - 40, x + 42, y + 22), 20, 160, fill=DEN, width=16)
    elif kieu == "nua":
        d.chord((x - 30, y - 30, x + 30, y + 30), 0, 180, fill=DEN)
        _net(d, [(x - 38, y), (x + 38, y)], 14)
    elif kieu == "do-la":
        _do_la(d, x, y - 10, 1.0, 12, (46, 125, 50, 255))
    else:  # cham
        r = 26
        d.ellipse((x + nx - r, y + ny - r, x + nx + r, y + ny + r), fill=DEN)


def _may(d: ImageDraw.ImageDraw, may) -> None:
    if not may:
        return
    goc_y = HY - 115
    for dau, cap in ((-1, may[0]), (1, may[1])):
        if cap is None:
            continue
        dy_trong, dy_ngoai = cap
        tam_x = HX + dau * 85
        ngoai = (tam_x + dau * 50, goc_y + dy_ngoai)
        trong = (tam_x - dau * 50, goc_y + dy_trong)
        _net(d, [ngoai, trong], 16)


def _mieng(d: ImageDraw.ImageDraw, kieu: str) -> None:
    x, y = HX, HY + 100
    if kieu == "cuoi":
        d.arc((x - 100, y - 90, x + 100, y + 50), 20, 160, fill=DEN, width=18)
    elif kieu == "cuoi-to":
        d.chord((x - 105, y - 60, x + 105, y + 80), 0, 180, fill=DEN)
        d.chord((x - 60, y + 20, x + 60, y + 76), 0, 180, fill=DO)
    elif kieu == "meu":
        d.arc((x - 90, y - 10, x + 90, y + 110), 200, 340, fill=DEN, width=18)
    elif kieu == "o":
        d.ellipse((x - 38, y - 30, x + 38, y + 60), fill=DEN)
    elif kieu == "ha-to":
        d.ellipse((x - 75, y - 50, x + 75, y + 80), fill=DEN)
    elif kieu == "luon-song":
        diem = [(x - 90 + i * 15, y + 20 + 14 * math.sin(i * math.pi / 2)) for i in range(13)]
        _net(d, diem, 16)
    elif kieu == "nhech":
        _net(d, [(x - 80, y + 30), (x + 30, y + 30), (x + 90, y - 10)], 16)
    elif kieu == "xien":
        _net(d, [(x - 70, y + 40), (x + 70, y + 5)], 16)
    elif kieu == "thang-lech":
        _net(d, [(x - 10, y + 30), (x + 70, y + 24)], 16)
    elif kieu == "nghien":  # nghiến răng: khung trắng viền đen + vạch răng
        d.rounded_rectangle((x - 90, y, x + 90, y + 64), radius=14, fill=TRANG, outline=DEN, width=14)
        _net(d, [(x - 84, y + 32), (x + 84, y + 32)], 10)
        for gx in (x - 45, x, x + 45):
            _net(d, [(gx, y + 4), (gx, y + 60)], 10)
    else:  # thang
        _net(d, [(x - 50, y + 30), (x + 50, y + 30)], 16)


# ---------------------------------------------------------------- nhân vật


def _ve_ban_may_tinh(d: ImageDraw.ImageDraw) -> None:
    """Bàn + laptop bên phải nhân vật ngồi (vẽ TRƯỚC chân để chân nằm trên)."""
    xam = (189, 189, 189, 255)
    d.rectangle((1250, 1250, 2000, 1300), fill=xam, outline=DEN, width=16)
    _net(d, [(1320, 1300), (1320, 1880)], 24)
    _net(d, [(1940, 1300), (1940, 1880)], 24)
    d.rectangle((1330, 1222, 1760, 1250), fill=(120, 120, 120, 255), outline=DEN, width=12)  # đế laptop
    d.polygon([(1745, 1240), (1785, 1240), (1900, 900), (1860, 900)], fill=(120, 120, 120, 255),
              outline=DEN, width=12)  # màn hình (nhìn nghiêng)


def _ve_dien_thoai_cam_tay(d: ImageDraw.ImageDraw) -> None:
    """Điện thoại cầm tay phải, màn hình có biểu đồ đường (không chữ / số)."""
    d.rounded_rectangle((1260, 600, 1440, 910), radius=26, fill=DEN)
    d.rectangle((1282, 640, 1418, 860), fill=TRANG)
    _net(d, [(1295, 830), (1325, 790), (1350, 805), (1380, 730), (1405, 700)], 12, XANH_LA)
    d.ellipse((1310, 870, 1370, 930), fill=DEN)  # bàn tay đè lên mép dưới


def _mau_dau(nhan_vat: str) -> tuple[int, int, int, int]:
    return HONG_NAO if nhan_vat == "brainy" else TRANG


def _ve_phu_kien(d: ImageDraw.ImageDraw, nhan_vat: str) -> None:
    """Dấu nhận dạng nhân vật phụ (docs/04 mục 5)."""
    if nhan_vat == "brainy":  # nếp não: một rãnh giữa + hai cung mỗi bên, trên vùng mắt
        _net(d, [(HX, HY - HR + 12), (HX, HY - HR * 55 // 100)], 12)
        for dau in (-1, 1):
            x0, x1 = sorted((HX + dau * HR * 18 // 100, HX + dau * HR * 62 // 100))
            d.arc((x0, HY - HR * 82 // 100, x1, HY - HR * 42 // 100), 200, 340, fill=DEN, width=12)
    elif nhan_vat == "ban":
        for goc_x, dinh in ((975, (945, 235)), (1024, (1024, 215)), (1073, (1103, 235))):  # chỏm tóc 3 nét
            _net(d, [(goc_x, HY - HR + 8), dinh], 22)


def _ve_nhan_vat(bieu_cam: str, tu_the: str, nhan_vat: str = "max", nhin=None) -> Image.Image:
    anh, d = _anh_moi()
    cau_hinh = BIEU_CAM[bieu_cam]

    # Chân (+ ghế khi ngồi, + bàn laptop)
    if tu_the in TU_THE_NGOI:
        if tu_the == "ngoi-may-tinh":
            _ve_ban_may_tinh(d)
        d.rectangle((760, 1390, 1200, 1460), fill=(158, 158, 158, 255), outline=DEN, width=16)
        _net(d, [(800, 1460), (800, 1880)], 24)
        _net(d, [(1160, 1460), (1160, 1880)], 24)
        _net(d, [(HX, HONG_Y), (1240, HONG_Y + 20), (1250, 1870), (1340, 1870)])
        _net(d, [(HX, HONG_Y), (1300, HONG_Y), (1310, 1850), (1400, 1850)])
    else:
        for chan in CHAN.get(tu_the, CHAN_THANG):
            _net(d, chan)

    # Thân
    _net(d, [(HX, HY + HR - 10), (HX, HONG_Y)])

    # Đầu + mặt
    d.ellipse((HX - HR, HY - HR, HX + HR, HY + HR), fill=_mau_dau(nhan_vat), outline=DEN, width=NET)
    for dau in (-1, 1):
        _mat(d, HX + dau * 85, HY - 20, cau_hinh["mat"], nhin if nhin is not None else cau_hinh["nhin"])
    _may(d, cau_hinh["may"])
    _mieng(d, cau_hinh["mieng"])
    _ve_them(d, cau_hinh["them"])
    _ve_phu_kien(d, nhan_vat)

    # Tay vẽ sau đầu để bàn tay ôm đầu nằm trên viền đầu
    for nhanh in TAY[tu_the]:
        _net(d, nhanh)
        x, y = nhanh[-1]
        d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=DEN)
    if tu_the == "chi-tay":
        _net(d, [(1640, 760), (1725, 740)], 22)  # ngón trỏ
    elif tu_the == "cam-dien-thoai":
        _ve_dien_thoai_cam_tay(d)

    return anh


def _ve_them(d: ImageDraw.ImageDraw, them) -> None:
    """Ký hiệu cảm xúc quanh đầu: mồ hôi / một giọt / nước mắt / hơi giận."""
    if them == "mo-hoi":
        _giot(d, HX + HR + 45, HY - 70, 26)
        _giot(d, HX - HR - 35, HY - 20, 20)
    elif them == "mot-giot":
        _giot(d, HX + HR + 40, HY - 90, 24)
    elif them == "nuoc-mat":
        _giot(d, HX - 85, HY + 50, 18)
    elif them == "hoi":  # hơi giận bốc trên đầu
        for cx, cy, r in ((HX - 170, HY - HR - 70, 34), (HX + 170, HY - HR - 70, 34), (HX + 230, HY - HR - 140, 24)):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(224, 224, 224, 255), outline=DEN, width=10)


def _ve_dam_dong(bieu_cam: str, tu_the: str, lat: bool, nhin) -> Image.Image:
    """7 người que cùng phong cách, cỡ hơi khác nhau, khung 16:9 (vẽ 2x)."""
    rong, cao = CO_VE, CO_VE * 9 // 16
    anh = Image.new("RGBA", (rong, cao), (0, 0, 0, 0))
    mot = _ve_nhan_vat(bieu_cam, tu_the, nhin=nhin)
    if lat:
        mot = mot.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    for i, co in enumerate((560, 520, 600, 540, 580, 510, 560)):
        nguoi = mot.resize((co, co), Image.Resampling.LANCZOS)
        x = 10 + i * 240
        y = max(0, cao - co - (i % 2) * 24)  # ảnh lọt hẳn trong khung (alpha_composite cần dest >= 0)
        anh.alpha_composite(nguoi, dest=(x, y))
    return anh


# ---------------------------------------------------------------- đạo cụ


def _ve_tien(d: ImageDraw.ImageDraw) -> None:
    xanh_dam = (46, 125, 50, 255)
    x0, y0, x1, y1 = 224, 624, 1824, 1424
    d.rounded_rectangle((x0, y0, x1, y1), radius=60, fill=(102, 187, 106, 255), outline=DEN, width=NET)
    d.rounded_rectangle((x0 + 90, y0 + 90, x1 - 90, y1 - 90), radius=40, outline=xanh_dam, width=20)
    cx, cy = 1024, 1024
    d.ellipse((cx - 260, cy - 260, cx + 260, cy + 260), fill=(165, 214, 167, 255), outline=xanh_dam, width=20)
    _do_la(d, cx, cy, 4.5, 44, (27, 94, 32, 255))
    for gx in (x0 + 210, x1 - 210):
        d.ellipse((gx - 50, cy - 50, gx + 50, cy + 50), outline=xanh_dam, width=16)


def _ve_bao_tien(d: ImageDraw.ImageDraw) -> None:
    nau = (200, 161, 101, 255)
    nau_dam = (141, 110, 62, 255)
    d.ellipse((424, 724, 1624, 1904), fill=nau, outline=DEN, width=NET)
    d.polygon([(724, 404), (1324, 404), (1144, 770), (904, 770)], fill=nau, outline=DEN, width=NET)
    d.rounded_rectangle((864, 720, 1184, 810), radius=30, fill=nau_dam, outline=DEN, width=NET)
    _do_la(d, 1024, 1330, 5.0, 50, nau_dam)


def _ve_bong_den(d: ImageDraw.ImageDraw) -> None:
    vang = (255, 235, 59, 255)
    cx, cy, r = 1024, 760, 380
    for i in range(9):
        a = math.radians(-180 + 22.5 * i)
        _net(
            d,
            [(cx + 460 * math.cos(a), cy + 460 * math.sin(a)), (cx + 610 * math.cos(a), cy + 610 * math.sin(a))],
            30,
            (255, 193, 7, 255),
        )
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=vang, outline=DEN, width=NET)
    # Cổ bóng phủ lên viền dưới của hình tròn rồi kẻ lại hai cạnh
    d.polygon([(854, 1100), (1194, 1100), (1164, 1310), (884, 1310)], fill=vang)
    _net(d, [(854, 1100), (884, 1310)])
    _net(d, [(1194, 1100), (1164, 1310)])
    _net(d, [(924, 1100), (964, 900), (1024, 980), (1084, 900), (1124, 1100)], 16, (255, 143, 0, 255))
    d.chord((944, 1470, 1104, 1600), 0, 180, fill=DEN)
    d.rounded_rectangle((864, 1300, 1184, 1520), radius=30, fill=(176, 176, 176, 255), outline=DEN, width=NET)
    for y in (1373, 1446):
        _net(d, [(884, y), (1164, y)], 18)


def _ve_dau_hoi(d: ImageDraw.ImageDraw) -> None:
    cx, cy, rc = 1024, 704, 330  # rc = bán kính đường tâm nét
    for mau, rong in ((DEN, 200), (DO, 136)):
        rb = rc + rong / 2  # cung của Pillow vẽ nét vào trong khung -> nới khung để tâm nét trùng nhau
        hop = (cx - rb, cy - rb, cx + rb, cy + rb)
        d.arc(hop, 180, 360, fill=mau, width=rong)
        d.arc(hop, 0, 75, fill=mau, width=rong)
        cuoi_cung = (cx + rc * math.cos(math.radians(75)), cy + rc * math.sin(math.radians(75)))
        _net(d, [(cx - rc, cy)], rong, mau)
        _net(d, [cuoi_cung, (cx, 1150), (cx, 1360)], rong, mau)
        rr = 100 + (rong - 136) / 2
        d.ellipse((cx - rr, 1640 - rr, cx + rr, 1640 + rr), fill=mau)


def _ve_nao(d: ImageDraw.ImageDraw) -> None:
    hong = (244, 143, 177, 255)
    hong_dam = (194, 24, 91, 255)
    vong = [
        (724, 824, 260), (1024, 724, 300), (1324, 824, 260), (624, 1124, 240),
        (1424, 1124, 240), (874, 1264, 250), (1174, 1264, 250), (1024, 1050, 300),
    ]
    for cx, cy, r in vong:  # bóng đen to hơn = viền chung của cả khối
        rr = r + NET
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=DEN)
    for cx, cy, r in vong:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hong)
    _net(d, [(1024, 470), (996, 760), (1050, 1010), (1024, 1420)], 18, hong_dam)
    d.arc((660, 700, 900, 940), 180, 330, fill=hong_dam, width=18)
    d.arc((1150, 700, 1390, 940), 210, 360, fill=hong_dam, width=18)
    d.arc((560, 1000, 800, 1240), 200, 340, fill=hong_dam, width=18)
    d.arc((1250, 1000, 1490, 1240), 200, 340, fill=hong_dam, width=18)
    d.arc((760, 1150, 960, 1350), 20, 160, fill=hong_dam, width=18)
    d.arc((1090, 1150, 1290, 1350), 20, 160, fill=hong_dam, width=18)


def _ve_can(d: ImageDraw.ImageDraw, lech: int = 0) -> None:
    """Cân hai đĩa. lech > 0: đĩa TRÁI thấp hơn (can-lech, docs/04)."""
    vang = (255, 193, 7, 255)
    d.polygon([(774, 1824), (1274, 1824), (1124, 1664), (924, 1664)], fill=vang, outline=DEN, width=NET)
    _net(d, [(1024, 1664), (1024, 520)], 50)
    _net(d, [(424, 600 + lech), (1624, 600 - lech)], 40)
    d.ellipse((964, 540, 1084, 660), fill=vang, outline=DEN, width=20)
    for x, yb in ((424, 600 + lech), (1624, 600 - lech)):
        _net(d, [(x, yb), (x - 200, yb + 500)], 14)
        _net(d, [(x, yb), (x + 200, yb + 500)], 14)
        d.chord((x - 260, yb + 350, x + 260, yb + 650), 0, 180, fill=vang, outline=DEN, width=NET)


def _ve_can_lech(d: ImageDraw.ImageDraw) -> None:
    _ve_can(d, 170)


def _ve_the_co_phieu(d: ImageDraw.ImageDraw, len_: bool) -> None:
    nen = (46, 125, 50, 255) if len_ else (229, 57, 53, 255)
    d.rounded_rectangle((424, 424, 1624, 1624), radius=120, fill=nen, outline=DEN, width=NET)
    _ve_mui_ten_khoi(d, 1024, 1024, 760, len_, TRANG, 20)


def _ve_co_phieu_xanh(d: ImageDraw.ImageDraw) -> None:
    _ve_the_co_phieu(d, True)


def _ve_co_phieu_do(d: ImageDraw.ImageDraw) -> None:
    _ve_the_co_phieu(d, False)


def _ve_mui_ten_khoi(d: ImageDraw.ImageDraw, cx: float, cy: float, cao: float, len_: bool, mau, vien: int) -> None:
    """Mũi tên khối thẳng đứng, tâm (cx, cy), cao `cao`."""
    s = cao / 1448.0  # khuôn gốc cao 1448 (300..1748)
    khuon = [(0, -724), (500, -124), (200, -124), (200, 724), (-200, 724), (-200, -124), (-500, -124)]
    diem = [(cx + x * s, cy + (y if len_ else -y) * s) for x, y in khuon]
    d.polygon(diem, fill=mau, outline=DEN, width=vien)


def _ve_mui_ten_len(d: ImageDraw.ImageDraw) -> None:
    _ve_mui_ten_khoi(d, 1024, 1024, 1448, True, XANH_LA, NET)


def _ve_mui_ten_xuong(d: ImageDraw.ImageDraw) -> None:
    _ve_mui_ten_khoi(d, 1024, 1024, 1448, False, DO, NET)


def _ve_may_tinh(d: ImageDraw.ImageDraw) -> None:
    xam = (176, 176, 176, 255)
    d.rounded_rectangle((474, 424, 1574, 1234), radius=40, fill=(66, 66, 66, 255), outline=DEN, width=NET)
    d.rectangle((554, 504, 1494, 1154), fill=(225, 245, 254, 255))
    d.polygon([(374, 1264), (1674, 1264), (1834, 1444), (214, 1444)], fill=xam, outline=DEN, width=NET)
    _net(d, [(874, 1354), (1174, 1354)], 22)


def _ve_dien_thoai(d: ImageDraw.ImageDraw) -> None:
    d.rounded_rectangle((744, 304, 1304, 1744), radius=90, fill=(33, 33, 33, 255), outline=DEN, width=NET)
    d.rectangle((804, 444, 1244, 1544), fill=TRANG)
    d.ellipse((974, 1590, 1074, 1690), outline=(189, 189, 189, 255), width=14)


def _ve_dong_xu(d: ImageDraw.ImageDraw) -> None:
    vang, vang_dam = (255, 202, 40, 255), (255, 160, 0, 255)
    for cx, cy in ((774, 1274), (1274, 1274), (1024, 874)):
        d.ellipse((cx - 330, cy - 330, cx + 330, cy + 330), fill=vang, outline=DEN, width=NET)
        d.ellipse((cx - 230, cy - 230, cx + 230, cy + 230), outline=vang_dam, width=22)


def _ve_dong_ho_cat(d: ImageDraw.ImageDraw) -> None:
    kinh, cat = (227, 242, 253, 255), (255, 224, 130, 255)
    d.polygon([(724, 424), (1324, 424), (1064, 1024), (984, 1024)], fill=kinh, outline=DEN, width=NET)
    d.polygon([(984, 1024), (1064, 1024), (1324, 1624), (724, 1624)], fill=kinh, outline=DEN, width=NET)
    d.polygon([(864, 704), (1184, 704), (1044, 984), (1004, 984)], fill=cat)
    d.polygon([(804, 1610), (1244, 1610), (1024, 1380)], fill=cat)
    _net(d, [(1024, 1030), (1024, 1380)], 10, cat)
    for y0 in (324, 1624):
        d.rounded_rectangle((604, y0, 1444, y0 + 100), radius=30, fill=(141, 110, 62, 255), outline=DEN, width=NET)


def _ve_dong_ho(d: ImageDraw.ImageDraw) -> None:
    c = 1024
    d.ellipse((324, 324, 1724, 1724), fill=TRANG, outline=DEN, width=60)
    for i in range(12):
        a = math.radians(i * 30)
        r1 = 500 if i % 3 == 0 else 560
        _net(
            d,
            [(c + r1 * math.sin(a), c - r1 * math.cos(a)), (c + 615 * math.sin(a), c - 615 * math.cos(a))],
            44 if i % 3 == 0 else 28,
        )

    def kim(goc_do: float, dai: float, rong: int, mau=DEN) -> None:
        a = math.radians(goc_do)
        _net(d, [(c, c), (c + dai * math.sin(a), c - dai * math.cos(a))], rong, mau)

    kim(300, 330, 54)   # kim giờ (10 giờ)
    kim(60, 500, 36)    # kim phút (10 phút)
    kim(160, 540, 14, DO)
    d.ellipse((c - 50, c - 50, c + 50, c + 50), fill=DEN)


# Tên tệp = bảng mục 6 docs/04 (dao-cu/<ten>.png)
DAO_CU = {
    "tien": _ve_tien,
    "bao-tien": _ve_bao_tien,
    "dong-xu": _ve_dong_xu,
    "co-phieu-xanh": _ve_co_phieu_xanh,
    "co-phieu-do": _ve_co_phieu_do,
    "bo-nao": _ve_nao,
    "can": _ve_can,
    "can-lech": _ve_can_lech,
    "dong-ho": _ve_dong_ho,
    "dong-ho-cat": _ve_dong_ho_cat,
    "bong-den": _ve_bong_den,
    "dau-hoi": _ve_dau_hoi,
    "may-tinh": _ve_may_tinh,
    "dien-thoai": _ve_dien_thoai,
    "mui-ten-len": _ve_mui_ten_len,
    "mui-ten-xuong": _ve_mui_ten_xuong,
}

# ---------------------------------------------------------------- biểu đồ

# Tên tệp = bảng mục 7 docs/04 (bieu-do/<ten>.png); cot-tang vẽ riêng
BIEU_DO = {
    "tang": [(0, 0.1), (0.15, 0.25), (0.3, 0.2), (0.45, 0.45), (0.6, 0.4), (0.78, 0.68), (0.9, 0.62), (1, 0.92)],
    "giam": [(0, 0.9), (0.15, 0.75), (0.3, 0.8), (0.45, 0.55), (0.6, 0.6), (0.78, 0.32), (0.9, 0.38), (1, 0.08)],
    "giam-manh": [(0, 0.15), (0.14, 0.3), (0.28, 0.26), (0.42, 0.48), (0.56, 0.55), (0.7, 0.82), (0.78, 0.78),
                  (1, 0.05)],
    "tang-giam": [(0, 0.3), (0.12, 0.6), (0.25, 0.4), (0.38, 0.85), (0.5, 0.35), (0.62, 0.7),
                  (0.75, 0.15), (0.88, 0.55), (1, 0.25)],
    "cot-tang": None,
}


def _ve_bieu_do(d: ImageDraw.ImageDraw, ten: str) -> None:
    # Lưới mờ + trục
    for y in (1330, 1000, 670, 340):
        d.line((330, y, 1780, y), fill=(0, 0, 0, 45), width=8)
    _net(d, [(300, 260), (300, 1760), (1800, 1760)], 30)
    _dau_mui_ten(d, (300, 400), (300, 190), 90, 50, DEN)
    _dau_mui_ten(d, (1700, 1760), (1870, 1760), 90, 50, DEN)

    if BIEU_DO[ten] is None:  # cot-tang: 5 cột xanh cao dần
        for i in range(5):
            x0 = 420 + i * 270
            d.rectangle((x0, 1745 - 260 - i * 260, x0 + 190, 1745), fill=XANH_LA, outline=DEN, width=24)
        return

    diem = [(400 + u * 1320, 1660 - v * 1320) for u, v in BIEU_DO[ten]]
    _net(d, diem, 66)  # viền đen chung
    for a, b in zip(diem, diem[1:]):
        if ten == "tang":
            mau = XANH_LA
        elif ten == "giam":
            mau = DO
        else:  # giam-manh, tang-giam: đoạn lên xanh, đoạn xuống đỏ
            mau = XANH_LA if b[1] < a[1] else DO
        _net(d, [a, b], 42, mau)

    if ten in ("tang", "giam", "giam-manh"):
        a, b = diem[-2], diem[-1]
        goc = math.atan2(b[1] - a[1], b[0] - a[0])
        dinh = (b[0] + 110 * math.cos(goc), b[1] + 110 * math.sin(goc))
        mau = XANH_LA if ten == "tang" else DO
        _dau_mui_ten(d, b, (dinh[0] + 14 * math.cos(goc), dinh[1] + 14 * math.sin(goc)), 190, 110, DEN)
        _dau_mui_ten(d, b, dinh, 160, 86, mau)


# ---------------------------------------------------------------- nền cảnh (16:9, không trong suốt)


def _ve_van_phong() -> Image.Image:
    """phong-nen/van-phong.png: nét xám mảnh trên nền trắng ngà, giữa khung để trống cho nhân vật."""
    rong, cao = 1920 * HE_SO, 1080 * HE_SO
    anh = Image.new("RGB", (rong, cao), (250, 250, 247))
    d = ImageDraw.Draw(anh)
    xam, w = (189, 189, 189), 8
    d.line((0, 1800, rong, 1800), fill=xam, width=w)                       # chân tường
    d.rectangle((1560, 220, 2280, 760), outline=xam, width=w)              # cửa sổ
    d.line((1920, 220, 1920, 760), fill=xam, width=w)
    d.line((1560, 490, 2280, 490), fill=xam, width=w)
    d.rectangle((3000, 1380, 3760, 1420), outline=xam, width=w)            # bàn bên phải
    for x in (3040, 3720):
        d.line((x, 1420, x, 1800), fill=xam, width=w)
    d.rectangle((3180, 960, 3580, 1240), outline=xam, width=w)             # màn hình
    d.line((3380, 1240, 3380, 1380), fill=xam, width=w)
    d.line((3300, 1380, 3460, 1380), fill=xam, width=w)
    d.polygon([(180, 1560), (420, 1560), (390, 1800), (210, 1800)], outline=xam, width=w)  # chậu cây trái
    for cx, cy, rx, ry in ((300, 1380, 70, 170), (200, 1440, 60, 140), (400, 1440, 60, 140)):
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=xam, width=w)
    return anh.resize((1920, 1080), Image.Resampling.LANCZOS)


PHONG_NEN = {"van-phong": _ve_van_phong}


# ---------------------------------------------------------------- âm thanh


def _ghi_wav(duong_dan: Path, mau: np.ndarray, tan_so: int = TAN_SO_SFX) -> None:
    """float [-1, 1] -> wav 16-bit mono (tự viết, không phụ thuộc am_thanh_io)."""
    mau = np.clip(np.asarray(mau, dtype=np.float32), -1.0, 1.0)
    du_lieu = (mau * 32767.0).astype("<i2").tobytes()
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(duong_dan), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(tan_so)
        w.writeframes(du_lieu)


def _t(giay: float) -> np.ndarray:
    return np.arange(int(TAN_SO_SFX * giay), dtype=np.float64) / TAN_SO_SFX


def _chuan(x: np.ndarray, dinh: float = 0.8) -> np.ndarray:
    """Vuốt 4ms đầu / cuối cho khỏi lách tách, chuẩn đỉnh về `dinh`."""
    x = np.asarray(x, dtype=np.float64).copy()
    n = min(len(x) // 4, int(0.004 * TAN_SO_SFX))
    if n > 0:
        doc = np.linspace(0.0, 1.0, n)
        x[:n] *= doc
        x[-n:] *= doc[::-1]
    m = float(np.max(np.abs(x))) if len(x) else 0.0
    if m > 0:
        x = x / m * dinh
    return x.astype(np.float32)


def _sfx_pop(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.14)
    f = 300.0 + 900.0 * (t / t[-1])
    pha = 2 * np.pi * np.cumsum(f) / TAN_SO_SFX
    return _chuan(np.sin(pha) * np.exp(-t * 30))


def _sfx_whoosh(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.6)
    on = rng.standard_normal(len(t))
    min_ = np.convolve(on, np.ones(12) / 12, mode="same")
    tram = np.convolve(on, np.ones(300) / 300, mode="same")
    dai = min_ - tram  # lọc thông dải thô
    bao = np.sin(np.pi * (t / t[-1]) ** 0.7) ** 2
    return _chuan(dai * bao, 0.7)


def _sfx_ding(rng: np.random.Generator) -> np.ndarray:
    t = _t(1.5)
    x = (np.sin(2 * np.pi * 1318.5 * t)
         + 0.4 * np.sin(2 * np.pi * 2637.0 * t) * np.exp(-6 * t)
         + 0.2 * np.sin(2 * np.pi * 3955.5 * t) * np.exp(-9 * t))
    return _chuan(x * np.exp(-3.5 * t))


def _sfx_tick(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.05)
    x = (0.5 * rng.standard_normal(len(t)) + np.sin(2 * np.pi * 3000 * t)) * np.exp(-t * 120)
    return _chuan(x, 0.7)


def _sfx_cash(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.9)
    x = np.zeros(len(t))
    n_cach = int(0.08 * TAN_SO_SFX)
    tc = t[:n_cach]
    x[:n_cach] += 0.8 * rng.standard_normal(n_cach) * np.exp(-tc * 60)
    for tre, f in ((0.05, 2093.0), (0.15, 2637.0)):
        bd = int(tre * TAN_SO_SFX)
        tt = t[: len(t) - bd]
        x[bd:] += np.sin(2 * np.pi * f * tt) * np.exp(-5 * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-9 * tt)
    return _chuan(x)


def _sfx_buzz(rng: np.random.Generator) -> np.ndarray:
    t = _t(0.45)
    x = 0.6 * np.sign(np.sin(2 * np.pi * 140 * t)) + 0.4 * np.sign(np.sin(2 * np.pi * 147 * t))
    x = np.convolve(x, np.ones(8) / 8, mode="same")
    bao = np.minimum(1.0, (t[-1] - t) / 0.08)
    return _chuan(x * bao, 0.6)


SFX = {
    "pop": _sfx_pop,
    "whoosh": _sfx_whoosh,
    "ding": _sfx_ding,
    "tick": _sfx_tick,
    "cash": _sfx_cash,
    "buzz": _sfx_buzz,
}

# ---------------------------------------------------------------- nhân vật ghép bộ phận (docs/10)
# Toạ độ 1x (ảnh xuất). Khung tham chiếu 1024x1024 trùng ảnh nhân vật tĩnh: tâm đầu (512, 270), cổ y 380,
# vai y 440, hông (512, 680). Mỗi đoạn tay / chân vẽ THẲNG ĐỨNG, khớp ở trên, đầu tròn hai khớp để xoay không hở.
GHEP_LE = 4                    # lề trong suốt quanh mỗi bộ phận (1x)
GHEP_R = NET // 4              # bán kính đầu tròn = nửa nét (1x)
GHEP_DAU_NUA = 420             # nửa cạnh vùng cắt đầu ở khung 2x -> ảnh đầu 420x420 (đủ chỗ mồ hôi / hơi)
GHEP_HONG = (512, 680)
GHEP_THAN, GHEP_VAI = 300, 60  # dài thân (cổ -> hông), vai cách cổ
GHEP_TAY_TREN, GHEP_TAY_DUOI, GHEP_CHAN = 125, 110, 140


def _doan_ghep(dai: int, r_dau: int = GHEP_R, r_cuoi: int = GHEP_R):
    """Đoạn thẳng đứng nét đen -> (ảnh 1x, điểm trên, điểm dưới) toạ độ 1x."""
    r = max(r_dau, r_cuoi)
    w = 2 * (r + GHEP_LE)
    cx, y_tren = w // 2, GHEP_LE + r
    y_duoi = y_tren + dai
    h = y_duoi + r + GHEP_LE
    anh = Image.new("RGBA", (w * HE_SO, h * HE_SO), (0, 0, 0, 0))
    d = ImageDraw.Draw(anh)
    X, Y1, Y2 = cx * HE_SO, y_tren * HE_SO, y_duoi * HE_SO
    d.line([(X, Y1), (X, Y2)], fill=DEN, width=NET)
    for y, rr in ((Y1, r_dau * HE_SO), (Y2, r_cuoi * HE_SO)):
        d.ellipse((X - rr, y - rr, X + rr, y + rr), fill=DEN)
    return anh.resize((w, h), Image.Resampling.LANCZOS), (cx, y_tren), (cx, y_duoi)


def _vung_dau() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Khung 2x đủ chứa vùng đầu (dùng lại các hàm vẽ mặt toạ độ tuyệt đối HX, HY)."""
    anh = Image.new("RGBA", (HX + GHEP_DAU_NUA, HY + GHEP_DAU_NUA), (0, 0, 0, 0))
    return anh, ImageDraw.Draw(anh)


def _cat_dau(anh: Image.Image) -> Image.Image:
    hop = (HX - GHEP_DAU_NUA, HY - GHEP_DAU_NUA, HX + GHEP_DAU_NUA, HY + GHEP_DAU_NUA)
    return anh.crop(hop).resize((GHEP_DAU_NUA, GHEP_DAU_NUA), Image.Resampling.LANCZOS)


def _mat_ghep(cau_hinh: dict, nham: bool) -> Image.Image:
    anh, d = _vung_dau()
    for dau in (-1, 1):
        x, y = HX + dau * 85, HY - 20
        if nham:
            _net(d, [(x - 40, y + 4), (x + 40, y + 4)], 16)
        else:
            _mat(d, x, y, cau_hinh["mat"], cau_hinh["nhin"])
    _may(d, cau_hinh["may"])
    _ve_them(d, cau_hinh["them"])
    return _cat_dau(anh)


def _mieng_ghep(kieu: str) -> Image.Image:
    anh, d = _vung_dau()
    x, y = HX, HY + 100
    if kieu == "dong":
        _net(d, [(x - 45, y + 30), (x + 45, y + 30)], 16)
    elif kieu == "ha-nho":
        d.ellipse((x - 34, y, x + 34, y + 56), fill=DEN)
    elif kieu == "ha-to":
        d.ellipse((x - 58, y - 24, x + 58, y + 80), fill=DEN)
        d.chord((x - 34, y + 30, x + 34, y + 74), 0, 180, fill=DO)
    else:
        _mieng(d, kieu)
    return _cat_dau(anh)


def tao_nhan_vat_ghep_tam(kho: Path, ten: str = "max", ghi_de: bool = False) -> list[Path]:
    """Vẽ nhân vật ghép tạm vào kho/nhan-vat-ghep/<ten>/ (bộ phận + mắt mọi biểu cảm + mắt nhắm + 3 miệng
    + khung.json). Tệp đã có giữ nguyên trừ khi ghi_de. Trả danh sách tệp ĐÃ ghi."""
    import json

    from .nhan_vat_ghep import TU_THE_GHEP

    goc = Path(kho) / "nhan-vat-ghep" / ten
    da_ghi: list[Path] = []

    def luu(rel: str, anh: Image.Image) -> None:
        p = goc / rel
        if ghi_de or not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            anh.save(p, "PNG")
            da_ghi.append(p)

    # thân: khớp gốc ở HÔNG (dưới), cổ ở trên
    than, than_tren, than_duoi = _doan_ghep(GHEP_THAN)
    vai = (than_tren[0], than_tren[1] + GHEP_VAI)
    luu("than.png", than)
    # đầu (+ phụ kiện nhân vật phụ): khớp ở cổ, 110px dưới tâm đầu
    anh, d = _vung_dau()
    d.ellipse((HX - HR, HY - HR, HX + HR, HY + HR), fill=_mau_dau(ten), outline=DEN, width=NET)
    _ve_phu_kien(d, ten)
    luu("dau.png", _cat_dau(anh))
    khop_dau = (GHEP_DAU_NUA // 2, GHEP_DAU_NUA // 2 + 110)

    tay_tren, tt_tren, tt_duoi = _doan_ghep(GHEP_TAY_TREN)
    tay_duoi, td_tren, _ = _doan_ghep(GHEP_TAY_DUOI, r_cuoi=15)  # bàn tay = chấm tròn to hơn
    chan_tren, ct_tren, ct_duoi = _doan_ghep(GHEP_CHAN)
    chan_duoi, cd_tren, cd_duoi = _doan_ghep(GHEP_CHAN)
    for ben in ("trai", "phai"):
        luu(f"tay-{ben}-tren.png", tay_tren)
        luu(f"tay-{ben}-duoi.png", tay_duoi)
        luu(f"chan-{ben}-tren.png", chan_tren)
        luu(f"chan-{ben}-duoi.png", chan_duoi)

    for bc, ch in BIEU_CAM.items():
        luu(f"mat/{bc}.png", _mat_ghep(ch, False))
        luu(f"mat/{bc}__nham.png", _mat_ghep(ch, True))
        luu(f"mieng/{bc}.png", _mieng_ghep(ch["mieng"]))
    luu("mat/nham.png", _mat_ghep({"mat": "cham", "nhin": (0, 0), "may": None, "them": None}, True))
    for kieu in ("dong", "ha-nho", "ha-to"):
        luu(f"mieng/{kieu}.png", _mieng_ghep(kieu))

    dung = TU_THE_GHEP["dung"]

    def bp(ten_bp, cha, khop, gan, lop, dau_mut=None):
        m = {"ten": ten_bp, "tep": f"{ten_bp}.png", "cha": cha, "khop": list(khop), "gan": list(gan),
             "lop": lop, "goc": dung.get(ten_bp, 0.0)}
        if dau_mut is not None:
            m["dau_mut"] = list(dau_mut)
        return m

    bo_phan = [bp("than", None, than_duoi, GHEP_HONG, 2), bp("dau", "than", khop_dau, than_tren, 3)]
    for ben in ("trai", "phai"):
        bo_phan += [
            bp(f"chan-{ben}-tren", "than", ct_tren, than_duoi, 1),
            bp(f"chan-{ben}-duoi", f"chan-{ben}-tren", cd_tren, ct_duoi, 1, (cd_duoi[0], cd_duoi[1] + GHEP_R)),
            bp(f"tay-{ben}-tren", "than", tt_tren, vai, 4),
            bp(f"tay-{ben}-duoi", f"tay-{ben}-tren", td_tren, tt_duoi, 5),
        ]
    khung = {
        "_ghi_chu": "Sinh bởi `nq hinh-tam` (ảnh tạm). Lược đồ: docs/10-NHAN-VAT-GHEP.md.",
        "ten": ten,
        "kich_thuoc": [CO, CO],
        "bieu_cam": "vui",
        "cham_dat": ["chan-trai-duoi", "chan-phai-duoi"],
        "mat": {"bo_phan": "dau", "khop": [0, 0], "gan": [0, 0]},
        "bo_phan": bo_phan,
        "tu_the": {},
    }
    p = goc / "khung.json"
    if ghi_de or not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(khung, ensure_ascii=False, indent=2), encoding="utf-8")
        da_ghi.append(p)
    return da_ghi


# ---------------------------------------------------------------- hàm chính


def tao_bo_hinh_tam(kho: Path, ghi_de: bool = False) -> list[Path]:
    """Vẽ bộ hình + SFX tạm vào `kho` (thường là kho-mau/). Trả danh sách tệp ĐÃ ghi.

    Tệp đã tồn tại được giữ nguyên trừ khi `ghi_de=True`.
    """
    kho = Path(kho)
    da_ghi: list[Path] = []

    def can_ghi(p: Path) -> bool:
        return ghi_de or not p.exists()

    to_hop = [("max", bc, tt) for bc in BIEU_CAM for tt in TU_THE]
    for ten_nv, (ds_bc, ds_tt) in NHAN_VAT_PHU.items():
        to_hop += [(ten_nv, bc, tt) for bc in ds_bc for tt in ds_tt]
    for i, (ten_nv, bieu_cam, tu_the) in enumerate(to_hop, 1):
        p = kho / "nhan-vat" / f"{ten_nv}__{bieu_cam}__{tu_the}.png"
        if can_ghi(p):
            _luu_anh(_ve_nhan_vat(bieu_cam, tu_the, ten_nv), p)
            da_ghi.append(p)
        if i % 20 == 0 or i == len(to_hop):
            print(f"  Nhân vật: {i}/{len(to_hop)}", flush=True)

    for ten_nv in ("max", *NHAN_VAT_PHU):  # nhân vật ghép bộ phận (docs/10)
        da_ghi += tao_nhan_vat_ghep_tam(kho, ten_nv, ghi_de)
    print("  Nhân vật ghép: " + ", ".join(("max", *NHAN_VAT_PHU)), flush=True)

    for ten, (bieu_cam, tu_the, lat, nhin) in DAM_DONG.items():
        p = kho / "nhan-vat" / f"{ten}.png"
        if can_ghi(p):
            anh = _ve_dam_dong(bieu_cam, tu_the, lat, nhin)
            p.parent.mkdir(parents=True, exist_ok=True)
            anh.resize((anh.width // HE_SO, anh.height // HE_SO), Image.Resampling.LANCZOS).save(p, "PNG")
            da_ghi.append(p)

    for ten, ham in PHONG_NEN.items():
        p = kho / "phong-nen" / f"{ten}.png"
        if can_ghi(p):
            p.parent.mkdir(parents=True, exist_ok=True)
            ham().save(p, "PNG")
            da_ghi.append(p)

    for ten, ham in DAO_CU.items():
        p = kho / "dao-cu" / f"{ten}.png"
        if can_ghi(p):
            anh, d = _anh_moi()
            ham(d)
            _luu_anh(anh, p)
            da_ghi.append(p)

    for ten in BIEU_DO:
        p = kho / "bieu-do" / f"{ten}.png"
        if can_ghi(p):
            anh, d = _anh_moi()
            _ve_bieu_do(d, ten)
            _luu_anh(anh, p)
            da_ghi.append(p)

    rng = np.random.default_rng(7)  # cố định để chạy lại ra cùng tệp
    for ten, ham in SFX.items():
        p = kho / "am-thanh" / f"{ten}.wav"
        if can_ghi(p):
            _ghi_wav(p, ham(rng))
            da_ghi.append(p)

    return da_ghi
