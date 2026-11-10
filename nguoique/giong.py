"""Động cơ giọng đọc + tạo giọng cho cả dự án.

Động cơ (cùng giao diện): thuộc tính `ten`, `tan_so`; phương thức `doc(van_ban, toc_do=None) -> (np.float32, sr)`
(`toc_do` None = tốc độ trong config; truyền số để đọc một cảnh nhanh / chậm hơn — `canh.toc_do`).

Tạo giọng một cảnh (tao_giong_du_an): lời -> chuẩn hoá (giữ dấu ngắt) -> tách mẩu theo dấu câu
(chuan_hoa.tach_manh) -> đọc TỪNG mẩu (bộ đệm theo mẩu ở build/giong/manh/<băm>.wav, sửa một câu chỉ
đọc lại câu đó) -> cắt lặng mỗi mẩu -> ghép, chèn lặng theo `tts.nghi` / `canh.nghi` -> build/giong/<id>-<băm>.wav
+ tệp mốc build/giong/<id>-<băm>.json (bắt đầu / kết thúc từng mẩu, để phụ đề khớp từng câu).
- Kokoro  : Kokoro-82M qua gói `kokoro` (đã đối chiếu kokoro 0.9.4, hexgrad/kokoro):
            `KPipeline(lang_code=, repo_id=, device=)`; gọi `pipeline(text, voice=, speed=, split_pattern=)`
            sinh ra `KPipeline.Result` (mở gói được thành graphemes, phonemes, audio — tương thích bản cũ
            trả tuple). audio là torch.FloatTensor, 24000 Hz.
- Piper   : gói `piper-tts`. Bản mới (>=1.3, OHF-Voice/piper1-gpl): `synthesize_wav(text, wav_file,
            syn_config=SynthesisConfig(length_scale=))`. Bản cũ (1.2.x): `synthesize(text, wav_file,
            length_scale=)`. Cả hai ghi vào đối tượng `wave.Wave_write`.
- GiaLap  : tiếng bíp, không cần mô hình — để thử luồng.
- KhachMayChu : gọi máy chủ `nq may-chu` qua HTTP.
"""

import hashlib
import io
import json
import os
import re
import time
import wave
from pathlib import Path

import numpy as np

from .am_thanh_io import doc_wav, ghi_wav, thoi_luong_wav
from .cauhinh import GOC
from .chuan_hoa import LOAI_NGHI, NGHI_MAC_DINH, chu_cho_dong_co, chuan_hoa, nap_tu_dien, tach_doan, tach_manh

KOKORO_REPO = "hexgrad/Kokoro-82M"
KOKORO_TAN_SO = 24000

TOC_DO_CANH_MIN, TOC_DO_CANH_MAX = 0.8, 1.3   # canh.toc_do cho phép (docs/00)
NGHI_TOI_DA = 5.0                               # giây, mỗi khoá trong tts.nghi / canh.nghi
DEM_MANH = 0.03                                 # giây lặng giữ lại mỗi đầu mẩu sau khi cắt lặng
PHIEN_BAN_MOC = 1                               # định dạng tệp mốc build/giong/<id>-<băm>.json


def _tts(ch: dict) -> dict:
    return (ch or {}).get("tts") or {}


def _duong_dan(p) -> Path:
    p = Path(p)
    return p if p.is_absolute() else GOC / p


def _chon_thiet_bi(ch: dict) -> str:
    """'cuda' nếu config muốn và torch thấy GPU; không thì 'cpu' (kèm cảnh báo)."""
    muon = str(_tts(ch).get("thiet_bi", "cuda")).lower()
    if muon != "cuda":
        return "cpu"
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        print("CẢNH BÁO: config muốn thiet_bi: cuda nhưng torch không thấy GPU -> chạy CPU (chậm hơn).\n"
              "  Cách sửa: cài torch bản CUDA (chạy lại setup.ps1) hoặc đặt tts.thiet_bi: cpu.")
    except ImportError:
        pass
    return "cpu"


# ======================================================================= động cơ


