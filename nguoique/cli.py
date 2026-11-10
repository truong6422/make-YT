"""Lệnh `nq` — nối các phần: kiểm tra máy, giọng, trộn âm, dựng video, kho mẫu, phân tích."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from .cauhinh import GOC, MAC_DINH, doc_cau_hinh, duong_dan, kho_mau, tep_cau_hinh, thu_muc_du_an
from .kichban import LoiKichBan, nap_kich_ban

# gói tuỳ chọn -> extra trong pyproject
_EXTRA = {"fastapi": "may-chu", "uvicorn": "may-chu", "pydantic": "may-chu", "kokoro": "kokoro",
          "soundfile": "kokoro", "torch": "kokoro", "piper": "piper", "yt_dlp": "phan-tich",
          "faster_whisper": "phan-tich", "ctranslate2": "phan-tich"}


def _dat_utf8() -> None:
    for luong in (sys.stdout, sys.stderr):
        try:
            luong.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _ch(args) -> dict:
    return doc_cau_hinh(getattr(args, "cau_hinh", None))


def _nap_du_an(args, ch: dict) -> tuple[Path, dict]:
    thu_muc = thu_muc_du_an(ch, args.du_an)
    kb = nap_kich_ban(thu_muc / "kich-ban.json", ch)
    return thu_muc, kb


def _loc_canh(kb: dict, chuoi: str | None) -> list[str]:
    """Giữ lại các cảnh trong --canh (theo thứ tự kịch bản). Trả danh sách id đã chọn."""
    if not chuoi:
        return []
    muon = [x.strip() for x in chuoi.split(",") if x.strip()]
    co = {c["id"] for c in kb["canh"]}
    thieu = [x for x in muon if x not in co]
    if thieu:
        raise LoiKichBan(f"--canh có id không tồn tại: {', '.join(thieu)}. Các id có: {', '.join(c['id'] for c in kb['canh'])}")
    tap = set(muon)
    kb["canh"] = [c for c in kb["canh"] if c["id"] in tap]
    return [c["id"] for c in kb["canh"]]


# ---------------- lệnh ----------------
def lenh_moi(args) -> int:
    ch = _ch(args)
    mau = GOC / "templates" / "kich-ban-mau.json"
    if not mau.is_file():
        raise FileNotFoundError(f"Thiếu mẫu {mau}.")
    thu_muc = thu_muc_du_an(ch, args.ten)
    dich = thu_muc / "kich-ban.json"
    if dich.exists() and not args.ghi_de:
        raise FileExistsError(f"Đã có {dich}. Cách sửa: đặt tên khác, hoặc thêm --ghi-de để chép đè.")
    thu_muc.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(mau, dich)
    print(f"Đã tạo {dich}\nSửa kịch bản rồi chạy: nq dung {args.ten} --nhap")
    return 0


def lenh_giong(args) -> int:
    ch = _ch(args)
    thu_muc, kb = _nap_du_an(args, ch)
    _loc_canh(kb, getattr(args, "canh", None))
    from .giong import tao_giong_du_an

    kq = tao_giong_du_an(kb, thu_muc / "build", ch)
    tong = sum(float(v[1]) for v in kq.values())
    print(f"Giọng: {len(kq)} cảnh, tổng {tong:.1f}s lời — {thu_muc / 'build'}")
    return 0


def lenh_kiem_nhip(args) -> int:
    ch = _ch(args)
    thu_muc, kb = _nap_du_an(args, ch)
    from .dong_thoi_gian import lap_dong_thoi_gian
    from .giong import tao_giong_du_an
    from .kiem_nhip import bao_cao_nhip, kiem_nhip

    ds, tong = lap_dong_thoi_gian(kb, tao_giong_du_an(kb, thu_muc / "build", ch), ch)
    print(bao_cao_nhip(kiem_nhip(kb, ds, tong, ch)))
    return 0


def lenh_dung(args) -> int:
    ch = _ch(args)
    thu_muc, kb = _nap_du_an(args, ch)
    ids = _loc_canh(kb, args.canh)
    build = thu_muc / "build"
    build.mkdir(parents=True, exist_ok=True)
    bat_dau = time.time()

    from .am_thanh import tron_am_thanh
    from .dong_thoi_gian import lap_dong_thoi_gian
    from .dung_hinh import dung_video
    from .giong import tao_giong_du_an
    from .phu_de import ghi_srt, lap_phu_de

    print("1/4 Tạo giọng...")
    giong = tao_giong_du_an(kb, build, ch)
    ds, tong = lap_dong_thoi_gian(kb, giong, ch)
    print(f"2/4 Dòng thời gian: {len(ds)} cảnh, {tong:.1f}s.")
    print("3/4 Trộn âm thanh...")
    tron = tron_am_thanh(kb, ds, tong, thu_muc, build, ch)

    ten = thu_muc.name
    goc_ten = f"xem-thu-{'-'.join(ids)}" if ids else ten
    tep_mp4 = thu_muc / f"{goc_ten}.mp4"
    tep_srt = thu_muc / f"{goc_ten}.srt"
    cum = lap_phu_de(ds, ch)
    ghi_srt(cum, tep_srt)
    dot_phu_de = bool((ch.get("phu_de") or {}).get("bat", True)) and not args.khong_phu_de

    print("4/4 Dựng hình" + (" (nháp 640x360, 15fps)" if args.nhap else "") + "...")
    dung_video(kb, ds, tron, tep_mp4, thu_muc, ch, nhap=args.nhap, phu_de=cum if dot_phu_de else None)
    print(f"Xong sau {time.time() - bat_dau:.0f}s:\n  {tep_mp4}\n  {tep_srt}")
    return 0


def lenh_lam(args) -> int:
    """Một lệnh làm hết: tách nền ảnh mới -> bù hình tạm còn thiếu -> danh mục -> kiểm nhịp -> dựng -> thumbnail."""
    from .hinh_tam import tao_bo_hinh_tam
    from .kho import DUOI_ANH, _dich_theo_ten, lap_danh_muc, tach_nen

    ch = _ch(args)
    kho = kho_mau(ch)
    cho = kho / "_cho-xu-ly"
    moi = []
    if cho.is_dir():
        for p in sorted(cho.iterdir()):
            if p.is_file() and p.suffix.lower() in DUOI_ANH:
                dich = _dich_theo_ten(kho, p.stem)
                if not dich.exists() or dich.stat().st_mtime < p.stat().st_mtime:
                    moi.append(p)
    print(f"[1/5] Ảnh Gemini mới cần tách nền: {len(moi)}")
    for p in moi:
        tach_nen(p, kho)
    print("[2/5] Bù hình tạm cho tệp còn thiếu (không đè ảnh thật)...")
    tao_bo_hinh_tam(kho, ghi_de=False)
    lap_danh_muc(kho)
    print("[3/5] Kiểm nhịp...")
    try:
        lenh_kiem_nhip(args)
    except Exception as e:  # chỉ cảnh báo, không chặn dựng
        print(f"  (bỏ qua kiểm nhịp: {e})")
    print("[4/5] Dựng video...")
    args.canh = getattr(args, "canh", None)
    args.khong_phu_de = False
    kq = lenh_dung(args)
    print("[5/5] Thumbnail...")
    try:
        args.ra = None
        lenh_thumbnail(args)
    except Exception as e:
        print(f"  (bỏ qua thumbnail: {e})")
    return kq


def lenh_kho(args) -> int:
    from .kho import lap_danh_muc

    ch = _ch(args)
    kho = kho_mau(ch)
    dm = lap_danh_muc(kho)
    print(f"Danh mục: {dm['so_tep']} tệp -> {kho / 'danh-muc.json'} và {kho / 'danh-muc.md'}")
    return 0


def lenh_hinh_tam(args) -> int:
    from .hinh_tam import tao_bo_hinh_tam
    from .kho import lap_danh_muc

    ch = _ch(args)
    kho = kho_mau(ch)
    kho.mkdir(parents=True, exist_ok=True)
    print(f"Vẽ bộ hình + âm thanh TẠM vào {kho}" + (" (ghi đè cả tệp đã có)" if args.ghi_de else " (giữ tệp đã có)") + "...")
    ds = tao_bo_hinh_tam(kho, ghi_de=args.ghi_de)
    dm = lap_danh_muc(kho)
    print(f"Đã tạo {len(ds)} tệp mới. Danh mục kho: {dm['so_tep']} tệp -> {kho / 'danh-muc.md'}\n"
          "Ảnh tạm chỉ để chạy thử; thay dần bằng ảnh Gemini cùng tên (docs/04-TAO-ANH-GEMINI.md).")
    return 0


def lenh_thumbnail(args) -> int:
    from .thumbnail import tao_thumbnail

    ch = _ch(args)
    thu_muc = thu_muc_du_an(ch, args.du_an)
    tep_kb = thu_muc / "kich-ban.json"
    if not tep_kb.is_file():
        raise LoiKichBan(f"Không thấy kịch bản '{tep_kb}'. Cách sửa: tạo dự án bằng `nq moi <ten>`.")
    try:
        kb = json.loads(tep_kb.read_text(encoding="utf-8-sig"))  # đọc thô: giữ khoá thumbnail
    except json.JSONDecodeError as e:
        raise LoiKichBan(f"{tep_kb}: JSON sai ở dòng {e.lineno}, cột {e.colno}: {e.msg}.") from None
    if not isinstance(kb, dict):
        raise LoiKichBan(f"{tep_kb}: gốc phải là đối tượng JSON.")
    cfg = kb.get("thumbnail") or {"chu": str(kb.get("tieu_de") or "")}
    ra = Path(args.ra) if args.ra else thu_muc / "thumbnail.png"
    font = (ch.get("phu_de") or {}).get("font")
    tao_thumbnail(cfg, ra, kho_mau(ch), str(duong_dan(font)) if font else None)
    print(f"Đã ghi {ra}")
    return 0


def lenh_tach_nen(args) -> int:
    from .kho import tach_nen

    kq = tach_nen(args.nguon, args.ra, nguong=args.nguong, dem=args.dem, mem=args.mem)
    print(f"Đã tách nền {len(kq)} ảnh vào {args.ra}. Nhớ chạy `nq kho` để cập nhật danh mục.")
    return 0


def lenh_tai_mo_hinh(args) -> int:
    from .tai_ve import tai_mo_hinh

    tai_mo_hinh(_ch(args), args.muc)
    return 0


def lenh_may_chu(args) -> int:
    from .may_chu import chay_may_chu

    ch = _ch(args)
    url = urlparse(str((ch.get("tts") or {}).get("dia_chi", "http://127.0.0.1:8765")))
    host = args.host or "127.0.0.1"
    port = args.port or url.port or 8765
    chay_may_chu(ch, host=host, port=int(port))
    return 0


def lenh_phan_tich(args) -> int:
    from .phan_tich import phan_tich

    kq = phan_tich(args.nguon, _ch(args), nguong_canh=args.nguong_canh, chep_loi=not args.khong_chep_loi)
    print(f"Kết quả phân tích: {kq}")
    return 0


# ---------------- kiem-tra ----------------
def lenh_giao_dien(args) -> int:
    from .giao_dien import chay_giao_dien

    chay_giao_dien(args.cong, mo_trinh_duyet=not args.khong_mo, cau_hinh=getattr(args, "cau_hinh", None))
    return 0


def _thu_import(ten: str):
    try:
        mod = importlib.import_module(ten)
        return True, str(getattr(mod, "__version__", "") or ""), mod
    except Exception as e:  # gói hỏng cũng tính là thiếu
        return False, f"{type(e).__name__}: {e}"[:80], None


def lenh_kiem_tra(args) -> int:
    hang: list[tuple[str, str, str, str]] = []
    thieu_bat_buoc = False

    def them(muc: str, ok: bool, chi_tiet: str = "", sua: str = "", bat_buoc: bool = False) -> None:
        nonlocal thieu_bat_buoc
        if not ok and bat_buoc:
            thieu_bat_buoc = True
        hang.append((muc, "OK" if ok else "THIẾU", chi_tiet, "" if ok else sua))

    v = sys.version_info
    them("Python", v >= (3, 11), f"{v.major}.{v.minor}.{v.micro}", "Cài Python 3.11 (setup.ps1)", True)

    for mod, goi in (("PIL", "pillow"), ("numpy", "numpy"), ("yaml", "pyyaml"), ("requests", "requests")):
        ok, ver, m = _thu_import(mod)
        if ok and mod == "PIL":
            try:
                so = tuple(int(x) for x in ver.split(".")[:2])
                if so < (10, 1):
                    ok, ver = False, f"{ver} (cần ≥ 10.1)"
            except ValueError:
                pass
        them(f"gói {goi}", ok, ver, 'pip install -e .', True)

    tep = tep_cau_hinh(getattr(args, "cau_hinh", None))
    try:
        ch = doc_cau_hinh(getattr(args, "cau_hinh", None))
        them("config.yaml", tep.is_file(), str(tep), "Chép config.yaml từ repo về gốc")
    except Exception as e:
        ch = json.loads(json.dumps(MAC_DINH))
        them("config.yaml", False, str(e)[:80], "Sửa cú pháp config.yaml", True)

    # ffmpeg + nvenc
    ff = None
    try:
        from .am_thanh_io import can_ffmpeg

        ff = can_ffmpeg()
        them("ffmpeg", True, ff)
    except Exception as e:
        them("ffmpeg", False, str(e).splitlines()[0][:80], "winget install Gyan.FFmpeg rồi mở lại terminal", True)
    if ff:
        try:
            enc = subprocess.run([ff, "-hide_banner", "-encoders"], capture_output=True, timeout=30).stdout
            co = b"h264_nvenc" in enc
            chay = False
            if co:
                thu = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                                      "color=c=black:s=256x256:d=0.2", "-c:v", "h264_nvenc", "-f", "null", "-"],
                                     capture_output=True, timeout=60)
                chay = thu.returncode == 0
            them("NVENC (h264_nvenc)", chay, "chạy được" if chay else ("có nhưng lỗi khi thử" if co else "ffmpeg không có"),
                 "Cập nhật driver NVIDIA / dùng bản ffmpeg full (sẽ tự lùi libx264)")
        except (OSError, subprocess.SubprocessError) as e:
            them("NVENC (h264_nvenc)", False, str(e)[:80], "Kiểm ffmpeg")

    # torch / cuda
    ok, ver, torch = _thu_import("torch")
    if ok:
        try:
            cuda = bool(torch.cuda.is_available())
            ten_gpu = torch.cuda.get_device_name(0) if cuda else "không thấy GPU"
        except Exception as e:
            cuda, ten_gpu = False, str(e)[:60]
        them("torch", True, ver)
        them("torch CUDA", cuda, ten_gpu, "Cài torch bản CUDA (setup.ps1) hoặc đặt tts.thiet_bi: cpu")
    else:
        them("torch", False, ver, 'pip install -e ".[kokoro]" (torch CUDA: xem setup.ps1)')

    for mod, nhan in (("kokoro", "kokoro"), ("soundfile", "soundfile"), ("piper", "piper-tts"),
                      ("fastapi", "fastapi"), ("uvicorn", "uvicorn"), ("yt_dlp", "yt-dlp"),
                      ("faster_whisper", "faster-whisper")):
        ok, ver, _ = _thu_import(mod)
        them(f"gói {nhan} (tuỳ chọn)", ok, ver, f'pip install -e ".[{_EXTRA.get(mod, "tat-ca")}]"')

    # Kokoro đọc từ lạ (tên riêng) nhờ espeak-ng; thiếu thì misaki BỎ QUA từ lạ (docs/03)
    if str((ch.get("tts") or {}).get("dong_co", "kokoro")) == "kokoro":
        es = shutil.which("espeak-ng") or next((str(p) for p in (Path("C:/Program Files/eSpeak NG/espeak-ng.exe"),)
                                                 if p.is_file()), None)
        if not es and _thu_import("espeakng_loader")[0]:
            es = "espeakng_loader (kèm misaki)"
        them("espeak-ng (từ lạ cho Kokoro)", bool(es), es or "không thấy",
             "Chạy lại setup.ps1 hoặc cài .msi từ github.com/espeak-ng/espeak-ng/releases")
        ok, ver, _ = _thu_import("en_core_web_sm")
        them("spaCy en_core_web_sm (misaki)", ok, ver, ".venv\\Scripts\\python -m spacy download en_core_web_sm")

    # font
    pd = ch.get("phu_de") or {}
    f1 = duong_dan(pd.get("font", "")) if pd.get("font") else None
    f2 = duong_dan(pd.get("font_du_phong", "")) if pd.get("font_du_phong") else None
    them("font phụ đề", bool(f1 and f1.is_file()), str(f1), "nq tai-mo-hinh font")
    if not (f1 and f1.is_file()):
        them("font dự phòng", bool(f2 and f2.is_file()), str(f2), "Sửa phu_de.font_du_phong trong config.yaml")

    # mô hình
    tts = ch.get("tts") or {}
    hf = Path(os.environ.get("HF_HUB_CACHE") or Path(os.environ.get("HF_HOME") or Path.home() / ".cache" / "huggingface") / "hub")
    kk = hf / "models--hexgrad--Kokoro-82M"
    them("mô hình Kokoro", kk.is_dir(), str(kk), "nq tai-mo-hinh kokoro")
    pm = duong_dan((tts.get("piper") or {}).get("mo_hinh", "mo-hinh/piper/en_US-norman-medium.onnx"))
    them("mô hình Piper (dự phòng)", pm.is_file(), str(pm), "nq tai-mo-hinh piper")

    # máy chủ giọng
    if str(tts.get("che_do", "may-chu")) == "may-chu" and str(tts.get("dong_co", "kokoro")) != "gia-lap":
        dia_chi = str(tts.get("dia_chi", "http://127.0.0.1:8765")).rstrip("/")
        try:
            import requests

            r = requests.get(f"{dia_chi}/trang-thai", timeout=3)
            r.raise_for_status()
            tt = r.json()
            them("máy chủ giọng", True, f"{dia_chi} ({tt.get('dong_co')}, {tt.get('tan_so')} Hz)")
        except Exception as e:
            them("máy chủ giọng", False, f"{dia_chi}: {type(e).__name__}",
                 "Mở cửa sổ khác chạy `nq may-chu` (hoặc đặt tts.che_do: truc-tiep)")
    else:
        hang.append(("máy chủ giọng", "—", f"không dùng (che_do: {tts.get('che_do')}, dong_co: {tts.get('dong_co')})", ""))

    kho = kho_mau(ch)
    them("kho mẫu", kho.is_dir(), str(kho), "Tạo thư mục kho-mau/ (xem kho-mau/README.md)")

    # in bảng
    rong = [max(len(h[i]) for h in hang) for i in range(3)]
    rong[2] = min(rong[2], 60)
    print(f"{'Mục'.ljust(rong[0])}  {'Trạng thái'.ljust(max(rong[1], 10))}  Chi tiết / cách sửa")
    print("-" * (rong[0] + rong[2] + 16))
    for muc, tt, chi_tiet, sua in hang:
        dong = f"{muc.ljust(rong[0])}  {tt.ljust(max(rong[1], 10))}  {chi_tiet}"
        if sua:
            dong += f"  -> {sua}"
        print(dong)
    so_thieu = sum(1 for h in hang if h[1] == "THIẾU")
    print(f"\n{so_thieu} mục THIẾU." + (" Có mục bắt buộc còn thiếu." if thieu_bat_buoc else ""))
    return 1 if thieu_bat_buoc else 0


# ---------------- parser ----------------
def _tao_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nq", description="Bộ dựng video người que (tâm lý học / tâm lý đầu tư).")
    p.add_argument("--cau-hinh", dest="cau_hinh", default=None, help="tệp cấu hình (mặc định config.yaml ở gốc repo)")
    sub = p.add_subparsers(dest="lenh", metavar="<lệnh>")

    s = sub.add_parser("giao-dien", help="mở giao diện quản trị trên trình duyệt (http://127.0.0.1:8770)")
    s.add_argument("--cong", type=int, default=8770, help="cổng (mặc định 8770)")
    s.add_argument("--khong-mo", dest="khong_mo", action="store_true", help="không tự mở trình duyệt")
    s.set_defaults(ham=lenh_giao_dien)

    s = sub.add_parser("kiem-tra", help="kiểm ffmpeg, NVENC, CUDA, gói, font, mô hình, máy chủ giọng")
    s.set_defaults(ham=lenh_kiem_tra)

    s = sub.add_parser("tai-mo-hinh", help="tải mô hình giọng / font")
    s.add_argument("muc", choices=["kokoro", "piper", "font", "tat-ca"])
    s.set_defaults(ham=lenh_tai_mo_hinh)

    s = sub.add_parser("may-chu", help="chạy máy chủ giọng (giữ mô hình trong GPU)")
    s.add_argument("--host", default=None)
    s.add_argument("--port", type=int, default=None)
    s.set_defaults(ham=lenh_may_chu)

    s = sub.add_parser("moi", help="tạo dự án mới từ kịch bản mẫu")
    s.add_argument("ten")
    s.add_argument("--ghi-de", action="store_true", help="chép đè nếu đã có kich-ban.json")
    s.set_defaults(ham=lenh_moi)

    s = sub.add_parser("giong", help="chỉ tạo giọng cho dự án")
    s.add_argument("du_an", metavar="du-an")
    s.add_argument("--canh", default=None, help="chỉ các cảnh này, vd. c01,c02")
    s.set_defaults(ham=lenh_giong)

    s = sub.add_parser("lam", help="LÀM HẾT: tách nền ảnh mới -> hình tạm còn thiếu -> kiểm nhịp -> dựng MP4 -> thumbnail")
    s.add_argument("du_an", metavar="du-an")
    s.add_argument("--nhap", action="store_true", help="bản nháp 640x360 cho nhanh")
    s.set_defaults(ham=lenh_lam)

    s = sub.add_parser("kiem-nhip", help="kiểm nhịp kịch bản so với khuôn docs/02 (cảnh dài, tốc độ, 8–15 phút)")
    s.add_argument("du_an", metavar="du-an")
    s.set_defaults(ham=lenh_kiem_nhip)

    s = sub.add_parser("dung", help="giọng -> trộn âm -> dựng MP4 + .srt")
    s.add_argument("du_an", metavar="du-an")
    s.add_argument("--nhap", action="store_true", help="bản nháp 640x360, 15fps, mã hoá nhanh")
    s.add_argument("--canh", default=None, help="chỉ dựng các cảnh này (xem thử), vd. c01,c02")
    s.add_argument("--khong-phu-de", dest="khong_phu_de", action="store_true", help="không đốt phụ đề vào hình")
    s.set_defaults(ham=lenh_dung)

    s = sub.add_parser("kho", help="quét kho-mau/ -> danh-muc.json + danh-muc.md")
    s.set_defaults(ham=lenh_kho)

    s = sub.add_parser("hinh-tam", help="vẽ bộ hình người que + SFX TẠM vào kho-mau/ (rồi tự lập danh mục)")
    s.add_argument("--ghi-de", dest="ghi_de", action="store_true", help="vẽ lại cả tệp đã có (đè cả ảnh thật cùng tên!)")
    s.set_defaults(ham=lenh_hinh_tam)

    s = sub.add_parser("thumbnail", help="tạo thumbnail 1280x720 từ khoá thumbnail trong kich-ban.json")
    s.add_argument("du_an", metavar="du-an")
    s.add_argument("--ra", default=None, help="tệp PNG xuất (mặc định du-an/<ten>/thumbnail.png)")
    s.set_defaults(ham=lenh_thumbnail)

    s = sub.add_parser("tach-nen", help="ảnh nền trắng -> PNG nền trong, tự cắt sát")
    s.add_argument("nguon", help="tệp ảnh hoặc thư mục")
    s.add_argument("--ra", required=True, help="thư mục đích; đưa gốc kho-mau để tự xếp theo tiền tố tên (dao-cu__x -> dao-cu/x.png, còn lại -> nhan-vat/)")
    s.add_argument("--nguong", type=int, default=235, help="độ sáng tối thiểu coi là nền trắng (0-255, mặc định 235)")
    s.add_argument("--dem", type=int, default=16, help="đệm quanh nhân vật sau khi cắt (px)")
    s.add_argument("--mem", type=float, default=1.0, help="độ mềm mép (bán kính làm mờ, 0 = cứng)")
    s.set_defaults(ham=lenh_tach_nen)

    s = sub.add_parser("phan-tich", help="phân tích video mẫu (cảnh, nhịp, lời)")
    s.add_argument("nguon", help="URL YouTube hoặc tệp video")
    s.add_argument("--nguong-canh", dest="nguong_canh", type=float, default=0.3)
    s.add_argument("--khong-chep-loi", dest="khong_chep_loi", action="store_true", help="bỏ bước chép lời (whisper)")
    s.set_defaults(ham=lenh_phan_tich)
    return p


def main(argv: list[str] | None = None) -> int:
    _dat_utf8()
    p = _tao_parser()
    args = p.parse_args(argv)
    if not getattr(args, "ham", None):
        p.print_help()
        return 0
    try:
        return int(args.ham(args) or 0)
    except KeyboardInterrupt:
        print("\nĐã dừng (Ctrl+C). Chạy lại lệnh sẽ dùng lại giọng đã đọc.", file=sys.stderr)
        return 130
    except LoiKichBan as e:
        print(f"LỖI kịch bản: {e}", file=sys.stderr)
        return 2
    except ModuleNotFoundError as e:
        ten = (e.name or "").split(".")[0]
        extra = _EXTRA.get(ten)
        goi_y = f'pip install -e ".[{extra}]"' if extra else "pip install -e . (hoặc chạy lại setup.ps1)"
        print(f"LỖI: thiếu gói Python '{ten}'. Cách sửa: {goi_y}", file=sys.stderr)
        return 1
    except (RuntimeError, FileNotFoundError, FileExistsError, ValueError, OSError) as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
