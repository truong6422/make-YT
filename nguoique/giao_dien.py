"""Giao diện quản trị chạy trên máy (chỉ thư viện chuẩn): `nq giao-dien` -> http://127.0.0.1:8770

Làm được từ trình duyệt: tạo dự án bằng cách DÁN kịch bản JSON (+ mô tả YouTube) đã viết sẵn, dựng nháp / bản thật,
kiểm nhịp, thumbnail, xem MP4, mô tả YouTube, đánh dấu danh sách kiểm chính sách (docs/12),
xem kho hình, tải ảnh Gemini vào kho-mau/_cho-xu-ly/ rồi tách nền, sửa config.yaml.

Mọi việc nặng chạy bằng `python -m nguoique ...` trong tiến trình con, xếp HÀNG (một việc một lúc,
vì GPU / CPU dùng chung) và đọc nhật ký qua /api/viec/<id>. Chỉ nghe 127.0.0.1.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .cauhinh import GOC, doc_cau_hinh, duong_dan, kho_mau, tep_cau_hinh

CONG_MAC_DINH = 8770
TRANG = Path(__file__).with_name("giao_dien.html")
RE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
RE_TEN_ANH = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,119}\.(png|jpg|jpeg|webp)$")
DUOI_XEM = {".mp4", ".png", ".jpg", ".jpeg", ".webp", ".srt", ".md", ".json", ".wav", ".mp3", ".ogg"}
NHOM_KHO = ("nhan-vat", "dao-cu", "bieu-do", "phong-nen", "_cho-xu-ly", "_mau-nhan-vat")
TU_MOI_PHUT = 150  # Kokoro ~150–160 từ/phút (docs/05)
NGHI_MOI_CANH = 0.35
TOI_DA_TAI_LEN = 25 * 1024 * 1024
TOI_DA_KICH_BAN = 2 * 1024 * 1024


class LoiGiaoDien(Exception):
    def __init__(self, thong_bao: str, ma: int = 400):
        super().__init__(thong_bao)
        self.ma = ma


# ---------------------------------------------------------------- dữ liệu


def thu_muc_goc_du_an(ch: dict) -> Path:
    return duong_dan(ch.get("du_an") or "du-an")


def kiem_slug(slug: str) -> str:
    if not RE_SLUG.match(slug or ""):
        raise LoiGiaoDien("Tên dự án chỉ gồm chữ thường a-z, số và dấu '-' (vd. loss-aversion).")
    return slug


def trong_thu_muc(goc: Path, rel: str) -> Path:
    """Ghép đường dẫn tương đối, chặn thoát ra ngoài `goc`."""
    p = (goc / unquote(rel)).resolve()
    goc_r = goc.resolve()
    if p != goc_r and goc_r not in p.parents:
        raise LoiGiaoDien("Đường dẫn không hợp lệ.", 403)
    return p


def _doc_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def _dem_tu(s: str) -> int:
    return len(re.findall(r"[A-Za-z0-9'’$%-]+", s or ""))


def tom_tat_kich_ban(kb: dict | None) -> dict:
    """Số cảnh, số từ, phút ước tính, số từ theo phần — đọc thô, không triển khai khuôn."""
    if not isinstance(kb, dict):
        return {"hop_le": False}
    canh = [c for c in (kb.get("canh") or []) if isinstance(c, dict)]
    tu = 0
    theo_phan: dict[str, int] = {}
    phan_hien = ""
    for c in canh:
        ts = c.get("tham_so") if isinstance(c.get("tham_so"), dict) else {}
        loi = c.get("loi") or ts.get("loi") or ""
        n = _dem_tu(str(loi))
        tu += n
        phan_hien = c.get("phan") or ts.get("phan") or phan_hien
        if phan_hien:
            theo_phan[phan_hien] = theo_phan.get(phan_hien, 0) + n
    phut = tu / TU_MOI_PHUT + len(canh) * NGHI_MOI_CANH / 60
    return {"hop_le": True, "tieu_de": kb.get("tieu_de") or "", "so_canh": len(canh), "so_tu": tu,
            "phut_uoc": round(phut, 1), "theo_phan": theo_phan}


def ds_du_an(ch: dict) -> list[dict]:
    goc = thu_muc_goc_du_an(ch)
    kq = []
    if not goc.is_dir():
        return kq
    for d in sorted(goc.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not d.is_dir() or not RE_SLUG.match(d.name):
            continue
        kb_p = d / "kich-ban.json"
        tt = tom_tat_kich_ban(_doc_json(kb_p)) if kb_p.is_file() else {"hop_le": False}
        mp4 = d / f"{d.name}.mp4"
        cs = _doc_json(d / "kiem-chinh-sach.json") or {}
        kq.append({
            "slug": d.name,
            "tieu_de": tt.get("tieu_de", ""),
            "co_kich_ban": kb_p.is_file(),
            "kich_ban_hop_le": tt.get("hop_le", False),
            "so_canh": tt.get("so_canh", 0),
            "phut_uoc": tt.get("phut_uoc", 0),
            "co_mp4": mp4.is_file(),
            "co_thumbnail": (d / "thumbnail.png").is_file(),
            "co_mo_ta": (d / "mo-ta-youtube.md").is_file(),
            "chinh_sach_xong": sum(1 for v in (cs.get("muc") or {}).values() if v),
            "sua_luc": int(d.stat().st_mtime),
        })
    return kq


def chi_tiet_du_an(ch: dict, slug: str) -> dict:
    d = thu_muc_goc_du_an(ch) / kiem_slug(slug)
    if not d.is_dir():
        raise LoiGiaoDien(f"Không có dự án '{slug}'.", 404)
    kb_p = d / "kich-ban.json"
    kb = _doc_json(kb_p) if kb_p.is_file() else None
    loi_json = None
    if kb_p.is_file() and kb is None:
        try:
            json.loads(kb_p.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            loi_json = str(e)
    canh = []
    phan_hien = ""
    for c in ((kb or {}).get("canh") or []) if isinstance(kb, dict) else []:
        if not isinstance(c, dict):
            continue
        ts = c.get("tham_so") if isinstance(c.get("tham_so"), dict) else {}
        phan_hien = c.get("phan") or ts.get("phan") or phan_hien
        canh.append({"id": c.get("id", ""), "phan": phan_hien,
                     "khuon": c.get("khuon") or "", "loi": c.get("loi") or ts.get("loi") or ""})
    tep = sorted(p.name for p in d.iterdir() if p.is_file() and p.suffix.lower() in DUOI_XEM)
    mo_ta = d / "mo-ta-youtube.md"
    return {
        "slug": slug,
        "tom_tat": tom_tat_kich_ban(kb),
        "loi_json": loi_json,
        "canh": canh,
        "tep": tep,
        "mp4": f"{slug}.mp4" if (d / f"{slug}.mp4").is_file() else None,
        "mp4_luc": int((d / f"{slug}.mp4").stat().st_mtime) if (d / f"{slug}.mp4").is_file() else 0,
        "thumb_luc": int((d / "thumbnail.png").stat().st_mtime) if (d / "thumbnail.png").is_file() else 0,
        "mo_ta": mo_ta.read_text(encoding="utf-8", errors="replace") if mo_ta.is_file() else "",
        "kich_ban_tho": kb_p.read_text(encoding="utf-8-sig", errors="replace") if kb_p.is_file() else "",
        "chinh_sach": _doc_json(d / "kiem-chinh-sach.json") or {"muc": {}, "ghi_chu": ""},
    }


def luu_chinh_sach(ch: dict, slug: str, du_lieu: dict) -> None:
    d = thu_muc_goc_du_an(ch) / kiem_slug(slug)
    if not d.is_dir():
        raise LoiGiaoDien(f"Không có dự án '{slug}'.", 404)
    muc = du_lieu.get("muc") if isinstance(du_lieu.get("muc"), dict) else {}
    sach = {"muc": {str(k)[:80]: bool(v) for k, v in list(muc.items())[:60]},
            "ghi_chu": str(du_lieu.get("ghi_chu") or "")[:4000], "luc": int(time.time())}
    (d / "kiem-chinh-sach.json").write_text(json.dumps(sach, ensure_ascii=False, indent=2), encoding="utf-8")


def luu_kich_ban_dan(ch: dict, slug: str, kich_ban: str, mo_ta: str = "", ghi_de: bool = False) -> dict:
    """Lưu kịch bản dán từ trang: kiểm JSON + lược đồ (triển khai khuôn) TRƯỚC khi ghi; bản cũ giữ ở .bak."""
    d = thu_muc_goc_du_an(ch) / kiem_slug(slug)
    dich = d / "kich-ban.json"
    if dich.exists() and not ghi_de:
        raise LoiGiaoDien(f"Dự án '{slug}' đã có kịch bản. Tick \"Ghi đè\" nếu muốn thay.", 409)
    kich_ban = (kich_ban or "").strip()
    if not kich_ban:
        raise LoiGiaoDien("Chưa dán kịch bản.")
    if kich_ban.startswith("```"):  # dán nguyên khối code từ chat
        kich_ban = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", kich_ban).strip()
    try:
        json.loads(kich_ban)
    except ValueError as e:
        raise LoiGiaoDien(f"JSON sai ở dòng {getattr(e, 'lineno', '?')}, cột {getattr(e, 'colno', '?')}: "
                          f"{getattr(e, 'msg', e)}. Kiểm dấu phẩy, ngoặc kép; JSON không cho chú thích //.") from None
    moi_tao = not d.exists()
    d.mkdir(parents=True, exist_ok=True)
    tam = d / ".kich-ban-dang-kiem.json"
    tam.write_text(kich_ban, encoding="utf-8")
    try:
        from .kichban import nap_kich_ban

        kb = nap_kich_ban(tam, ch)
    except Exception as e:  # noqa: BLE001 — LoiKichBan, LoiKhuonCanh…: báo nguyên văn cho người dùng
        tam.unlink(missing_ok=True)
        if moi_tao and not any(d.iterdir()):
            d.rmdir()
        raise LoiGiaoDien("Kịch bản chưa hợp lệ, CHƯA lưu:\n" + str(e).replace(str(tam), "kich-ban.json")) from None
    if dich.exists():
        shutil.copyfile(dich, d / "kich-ban.json.bak")
    tam.replace(dich)
    if (mo_ta or "").strip():
        (d / "mo-ta-youtube.md").write_text(mo_ta.strip() + "\n", encoding="utf-8")
    tt = tom_tat_kich_ban(json.loads(kich_ban))
    return {"slug": slug, "so_canh": len(kb.get("canh") or []), "phut_uoc": tt.get("phut_uoc", 0)}


def ds_kho(ch: dict) -> dict:
    kho = kho_mau(ch)
    kq: dict[str, list[dict]] = {}
    for nhom in NHOM_KHO:
        g = kho / nhom
        ds = []
        if g.is_dir():
            for p in sorted(g.iterdir()):
                if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                    ds.append({"ten": p.name, "rel": f"{nhom}/{p.name}", "kb": round(p.stat().st_size / 1024)})
        kq[nhom] = ds
    return kq


def luu_anh_tai_len(ch: dict, ten: str, du_lieu: bytes) -> Path:
    ten = (ten or "").strip().lower()
    if not RE_TEN_ANH.match(ten):
        raise LoiGiaoDien("Tên ảnh chỉ gồm a-z, 0-9, '_', '-', '.', đuôi png/jpg/webp — đặt theo docs/04 mục 9 "
                          "(vd. max__vui__dung.png, dao-cu__dong-ho.png).")
    if not du_lieu:
        raise LoiGiaoDien("Tệp rỗng.")
    if len(du_lieu) > TOI_DA_TAI_LEN:
        raise LoiGiaoDien("Ảnh quá 25 MB.")
    if not (du_lieu[:8] == b"\x89PNG\r\n\x1a\n" or du_lieu[:3] == b"\xff\xd8\xff" or du_lieu[8:12] == b"WEBP"):
        raise LoiGiaoDien("Không phải ảnh PNG / JPG / WEBP.")
    cho = kho_mau(ch) / "_cho-xu-ly"
    cho.mkdir(parents=True, exist_ok=True)
    p = cho / ten
    p.write_bytes(du_lieu)
    return p


# ---------------------------------------------------------------- hàng việc


class Viec:
    TOI_DA_DONG = 5000

    def __init__(self, ma: int, ten: str, lenh: list[str], cwd: Path):
        self.ma, self.ten, self.lenh, self.cwd = ma, ten, lenh, cwd
        self.trang_thai = "cho"  # cho | chay | xong | loi | dung
        self.dong: list[str] = []
        self.da_bo = 0  # số dòng đầu đã bỏ khi nhật ký quá dài (chỉ số dòng luôn tuyệt đối)
        self.tien_do = ""  # dòng tiến độ in bằng \r (thanh dựng hình), không cộng vào nhật ký
        self.ma_thoat: int | None = None
        self.tao_luc = time.time()
        self.bat_dau: float | None = None
        self.ket_thuc: float | None = None
        self.tien_trinh: subprocess.Popen | None = None
        self.huy = False

    def them_dong(self, dong: str) -> None:
        self.dong.append(dong)
        if len(self.dong) > self.TOI_DA_DONG:
            bo = len(self.dong) - self.TOI_DA_DONG + 1000
            del self.dong[:bo]
            self.da_bo += bo

    def thong_tin(self, tu: int = 0) -> dict:
        return {"ma": self.ma, "ten": self.ten, "trang_thai": self.trang_thai, "ma_thoat": self.ma_thoat,
                "tao_luc": self.tao_luc, "bat_dau": self.bat_dau, "ket_thuc": self.ket_thuc,
                "so_dong": self.da_bo + len(self.dong), "tien_do": self.tien_do,
                "dong": self.dong[max(0, tu - self.da_bo):] if tu >= 0 else []}


def _giet_ca_cay(tt: subprocess.Popen) -> None:
    """Windows: tiến trình con có thể sinh tiếp (ffmpeg…); terminate() chỉ giết lớp ngoài nên dùng taskkill /T."""
    if tt.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(tt.pid)], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False)
    else:
        tt.terminate()


def tach_dong(dang: str, them, tien_do) -> str:
    """Tách `dang` theo \n (gọi them(dòng)); đoạn kết thúc bằng \r (thanh tiến độ) gọi tien_do(chữ).
    Trả phần còn dở chưa hết dòng. \r ở cuối khối giữ lại chờ khối sau (có thể là nửa \r\n)."""
    dang = dang.replace("\r\n", "\n")
    while True:
        i_n, i_r = dang.find("\n"), dang.find("\r")
        if i_r == len(dang) - 1:
            i_r = -1
        if i_n == -1 and i_r == -1:
            return dang
        if i_r != -1 and (i_n == -1 or i_r < i_n):
            if dang[:i_r].strip():
                tien_do(dang[:i_r].strip())
            dang = dang[i_r + 1:]
        else:
            them(dang[:i_n])
            dang = dang[i_n + 1:]


class HangViec:
    """Chạy lần lượt từng việc (một tiến trình con một lúc)."""

    def __init__(self):
        self._khoa = threading.Lock()
        self._co_viec = threading.Condition(self._khoa)
        self._viec: list[Viec] = []
        self._dem = 0
        threading.Thread(target=self._chay_mai, daemon=True, name="hang-viec").start()

    def them(self, ten: str, lenh: list[str], cwd: Path = GOC) -> Viec:
        with self._co_viec:
            self._dem += 1
            v = Viec(self._dem, ten, lenh, cwd)
            self._viec.append(v)
            self._viec = self._viec[-50:]
            self._co_viec.notify()
            return v

    def lay(self, ma: int) -> Viec:
        with self._khoa:
            for v in self._viec:
                if v.ma == ma:
                    return v
        raise LoiGiaoDien(f"Không có việc #{ma}.", 404)

    def tat_ca(self) -> list[dict]:
        with self._khoa:
            return [v.thong_tin(-1) for v in reversed(self._viec)]

    def dung(self, ma: int) -> None:
        v = self.lay(ma)
        with self._khoa:
            v.huy = True
            if v.trang_thai == "cho":
                v.trang_thai = "dung"
                v.ket_thuc = time.time()
                return
            tt = v.tien_trinh
        if tt is not None:
            _giet_ca_cay(tt)

    def _chay_mai(self) -> None:
        while True:
            with self._co_viec:
                v = next((x for x in self._viec if x.trang_thai == "cho"), None)
                if v is None:
                    self._co_viec.wait()
                    continue
                v.trang_thai = "chay"
            self._chay(v)

    def _chay(self, v: Viec) -> None:
        v.bat_dau = time.time()
        v.them_dong("$ " + " ".join(v.lenh))
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        co = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        try:
            with self._khoa:
                if v.huy:
                    v.trang_thai, v.ket_thuc = "dung", time.time()
                    return
                v.tien_trinh = subprocess.Popen(v.lenh, cwd=str(v.cwd), stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
                                                creationflags=co)
            luong = v.tien_trinh.stdout
            assert luong is not None
            dang = ""
            while True:
                b = luong.read1(8192)
                if not b:
                    break
                dang = tach_dong(dang + b.decode("utf-8", errors="replace"), v.them_dong,
                                 lambda s: setattr(v, "tien_do", s))
            if dang.strip("\r"):
                v.them_dong(dang.strip("\r"))
            v.ma_thoat = v.tien_trinh.wait()
            v.trang_thai = "dung" if v.huy else ("xong" if v.ma_thoat == 0 else "loi")
        except OSError as e:
            v.them_dong(f"LỖI không chạy được lệnh: {e}")
            v.trang_thai = "loi"
        v.tien_do = ""
        v.ket_thuc = time.time()


def lenh_cho_viec(loai: str, slug: str | None, chu_de: str | None, cau_hinh: str | None,
                  ch: dict | None = None) -> tuple[str, list[str]]:
    py = [sys.executable, "-m", "nguoique"] + (["--cau-hinh", cau_hinh] if cau_hinh else [])
    can_slug = {"nhap", "that", "kiem-nhip", "thumbnail", "moi"}
    if loai in can_slug:
        slug = kiem_slug(slug or "")
    kho = kho_mau(ch or {})
    bang = {
        "nhap": (f"Dựng nháp {slug}", py + ["lam", str(slug), "--nhap"]),
        "that": (f"Dựng bản thật {slug}", py + ["lam", str(slug)]),
        "kiem-nhip": (f"Kiểm nhịp {slug}", py + ["kiem-nhip", str(slug)]),
        "thumbnail": (f"Thumbnail {slug}", py + ["thumbnail", str(slug)]),
        "moi": (f"Tạo dự án mẫu {slug}", py + ["moi", str(slug)]),
        "kho": ("Lập danh mục kho", py + ["kho"]),
        "hinh-tam": ("Bù hình tạm còn thiếu", py + ["hinh-tam"]),
        "tach-nen": ("Tách nền ảnh chờ xử lý", py + ["tach-nen", str(kho / "_cho-xu-ly"), "--ra", str(kho)]),
        "kiem-tra": ("Kiểm tra máy", py + ["kiem-tra"]),
    }
    if loai in bang:
        return bang[loai]
    raise LoiGiaoDien(f"Không biết việc '{loai}'.")


# ---------------------------------------------------------------- HTTP


def tao_xu_ly(hang: HangViec, cau_hinh: str | None):
    class XuLy(BaseHTTPRequestHandler):
        server_version = "nq-giao-dien"

        def log_message(self, fmt, *a):  # im lặng, trừ lỗi
            pass

        # ---- trả lời
        def _json(self, du_lieu, ma: int = 200) -> None:
            b = json.dumps(du_lieu, ensure_ascii=False).encode("utf-8")
            self.send_response(ma)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(b)

        def _tep(self, p: Path) -> None:
            if not p.is_file():
                raise LoiGiaoDien("Không có tệp.", 404)
            kieu = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            if p.suffix.lower() in {".md", ".srt", ".json"}:
                kieu = "text/plain; charset=utf-8"
            co = p.stat().st_size
            dau, cuoi, ma = 0, co - 1, 200
            m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", ""))
            if m and co:
                if m.group(1):
                    dau = int(m.group(1))
                    cuoi = min(int(m.group(2)), co - 1) if m.group(2) else co - 1
                elif m.group(2):
                    dau = max(0, co - int(m.group(2)))
                if dau > cuoi or dau >= co:
                    self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                    self.send_header("Content-Range", f"bytes */{co}")
                    self.end_headers()
                    return
                ma = 206
            self.send_response(ma)
            self.send_header("Content-Type", kieu)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Length", str(cuoi - dau + 1 if co else 0))
            self.send_header("Cache-Control", "no-cache")
            if ma == 206:
                self.send_header("Content-Range", f"bytes {dau}-{cuoi}/{co}")
            self.end_headers()
            if not co:
                return
            with p.open("rb") as f:
                f.seek(dau)
                con = cuoi - dau + 1
                while con > 0:
                    b = f.read(min(1 << 20, con))
                    if not b:
                        break
                    try:
                        self.wfile.write(b)
                    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                        return
                    con -= len(b)

        def _than(self, toi_da: int = 1 << 20) -> bytes:
            n = int(self.headers.get("Content-Length") or 0)
            if n > toi_da:
                raise LoiGiaoDien("Dữ liệu gửi lên quá lớn.", 413)
            return self.rfile.read(n) if n else b""

        def _than_json(self) -> dict:
            try:
                d = json.loads(self._than().decode("utf-8") or "{}")
            except ValueError:
                raise LoiGiaoDien("JSON gửi lên không hợp lệ.") from None
            if not isinstance(d, dict):
                raise LoiGiaoDien("JSON gửi lên phải là đối tượng.")
            return d

        def _chay(self, ham) -> None:
            try:
                ham()
            except LoiGiaoDien as e:
                self._json({"loi": str(e)}, e.ma)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            except Exception as e:  # noqa: BLE001 — báo lỗi cho trang, không sập máy chủ
                self._json({"loi": f"Lỗi máy chủ: {type(e).__name__}: {e}"}, 500)

        def _ch(self) -> dict:
            try:
                return doc_cau_hinh(cau_hinh)
            except Exception as e:  # noqa: BLE001
                raise LoiGiaoDien(f"config.yaml đang lỗi ({e}). Cách sửa: mở tab Cài đặt, sửa rồi Lưu.", 500) from None

        def _so(self, chuoi: str) -> int:
            try:
                return int(chuoi)
            except (TypeError, ValueError):
                raise LoiGiaoDien("Mã việc / vị trí phải là số.", 400) from None

        def _chan_ngoai(self) -> None:
            """Chặn trang web lạ gửi lệnh tới máy chủ (CSRF / DNS rebinding)."""
            host = (self.headers.get("Host") or "").split(":")[0]
            if host not in ("127.0.0.1", "localhost"):
                raise LoiGiaoDien("Chỉ mở từ 127.0.0.1.", 403)
            nguon = self.headers.get("Origin")
            if nguon and urlparse(nguon).hostname not in ("127.0.0.1", "localhost"):
                raise LoiGiaoDien("Nguồn gửi không hợp lệ.", 403)

        # ---- GET
        def do_GET(self):  # noqa: N802
            self._chay(self._get)

        def _get(self):
            self._chan_ngoai()
            u = urlparse(self.path)
            duong = u.path
            q = parse_qs(u.query)
            if duong in ("/", "/index.html"):
                b = TRANG.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(b)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(b)
            elif duong == "/api/tong-quan":
                try:
                    du_an, loi_cfg = ds_du_an(self._ch()), ""
                except LoiGiaoDien as e:
                    du_an, loi_cfg = [], str(e)
                self._json({"du_an": du_an, "loi_cau_hinh": loi_cfg, "viec": hang.tat_ca(),
                            "goc": str(GOC),
                            "python": sys.version.split()[0]})
            elif duong.startswith("/api/du-an/"):
                self._json(chi_tiet_du_an(self._ch(), duong.split("/")[3]))
            elif duong == "/api/viec":
                self._json(hang.tat_ca())
            elif duong.startswith("/api/viec/"):
                tu = self._so((q.get("tu") or ["0"])[0] or "0")
                self._json(hang.lay(self._so(duong.split("/")[3])).thong_tin(max(0, tu)))
            elif duong == "/api/kho":
                self._json(ds_kho(self._ch()))
            elif duong == "/api/cau-hinh":
                p = tep_cau_hinh(cau_hinh)
                self._json({"duong": str(p), "noi_dung": p.read_text(encoding="utf-8") if p.is_file() else ""})
            elif duong.startswith("/tep/du-an/"):
                phan = duong[len("/tep/du-an/"):].split("/", 1)
                if len(phan) != 2:
                    raise LoiGiaoDien("Đường dẫn không hợp lệ.", 404)
                d = thu_muc_goc_du_an(self._ch()) / kiem_slug(phan[0])
                p = trong_thu_muc(d, phan[1])
                if p.suffix.lower() not in DUOI_XEM:
                    raise LoiGiaoDien("Không cho xem loại tệp này.", 403)
                self._tep(p)
            elif duong.startswith("/tep/kho/"):
                p = trong_thu_muc(kho_mau(self._ch()), duong[len("/tep/kho/"):])
                if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                    raise LoiGiaoDien("Không cho xem loại tệp này.", 403)
                self._tep(p)
            else:
                raise LoiGiaoDien("Không có trang này.", 404)

        # ---- POST
        def do_POST(self):  # noqa: N802
            self._chay(self._post)

        def _post(self):
            self._chan_ngoai()
            u = urlparse(self.path)
            duong = u.path
            if duong == "/api/viec":
                d = self._than_json()
                ten, lenh = lenh_cho_viec(str(d.get("loai") or ""), d.get("du_an"), d.get("chu_de"), cau_hinh, self._ch())
                self._json(hang.them(ten, lenh).thong_tin(-1))
            elif re.fullmatch(r"/api/viec/\d+/dung", duong):
                hang.dung(int(duong.split("/")[3]))
                self._json({"ok": True})
            elif duong == "/api/du-an":
                d = json.loads(self._than(TOI_DA_KICH_BAN).decode("utf-8") or "{}")
                if not isinstance(d, dict):
                    raise LoiGiaoDien("JSON gửi lên phải là đối tượng.")
                self._json(luu_kich_ban_dan(self._ch(), str(d.get("slug") or ""), str(d.get("kich_ban") or ""),
                                            str(d.get("mo_ta") or ""), bool(d.get("ghi_de"))))
            elif re.fullmatch(r"/api/du-an/[^/]+/chinh-sach", duong):
                luu_chinh_sach(self._ch(), duong.split("/")[3], self._than_json())
                self._json({"ok": True})
            elif duong == "/api/kho/tai-len":
                ten = (parse_qs(u.query).get("ten") or [""])[0]
                p = luu_anh_tai_len(self._ch(), ten, self._than(TOI_DA_TAI_LEN))
                self._json({"ok": True, "tep": p.name})
            elif duong == "/api/cau-hinh":
                import yaml

                noi_dung = str(self._than_json().get("noi_dung") or "")
                try:
                    if not isinstance(yaml.safe_load(noi_dung), dict):
                        raise LoiGiaoDien("config.yaml phải là một bảng khoá: giá trị.")
                except yaml.YAMLError as e:
                    raise LoiGiaoDien(f"YAML sai: {e}") from None
                p = tep_cau_hinh(cau_hinh)
                if p.is_file():
                    shutil.copyfile(p, p.with_suffix(".yaml.bak"))
                p.write_text(noi_dung, encoding="utf-8")
                self._json({"ok": True, "sao_luu": str(p.with_suffix(".yaml.bak"))})
            else:
                raise LoiGiaoDien("Không có thao tác này.", 404)

    return XuLy


def tao_may_chu(cong: int = CONG_MAC_DINH, cau_hinh: str | None = None) -> ThreadingHTTPServer:
    httpd = ThreadingHTTPServer(("127.0.0.1", cong), tao_xu_ly(HangViec(), cau_hinh))
    httpd.daemon_threads = True
    return httpd


def chay_giao_dien(cong: int = CONG_MAC_DINH, mo_trinh_duyet: bool = True, cau_hinh: str | None = None) -> None:
    try:
        httpd = tao_may_chu(cong, cau_hinh)
    except OSError as e:
        raise OSError(f"Không mở được cổng {cong} ({e}). Cách sửa: giao diện đã chạy ở cửa sổ khác "
                      f"(mở http://127.0.0.1:{cong}), hoặc chạy `nq giao-dien --cong <số khác>`.") from None
    url = f"http://127.0.0.1:{cong}/"
    print(f"Giao diện: {url}  (Ctrl+C để tắt)", flush=True)
    if mo_trinh_duyet:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()