class Kokoro:
    ten = "kokoro"

    def __init__(self, ch: dict):
        cfg = _tts(ch).get("kokoro") or {}
        try:
            from kokoro import KPipeline
        except ImportError as loi:
            raise RuntimeError(
                "Chưa cài gói Kokoro.\n"
                "  Cách sửa: chạy lại `powershell -ExecutionPolicy Bypass -File setup.ps1 -DongCo kokoro`\n"
                "  hoặc `pip install -e \".[kokoro]\"` trong .venv; hoặc đổi tts.dong_co: piper / gia-lap."
            ) from loi
        self.ma_ngon_ngu = str(cfg.get("ma_ngon_ngu", "a"))
        self.giong = str(cfg.get("giong", "am_michael"))
        self.toc_do = float(cfg.get("toc_do", 1.0))
        self.thiet_bi = _chon_thiet_bi(ch)
        self.tan_so = KOKORO_TAN_SO
        print(f"Nạp Kokoro-82M (giọng {self.giong}, ngôn ngữ '{self.ma_ngon_ngu}', {self.thiet_bi})…")
        self.pipeline = KPipeline(lang_code=self.ma_ngon_ngu, repo_id=KOKORO_REPO, device=self.thiet_bi)

    def doc(self, van_ban: str, toc_do=None):
        phan = []
        toc = float(toc_do) if toc_do else self.toc_do
        # tự cắt theo câu để mỗi lượt ngắn (Kokoro giới hạn ~510 token mỗi lượt)
        for doan in tach_doan(van_ban, 350):
            for kq in self.pipeline(doan, voice=self.giong, speed=toc, split_pattern=r"\n+"):
                _, _, audio = kq  # Result mở gói được (graphemes, phonemes, audio); bản cũ là tuple
                if audio is None:
                    continue
                if hasattr(audio, "detach"):
                    audio = audio.detach().cpu().numpy()
                phan.append(np.asarray(audio, dtype=np.float32).reshape(-1))
        if not phan:
            return np.zeros(0, dtype=np.float32), self.tan_so
        return np.concatenate(phan), self.tan_so


class Piper:
    ten = "piper"

    def __init__(self, ch: dict):
        cfg = _tts(ch).get("piper") or {}
        try:
            from piper import PiperVoice
        except ImportError as loi:
            raise RuntimeError(
                "Chưa cài gói piper-tts.\n"
                "  Cách sửa: chạy lại setup.ps1 -DongCo piper hoặc `pip install -e \".[piper]\"`."
            ) from loi
        self.mo_hinh = _duong_dan(cfg.get("mo_hinh", "mo-hinh/piper/en_US-norman-medium.onnx"))
        if not self.mo_hinh.is_file():
            raise RuntimeError(
                f"Không thấy mô hình Piper: {self.mo_hinh}\n  Cách sửa: chạy `nq tai-mo-hinh piper`."
            )
        cau_hinh_json = Path(str(self.mo_hinh) + ".json")
        if not cau_hinh_json.is_file():
            raise RuntimeError(
                f"Thiếu tệp cấu hình {cau_hinh_json.name} cạnh mô hình.\n  Cách sửa: chạy `nq tai-mo-hinh piper`."
            )
        self.toc_do = float(cfg.get("toc_do", 1.0)) or 1.0
        dung_cuda = False
        if _tts(ch).get("thiet_bi", "cuda") == "cuda":
            try:
                import onnxruntime

                dung_cuda = "CUDAExecutionProvider" in onnxruntime.get_available_providers()
            except ImportError:
                dung_cuda = False
        print(f"Nạp Piper ({self.mo_hinh.name}, {'cuda' if dung_cuda else 'cpu'})…")
        self.voice = PiperVoice.load(str(self.mo_hinh), config_path=str(cau_hinh_json), use_cuda=dung_cuda)
        self.tan_so = int(self.voice.config.sample_rate)

    def doc(self, van_ban: str, toc_do=None):
        if not van_ban.strip():
            return np.zeros(0, dtype=np.float32), self.tan_so
        length_scale = 1.0 / (float(toc_do) if toc_do else self.toc_do)  # length_scale lớn = đọc chậm
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            if hasattr(self.voice, "synthesize_wav"):
                # piper-tts >= 1.3
                from piper import SynthesisConfig

                self.voice.synthesize_wav(van_ban, wf, syn_config=SynthesisConfig(length_scale=length_scale))
            else:
                # piper-tts 1.2.x (tự đặt định dạng wav, đặt trước cho chắc)
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.tan_so)
                self.voice.synthesize(van_ban, wf, length_scale=length_scale)
        mau, sr = doc_wav(buf.getvalue())
        return np.asarray(mau, dtype=np.float32), sr


