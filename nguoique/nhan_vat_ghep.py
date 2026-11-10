"""Nhân vật ghép bộ phận (cut-out rig): xoay quanh khớp theo cây cha–con, tư thế, hoạt cảnh, chớp mắt, khớp miệng.

Thư mục một nhân vật: kho-mau/nhan-vat-ghep/<ten>/ (chi tiết docs/10-NHAN-VAT-GHEP.md)
  khung.json                    danh sách bộ phận + khớp
  <bo-phan>.png                 than, dau, tay-trai-tren, tay-trai-duoi, tay-phai-..., chan-...
  mat/<bieu-cam>.png            mắt + lông mày + ký hiệu của biểu cảm (lớp phủ lên đầu)
  mat/<bieu-cam>__nham.png      (tuỳ chọn) mắt nhắm khi chớp của biểu cảm đó; không có -> mat/nham.png
  mieng/<bieu-cam>.png          (tuỳ chọn) miệng khi im của biểu cảm; không có -> mieng/dong.png
  mieng/dong.png | ha-nho.png | ha-to.png   miệng khi nói

Quy ước:
- Góc tính bằng độ, DƯƠNG = ngược chiều kim đồng hồ trên màn hình (như Image.rotate). Góc của bộ phận
  con là góc TƯƠNG ĐỐI với cha. Góc 0 = bộ phận đúng như vẽ trong PNG (tay / chân buông thẳng xuống,
  thân thẳng đứng, đầu thẳng).
- Trái / phải = theo NGƯỜI XEM (tay-phai là cánh tay bên phải khung hình).
- Toạ độ trong khung.json = pixel của chính ảnh PNG đó; gốc cây ('cha' = null) có 'gan' = vị trí khớp
  trong khung tham chiếu 'kich_thuoc' (cùng cỡ ảnh nhân vật tĩnh 1024x1024, nên 'co' dùng như lớp ảnh).

Module này không phụ thuộc dung_hinh / kichban (để kichban nhập được tên tư thế, không vòng nhập).
"""

from __future__ import annotations

import bisect
import json
import math
import random
import sys
from collections import OrderedDict, namedtuple
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

BICUBIC = Image.Resampling.BICUBIC
LANCZOS = Image.Resampling.LANCZOS

NHIP_HINH_MAC_DINH = 15          # tư thế cập nhật 15 lần/giây (máy quay vẫn 30 fps)
NHIP_BAO = 15                    # đường bao âm lượng: RMS mỗi 1/15 s
THOI_GIAN_NHAM = 0.12            # mắt nhắm khi chớp
KHOANG_CHOP = (2.5, 5.0)         # giây giữa hai lần chớp
CHU_KY_DI = 1.0                  # giây cho 4 hình di-bo-1..4 (2 bước)
THOI_GIAN_VAO_DI = 0.2           # trộn dần vào / ra chu kỳ đi
CHU_KY_MIENG = 0.56              # mở-đóng khi nói mà không có bao giọng (đo video 03/04)
GIU_MIENG_TOI_THIEU = 0.15       # mỗi hình miệng giữ tối thiểu chừng này giây
NGUONG_MIENG = (0.18, 0.55)      # tỉ lệ RMS / mức tham chiếu: < a đóng, < b hé, còn lại há to
MIENG = ("dong", "ha-nho", "ha-to")

BO_PHAN_CHUAN = ("than", "dau", "tay-trai-tren", "tay-trai-duoi", "tay-phai-tren", "tay-phai-duoi",
                 "chan-trai-tren", "chan-trai-duoi", "chan-phai-tren", "chan-phai-duoi")

# ---------------- thư viện tư thế (góc tương đối, độ) ----------------
_DUNG = {"than": 0.0, "dau": 0.0,
         "tay-trai-tren": -28.0, "tay-trai-duoi": 10.0, "tay-phai-tren": 28.0, "tay-phai-duoi": -10.0,
         "chan-trai-tren": -12.0, "chan-trai-duoi": 0.0, "chan-phai-tren": 12.0, "chan-phai-duoi": 0.0}


def _tt(**sua) -> dict[str, float]:
    kq = dict(_DUNG)
    kq.update({k.replace("_", "-"): float(v) for k, v in sua.items()})
    return kq


