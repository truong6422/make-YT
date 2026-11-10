"""Thư viện khuôn cảnh (docs/11-KHUON-CANH.md).

Cảnh dạng
    {"khuon": "ten-khai-niem", "id": "c12", "tham_so": {"loi": "...", "khai_niem": "LOSS AVERSION"}, ...ghi đè}
được thay bằng nội dung `canh` của tệp `<thu_muc_khuon>/ten-khai-niem.json` sau khi điền tham số vào mọi chỗ
trống `{{ten}}` (đệ quy qua chuỗi / danh sách / đối tượng). Quy tắc:

- Chuỗi chỉ gồm đúng một chỗ trống (vd. `"tre": "{{tre_chu}}"`) nhận nguyên giá trị tham số (số, null, danh sách…);
  chỗ trống nằm giữa chữ thì thay bằng dạng chữ (null -> "").
- Tham số lấy theo thứ tự: `tham_so` của cảnh > `tham_so_chung` ở gốc kịch bản (chỉ tham số khuôn có khai báo)
  > `mac_dinh` trong `_tham_so` của khuôn. Tham số không có `mac_dinh` (hoặc `"bat_buoc": true`) là bắt buộc.
- Khoá khác của cảnh (trừ `khuon`, `tham_so`) **ghi đè** khoá cùng tên của khuôn (thay nguyên, không trộn sâu,
  không điền chỗ trống). `lop_them` / `chu_them` / `am_thanh_them` nối thêm vào danh sách của khuôn.
- Sau khi điền: lớp có `anh` rỗng / null, chữ có `noi_dung` rỗng / null, âm thanh có `tep` rỗng bị bỏ
  (đặt tham số đạo cụ / chữ = "" để tắt phần đó).

Chỉ dùng thư viện chuẩn. Lỗi gom vào một `LoiKhuonCanh` (con của `LoiKichBan` nên CLI in như lỗi kịch bản).
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from .kichban import LoiKichBan

THU_MUC_KHUON = Path(__file__).resolve().parent.parent / "templates" / "khuon-canh"
KHOA_GOC_THAM_SO = "tham_so_chung"
_KHOA_DIEU_KHIEN = ("khuon", "tham_so")
_KHOA_NOI_THEM = {"lop_them": "lop", "chu_them": "chu", "am_thanh_them": "am_thanh"}
_CHO_TRONG = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
_TEN_KHUON = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class LoiKhuonCanh(LoiKichBan):
    """Khuôn cảnh sai / thiếu tham số / không tồn tại: thông điệp liệt kê mọi lỗi kèm cách sửa."""


def _ds_thu_muc(thu_muc_khuon) -> list[Path]:
    if thu_muc_khuon is None:
        return [THU_MUC_KHUON]
    if isinstance(thu_muc_khuon, (str, Path)):
        return [Path(thu_muc_khuon)]
    return [Path(t) for t in thu_muc_khuon]


def danh_sach_khuon(thu_muc_khuon=None) -> list[str]:
    """Tên mọi khuôn tìm thấy (thư mục đứng trước được ưu tiên khi trùng tên)."""
    ten: set[str] = set()
    for tm in _ds_thu_muc(thu_muc_khuon):
        if tm.is_dir():
            ten.update(p.stem for p in tm.glob("*.json"))
    return sorted(ten)


def doc_khuon(ten: str, thu_muc_khuon=None) -> dict:
    """Đọc + kiểm sơ bộ một tệp khuôn: {"_mo_ta", "_tham_so": {...}, "canh": {...}}."""
    ds = _ds_thu_muc(thu_muc_khuon)
    if not isinstance(ten, str) or not _TEN_KHUON.match(ten):
        raise LoiKhuonCanh(f"Tên khuôn {ten!r} không hợp lệ: chỉ chữ thường không dấu, số và '-' (vd. \"ten-khai-niem\").")
    tep = next((tm / f"{ten}.json" for tm in ds if (tm / f"{ten}.json").is_file()), None)
    if tep is None:
        co = danh_sach_khuon(ds)
        raise LoiKhuonCanh(
            f"Không có khuôn '{ten}' trong {', '.join(str(t) for t in ds)}.\n"
            f"Các khuôn có: {', '.join(co) if co else '(trống)'}. Cách sửa: sửa tên 'khuon' hoặc tạo tệp {ten}.json "
            "(xem docs/11-KHUON-CANH.md)."
        )
    try:
        khuon = json.loads(tep.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise LoiKhuonCanh(f"{tep}: JSON sai ở dòng {e.lineno}, cột {e.colno}: {e.msg}.") from None
    if not isinstance(khuon, dict) or not isinstance(khuon.get("canh"), dict):
        raise LoiKhuonCanh(f"{tep}: khuôn phải là {{\"_tham_so\": {{...}}, \"canh\": {{...một cảnh...}}}}.")
    tham_so = khuon.get("_tham_so") or {}
    if not isinstance(tham_so, dict) or not all(isinstance(v, dict) for v in tham_so.values()):
        raise LoiKhuonCanh(f"{tep}: '_tham_so' phải là {{\"ten\": {{\"mac_dinh\": ..., \"mo_ta\": \"...\"}}}}.")
    khuon["_tham_so"] = tham_so
    khuon["_tep"] = str(tep)
    return khuon


def la_bat_buoc(dac_ta: dict) -> bool:
    return dac_ta.get("bat_buoc") is True or "mac_dinh" not in dac_ta


def tham_so_mau(khuon: dict) -> dict:
    """Bộ tham số dùng thử: `mac_dinh`, tham số bắt buộc lấy `vi_du` (để xem trước / test)."""
    kq = {}
    for ten, dt in khuon["_tham_so"].items():
        if la_bat_buoc(dt):
            if "vi_du" in dt:
                kq[ten] = copy.deepcopy(dt["vi_du"])
        else:
            kq[ten] = copy.deepcopy(dt["mac_dinh"])
    return kq


def _cho_trong_trong(gt, ra: set) -> set:
    if isinstance(gt, str):
        ra.update(_CHO_TRONG.findall(gt))
    elif isinstance(gt, dict):
        for v in gt.values():
            _cho_trong_trong(v, ra)
    elif isinstance(gt, list):
        for v in gt:
            _cho_trong_trong(v, ra)
    return ra


def _dien(gt, ts: dict, loi: list, cho: str):
    """Điền tham số đệ quy. Chỗ trống đứng một mình giữ nguyên kiểu giá trị."""
    if isinstance(gt, str):
        m = _CHO_TRONG.fullmatch(gt)
        if m:
            return copy.deepcopy(ts.get(m.group(1)))

        def thay(m2):
            v = ts.get(m2.group(1))
            if v is None:
                return ""
            if isinstance(v, (dict, list)):
                loi.append(f"- {cho}: tham số '{m2.group(1)}' là danh sách / đối tượng, không chèn giữa chữ được")
                return ""
            if isinstance(v, bool):
                return "true" if v else "false"
            return str(v)

        return _CHO_TRONG.sub(thay, gt)
    if isinstance(gt, dict):
        return {k: _dien(v, ts, loi, cho) for k, v in gt.items()}
    if isinstance(gt, list):
        return [_dien(v, ts, loi, cho) for v in gt]
    return gt


def _rong(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def _bo_phan_rong(canh: dict) -> None:
    if isinstance(canh.get("lop"), list):
        canh["lop"] = [l for l in canh["lop"]
                       if not (isinstance(l, dict) and "anh" in l and "nhan_vat" not in l and _rong(l["anh"]))]
    if isinstance(canh.get("chu"), list):
        canh["chu"] = [c for c in canh["chu"] if not (isinstance(c, dict) and "noi_dung" in c and _rong(c["noi_dung"]))]
    if isinstance(canh.get("am_thanh"), list):
        canh["am_thanh"] = [a for a in canh["am_thanh"]
                            if not (_rong(a) if not isinstance(a, dict) else ("tep" in a and _rong(a["tep"])))]


def trien_khai_canh(canh: dict, khuon: dict, chung: dict | None = None, cho: str = "cảnh") -> tuple[dict, list[str]]:
    """Một cảnh dùng khuôn -> (cảnh đã điền + ghi đè, danh sách lỗi)."""
    loi: list[str] = []
    dac_ta = khuon["_tham_so"]
    ten_khuon = canh.get("khuon")
    rieng = canh.get("tham_so") or {}
    if not isinstance(rieng, dict):
        return {}, [f"- {cho}: 'tham_so' phải là đối tượng {{\"ten\": giá trị}}, nhận {rieng!r}"]

    la = sorted(k for k in rieng if k not in dac_ta)
    if la:
        loi.append(f"- {cho}: khuôn '{ten_khuon}' không có tham số {', '.join(la)} (gõ nhầm?). "
                   f"Tham số có: {', '.join(dac_ta) or '(không)'}")
    ts = {}
    for ten, dt in dac_ta.items():
        if ten in rieng:
            ts[ten] = rieng[ten]
        elif chung and ten in chung:
            ts[ten] = chung[ten]
        elif not la_bat_buoc(dt):
            ts[ten] = dt["mac_dinh"]
    thieu = [t for t, dt in dac_ta.items() if t not in ts and la_bat_buoc(dt)]
    if thieu:
        goi_y = "; ".join(f"{t}: {dac_ta[t].get('mo_ta', '')}".rstrip(": ") for t in thieu)
        loi.append(f"- {cho}: khuôn '{ten_khuon}' thiếu tham số bắt buộc {', '.join(thieu)} "
                   f"— thêm vào \"tham_so\" ({goi_y})")
    khong_khai = sorted(_cho_trong_trong(khuon["canh"], set()) - set(dac_ta))
    if khong_khai:
        loi.append(f"- {khuon.get('_tep', ten_khuon)}: chỗ trống {', '.join(khong_khai)} chưa khai trong '_tham_so'")
    if loi:
        return {}, loi

    kq = _dien(copy.deepcopy(khuon["canh"]), ts, loi, cho)
    for k, v in canh.items():
        if k in _KHOA_DIEU_KHIEN or k in _KHOA_NOI_THEM:
            continue
        kq[k] = copy.deepcopy(v)
    for k, dich in _KHOA_NOI_THEM.items():
        if k in canh:
            them = canh[k]
            if not isinstance(them, list):
                loi.append(f"- {cho}: '{k}' phải là danh sách")
                continue
            goc = kq.get(dich) or []
            kq[dich] = (goc if isinstance(goc, list) else [goc]) + copy.deepcopy(them)
    _bo_phan_rong(kq)
    if "id" in kq:  # để id lên đầu cho dễ đọc khi in ra
        kq = {"id": kq["id"], **{k: v for k, v in kq.items() if k != "id"}}
    return kq, loi


def trien_khai(kb, thu_muc_khuon=None):
    """Thay mọi cảnh {"khuon": ...} bằng nội dung khuôn đã điền. Trả bản mới (không sửa `kb`).

    `thu_muc_khuon`: một thư mục hoặc danh sách (thư mục đầu được ưu tiên, vd. [du-an/<ten>/khuon-canh, THU_MUC_KHUON]);
    None = `templates/khuon-canh`. Gốc không phải đối tượng / không có cảnh dùng khuôn -> trả bản sao nguyên.
    """
    if not isinstance(kb, dict):
        return kb
    kb = copy.deepcopy(kb)
    chung = kb.pop(KHOA_GOC_THAM_SO, None) or {}
    loi: list[str] = []
    if not isinstance(chung, dict):
        loi.append(f"- gốc: '{KHOA_GOC_THAM_SO}' phải là đối tượng {{\"ten\": giá trị}}")
        chung = {}
    ds = kb.get("canh")
    if not isinstance(ds, list):
        if loi:
            raise LoiKhuonCanh("Kịch bản có lỗi khuôn cảnh:\n" + "\n".join(loi))
        return kb

    bo_dem: dict[str, dict] = {}
    ra = []
    for i, canh in enumerate(ds):
        if not isinstance(canh, dict) or "khuon" not in canh:
            ra.append(canh)
            continue
        cho = f"cảnh {canh.get('id') or '#' + str(i + 1)}"
        ten = canh.get("khuon")
        if not isinstance(ten, str):
            loi.append(f"- {cho}: 'khuon' phải là tên khuôn dạng chuỗi (vd. \"ten-khai-niem\"), nhận {ten!r}")
            ra.append(canh)
            continue
        try:
            if ten not in bo_dem:
                bo_dem[ten] = doc_khuon(ten, thu_muc_khuon)
        except LoiKhuonCanh as e:
            loi.append(f"- {cho}: {e}")
            ra.append(canh)
            continue
        moi, l = trien_khai_canh(canh, bo_dem[ten], chung, cho)
        loi.extend(l)
        ra.append(moi if not l else canh)
    if loi:
        raise LoiKhuonCanh(
            f"Kịch bản có {len(loi)} lỗi khuôn cảnh:\n" + "\n".join(loi)
            + "\nCách sửa: xem bảng khuôn và tham số ở docs/11-KHUON-CANH.md."
        )
    kb["canh"] = ra
    return kb