class GiaLap:
    """Tiếng bíp dài ~ số ký tự / 15 giây. Không cần mô hình."""

    ten = "gia-lap"

    def __init__(self, ch: dict = None):
        self.tan_so = 24000

    def doc(self, van_ban: str, toc_do=None):
        sr = self.tan_so
        tong = max(0.4, len(van_ban.strip()) / 15.0 / (float(toc_do) if toc_do else 1.0))
        n = int(round(tong * sr))
        ra = np.zeros(n, dtype=np.float32)
        bip, nghi = int(0.12 * sr), int(0.06 * sr)
        t = np.arange(bip, dtype=np.float32) / sr
        vien = np.minimum(1.0, np.minimum(t, t[::-1]) / 0.01).astype(np.float32)  # mờ 10ms hai đầu
        tan = (440.0, 660.0, 550.0)
        i, k = 0, 0
        while i + bip <= n:
            ra[i:i + bip] = 0.3 * np.sin(2 * np.pi * tan[k % 3] * t) * vien
            i += bip + nghi
            k += 1
        return ra, sr


class KhachMayChu:
    """Client HTTP tới máy chủ giọng (`nq may-chu`)."""

    def __init__(self, ch: dict):
        import requests

        self._requests = requests
        self.dia_chi = str(_tts(ch).get("dia_chi", "http://127.0.0.1:8765")).rstrip("/")
        try:
            r = requests.get(f"{self.dia_chi}/trang-thai", timeout=5)
            r.raise_for_status()
            tt = r.json()
        except requests.exceptions.ConnectionError as loi:
            raise RuntimeError(self._huong_dan()) from loi
        except requests.exceptions.RequestException as loi:
            raise RuntimeError(f"Máy chủ giọng {self.dia_chi} trả lỗi: {loi}\n{self._huong_dan()}") from loi
        self.ten = f"may-chu:{tt.get('dong_co', '?')}"
        self.tan_so = int(tt.get("tan_so", 24000))
        # máy chủ cũ (trước khi có canh.toc_do) không đọc khoá toc_do -> phải biết để báo khởi động lại
        self.ho_tro_toc_do = "toc_do" in (tt.get("ho_tro") or [])
        # Bộ đệm giọng băm theo config của lệnh này; máy chủ nạp config lúc khởi động -> phải khớp,
        # không thì tệp đệm mang tên giọng mới nhưng tiếng là giọng cũ.
        cua_may_chu = tt.get("dinh_danh")
        cua_minh = "|".join(str(x) for x in _dinh_danh_giong(ch))
        if cua_may_chu and cua_may_chu != cua_minh:
            raise RuntimeError(
                f"Máy chủ giọng đang chạy cấu hình giọng khác ({cua_may_chu}) với config.yaml hiện tại ({cua_minh}).\n"
                "  Cách sửa: tắt cửa sổ `nq may-chu` (Ctrl+C) rồi chạy lại `nq may-chu` để nạp config mới."
            )

    def _huong_dan(self) -> str:
        return (
            f"Không kết nối được máy chủ giọng ở {self.dia_chi}.\n"
            "  Cách sửa: mở một cửa sổ PowerShell khác, chạy `nq may-chu` (để nguyên cửa sổ đó),\n"
            "  hoặc đổi trong config.yaml: tts.che_do: truc-tiep (nạp mô hình ngay trong lệnh này)."
        )

    def doc(self, van_ban: str, toc_do=None):
        rq = self._requests
        yeu_cau = {"van_ban": van_ban}
        if toc_do:
            if not self.ho_tro_toc_do:
                raise RuntimeError(
                    "Máy chủ giọng đang chạy là bản cũ, chưa hỗ trợ tốc độ riêng từng cảnh (canh.toc_do).\n"
                    "  Cách sửa: tắt cửa sổ `nq may-chu` (Ctrl+C) rồi chạy lại `nq may-chu`."
                )
            yeu_cau["toc_do"] = float(toc_do)
        try:
            r = rq.post(f"{self.dia_chi}/doc", json=yeu_cau, timeout=600)
        except rq.exceptions.ConnectionError as loi:
            raise RuntimeError(self._huong_dan()) from loi
        if r.status_code != 200:
            raise RuntimeError(f"Máy chủ giọng báo lỗi {r.status_code}: {r.text[:500]}")
        return doc_wav(r.content)