# Đi bộ thiết kế cho hướng sang PHẢI; đi sang trái thì tự lật gương.
TU_THE_GHEP: dict[str, dict[str, float]] = {
    "dung": dict(_DUNG),
    "chi-tay-phai": _tt(tay_phai_tren=100, tay_phai_duoi=4, dau=-4),
    "chi-tay-trai": _tt(tay_trai_tren=-100, tay_trai_duoi=-4, dau=4),
    "om-dau": _tt(tay_trai_tren=-104, tay_trai_duoi=-83, tay_phai_tren=104, tay_phai_duoi=83),
    "gio-hai-tay": _tt(tay_trai_tren=-150, tay_trai_duoi=-10, tay_phai_tren=150, tay_phai_duoi=10),
    "nhun-vai": _tt(tay_trai_tren=-50, tay_trai_duoi=-95, tay_phai_tren=50, tay_phai_duoi=95, dau=6),
    "khoanh-tay": _tt(tay_trai_tren=-12, tay_trai_duoi=97, tay_phai_tren=12, tay_phai_duoi=-107),
    "vay-tay": _tt(tay_phai_tren=125, tay_phai_duoi=35, dau=-3),
    "suy-nghi-tay-cam": _tt(tay_phai_tren=104, tay_phai_duoi=155, tay_trai_tren=-20, tay_trai_duoi=8, dau=6),
    "di-bo-1": _tt(than=-3, tay_trai_tren=22, tay_trai_duoi=18, tay_phai_tren=-22, tay_phai_duoi=10,
                   chan_trai_tren=-24, chan_trai_duoi=-10, chan_phai_tren=26, chan_phai_duoi=4),
    "di-bo-2": _tt(than=-2, tay_trai_tren=4, tay_trai_duoi=12, tay_phai_tren=-4, tay_phai_duoi=12,
                   chan_phai_tren=-4, chan_phai_duoi=0, chan_trai_tren=14, chan_trai_duoi=-38),
    "di-bo-3": _tt(than=-3, tay_phai_tren=22, tay_phai_duoi=18, tay_trai_tren=-22, tay_trai_duoi=10,
                   chan_phai_tren=-24, chan_phai_duoi=-10, chan_trai_tren=26, chan_trai_duoi=4),
    "di-bo-4": _tt(than=-2, tay_phai_tren=4, tay_phai_duoi=12, tay_trai_tren=-4, tay_trai_duoi=12,
                   chan_trai_tren=-4, chan_trai_duoi=0, chan_phai_tren=14, chan_phai_duoi=-38),
}
# Dao động lặp khi đang ở tư thế: bộ phận -> (biên độ độ, chu kỳ giây)
DAO_DONG: dict[str, dict[str, tuple[float, float]]] = {"vay-tay": {"tay-phai-duoi": (18.0, 0.5)}}
DI_BO = ("di-bo-1", "di-bo-2", "di-bo-3", "di-bo-4")

_da_bao: set[str] = set()


def _bao_mot_lan(khoa: str, thong_diep: str) -> None:
    if khoa not in _da_bao:
        _da_bao.add(khoa)
        print(f"\nCẢNH BÁO: {thong_diep}", file=sys.stderr)


