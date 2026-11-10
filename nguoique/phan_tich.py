"""Phân tích video mẫu: nhịp cắt cảnh, khoảng nghỉ, tốc độ đọc, chép lời, ảnh tổng quan.

Kết quả ở `phan-tich/<id>/`: video.mp4 (nếu tải từ URL), canh/0001.jpg…, bao-cao.md, tong-quan-01.jpg…
Chỉ để học cấu trúc / nhịp — không dùng lại hình, lời, nhạc của video mẫu.
"""

import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

from .am_thanh_io import can_ffmpeg
from .cauhinh import GOC

COT, HANG = 8, 6
CAO_NHAN = 16


def _chay(lenh: list, mo_ta: str, bo_qua_loi: bool = False) -> subprocess.CompletedProcess:
    kq = subprocess.run(lenh, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if kq.returncode != 0 and not bo_qua_loi:
        duoi = (kq.stderr or kq.stdout or "").strip()[-1500:]
        raise RuntimeError(f"{mo_ta} thất bại (mã {kq.returncode}):\n{duoi}")
    return kq


def _ffprobe(ffmpeg: str) -> str:
    p = Path(ffmpeg)
    for ten in ("ffprobe.exe", "ffprobe"):
        ung_vien = p.with_name(ten)
        if ung_vien.is_file():
            return str(ung_vien)
    tim = shutil.which("ffprobe")
    if tim:
        return tim
    raise RuntimeError("Không thấy ffprobe (đi kèm ffmpeg). Cách sửa: cài lại ffmpeg đầy đủ (winget install Gyan.FFmpeg).")


def _an_toan(ten: str) -> str:
    return re.sub(r"[^\w.-]+", "_", ten).strip("_") or "video"


def _gio(giay: float) -> str:
    giay = max(0.0, float(giay))
    p, s = divmod(giay, 60)
    g, p = divmod(int(p), 60)
    return f"{g}:{p:02d}:{s:04.1f}" if g else f"{p:02d}:{s:04.1f}"


# ---------------------------------------------------------------- nguồn


def _lay_video(nguon: str, ffmpeg: str):
    """-> (thư mục kết quả, tệp video)."""
    if re.match(r"^https?://", nguon, re.IGNORECASE):
        yt = [sys.executable, "-m", "yt_dlp"]
        kq = _chay(yt + ["--print", "id", "--skip-download", "--no-playlist", nguon], "yt-dlp lấy id video")
        vid = _an_toan((kq.stdout or "").strip().splitlines()[-1] if kq.stdout.strip() else "video")
        thu_muc = GOC / "phan-tich" / vid
        thu_muc.mkdir(parents=True, exist_ok=True)
        co_san = sorted(thu_muc.glob("video.*"))
        co_san = [p for p in co_san if p.suffix.lower() in (".mp4", ".mkv", ".webm")]
        if co_san:
            print(f"Đã có video: {co_san[0]}")
            return thu_muc, co_san[0]
        print(f"Tải video {vid} (≤720p)…")
        _chay(yt + [
            "--no-playlist",
            "-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/bv*[height<=720]+ba/b[height<=720]/b",
            "--merge-output-format", "mp4",
            "--ffmpeg-location", str(Path(ffmpeg).parent),
            "-o", str(thu_muc / "video.%(ext)s"),
            nguon,
        ], "yt-dlp tải video")
        tep = [p for p in sorted(thu_muc.glob("video.*")) if p.suffix.lower() in (".mp4", ".mkv", ".webm")]
        if not tep:
            raise RuntimeError(f"yt-dlp chạy xong nhưng không thấy tệp video trong {thu_muc}.")
        return thu_muc, tep[0]
    tep = Path(nguon)
    if not tep.is_absolute() and not tep.is_file():
        tep = GOC / nguon
    if not tep.is_file():
        raise RuntimeError(f"Không thấy tệp '{nguon}'. Cách sửa: đưa URL YouTube hoặc đường dẫn tệp video có thật.")
    thu_muc = GOC / "phan-tich" / _an_toan(tep.stem)
    thu_muc.mkdir(parents=True, exist_ok=True)
    return thu_muc, tep


# ---------------------------------------------------------------- đo


def _thoi_luong(ffprobe: str, tep: Path) -> float:
    kq = _chay([ffprobe, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(tep)], "ffprobe đọc thời lượng")
    try:
        return float(kq.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        raise RuntimeError(f"ffprobe không trả thời lượng cho {tep}: {kq.stdout!r}")


def _cat_canh(ffmpeg: str, tep: Path, thu_muc_anh: Path, nguong: float) -> list:
    """Một lượt ffmpeg: ảnh đầu mỗi cảnh + mốc pts_time. Luôn lấy khung đầu tiên (cảnh 1)."""
    thu_muc_anh.mkdir(parents=True, exist_ok=True)
    for cu in thu_muc_anh.glob("*.jpg"):
        cu.unlink()
    # dấu phẩy nằm trong nháy đơn nên không tách bộ lọc; lấy khung 0 + khung đổi cảnh
    loc = f"select='eq(n,0)+gt(scene,{nguong})',showinfo,scale=320:-2"
    goc = [ffmpeg, "-hide_banner", "-nostats", "-i", str(tep), "-an", "-vf", loc]
    ra = ["-q:v", "4", str(thu_muc_anh / "%04d.jpg")]
    print(f"Dò cảnh (ngưỡng {nguong})… có thể mất vài phút.")
    kq = _chay(goc + ["-fps_mode", "vfr"] + ra, "ffmpeg dò cảnh", bo_qua_loi=True)
    if kq.returncode != 0 and ("fps_mode" in (kq.stderr or "")):
        kq = _chay(goc + ["-vsync", "vfr"] + ra, "ffmpeg dò cảnh (-vsync)")  # ffmpeg < 5.1
    elif kq.returncode != 0:
        raise RuntimeError(f"ffmpeg dò cảnh thất bại:\n{(kq.stderr or '')[-1500:]}")
    moc = [float(x) for x in re.findall(r"\[Parsed_showinfo[^\]]*\].*?pts_time:\s*(-?[\d.]+)", kq.stderr or "")]
    return moc


def _khoang_nghi(ffmpeg: str, tep: Path, nguong_db: int = -35, toi_thieu: float = 0.3) -> list:
    kq = _chay([ffmpeg, "-hide_banner", "-nostats", "-i", str(tep), "-vn",
                "-af", f"silencedetect=noise={nguong_db}dB:d={toi_thieu}", "-f", "null", "-"],
               "ffmpeg silencedetect", bo_qua_loi=True)
    dau = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", kq.stderr or "")]
    cuoi = re.findall(r"silence_end:\s*(-?[\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", kq.stderr or "")
    ds = []
    for i, (e, d) in enumerate(cuoi):
        s = dau[i] if i < len(dau) else float(e) - float(d)
        ds.append((max(0.0, s), float(e), float(d)))
    return ds


def _chep_loi(tep: Path, ch: dict):
    """-> (ngôn ngữ, [(đầu, cuối, chữ)]) hoặc None nếu chưa cài faster-whisper."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("Bỏ qua chép lời: chưa cài faster-whisper (pip install -e \".[phan-tich]\").")
        return None
    co_mo_hinh = str(((ch or {}).get("phan_tich") or {}).get("whisper", "small"))
    thiet_bi = "cpu"
    try:
        import ctranslate2

        if ctranslate2.get_cuda_device_count() > 0:
            thiet_bi = "cuda"
    except Exception:
        pass

    def _chay_whisper(tb: str):
        print(f"Chép lời bằng faster-whisper '{co_mo_hinh}' ({tb}, int8)…")
        mh = WhisperModel(co_mo_hinh, device=tb, compute_type="int8")
        doan, info = mh.transcribe(str(tep), language=None, vad_filter=True, beam_size=5)
        ds = []
        for d in doan:  # generator: suy luận thật sự chạy ở đây
            ds.append((float(d.start), float(d.end), d.text.strip()))
        return info.language, ds

    try:
        return _chay_whisper(thiet_bi)
    except Exception as loi:
        if thiet_bi != "cuda":
            raise
        # hay gặp trên Windows: thiếu cuBLAS / cuDNN cho ctranslate2
        print(f"CẢNH BÁO: whisper trên GPU lỗi ({loi}); chạy lại bằng CPU.")
        return _chay_whisper("cpu")


# ---------------------------------------------------------------- ảnh tổng quan


def _anh_tong_quan(anh: list, moc: list, thu_muc: Path) -> list:
    from PIL import Image, ImageDraw, ImageFont

    if not anh:
        return []
    with Image.open(anh[0]) as a0:
        w, h = a0.size
    font = ImageFont.load_default()
    o_cao = h + CAO_NHAN
    moi_trang = COT * HANG
    ra = []
    for trang in range(0, len(anh), moi_trang):
        nhom = anh[trang:trang + moi_trang]
        so_hang = (len(nhom) + COT - 1) // COT
        tam = Image.new("RGB", (COT * w, so_hang * o_cao), (24, 24, 24))
        ve = ImageDraw.Draw(tam)
        for i, p in enumerate(nhom):
            x, y = (i % COT) * w, (i // COT) * o_cao
            with Image.open(p) as a:
                a = a.convert("RGB")
                if a.size != (w, h):
                    a = a.resize((w, h))
                tam.paste(a, (x, y))
            so = trang + i
            nhan = f"#{so + 1}  {_gio(moc[so]) if so < len(moc) else '?'}"
            ve.text((x + 4, y + h + 2), nhan, fill=(235, 235, 235), font=font)
        tep = thu_muc / f"tong-quan-{trang // moi_trang + 1:02d}.jpg"
        tam.save(tep, quality=85)
        ra.append(tep)
    return ra


# ---------------------------------------------------------------- báo cáo


def _so(x: float) -> str:
    return f"{x:.2f}"


def phan_tich(nguon: str, ch: dict, nguong_canh=0.3, chep_loi=True) -> Path:
    ffmpeg = can_ffmpeg()
    ffprobe = _ffprobe(ffmpeg)
    thu_muc, tep = _lay_video(nguon, ffmpeg)
    for cu in thu_muc.glob("tong-quan-*.jpg"):
        cu.unlink()

    tong = _thoi_luong(ffprobe, tep)
    moc = sorted(round(m, 3) for m in _cat_canh(ffmpeg, tep, thu_muc / "canh", float(nguong_canh)))
    anh = sorted((thu_muc / "canh").glob("*.jpg"))
    if moc:
        moc[0] = 0.0  # khung đầu tiên luôn được chọn (eq(n,0)); start_time có thể khác 0
    else:
        moc = [0.0]
    if len(moc) != len(anh):
        print(f"CẢNH BÁO: số mốc ({len(moc)}) khác số ảnh ({len(anh)}); nhãn ảnh có thể lệch.")
    dai = [b - a for a, b in zip(moc, moc[1:] + [tong]) if b - a > 0]
    nghi = _khoang_nghi(ffmpeg, tep)
    loi = _chep_loi(tep, ch) if chep_loi else None
    tong_quan = _anh_tong_quan(anh, moc, thu_muc)

    # ---- viết báo cáo
    d = []
    d.append(f"# Phân tích video: {tep.name}\n")
    d.append(f"- Nguồn: {nguon}")
    d.append(f"- Thời lượng: {_gio(tong)} ({tong:.1f}s)")
    d.append(f"- Số cảnh (ngưỡng scene {nguong_canh}): {len(dai)}")
    if tong > 0:
        d.append(f"- Cảnh / phút: {len(dai) / (tong / 60):.1f}")
    if dai:
        d.append(f"- Độ dài cảnh (giây): trung bình {_so(statistics.mean(dai))}, trung vị {_so(statistics.median(dai))}, "
                 f"ngắn nhất {_so(min(dai))}, dài nhất {_so(max(dai))}")
        nhom = [("< 2s", lambda x: x < 2), ("2–4s", lambda x: 2 <= x < 4),
                ("4–8s", lambda x: 4 <= x < 8), ("> 8s", lambda x: x >= 8)]
        d.append("\n## Phân bố độ dài cảnh\n")
        d.append("| Khoảng | Số cảnh | Tỉ lệ |")
        d.append("|---|---:|---:|")
        for ten, f in nhom:
            n = sum(1 for x in dai if f(x))
            d.append(f"| {ten} | {n} | {100.0 * n / len(dai):.0f}% |")
    d.append("\n## Khoảng nghỉ (silencedetect −35dB, ≥0,3s)\n")
    d.append("> Lưu ý: nhạc nền liên tục làm silencedetect không thấy chỗ nghỉ của lời — số này chỉ tham khảo.\n")
    if nghi:
        tg = [x[2] for x in nghi]
        d.append(f"- Số khoảng nghỉ: {len(nghi)}; trung bình {_so(statistics.mean(tg))}s, trung vị {_so(statistics.median(tg))}s, dài nhất {_so(max(tg))}s")
        d.append(f"- Tổng lặng: {sum(tg):.1f}s ({100.0 * sum(tg) / tong:.0f}% thời lượng)" if tong > 0 else "")
    else:
        d.append("- Không phát hiện khoảng lặng (có thể do nhạc nền).")
    if loi is not None:
        ngon_ngu, doan = loi
        so_tu = sum(len(t.split()) for _, _, t in doan)
        noi = sum(max(0.0, e - s) for s, e, _ in doan)
        d.append("\n## Tốc độ đọc\n")
        d.append(f"- Ngôn ngữ nhận được: {ngon_ngu}")
        d.append(f"- Số từ: {so_tu}")
        if tong > 0:
            d.append(f"- Từ / phút (trên cả video): {so_tu / (tong / 60):.0f}")
        if noi > 0:
            d.append(f"- Từ / phút (chỉ lúc có lời, theo VAD): {so_tu / (noi / 60):.0f}")
        d.append("\n## Chép lời\n")
        for s, e, t in doan:
            d.append(f"- `[{_gio(s)} → {_gio(e)}]` {t}")
    elif chep_loi:
        d.append("\n## Chép lời\n\n- Chưa có (thiếu faster-whisper).")
    d.append("\n## Mốc cảnh\n")
    d.append(", ".join(f"{i + 1}: {_gio(m)}" for i, m in enumerate(moc)))
    if tong_quan:
        d.append("\n## Ảnh tổng quan\n")
        for p in tong_quan:
            d.append(f"![{p.name}]({p.name})")
    (thu_muc / "bao-cao.md").write_text("\n".join(x for x in d if x is not None) + "\n", encoding="utf-8")
    print(f"Xong: {thu_muc / 'bao-cao.md'}  ({len(dai)} cảnh, {len(tong_quan)} ảnh tổng quan)")
    return thu_muc