def tao_dong_co_truc_tiep(ch: dict):
    """Nạp động cơ local theo tts.dong_co (dùng cho chế độ truc-tiep và cho máy chủ)."""
    ten = str(_tts(ch).get("dong_co", "kokoro")).lower()
    if ten == "kokoro":
        return Kokoro(ch)
    if ten == "piper":
        return Piper(ch)
    if ten in ("gia-lap", "gia_lap"):
        return GiaLap(ch)
    raise ValueError(f"tts.dong_co không hợp lệ: '{ten}'. Chọn một trong: kokoro, piper, gia-lap.")


def tao_dong_co(ch: dict):
    """Theo tts.che_do: may-chu -> client HTTP; truc-tiep -> động cơ local. gia-lap luôn chạy local."""
    tts = _tts(ch)
    if str(tts.get("dong_co", "kokoro")).lower() in ("gia-lap", "gia_lap"):
        return GiaLap(ch)
    che_do = str(tts.get("che_do", "may-chu")).lower()
    if che_do in ("may-chu", "may_chu"):
        return KhachMayChu(ch)
    if che_do in ("truc-tiep", "truc_tiep"):
        return tao_dong_co_truc_tiep(ch)
    raise ValueError(f"tts.che_do không hợp lệ: '{che_do}'. Chọn may-chu hoặc truc-tiep.")


# ======================================================================= tạo giọng dự án


def _dinh_danh_giong(ch: dict):
    """(động cơ, giọng, tốc độ) lấy từ config — dùng làm khoá băm, không cần nạp động cơ."""
    tts = _tts(ch)
    dong_co = str(tts.get("dong_co", "kokoro")).lower()
    if dong_co == "kokoro":
        cfg = tts.get("kokoro") or {}
        return dong_co, f"{cfg.get('giong', 'am_michael')}@{cfg.get('ma_ngon_ngu', 'a')}", float(cfg.get("toc_do", 1.0))
    if dong_co == "piper":
        cfg = tts.get("piper") or {}
        return dong_co, Path(str(cfg.get("mo_hinh", "piper"))).stem, float(cfg.get("toc_do", 1.0))
    return dong_co, "bip", 1.0


def _bam(dong_co: str, giong: str, toc_do: float, chu: str) -> str:
    return hashlib.sha1(f"{dong_co}|{giong}|{toc_do:g}|{chu}".encode("utf-8")).hexdigest()[:10]


def cat_lang(mau: np.ndarray, tan_so: int, dem: float = 0.05) -> np.ndarray:
    """Cắt lặng đầu / cuối, giữ đệm `dem` giây mỗi bên."""
    mau = np.asarray(mau, dtype=np.float32).reshape(-1)
    if mau.size == 0:
        return mau
    dinh = float(np.max(np.abs(mau)))
    if dinh <= 1e-6:
        return mau
    nguong = max(1e-3, 0.02 * dinh)
    # làm mượt 5ms để tiếng lách tách lẻ không tính là lời
    cua = max(1, int(0.005 * tan_so))
    nang = np.convolve(np.abs(mau), np.ones(cua, dtype=np.float32) / cua, mode="same")
    vi_tri = np.nonzero(nang > nguong)[0]
    if vi_tri.size == 0:
        return mau
    giu = int(dem * tan_so)
    dau = max(0, int(vi_tri[0]) - giu)
    cuoi = min(mau.size, int(vi_tri[-1]) + 1 + giu)
    return mau[dau:cuoi]


def _rut_gon(s: str, n: int = 60) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def nghi_cua_canh(ch: dict, canh: dict | None = None) -> dict:
    """Bảng nghỉ (giây) theo loại dấu: mặc định <- tts.nghi <- canh.nghi (ghi đè từng khoá)."""
    kq = dict(NGHI_MAC_DINH)
    cid = str((canh or {}).get("id", "?"))
    for ten, nguon in (("tts.nghi", _tts(ch).get("nghi")), (f"cảnh {cid}: nghi", (canh or {}).get("nghi"))):
        if nguon is None:
            continue
        if not isinstance(nguon, dict):
            raise ValueError(f"{ten} phải là bảng {{phay, cham, hoi, ngat, doan}} (giây), nhận {nguon!r}.")
        for k, v in nguon.items():
            if k not in LOAI_NGHI:
                raise ValueError(f"{ten}: khoá lạ '{k}'. Cách sửa: chỉ dùng {', '.join(LOAI_NGHI)}.")
            if v is None:
                continue
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0.0 <= float(v) <= NGHI_TOI_DA:
                raise ValueError(f"{ten}.{k} = {v!r}: phải là số giây 0..{NGHI_TOI_DA:g}.")
            kq[k] = float(v)
    return kq