# ---------------- easing ----------------
def _kep(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def _ra(p: float) -> float:
    p = _kep(p)
    return 1.0 - (1.0 - p) ** 3


def _vao_ra(p: float) -> float:
    p = _kep(p)
    return p * p * (3.0 - 2.0 * p)


def _nay(p: float, s: float = 1.70158) -> float:
    p = _kep(p)
    q = p - 1.0
    return 1.0 + (s + 1.0) * q ** 3 + s * q ** 2


EASING_HAM = {"ra": _ra, "vao-ra": _vao_ra, "nay": _nay}


def lam_muot(ten: str | None, p: float) -> float:
    """ra = ease-out (cubic), vao-ra = ease-in-out, nay = ease-out-back (vượt nhẹ rồi về)."""
    return EASING_HAM.get(ten or "ra", _ra)(p)


def buoc_hinh(t: float, nhip: float | None) -> float:
    """Lượng tử thời gian theo nhịp hoạt hình (vd. 15 -> mỗi 1/15 s). nhip 0/None = mượt."""
    if not nhip or nhip <= 0:
        return t
    return math.floor(t * nhip + 1e-6) / nhip


def xoay_vec(vx: float, vy: float, goc_do: float) -> tuple[float, float]:
    """Xoay vector (toạ độ màn hình, y hướng xuống) NGƯỢC chiều kim đồng hồ `goc_do` độ — khớp Image.rotate."""
    r = math.radians(goc_do)
    c, s = math.cos(r), math.sin(r)
    return vx * c + vy * s, -vx * s + vy * c


# ---------------- hoạt cảnh (hàm thuần, test được không cần ảnh) ----------------
def tu_the_day_du(ten: str, thu_vien: dict | None = None, mac_dinh: dict | None = None) -> dict[str, float]:
    thu_vien = thu_vien if thu_vien is not None else TU_THE_GHEP
    tt = thu_vien.get(ten)
    if tt is None:
        _bao_mot_lan(f"tu-the:{ten}", f"tư thế '{ten}' không có trong thư viện (docs/10-NHAN-VAT-GHEP.md) "
                                      "hoặc khung.json — dùng 'dung'.")
        tt = thu_vien.get("dung", _DUNG)
    kq = dict(mac_dinh or {})
    kq.update(tt)
    return kq


def _theo_luc(ds) -> list:
    return sorted((m for m in ds or [] if isinstance(m, dict)), key=lambda m: float(m.get("luc") or 0.0))


def goc_tai(lop: dict, t: float, thu_vien: dict | None = None, mac_dinh: dict | None = None) -> dict[str, float]:
    """Góc mọi bộ phận ở giây t của cảnh: tư thế gốc rồi lần lượt nội suy tới tư thế của từng dong_tac."""
    goc_tt = lop.get("tu_the") or "dung"
    cur = tu_the_day_du(goc_tt, thu_vien, mac_dinh)
    bien = {k: a for k, (a, _) in DAO_DONG.get(goc_tt, {}).items()}
    chu_ky = {k: T for k, (_, T) in DAO_DONG.get(goc_tt, {}).items()}
    for m in _theo_luc(lop.get("dong_tac")):
        ten = m.get("tu_the")
        if not ten:
            continue
        luc = float(m.get("luc") or 0.0)
        if t < luc:
            break
        tl = m.get("thoi_luong")
        tl = 0.7 if tl is None else float(tl)
        e = 1.0 if tl <= 0 else lam_muot(m.get("easing"), (t - luc) / tl)
        dich = tu_the_day_du(ten, thu_vien, mac_dinh)
        cur = {k: cur.get(k, 0.0) + (dich.get(k, 0.0) - cur.get(k, 0.0)) * e for k in set(cur) | set(dich)}
        dao = DAO_DONG.get(ten, {})
        bien = {k: bien.get(k, 0.0) + ((dao[k][0] if k in dao else 0.0) - bien.get(k, 0.0)) * e
                for k in set(bien) | set(dao)}
        for k, (_, T) in dao.items():
            chu_ky[k] = T
    for k, a in bien.items():
        if abs(a) > 1e-6:
            cur[k] = cur.get(k, 0.0) + a * math.sin(2.0 * math.pi * t / max(0.05, chu_ky.get(k, 0.5)))
    return cur


def bieu_cam_tai(lop: dict, t: float, mac_dinh: str = "vui") -> str:
    bc = lop.get("bieu_cam") or mac_dinh
    for m in _theo_luc(lop.get("dong_tac")):
        if float(m.get("luc") or 0.0) > t:
            break
        if m.get("bieu_cam"):
            bc = m["bieu_cam"]
    return bc


def vi_tri_tai(lop: dict, t: float) -> tuple[float, float, float, float, bool | None]:
    """-> (x, y chuẩn hoá, trọng số chu kỳ đi 0..1, pha chu kỳ 0..1, đi sang trái? | None khi không đi)."""
    vt = lop.get("vi_tri") or [0.5, 0.5]
    di = lop.get("di")
    if not di:
        return float(vt[0]), float(vt[1]), 0.0, 0.0, None
    tu, den = di.get("tu") or vt, di.get("den") or vt
    luc = float(di.get("luc") or 0.0)
    tl = max(1e-6, float(di.get("thoi_luong") or 2.0))
    p = _kep((t - luc) / tl)
    x = tu[0] + (den[0] - tu[0]) * p
    y = tu[1] + (den[1] - tu[1]) * p
    w, pha = 0.0, 0.0
    if luc <= t < luc + tl:
        w = _kep(min((t - luc) / THOI_GIAN_VAO_DI, (luc + tl - t) / THOI_GIAN_VAO_DI))
        pha = ((t - luc) / max(0.2, float(di.get("chu_ky") or CHU_KY_DI))) % 1.0
    return float(x), float(y), w, pha, den[0] < tu[0]


def goc_di_bo(pha: float, thu_vien: dict | None = None, mac_dinh: dict | None = None) -> dict[str, float]:
    """Chu kỳ 4 hình di-bo-1..4, nội suy ease-in-out giữa hai hình liền nhau."""
    x = (pha % 1.0) * 4.0
    k = int(x) % 4
    e = _vao_ra(x - math.floor(x))
    a = tu_the_day_du(DI_BO[k], thu_vien, mac_dinh)
    b = tu_the_day_du(DI_BO[(k + 1) % 4], thu_vien, mac_dinh)
    return {ten: a.get(ten, 0.0) + (b.get(ten, 0.0) - a.get(ten, 0.0)) * e for ten in set(a) | set(b)}


def tron_goc(a: dict, b: dict, w: float) -> dict[str, float]:
    kq = dict(a)
    for k, v in b.items():
        kq[k] = a.get(k, v) + (v - a.get(k, v)) * w
    return kq


def lich_chop_mat(hat_giong: str, dai: float) -> list[float]:
    """Mốc bắt đầu chớp (giây trong cảnh) — ngẫu nhiên nhưng cố định theo hạt giống (id cảnh | lớp)."""
    rng = random.Random(f"chop|{hat_giong}")
    t = rng.uniform(0.6, KHOANG_CHOP[0])
    ds: list[float] = []
    while t < dai:
        ds.append(t)
        t += rng.uniform(*KHOANG_CHOP)
    return ds


def dang_nham(lich: list[float], t: float, dai_nham: float = THOI_GIAN_NHAM) -> bool:
    i = bisect.bisect_right(lich, t) - 1
    return i >= 0 and t < lich[i] + dai_nham


def tinh_bao_giong(mau: np.ndarray, tan_so: int, nhip: int = NHIP_BAO) -> np.ndarray:
    """RMS mỗi 1/nhip giây (float32)."""
    x = np.asarray(mau, dtype=np.float32).reshape(-1)
    buoc = max(1, int(round(tan_so / float(nhip))))
    n = int(math.ceil(x.size / buoc))
    if n == 0:
        return np.zeros(0, dtype=np.float32)
    dem = np.zeros(n * buoc, dtype=np.float32)
    dem[: x.size] = x
    return np.sqrt(np.mean(dem.reshape(n, buoc) ** 2, axis=1)).astype(np.float32)


def bao_giong_tu_tep(tep, nhip: int = NHIP_BAO, tan_so: int = 16000) -> np.ndarray:
    """Đọc tệp giọng (qua ffmpeg, am_thanh_io.giai_ma) -> đường bao RMS."""
    from .am_thanh_io import giai_ma

    return tinh_bao_giong(giai_ma(tep, tan_so), tan_so, nhip)


def muc_tham_chieu(bao) -> float:
    if bao is None:
        return 0.0
    v = np.asarray(bao, dtype=np.float32)
    v = v[v > 1e-4]
    return float(np.percentile(v, 90)) if v.size else 0.0


def chon_mieng(bao, t_giong: float, ref: float | None = None, nhip: int = NHIP_BAO) -> str:
    """Hình miệng theo RMS tại t_giong (giây tính từ lúc giọng bắt đầu). Không giữ tối thiểu — xem trang_thai_mieng."""
    if bao is None or len(bao) == 0 or t_giong < 0:
        return "dong"
    i = int(t_giong * nhip)
    if i >= len(bao):
        return "dong"
    ref = muc_tham_chieu(bao) if ref is None else ref
    if ref <= 0:
        return "dong"
    r = float(bao[i]) / ref
    return "dong" if r < NGUONG_MIENG[0] else "ha-nho" if r < NGUONG_MIENG[1] else "ha-to"


def trang_thai_mieng(bao, nhip: int = NHIP_BAO, giu: float = GIU_MIENG_TOI_THIEU) -> list[str]:
    """Hình miệng từng ô 1/nhip của bao giọng, mỗi hình giữ tối thiểu `giu` giây cho đỡ giật."""
    if bao is None or len(bao) == 0:
        return []
    ref = muc_tham_chieu(bao)
    tho = [chon_mieng(bao, (i + 0.5) / nhip, ref, nhip) for i in range(len(bao))]
    toi_thieu = max(1, int(math.ceil(giu * nhip - 1e-9)))
    kq: list[str] = []
    hien, con = tho[0], 0
    for s in tho:
        if s != hien and con >= toi_thieu:
            hien, con = s, 0
        kq.append(hien)
        con += 1
    return kq


def mieng_chu_ky(t_giong: float, chu_ky: float = CHU_KY_MIENG) -> str:
    """Không có bao giọng: mở nửa chu kỳ, đóng nửa chu kỳ (~0,56 s); lần mở xen hé / há to."""
    if t_giong < 0:
        return "dong"
    n = int(t_giong / chu_ky)
    if (t_giong - n * chu_ky) >= chu_ky / 2.0:
        return "dong"
    return "ha-to" if n % 3 == 1 else "ha-nho"


# ---------------- nhân vật ----------------
class LoiNhanVatGhep(ValueError):
    """khung.json sai / thiếu: thông điệp tiếng Việt kèm cách sửa."""


class _LRU:
    def __init__(self, toi_da: int) -> None:
        self.d: OrderedDict = OrderedDict()
        self.toi_da = toi_da

    def lay(self, k):
        v = self.d.get(k)
        if v is not None:
            self.d.move_to_end(k)
        return v

    def dat(self, k, v):
        self.d[k] = v
        self.d.move_to_end(k)
        while len(self.d) > self.toi_da:
            self.d.popitem(last=False)
        return v


class BoPhan:
    __slots__ = ("ten", "tep", "cha", "khop", "gan", "lop", "goc", "dau_mut")

    def __init__(self, ten, tep, cha, khop, gan, lop, goc, dau_mut) -> None:
        self.ten, self.tep, self.cha = ten, tep, cha
        self.khop, self.gan, self.lop, self.goc, self.dau_mut = khop, gan, lop, goc, dau_mut


# Thông số ảnh đã thu theo tỉ lệ: ảnh (None nếu thiếu), tỉ lệ thật theo trục, cỡ gốc, cỡ đã thu
_ThongSo = namedtuple("_ThongSo", "anh sx sy w_o h_o w_s h_s")
# Biến đổi thế giới của một bộ phận: vị trí khớp (px khung), góc vẽ (lượng tử 1°), góc thật, ...
_TheGioi = namedtuple("_TheGioi", "px py gq g_that sx sy kx ky w_o w_s h_s")


def _diem2(v, ten: str, cho: str, mac_dinh=None) -> tuple[float, float]:
    if v is None and mac_dinh is not None:
        return mac_dinh
    if not (isinstance(v, (list, tuple)) and len(v) == 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)):
        raise LoiNhanVatGhep(f"{cho}: '{ten}' phải là [x, y] (pixel trong ảnh), nhận {v!r}.")
    return float(v[0]), float(v[1])


