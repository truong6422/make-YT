"""Kho mẫu: lập danh mục (json + md) và tách nền trắng ảnh Gemini thành PNG nền trong."""

from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

DUOI_ANH = {".png", ".jpg", ".jpeg", ".webp"}
DUOI_AM = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
DUOI_FONT = {".ttf", ".otf"}


def _loai(duoi: str) -> str | None:
    if duoi in DUOI_ANH:
        return "anh"
    if duoi in DUOI_AM:
        return "am-thanh"
    if duoi in DUOI_FONT:
        return "font"
    return None


def lap_danh_muc(kho) -> dict:
    """Quét kho-mau/ (bỏ thư mục / tệp bắt đầu bằng '_' hoặc '.') -> ghi danh-muc.json + danh-muc.md. Trả danh mục."""
    kho = Path(kho)
    if not kho.is_dir():
        raise FileNotFoundError(f"Không thấy kho mẫu '{kho}'. Cách sửa: kiểm khoá kho_mau trong config.yaml.")
    from PIL import Image

    ds: list[dict] = []
    for p in sorted(kho.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(kho)
        if len(rel.parts) < 2 or any(x.startswith(("_", ".")) for x in rel.parts):
            continue  # tệp ở gốc kho (README, danh-muc) và thư mục ẩn / chờ xử lý
        loai = _loai(p.suffix.lower())
        if loai is None:
            continue
        the = [x for x in p.stem.split("__") if x]
        muc = {"tep": rel.as_posix(), "nhom": rel.parts[0], "ten": p.stem, "the": the, "loai": loai,
               "dung_luong_kb": round(p.stat().st_size / 1024.0, 1)}
        if loai == "anh":
            try:
                with Image.open(p) as im:
                    muc["kich_thuoc"] = [im.width, im.height]
                    muc["trong_suot"] = im.mode in ("RGBA", "LA", "PA") or "transparency" in im.info
            except OSError as e:
                muc["loi"] = f"không mở được: {e}"
        if rel.parts[0] == "nhan-vat" and len(the) >= 2:
            muc["nhan_vat"] = the[0]
            muc["bieu_cam"] = the[1]
            if len(the) >= 3:
                muc["tu_the"] = the[2]
        ds.append(muc)

    danh_muc = {"cap_nhat": _dt.datetime.now().isoformat(timespec="seconds"), "so_tep": len(ds), "tep": ds}
    (kho / "danh-muc.json").write_text(json.dumps(danh_muc, ensure_ascii=False, indent=2), encoding="utf-8")
    (kho / "danh-muc.md").write_text(_md(danh_muc), encoding="utf-8")
    return danh_muc


def _md(dm: dict) -> str:
    dong = ["# Danh mục kho mẫu", "", f"Cập nhật: {dm['cap_nhat']} — {dm['so_tep']} tệp. "
            "Sinh tự động bằng `nq kho`, đừng sửa tay.", ""]
    nhan_vat: dict[str, dict[str, list[str]]] = {}
    for m in dm["tep"]:
        if m.get("nhan_vat"):
            nhan_vat.setdefault(m["nhan_vat"], {}).setdefault(m["bieu_cam"], []).append(m.get("tu_the", ""))
    if nhan_vat:
        dong += ["## Nhân vật (biểu cảm → tư thế)", ""]
        for ten in sorted(nhan_vat):
            dong.append(f"- **{ten}**: " + "; ".join(
                f"{bc} ({', '.join(x for x in sorted(tt) if x) or '—'})" for bc, tt in sorted(nhan_vat[ten].items())))
        dong.append("")
    nhom: dict[str, list[dict]] = {}
    for m in dm["tep"]:
        nhom.setdefault(m["nhom"], []).append(m)
    for ten in sorted(nhom):
        dong += [f"## {ten} ({len(nhom[ten])})", "", "| Tệp | Thẻ | Kích thước | Nền trong |", "|---|---|---|---|"]
        for m in nhom[ten]:
            kt = "x".join(str(v) for v in m["kich_thuoc"]) if m.get("kich_thuoc") else "—"
            tr = ("có" if m.get("trong_suot") else "không") if m["loai"] == "anh" else "—"
            dong.append(f"| `{m['tep']}` | {', '.join(m['the'])} | {kt} | {tr} |")
        dong.append("")
    if not dm["tep"]:
        dong += ["_Kho còn trống._ Thêm ảnh theo docs/04-TAO-ANH-GEMINI.md rồi chạy lại `nq kho`.", ""]
    return "\n".join(dong)


def tach_nen(nguon, ra, nguong: int = 235, dem: int = 16, mem: float = 1.0) -> list[Path]:
    """Ảnh nền trắng -> PNG nền trong. Chỉ phần trắng NỐI VỚI VIỀN ảnh bị xoá (loang từ viền),
    phần trắng bên trong nhân vật (mắt, áo...) được giữ. Mép mềm, cắt sát + đệm `dem` px.
    nguon: tệp hoặc thư mục; ra: thư mục đích. Trả danh sách tệp đã ghi."""
    nguon, ra = Path(nguon), Path(ra)
    if nguon.is_dir():
        ds = [p for p in sorted(nguon.iterdir()) if p.is_file() and p.suffix.lower() in DUOI_ANH]
    elif nguon.is_file():
        ds = [nguon]
    else:
        raise FileNotFoundError(f"Không thấy '{nguon}'. Cách sửa: đưa đường dẫn tệp ảnh hoặc thư mục ảnh.")
    if not ds:
        raise FileNotFoundError(f"Thư mục '{nguon}' không có ảnh (.png/.jpg/.jpeg/.webp).")
    ra.mkdir(parents=True, exist_ok=True)
    kq = []
    for i, p in enumerate(ds, 1):
        dich = _dich_theo_ten(ra, p.stem)
        if dich.resolve() == p.resolve():
            dich = ra / f"{p.stem}-trong.png"
        _tach_mot(p, dich, int(nguong), int(dem), float(mem))
        print(f"[{i}/{len(ds)}] {p.name} -> {dich}")
        kq.append(dich)
    return kq


NHOM_KHO = ("nhan-vat", "dao-cu", "bieu-do", "phong-nen")


def _dich_theo_ten(ra: Path, ten: str) -> Path:
    """Khi `ra` là gốc kho (có thư mục nhan-vat/), phân loại theo tiền tố tên tệp:
    'dao-cu__tien' -> dao-cu/tien.png; tên không có tiền tố nhóm (vd. 'max__vui__dung') -> nhan-vat/.
    `ra` là thư mục thường -> ghi thẳng <ra>/<ten>.png như cũ."""
    if not (ra / "nhan-vat").is_dir():
        return ra / f"{ten}.png"
    nhom, _, con_lai = ten.partition("__")
    if nhom in NHOM_KHO and con_lai:
        return ra / nhom / f"{con_lai}.png"
    return ra / "nhan-vat" / f"{ten}.png"


def _xoa_dau_goc(alpha, ti_le: float = 0.12, toi_da: float = 0.004):
    """Gemini đóng dấu ngôi sao mờ ở góc dưới phải. Nếu ô góc (ti_le × cạnh) chỉ có rất ít điểm
    không trong suốt (< toi_da diện tích ô) thì coi là dấu, xoá — tránh làm hỏng khung cắt sát.
    Nhân vật chạm góc thật sẽ chiếm nhiều điểm hơn nên được giữ."""
    h, w = alpha.shape
    y0, x0 = int(h * (1 - ti_le)), int(w * (1 - ti_le))
    o = alpha[y0:, x0:]
    if o.size and (o > 8).sum() < toi_da * o.size:
        alpha[y0:, x0:] = 0
    return alpha


def _tach_mot(p: Path, dich: Path, nguong: int, dem: int, mem: float) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    with Image.open(p) as f:
        im = f.convert("RGBA")
    a = np.array(im)  # (h, w, 4) uint8, ghi được
    rgb = a[..., :3].astype(np.int16)
    thap, cao = rgb.min(axis=2), rgb.max(axis=2)
    # gần trắng: sáng và gần xám (tránh ăn vào màu nhạt); điểm đã trong suốt cũng tính là nền
    gan_trang = ((thap >= nguong) & ((cao - thap) <= 30)) | (a[..., 3] < 16)
    h, w = gan_trang.shape
    mat = np.zeros((h + 2, w + 2), dtype=np.uint8)
    mat[1:-1, 1:-1][gan_trang] = 255
    mat[0, :] = 255
    mat[-1, :] = 255
    mat[:, 0] = 255
    mat[:, -1] = 255  # vành ngoài nối mọi vùng trắng chạm viền thành một vùng
    m = Image.fromarray(mat)
    ImageDraw.floodfill(m, (0, 0), 128, thresh=0)
    nen = np.asarray(m)[1:-1, 1:-1] == 128
    alpha = np.where(nen, 0, a[..., 3]).astype(np.uint8)
    if mem > 0:
        am = Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(mem))
        alpha = np.minimum(np.asarray(am), alpha).astype(np.uint8)  # mép mềm, nền vẫn trong hẳn
    alpha = _xoa_dau_goc(np.array(alpha, dtype=np.uint8))
    a[..., 3] = alpha
    ket_qua = Image.fromarray(a)
    hop = Image.fromarray(((alpha > 8).astype(np.uint8) * 255)).getbbox()
    if hop is None:
        print(f"CẢNH BÁO: '{p.name}' gần như toàn trắng — giữ nguyên khung. Thử hạ --nguong.", file=sys.stderr)
    else:
        l, t, r, b = hop
        ket_qua = ket_qua.crop((max(0, l - dem), max(0, t - dem), min(w, r + dem), min(h, b + dem)))
    dich.parent.mkdir(parents=True, exist_ok=True)
    ket_qua.save(dich, optimize=True)