def toc_do_cua_canh(ch: dict, canh: dict | None = None) -> float:
    """canh.toc_do (0,8–1,3) nếu có, không thì tốc độ của động cơ trong config."""
    mac_dinh = float(_dinh_danh_giong(ch)[2])
    v = (canh or {}).get("toc_do")
    if v is None:
        return mac_dinh
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not TOC_DO_CANH_MIN <= float(v) <= TOC_DO_CANH_MAX:
        raise ValueError(
            f"Cảnh {(canh or {}).get('id', '?')}: toc_do = {v!r} không hợp lệ. "
            f"Cách sửa: ghi số {TOC_DO_CANH_MIN:g}–{TOC_DO_CANH_MAX:g} (1.0 = bình thường) hoặc bỏ khoá."
        )
    return float(v)


def _ghi_thay(tep: Path, ghi) -> None:
    """Ghi vào tệp tạm rồi đổi tên: tắt máy giữa chừng không để lại tệp hỏng."""
    tam = tep.with_name(tep.stem + ".tam" + tep.suffix)
    ghi(tam)
    os.replace(tam, tep)


def _doc_mot_manh(dc, chu: str, toc_do: float, toc_do_cfg: float):
    # tốc độ bằng config -> gọi như cũ (động cơ / máy chủ cũ không có tham số toc_do vẫn chạy)
    if abs(toc_do - toc_do_cfg) < 1e-9:
        return dc.doc(chu)
    return dc.doc(chu, toc_do=toc_do)


def _ghep_canh(cid: str, tep: Path, tep_moc: Path, manh: list, toc_do: float) -> float:
    """Ghép các mẩu đã đọc + lặng giữa mẩu -> tệp wav cảnh + tệp mốc. Trả số giây."""
    phan, ds_moc, sr = [], [], None
    vi_tri = 0
    for chu, loai, nghi, tep_manh in manh:
        mau, sr_m = doc_wav(tep_manh.read_bytes())
        if sr is None:
            sr = sr_m
        elif sr_m != sr:
            raise RuntimeError(
                f"Cảnh {cid}: các mẩu giọng khác tần số ({sr} / {sr_m} Hz).\n"
                f"  Cách sửa: xoá thư mục {tep_manh.parent} rồi chạy lại."
            )
        mau = np.asarray(mau, dtype=np.float32).reshape(-1)
        n_lang = int(round(float(nghi) * sr))
        ds_moc.append({"chu": chu, "loai": loai, "bat_dau": round(vi_tri / sr, 4),
                       "ket_thuc": round((vi_tri + mau.size) / sr, 4), "nghi_sau": float(nghi)})
        phan.append(mau)
        vi_tri += mau.size
        if n_lang > 0:
            phan.append(np.zeros(n_lang, dtype=np.float32))
            vi_tri += n_lang
    tat_ca = np.concatenate(phan) if phan else np.zeros(0, dtype=np.float32)
    giay = tat_ca.size / float(sr)
    moc = {"phien_ban": PHIEN_BAN_MOC, "id": cid, "tan_so": int(sr), "toc_do": float(toc_do),
           "thoi_luong": round(giay, 4), "manh": ds_moc}
    _ghi_thay(tep_moc, lambda p: p.write_text(json.dumps(moc, ensure_ascii=False, indent=1), encoding="utf-8"))
    _ghi_thay(tep, lambda p: ghi_wav(p, tat_ca, sr))  # wav ghi sau cùng: có wav là có mốc
    return giay