class NhanVatGhep:
    """Một nhân vật ghép nạp từ thư mục có khung.json. Ảnh bộ phận nạp lười, ảnh xoay đệm theo góc 1°."""

    def __init__(self, thu_muc) -> None:
        self.thu_muc = Path(thu_muc)
        tep = self.thu_muc / "khung.json"
        cach_sua = "Cách sửa: chạy `nq hinh-tam` để tạo nhân vật tạm, hoặc xem docs/10-NHAN-VAT-GHEP.md."
        try:
            du = json.loads(tep.read_text(encoding="utf-8-sig"))
        except FileNotFoundError:
            raise LoiNhanVatGhep(f"thiếu '{tep}'. {cach_sua}") from None
        except json.JSONDecodeError as e:
            raise LoiNhanVatGhep(f"'{tep}': JSON sai ở dòng {e.lineno}, cột {e.colno}: {e.msg}. {cach_sua}") from None
        if not isinstance(du, dict):
            raise LoiNhanVatGhep(f"'{tep}': gốc phải là đối tượng JSON. {cach_sua}")
        self.ten = str(du.get("ten") or self.thu_muc.name)
        kt = _diem2(du.get("kich_thuoc"), "kich_thuoc", str(tep), (1024.0, 1024.0))
        if kt[0] <= 0 or kt[1] <= 0:
            raise LoiNhanVatGhep(f"'{tep}': 'kich_thuoc' phải dương.")
        self.kich_thuoc = kt
        self.bieu_cam_mac_dinh = str(du.get("bieu_cam") or "vui")

        ds = du.get("bo_phan")
        if not isinstance(ds, list) or not ds:
            raise LoiNhanVatGhep(f"'{tep}': 'bo_phan' phải là danh sách có ít nhất một bộ phận. {cach_sua}")
        self.bo_phan: dict[str, BoPhan] = {}
        for i, m in enumerate(ds):
            cho = f"{tep} bo_phan[{i}]"
            if not isinstance(m, dict) or not isinstance(m.get("ten"), str) or not isinstance(m.get("tep"), str):
                raise LoiNhanVatGhep(f"{cho}: cần {{\"ten\", \"tep\", \"cha\", \"khop\", \"gan\", \"lop\", \"goc\"}}.")
            ten = m["ten"]
            if ten in self.bo_phan:
                raise LoiNhanVatGhep(f"{cho}: tên bộ phận '{ten}' bị trùng.")
            cha = m.get("cha")
            if cha is not None and not isinstance(cha, str):
                raise LoiNhanVatGhep(f"{cho}: 'cha' phải là tên bộ phận hoặc null.")
            lop = m.get("lop", i)
            goc = m.get("goc", 0.0)
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (lop, goc)):
                raise LoiNhanVatGhep(f"{cho}: 'lop' và 'goc' phải là số.")
            dm = m.get("dau_mut")
            self.bo_phan[ten] = BoPhan(ten, m["tep"], cha or None, _diem2(m.get("khop"), "khop", cho, (0.0, 0.0)),
                                       _diem2(m.get("gan"), "gan", cho, (0.0, 0.0)), float(lop), float(goc),
                                       None if dm is None else _diem2(dm, "dau_mut", cho))
        # thứ tự cây: cha trước con; báo lỗi cha lạ / vòng
        self.thu_tu: list[str] = []
        da: set[str] = set()
        con_lai = list(self.bo_phan)
        while con_lai:
            them = [t for t in con_lai if self.bo_phan[t].cha is None or self.bo_phan[t].cha in da]
            if not them:
                bp = self.bo_phan[con_lai[0]]
                ly_do = "không có" if bp.cha not in self.bo_phan else "tạo vòng"
                raise LoiNhanVatGhep(f"'{tep}': bộ phận '{bp.ten}' có cha '{bp.cha}' {ly_do}.")
            for t in them:
                self.thu_tu.append(t)
                da.add(t)
                con_lai.remove(t)
        self.goc_mac_dinh = {t: bp.goc for t, bp in self.bo_phan.items()}

        rieng = du.get("tu_the") or {}
        self.thu_vien = dict(TU_THE_GHEP)
        if isinstance(rieng, dict):
            for ten, g in rieng.items():
                if str(ten).startswith("_"):
                    continue
                if not isinstance(g, dict):
                    raise LoiNhanVatGhep(f"'{tep}': tư thế '{ten}' phải là {{bộ phận: góc}}.")
                self.thu_vien[str(ten)] = {**_DUNG, **{str(k): float(v) for k, v in g.items()
                                                      if isinstance(v, (int, float)) and not isinstance(v, bool)}}
        self.cham_dat = [t for t in du.get("cham_dat") or [] if t in self.bo_phan and self.bo_phan[t].dau_mut]

        def gan_phu(v):
            v = v if isinstance(v, dict) else {}
            cha = v.get("bo_phan") or ("dau" if "dau" in self.bo_phan else self.thu_tu[0])
            if cha not in self.bo_phan:
                raise LoiNhanVatGhep(f"'{tep}': lớp mặt gắn vào bộ phận lạ '{cha}'.")
            return cha, _diem2(v.get("khop"), "khop", str(tep), (0.0, 0.0)), _diem2(v.get("gan"), "gan", str(tep), (0.0, 0.0))

        self.gan_mat = gan_phu(du.get("mat"))
        self.gan_mieng = gan_phu(du.get("mieng") if isinstance(du.get("mieng"), dict) else du.get("mat"))
        self._anh: dict[str, Image.Image | None] = {}
        self._co: dict[str, bool] = {}
        self._ti_le = _LRU(400)
        self._xoay = _LRU(1500)
        self._nen_dat: float | None = None

    # ---- tệp ----
    def co_tep(self, rel: str) -> bool:
        v = self._co.get(rel)
        if v is None:
            v = self._co[rel] = (self.thu_muc / rel).is_file()
        return v

    def anh_goc(self, rel: str) -> Image.Image | None:
        if rel in self._anh:
            return self._anh[rel]
        p = self.thu_muc / rel
        im = None
        try:
            with Image.open(p) as f:
                f.load()
                im = f.convert("RGBA")
        except FileNotFoundError:
            _bao_mot_lan(f"ghep:{p}", f"nhân vật ghép '{self.ten}' thiếu ảnh '{p}' — bỏ qua bộ phận này.")
        except OSError as e:
            _bao_mot_lan(f"ghep:{p}", f"không mở được '{p}' ({e}) — bỏ qua bộ phận này.")
        self._anh[rel] = im
        return im

    def tep_mat(self, bieu_cam: str, nham: bool) -> str | None:
        if nham:
            for rel in (f"mat/{bieu_cam}__nham.png", "mat/nham.png"):
                if self.co_tep(rel):
                    return rel
        rel = f"mat/{bieu_cam}.png"
        if self.co_tep(rel):
            return rel
        _bao_mot_lan(f"ghep-mat:{self.ten}:{bieu_cam}", f"nhân vật ghép '{self.ten}' thiếu '{self.thu_muc / rel}' — "
                                                        "vẽ không có mắt. Cách sửa: thêm ảnh mắt của biểu cảm này.")
        return None

    def tep_mieng(self, bieu_cam: str, trang: str) -> str | None:
        if trang != "dong" and self.co_tep(f"mieng/{trang}.png"):
            return f"mieng/{trang}.png"
        for rel in (f"mieng/{bieu_cam}.png", "mieng/dong.png"):
            if self.co_tep(rel):
                return rel
        return None

    def goc_tu_the(self, ten: str) -> dict[str, float]:
        return tu_the_day_du(ten, self.thu_vien, self.goc_mac_dinh)

    # ---- ảnh theo tỉ lệ / xoay (đệm) ----
    def _thong_so(self, rel: str, s: float, lat: bool) -> _ThongSo:
        khoa = (rel, int(round(s * 2000)), lat)
        v = self._ti_le.lay(khoa)
        if v is None:
            g = self.anh_goc(rel)
            if g is None:
                v = _ThongSo(None, s, s, 0, 0, 0, 0)
            else:
                w, h = max(1, int(round(g.width * s))), max(1, int(round(g.height * s)))
                im = g if (w, h) == g.size else g.resize((w, h), LANCZOS if w < g.width else BICUBIC)
                if lat:
                    im = ImageOps.mirror(im)
                v = _ThongSo(im, w / g.width, h / g.height, g.width, g.height, w, h)
            self._ti_le.dat(khoa, v)
        return v

    def _anh_xoay(self, rel: str, s: float, lat: bool, gq: int) -> Image.Image | None:
        gq = gq % 360
        khoa = (rel, int(round(s * 2000)), lat, gq)
        im = self._xoay.lay(khoa)
        if im is None:
            g = self._thong_so(rel, s, lat).anh
            if g is None:
                return None
            im = g if gq == 0 else g.rotate(gq, resample=BICUBIC, expand=True)
            self._xoay.dat(khoa, im)
        return im

    # ---- hình học ----
    @staticmethod
    def _diem(c: _TheGioi, q, lat: bool) -> tuple[float, float]:
        """Điểm q (pixel ảnh gốc của bộ phận c) -> toạ độ khung hình."""
        qx = (c.w_o - q[0]) if lat else q[0]
        rx, ry = xoay_vec((qx - c.kx) * c.sx, (q[1] - c.ky) * c.sy, c.gq)
        return c.px + rx, c.py + ry

    def cay(self, goc: dict, s: float, lat: bool = False, x0: float = 0.0, y0: float = 0.0) -> dict[str, _TheGioi]:
        """Biến đổi thế giới mọi bộ phận. (x0, y0) = góc trên trái khung tham chiếu trên khung hình."""
        tg: dict[str, _TheGioi] = {}
        for ten in self.thu_tu:
            bp = self.bo_phan[ten]
            g = float(goc.get(ten, bp.goc))
            if lat:
                g = -g
            ts = self._thong_so(bp.tep, s, lat)
            if bp.cha is None:
                gx = (self.kich_thuoc[0] - bp.gan[0]) if lat else bp.gan[0]
                px, py = x0 + gx * s, y0 + bp.gan[1] * s
                g_that = g
            else:
                c = tg[bp.cha]
                px, py = self._diem(c, bp.gan, lat)
                g_that = c.g_that + g
            kx = (ts.w_o - bp.khop[0]) if lat else bp.khop[0]
            tg[ten] = _TheGioi(px, py, int(round(g_that)), g_that, ts.sx, ts.sy, kx, bp.khop[1], ts.w_o, ts.w_s, ts.h_s)
        return tg

    def nen_dat(self) -> float:
        """Toạ độ y (pixel khung tham chiếu) của mặt đất ở tư thế 'dung'; không khai 'cham_dat' -> đáy khung."""
        if self._nen_dat is None:
            if not self.cham_dat:
                self._nen_dat = self.kich_thuoc[1]
            else:
                tg = self.cay(self.goc_tu_the("dung"), 1.0)
                self._nen_dat = max(self._diem(tg[t], self.bo_phan[t].dau_mut, False)[1] for t in self.cham_dat)
        return self._nen_dat

    def bo_tri(self, goc: dict, s: float, lat: bool, x0: float, y0: float, mat: str | None = None,
               mieng: str | None = None, cham_dat: bool = True) -> list[tuple[Image.Image, float, float]]:
        """-> [(ảnh RGBA đã xoay, x, y góc trên trái trên khung hình)] theo thứ tự vẽ (lớp dưới trước).

        cham_dat: dịch cả người để bàn chân thấp nhất chạm mặt đất của tư thế đứng (đi bộ tự nhún).
        """
        tg = self.cay(goc, s, lat, x0, y0)
        muc = [(self.bo_phan[t].lop, i, self.bo_phan[t].tep, tg[t]) for i, t in enumerate(self.thu_tu)]
        n = len(muc)
        for j, (rel, (cha, khop, gan)) in enumerate(((mat, self.gan_mat), (mieng, self.gan_mieng))):
            if not rel or cha not in tg or not self.co_tep(rel):
                continue
            c = tg[cha]
            px, py = self._diem(c, gan, lat)
            ts = self._thong_so(rel, s, lat)
            kx = (ts.w_o - khop[0]) if lat else khop[0]
            muc.append((self.bo_phan[cha].lop + 0.001 * (j + 1), n + j, rel,
                        _TheGioi(px, py, c.gq, c.g_that, ts.sx, ts.sy, kx, khop[1], ts.w_o, ts.w_s, ts.h_s)))
        dy = 0.0
        if cham_dat and self.cham_dat:
            thap = max(self._diem(tg[t], self.bo_phan[t].dau_mut, lat)[1] for t in self.cham_dat)
            dy = (y0 + self.nen_dat() * s) - thap
        ra: list[tuple[Image.Image, float, float]] = []
        for _, _, rel, c in sorted(muc, key=lambda m: (m[0], m[1])):
            im = self._anh_xoay(rel, s, lat, c.gq)
            if im is None:
                continue
            # khớp trong ảnh đã xoay: tâm ảnh xoay ↔ tâm ảnh trước khi xoay (Image.rotate expand=True)
            rx, ry = xoay_vec(c.kx * c.sx - c.w_s / 2.0, c.ky * c.sy - c.h_s / 2.0, c.gq)
            ra.append((im, c.px - (im.width / 2.0 + rx), c.py + dy - (im.height / 2.0 + ry)))
        return ra