def tao_giong_du_an(kb: dict, thu_muc_build: Path, ch: dict) -> dict:
    """id cảnh -> (tệp wav, số giây). Bộ đệm hai tầng: cảnh (build/giong/<id>-<băm>.wav + .json mốc)
    và mẩu (build/giong/manh/<băm>.wav). Chỉ nạp động cơ khi có mẩu chưa đọc."""
    thu_muc = Path(thu_muc_build) / "giong"
    thu_muc_manh = thu_muc / "manh"
    thu_muc_manh.mkdir(parents=True, exist_ok=True)

    tu_dien_cfg = _tts(ch).get("tu_dien", "tu-dien-doc.yaml")
    tu_dien = nap_tu_dien(_duong_dan(tu_dien_cfg)) if tu_dien_cfg else {}
    dong_co, giong, toc_do_cfg = _dinh_danh_giong(ch)

    ket_qua = {}
    can_ghep = []  # (id, tệp wav, tệp mốc, [(chữ, loại, nghỉ, tệp mẩu)], tốc độ)
    for canh in kb.get("canh") or []:
        cid = str(canh.get("id", "")).strip()
        loi = canh.get("loi")
        if not cid or not loi or not str(loi).strip():
            continue  # cảnh không lời: bỏ qua
        nguon = canh.get("loi_doc") or loi
        chu = chuan_hoa(str(nguon), tu_dien, giu_ngat=True)
        if not chu:
            continue
        nghi = nghi_cua_canh(ch, canh)
        toc_do = toc_do_cua_canh(ch, canh)
        manh = []
        for chu_m, loai in tach_manh(chu):
            doc_chu = chu_cho_dong_co(chu_m)
            if not doc_chu:
                continue
            tep_manh = thu_muc_manh / f"{_bam(dong_co, giong, toc_do, doc_chu)}.wav"
            manh.append([doc_chu, loai, float(nghi[loai]) if loai else 0.0, tep_manh])
        if not manh:
            continue
        manh[-1][1], manh[-1][2] = None, 0.0  # sau mẩu cuối không nghỉ (dem_sau lo)
        dau_an = "\n".join(f"{c}\t{n:g}" for c, _, n, _ in manh)
        tep = thu_muc / f"{cid}-{_bam(dong_co, giong, toc_do, dau_an)}.wav"
        tep_moc = tep.with_suffix(".json")
        # xoá tệp cũ của cùng cảnh (lời / giọng / nghỉ đã đổi); mẩu cũ giữ lại để dùng lại
        mau_ten = re.compile(re.escape(cid) + r"-[0-9a-f]{10}\.(?:wav|json)$")
        for cu in thu_muc.glob(f"{cid}-*"):
            if cu not in (tep, tep_moc) and mau_ten.fullmatch(cu.name):
                try:
                    cu.unlink()
                except OSError:
                    pass
        if tep.is_file() and tep.stat().st_size > 44 and tep_moc.is_file():
            ket_qua[cid] = (tep, float(thoi_luong_wav(tep)))
        else:
            ket_qua[cid] = None  # giữ thứ tự cảnh
            can_ghep.append((cid, tep, tep_moc, [tuple(m) for m in manh], toc_do))

    so_co_san = sum(1 for v in ket_qua.values() if v is not None)
    if so_co_san:
        print(f"Giọng: {so_co_san} cảnh đã có sẵn (bộ đệm), {len(can_ghep)} cảnh cần làm.")

    if can_ghep:
        thieu = {}  # tệp mẩu -> (id cảnh, chữ, tốc độ); trùng chữ giữa các cảnh chỉ đọc một lần
        for cid, _t, _m, manh, toc_do in can_ghep:
            for doc_chu, _l, _n, tep_manh in manh:
                if not (tep_manh.is_file() and tep_manh.stat().st_size > 44):
                    thieu.setdefault(tep_manh, (cid, doc_chu, toc_do))
        if thieu:
            dc = tao_dong_co(ch)
            bat_dau = time.time()
            for i, (tep_manh, (cid, doc_chu, toc_do)) in enumerate(thieu.items(), 1):
                print(f"[{i}/{len(thieu)}] {cid} {_rut_gon(doc_chu)}", flush=True)
                mau, sr = _doc_mot_manh(dc, doc_chu, toc_do, toc_do_cfg)
                mau = cat_lang(mau, sr, dem=DEM_MANH)
                if mau.size == 0:
                    raise RuntimeError(
                        f"Cảnh {cid}: động cơ {dc.ten} trả âm thanh rỗng cho: {_rut_gon(doc_chu, 120)}")
                _ghi_thay(tep_manh, lambda p, m=mau, s=sr: ghi_wav(p, m, s))
            print(f"Đọc xong {len(thieu)} mẩu trong {time.time() - bat_dau:.1f}s.")
        for cid, tep, tep_moc, manh, toc_do in can_ghep:
            ket_qua[cid] = (tep, _ghep_canh(cid, tep, tep_moc, manh, toc_do))

    return {k: v for k, v in ket_qua.items() if v is not None}
