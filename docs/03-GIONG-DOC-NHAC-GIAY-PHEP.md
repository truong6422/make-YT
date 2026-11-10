# Giọng đọc, nhạc nền, hiệu ứng âm thanh và giấy phép

Kiểm chứng ngày **10/11/2026** bằng tra cứu web (không cài / chạy thử gì). Mục tiêu: kênh YouTube tiếng Anh, hoạt hình người que, **sẽ bật kiếm tiền**, chi phí 0đ, chạy trên Acer Aspire 7 (Ryzen 5 5500U, 16GB RAM, GTX 1650 4GB, Windows 11).

> Đây không phải tư vấn pháp lý. Giấy phép có thể đổi; trước khi dùng một mô hình / bản nhạc, mở lại trang nguồn ghi bên cạnh. Chỗ nào chưa chắc đều ghi rõ **(chưa chắc)**.

## Tóm tắt quyết định

| Việc | Chọn | Lý do ngắn |
|---|---|---|
| Giọng mặc định | **Kokoro-82M** (`kokoro` 0.9.4) | Mã + trọng số Apache-2.0, dữ liệu huấn luyện "permissive/non-copyrighted"; nhẹ (~1–2GB VRAM), chạy được cả CPU; chất lượng tiếng Anh tốt nhất trong nhóm giấy phép thoáng cỡ nhỏ |
| Giọng dự phòng | **Piper** (`piper-tts` 1.8.0) với giọng **đã được dự án xác nhận dùng thương mại**: `en_US-norman-medium`, `en_US-ljspeech-high`, `en_US-libritts-high`, `en_US-joe-medium`, `en_US-john-medium`, `en_US-kristin-medium` | Rất nhanh trên CPU, có wheel Windows, nhúng sẵn espeak-ng |
| **Không** dùng | `en_US-ryan-*`, `en_US-lessac-*`, `en_US-amy-*`, `en_US-hfc_*` (Piper); XTTS-v2; F5-TTS; Spark-TTS; Fish Audio S2; IndexTTS | Dữ liệu / trọng số phi thương mại hoặc không rõ giấy phép |
| Nhạc nền | YouTube Audio Library (lọc "Attribution not required") trước; Pixabay Music; Incompetech (phải ghi công) | An toàn Content ID nhất là Audio Library |
| Hiệu ứng âm | YouTube Audio Library SFX, Kenney (CC0), Freesound **chỉ CC0 / CC BY**, Pixabay SFX, Sonniss GDC bundle | Xem mục 2.4 |

**Điểm khác với `00-HOP-DONG.md` (cần sửa):**
1. `config.yaml` đang đặt `piper.mo_hinh: mo-hinh/piper/en_US-ryan-high.onnx` — **sai**: bộ dữ liệu *ryan* là phi thương mại, Piper tự liệt nó vào nhóm loại trừ ([COMMERCIAL_USE.md](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/COMMERCIAL_USE.md)). Đề nghị đổi sang `en_US-norman-medium` (giọng nam, public domain) hoặc `en_US-ljspeech-high` (giọng nữ, public domain). `tai_ve.py` cũng phải tải giọng mới này.
2. Giọng Kokoro `am_michael` chỉ được chính tác giả chấm **C+**; giọng tốt nhất là `af_heart` (**A**) và `af_bella` (**A-**), đều giọng nữ ([VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)). Nếu cần giọng nam thì `am_michael` / `am_fenrir` / `am_puck` ngang nhau (C+) — nên nghe thử rồi chốt; khuyến nghị mặc định `af_heart`.
3. Piper (bản đang phát triển `piper1-gpl`) có mã **GPL-3.0**, không còn MIT như bản `rhasspy/piper` cũ ([PyPI](https://pypi.org/project/piper-tts/)). Dùng nội bộ để sinh âm thanh thì không vướng (GPL ràng buộc việc **phân phối phần mềm**, không phải tệp âm thanh sinh ra — theo cách hiểu phổ biến; Piper không tuyên bố gì về điểm này). Chỉ cần lưu ý nếu sau này phát hành repo kèm Piper.
4. Hợp đồng nói đúng: XTTS-v2 (CPML) và F5-TTS (CC-BY-NC) không dùng được cho kênh kiếm tiền.
5. Kokoro ra **24 kHz**, Piper tuỳ giọng (thường 22,05 kHz); `am_thanh.tan_so: 48000` vẫn được, chỉ cần `giai_ma` / trộn đổi tần số mẫu — động cơ phải trả đúng `tan_so` thật của mô hình.
6. Gói `kokoro` yêu cầu **Python >=3.10, <3.13** ([PyPI](https://pypi.org/project/kokoro/)) — Python 3.11 trong hợp đồng hợp lệ; đừng nâng lên 3.13.

---

## 1. Giọng đọc tiếng Anh chạy local

### 1.1 Bảng so sánh

| Mô hình | Giấy phép mã / trọng số | Kiếm tiền YouTube? | Nhân bản giọng | Phần cứng (máy này) | Cài trên Windows |
|---|---|---|---|---|---|
| **Kokoro-82M** v1.0 | Apache-2.0 / Apache-2.0; dữ liệu: public domain, Apache/MIT, âm thanh tổng hợp từ TTS đóng ([model card](https://huggingface.co/hexgrad/Kokoro-82M)) | **Được** | Không (chỉ 54 giọng có sẵn, có thể trộn giọng) | 82M tham số; ~1,2GB VRAM đo trên RTX 3090, <2GB theo hướng dẫn khác ([nguồn tổng hợp](https://docs.clore.ai/guides/audio-and-voice/kokoro-tts)); CPU 8 nhân ~5× thời gian thực. **Chưa có số đo trên GTX 1650** — dự kiến vừa VRAM, nhanh hơn thời gian thực (chưa chắc) | Dễ-vừa: cần PyTorch; espeak-ng chỉ là dự phòng cho từ lạ (xem 1.2) |
| **Piper** (`piper-tts` 1.8.0, 04/09/2026) | GPL-3.0 / **mỗi giọng một giấy phép** theo bộ dữ liệu ([COMMERCIAL_USE.md](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/COMMERCIAL_USE.md)) | Được **với giọng trong danh sách 1.3** | Không (phải huấn luyện lại) | VITS nhỏ, ONNX; chạy CPU rất nhanh; GPU cần `onnxruntime-gpu` | **Dễ nhất**: có wheel `win_amd64`, nhúng espeak-ng ([PyPI](https://pypi.org/project/piper-tts/)) |
| **Chatterbox** (Resemble AI) — Turbo 350M, Nano 110M, Multilingual V3 500M | MIT / MIT | Được, nhưng **mọi tệp có thuỷ vân Perth** | Có (mẫu ~10s) | Turbo "ít VRAM hơn bản cũ" — không công bố số; Nano ~3× thời gian thực trên 8 nhân CPU. Vừa 4GB hay không: **chưa chắc** | Vừa; thử trên Python 3.11/Linux. **Từ 08/2026 dự án "retired", không bảo trì** ([GitHub](https://github.com/resemble-ai/chatterbox)) |
| **StyleTTS2** | MIT / trọng số kèm điều kiện: phải báo người nghe là giọng tổng hợp (trừ khi có phép của chủ giọng) ([GitHub](https://github.com/yl4579/StyleTTS2)) | Được nếu ghi rõ giọng tổng hợp | Có | Nặng hơn Kokoro; có lỗi tiếng rít trên GPU cũ (issue) | Khó: phụ thuộc phonemizer + espeak-ng (GPL, không kèm), repo nhiều issue mở. Kokoro chính là bản kế thừa kiến trúc này nên không cần |
| **XTTS-v2** (Coqui) | MPL (mã) / **CPML** ([HF](https://huggingface.co/coqui/XTTS-v2)) | **Không** — CPML phi thương mại; Coqui đã đóng cửa (đầu 2024) nên không còn nơi mua giấy phép thương mại (theo thông tin rộng rãi, chưa tìm được trang chính thức vì coqui.ai/cpml đã 404) | Có (6s) | ~2,5GB VRAM | Vừa |
| **F5-TTS** v1 | MIT / **CC-BY-NC** do dữ liệu Emilia ([GitHub](https://github.com/SWivid/F5-TTS)) | **Không** | Có | GPU | Vừa |
| **Qwen3-TTS** 0.6B / 1.7B (22/01/2026) | Apache-2.0 / Apache-2.0 | Được | Có (~3s) | Nặng: 0.6B chạy 0,2× thời gian thực trên M4 16GB ([yaps.ai](https://www.yaps.ai/blog/best-local-tts-models)) — **quá chậm cho GTX 1650 / CPU này** (suy luận) | Vừa |
| **Kitten TTS** mini 80M / micro / nano 15M (ONNX) | Mã Apache-2.0; trọng số "licensed separately"; bản KittenTTS 2 (1.7B) dùng Stellon Labs Community License ([GitHub](https://github.com/KittenML/KittenTTS)) | **Chưa chắc** — phải đọc model card từng bản | Chỉ bản 2 | Rất nhẹ, CPU | Dễ |
| **Kyutai Pocket TTS** 100M | CC BY 4.0 + điều khoản cấm dùng sai ([yaps.ai](https://www.yaps.ai/blog/best-local-tts-models)) | Có vẻ được (ghi công) — chưa chắc | Có (repo gated) | CPU ~6× thời gian thực | Chưa kiểm |
| Orpheus 3B, Maya1 3B, Dia 1.6B, Zonos, Sesame CSM-1B | Apache-2.0 (Orpheus còn chịu giấy phép Llama 3.2) ([Cartesia](https://www.cartesia.ai/learn/open-source-tts)) | Được (Orpheus: đọc thêm điều khoản Llama) | Tuỳ mô hình | 1B–3B, Zonos cần ≥6GB → **không hợp 4GB VRAM** | — |
| Spark-TTS, Fish Audio S2, IndexTTS-2.5, Breeze TTS 2, VibeVoice | CC BY-NC-SA / research / bilibili license / research-only | **Không** | — | — | — |

Xếp hạng chất lượng chung (Artificial Analysis, 10/2026, theo [Cartesia](https://www.cartesia.ai/learn/open-source-tts)): trong nhóm giấy phép thoáng, Kokoro 82M đứng đầu cùng NVIDIA Magpie (1064), trên Maya1 (1047), Chatterbox (1023), Zonos (1000). Các mô hình điểm cao hơn (Fish S2, Breeze) đều phi thương mại. Nguồn là blog tổng hợp — coi là tham khảo.

### 1.2 Kokoro — API Python hiện tại (đã đối chiếu mã nguồn)

- Gói: `pip install "kokoro>=0.9.4" soundfile` (bản mới nhất 0.9.4, 05/04/2025; Python 3.10–3.12) ([PyPI](https://pypi.org/project/kokoro/), [README](https://github.com/hexgrad/kokoro)).
- `KPipeline(lang_code, repo_id=None, model=True, trf=False, device=None)`; `lang_code='a'` = American English, `'b'` = British; bí danh `'en-us'`→`'a'`, `'en-gb'`→`'b'` ([pipeline.py](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)).
- Gọi `pipeline(text, voice=None, speed=1, split_pattern=r'\n+', model=None)` → **generator**, mỗi phần tử là `Result` (gỡ được thành bộ ba `(graphemes, phonemes, audio)`). `audio` là `torch.FloatTensor` trên CPU.
- Tần số mẫu cố định **24000 Hz**.
- Giọng phải khớp `lang_code`: giọng `af_*`/`am_*` với `'a'`, `bf_*`/`bm_*` với `'b'`. Nên đặt `repo_id='hexgrad/Kokoro-82M'` để tắt cảnh báo và cố định nguồn tải.
- **espeak-ng trên Windows:** Kokoro chỉ dùng espeak-ng làm **dự phòng cho từ ngoài từ điển** (tên riêng, từ lạ). Nếu khởi tạo thất bại, mã ghi cảnh báo `"EspeakFallback not Enabled: OOD words will be skipped"` — tức **từ lạ bị bỏ qua không đọc**, rất nguy hiểm cho video. `misaki[en]` phụ thuộc gói `espeakng-loader` (có wheel `win_amd64` 9,4MB, nhiều khả năng đóng gói sẵn thư viện espeak-ng — **chưa chắc**) ([misaki pyproject](https://github.com/hexgrad/misaki/blob/main/pyproject.toml), [PyPI espeakng-loader](https://pypi.org/project/espeakng-loader/)). README chính thức vẫn khuyên cài tệp `.msi` từ [espeak-ng releases](https://github.com/espeak-ng/espeak-ng/releases). → `setup.ps1` nên cài MSI cho chắc, và `nq kiem-tra` nên bắt cảnh báo trên (đọc thử một từ lạ, ví dụ "Kahneman", kiểm tra có âm thanh).
- misaki tải mô hình spaCy `en_core_web_sm` lúc chạy lần đầu; nên tải trước trong `setup.ps1` (`python -m spacy download en_core_web_sm`) để không lỗi khi offline ([Kokoro-FastAPI ghi chú](https://code.amethyst.name/public-mirrors/Kokoro-FastAPI/src/branch/v0.1.5-pre/docs/architecture/nlp_dependencies.md)).
- Có hàm `pipeline.load_voice(...)` / có thể truyền tensor giọng `.pt`; trộn giọng bằng chuỗi phân cách dấu phẩy (vd. `"af_heart,af_bella"`) theo mã nguồn — **chưa kiểm chạy**.

```python
# Động cơ Kokoro tối thiểu cho giong.py
import numpy as np
from kokoro import KPipeline

TAN_SO_KOKORO = 24000

pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cuda")  # hoặc "cpu"

def doc(van_ban: str, giong: str = "af_heart", toc_do: float = 1.0) -> tuple[np.ndarray, int]:
    cac_doan = []
    for _gs, _ps, audio in pipeline(van_ban, voice=giong, speed=toc_do, split_pattern=r"\n+"):
        if audio is None:            # đoạn rỗng
            continue
        cac_doan.append(audio.detach().cpu().numpy().astype(np.float32))
    if not cac_doan:
        return np.zeros(0, dtype=np.float32), TAN_SO_KOKORO
    return np.concatenate(cac_doan), TAN_SO_KOKORO
```

Giọng Kokoro tiếng Anh đáng dùng (điểm do tác giả chấm, [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)): `af_heart` A, `af_bella` A-, `af_nicole` B-, `bf_emma` B-, `am_michael` / `am_fenrir` / `am_puck` C+, `af_aoede` / `af_kore` / `af_sarah` C+. Tránh `am_adam` (F+), `am_santa` (D-).

### 1.3 Piper — API Python bản mới (`piper1-gpl`, `piper-tts` 1.8.0)

Đối chiếu mã nguồn [`__init__.py`](https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/__init__.py), [`config.py`](https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/config.py), [`voice.py`](https://github.com/OHF-Voice/piper1-gpl/blob/main/src/piper/voice.py), [API_PYTHON.md](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md):

- `from piper import PiperVoice, SynthesisConfig` (cũng có `AudioChunk`, `PiperConfig`).
- `PiperVoice.load(model_path, config_path=None, use_cuda=False, espeak_data_dir=<dữ liệu kèm gói>, download_dir=None, include_alignments=False)`; `use_cuda=True` cần cài `onnxruntime-gpu`. Tệp `.onnx.json` đặt cạnh `.onnx`.
- `SynthesisConfig(speaker_id=None, length_scale=None, noise_scale=None, noise_w_scale=None, normalize_audio=True, volume=1.0)` — `length_scale` < 1 nhanh hơn, > 1 chậm hơn (để `None` = theo tệp cấu hình giọng). Tốc độ kiểu Kokoro ⇒ `length_scale = 1 / toc_do`.
- `voice.synthesize_wav(text, wav_file: wave.Wave_write, syn_config=None, set_wav_format=True, include_alignments=False)`.
- `voice.synthesize(text, syn_config=None)` → các `AudioChunk` có `sample_rate`, `sample_width`, `sample_channels`, `audio_float_array` (np.ndarray), `audio_int16_bytes`.
- Tần số mẫu: `voice.config.sample_rate`.
- Tải giọng: `python -m piper.download_voices en_US-norman-medium --data-dir mo-hinh/piper` ([CLI.md](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/CLI.md)); giọng lưu trên [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main).

```python
import wave
import numpy as np
from piper import PiperVoice, SynthesisConfig

voice = PiperVoice.load("mo-hinh/piper/en_US-norman-medium.onnx", use_cuda=False)
cfg = SynthesisConfig(length_scale=1.0 / 1.0, normalize_audio=True, volume=1.0)

# Cách 1: ghi thẳng WAV
with wave.open("thu.wav", "wb") as wf:
    voice.synthesize_wav("Loss aversion makes losses feel twice as painful.", wf, syn_config=cfg)

# Cách 2: lấy mảng float32 cho giong.py
def doc(van_ban: str) -> tuple[np.ndarray, int]:
    doan = [c.audio_float_array for c in voice.synthesize(van_ban, syn_config=cfg)]
    mau = np.concatenate(doan).astype(np.float32) if doan else np.zeros(0, np.float32)
    return mau, voice.config.sample_rate
```

**Giọng Piper tiếng Anh dùng thương mại được** (theo [COMMERCIAL_USE.md](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/COMMERCIAL_USE.md)):

| Giọng | Giấy phép dữ liệu | Ghi chú |
|---|---|---|
| `en_US-ljspeech-high` / `-medium` | Public domain | Nữ, giọng đọc sách; chất lượng "high" |
| `en_US-norman-medium` | Public domain | Nam — **đề nghị thay ryan** |
| `en_US-kristin-medium`, `en_US-john-medium` | Public domain | |
| `en_US-joe-medium`, `en_US-mike-medium` | CC0 | |
| `en_US-libritts-high` | CC BY 4.0 | Nhiều người nói (`speaker_id`); phải ghi công LibriTTS |
| `en_US-hifi_tts_92-medium`, `en_GB-alba-medium`, `en_GB-cori-medium` | CC BY 4.0 | Ghi công Hi-Fi TTS |
| `en_GB-cori-high` | Public domain | |
| `en_GB-jenny_dioco-medium` | Riêng, cho thương mại | Phải gọi tên giọng là "Jenny (Dioco)" khi có thể |

**Loại trừ:** `ryan` (phi thương mại), `lessac` và mọi giọng tinh chỉnh từ lessac, `amy` (không rõ giấy phép), `hfc_female` / `hfc_male` (CC BY-NC-SA), `l2arctic`; `bryce` chưa rõ gốc. Lưu ý trang này nói nhiều giọng được **huấn luyện lại cuối 2026 để bỏ gốc lessac**, bản tải cũ cùng tên tệp có thể không đạt — phải mở `MODEL_CARD` kèm giọng, mục Training không được nhắc lessac. `tai_ve.py` nên tải kèm `MODEL_CARD` và lưu cạnh mô hình.

Về chất lượng: theo cảm nhận chung giọng `-high` (ljspeech, libritts) tự nhiên hơn `-medium`, nhưng Piper vẫn kém Kokoro rõ rệt về ngữ điệu (đánh giá định tính, chưa có số đo cùng thước). Phù hợp vai dự phòng / chạy nháp nhanh.

### 1.4 Kết luận giọng

- **Mặc định: Kokoro-82M**, `lang_code='a'`, giọng `af_heart` (hoặc nam `am_michael` sau khi nghe thử), `device='cuda'`, rơi về `cpu` nếu không có CUDA. Kokoro đủ nhẹ để chạy CPU 5500U nếu GPU bận dựng hình.
- **Dự phòng: Piper** `en_US-norman-medium` (nam) / `en_US-ljspeech-high` (nữ), CPU.
- Không đưa mô hình nhân bản giọng vào lúc này: không cần (kênh dùng một giọng cố định), mô hình nhân bản hợp giấy phép (Chatterbox đã ngừng bảo trì, Qwen3-TTS quá nặng) không đáng rủi ro. Nếu sau này muốn giọng riêng: chỉ nhân bản **giọng của chính chủ kênh** (YouTube coi là thay đổi nhỏ, xem 3.2), không bao giờ nhân bản giọng người khác.
- Lưu ý chung: giọng tổng hợp đọc sai số, ký hiệu, tên riêng → giữ `chuan_hoa.py` + `tu-dien-doc.yaml`; sau mỗi lần `nq giong` nên nghe lướt.

---

## 2. Nhạc nền và hiệu ứng âm thanh miễn phí cho kênh kiếm tiền

### 2.1 Nguồn và điều kiện

| Nguồn | Giấy phép | Ghi công | Kiếm tiền | Ghi chú |
|---|---|---|---|---|
| **YouTube Audio Library** (YouTube Studio → Audio library) | Giấy phép riêng của YouTube, hoặc Creative Commons tuỳ bài | Bài "Attribution not required": không cần. Bài Creative Commons: **phải** ghi trong mô tả (bấm biểu tượng CC để chép dòng ghi công) | Được trong YPP | "Chỉ nhạc và SFX trong Audio Library là thứ YouTube biết chắc an toàn bản quyền"; không bị Content ID nhận ([Help](https://support.google.com/youtube/answer/3376882)). Không rõ dùng ngoài YouTube được không — chỉ dùng cho YouTube |
| **Pixabay Music / SFX** | Pixabay Content License | Không bắt buộc | Được | Cấm bán / phân phối lại bản nhạc rời, cấm đăng ký nội dung Pixabay vào Content ID (theo điều khoản đã biết; trang [license](https://pixabay.com/service/license/) trả lỗi 429 khi kiểm — **mở lại để xác nhận**). Một số bài vẫn **có thể bị Content ID nhận nhầm**; giải quyết bằng chứng nhận giấy phép tải kèm (chỉ có khi đăng nhập) ([Pixabay blog](https://pixabay.com/ko/blog/posts/intellectual-property-explained-441/)). → Tải và lưu chứng nhận cho từng bài |
| **Freesound** | CC0 / CC BY / CC BY-NC / Sampling+ (từng âm khác nhau) | CC BY: ghi tên âm, người đăng, link, giấy phép | **Chỉ CC0 và CC BY**. CC BY-NC và Sampling+ **không** dùng cho video kiếm tiền | Mẫu ghi công: `"sound1" by user1 (https://freesound.org/s/<id>/) licensed under CC BY 4.0`; có trang danh sách đã tải `freesound.org/home/attribution/` ([FAQ](https://freesound.org/help/faq/)) |
| **Incompetech** (Kevin MacLeod) | CC BY 4.0 | **Bắt buộc** (mô tả hoặc trong video) | Được ([FAQ](https://incompetech.com/music/royalty-free/faq.html)) | Mẫu: `"<Tên bài>" Kevin MacLeod (incompetech.com)` / `Licensed under Creative Commons: By Attribution 4.0 License` / `http://creativecommons.org/licenses/by/4.0/`. Nhạc rất phổ biến → nghe "cũ" |
| **Kenney** (kenney.nl, gói Interface Sounds, UI Audio, Impact Sounds…) | CC0 (ghi trên từng trang gói — chưa mở lại kiểm hôm nay) | Không | Được | Rất hợp tiếng click / pop / UI |
| **Sonniss GDC Game Audio Bundle** (phát miễn phí hằng năm) | Giấy phép royalty-free của Sonniss | Không | Được | Bản 2024 trở đi cấm dùng để huấn luyện AI; điều khoản đổi theo năm — đọc tệp license trong gói ([licenseorg](https://licenseorg.com/guide/music-audio/sonniss)) |
| Zapsplat | Standard License | **Bắt buộc** với tài khoản miễn phí | Được ([FAQ](https://www.zapsplat.com/faq-category/license-and-usage/)) | Dùng khi cần, nhớ ghi công |
| Mixkit SFX | Mixkit License | Không (theo nguồn thứ cấp — chưa chắc) | Được (chưa chắc) | Video Mixkit có giấy phép khác, không dùng |

Quy ước cho repo: mỗi tệp trong `kho-mau/nhac-nen/` và `kho-mau/am-thanh/` đi kèm một dòng trong `kho-mau/nguon-am-thanh.md` (hoặc `.yaml`): tên tệp, nguồn, link, giấy phép, dòng ghi công. `nq kho` có thể gom các dòng cần ghi công để dán vào mô tả video. **Không** dùng nhạc tạo bằng AI (Suno, Udio…) làm nhạc nền chính nếu chưa đọc điều khoản; nếu nhạc AI là trọng tâm video thì phải bật nhãn nội dung tổng hợp ([Help](https://support.google.com/youtube/answer/14328491)).

### 2.2 Thể loại nhạc hợp nội dung giải thích tâm lý

Tìm trong Audio Library / Pixabay theo tâm trạng (bộ lọc "Mood": Calm, Bright, Funny, Dramatic) và các từ khoá sau:

| Đoạn video | Tâm trạng | Từ khoá tìm |
|---|---|---|
| Hook, đặt câu hỏi | tò mò, tinh nghịch | `curious`, `quirky`, `pizzicato`, `playful`, `mystery light`, `marimba` |
| Giải thích, ví dụ | nhẹ, đều, không lời | `lo-fi`, `chill`, `corporate light`, `ukulele soft`, `minimal piano`, `background explainer` |
| Nghiên cứu / bất ngờ | hồi hộp nhẹ | `suspense light`, `tension pulse`, `investigation`, `ticking`, `thinking` |
| Sai lầm / thua lỗ | trầm, hơi buồn cười | `sad comedic`, `awkward`, `melancholy piano` |
| Cách tránh / kết | sáng, lạc quan | `uplifting`, `inspiring light`, `hopeful` |

Nguyên tắc: không lời, nhịp 80–110 BPM, ít dải trung âm (để không đè giọng), lặp được. Mỗi video 1–3 bài; `sidechaincompress` đã lo giảm nhạc khi có lời. Tránh dùng đúng một bài cho mọi video (giảm cảm giác "mass-produced", xem 3.1).

### 2.3 Danh sách SFX cần có (`kho-mau/am-thanh/`)

| Tên tệp đề xuất | Dùng khi | Nguồn gợi ý |
|---|---|---|
| `pop.wav` | nhân vật / đạo cụ bật lên | Kenney Interface Sounds, YT Audio Library ("pop"), Pixabay |
| `whoosh.wav`, `whoosh-nhe.wav` | chuyển cảnh, trượt | YT Audio Library, Pixabay, Freesound CC0 |
| `ding.wav` | ý đúng, mẹo | YT Audio Library ("bell", "ding"), Kenney |
| `tick.wav`, `go-phim.wav` | gõ chữ (`go-chu`) | Kenney UI Audio, Freesound CC0 ("typewriter", "keyboard") |
| `dong-ho-tich-tac.wav` | áp lực thời gian | Pixabay, Freesound CC0 |
| `cash.wav` (cha-ching), `xu-roi.wav` | tiền vào, lãi | Pixabay ("cash register"), YT Audio Library |
| `error-buzz.wav` | sai, thua lỗ | Kenney, Pixabay ("wrong answer buzzer") |
| `record-scratch.wav` | khựng lại, "wait…" | Pixabay, Freesound CC0 |
| `boing.wav`, `cartoon-slip.wav` | hài, ngã | YT Audio Library (thư mục Cartoon), Pixabay |
| `drum-roll.wav`, `ta-da.wav` | tiết lộ kết quả | YT Audio Library, Pixabay |
| `thud.wav` | biểu đồ rơi, va chạm | Kenney Impact Sounds, Sonniss |
| `rise-tension.wav` (riser) | dẫn vào điểm bất ngờ | Sonniss, Pixabay |
| `crowd-gasp.wav`, `crowd-laugh.wav` | phản ứng | YT Audio Library, Freesound CC BY (ghi công) |
| `heartbeat.wav` | lo lắng, sợ hãi | Pixabay, Freesound CC0 |
| `paper.wav`, `marker.wav` | vẽ biểu đồ, viết bảng | Freesound CC0, Kenney |
| `notification.wav` | tin tức, điện thoại | Kenney, Pixabay |

Chuẩn hoá: WAV 48 kHz mono, cắt lặng đầu, độ lớn đỉnh khoảng −3 dBFS (để `am_luong` trong kịch bản điều chỉnh).

---

## 3. Chính sách YouTube 2025–2026 với giọng AI / tự động hoá

### 3.1 Điều kiện kiếm tiền (YPP)

- **15/07/2025**: chính sách "repetitious content" đổi tên thành **"inauthentic content"**, làm rõ bao gồm nội dung "repetitive or mass-produced". Ví dụ không được kiếm tiền: slideshow / chữ chạy ít lời bình hoặc ít giá trị giáo dục; nhân vật đặt vào cùng tình huống với cùng kết quả lặp lại; "AI-generated content made with generic or unoriginal templates giving the impression of mass production" ([YPP policies](https://support.google.com/youtube/answer/1311392)). YouTube nói rõ: kênh dùng công cụ AI **vẫn đủ điều kiện kiếm tiền** ([eWeek](https://www.eweek.com/news/youtube-responds-to-ai-concerns/), [Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/)).
- **16/07/2026**: hướng dẫn tách thành ba nhóm không kiếm tiền ([TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/), [Tubefilter](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/), [YPP policies](https://support.google.com/youtube/answer/1311392)):
  1. *Generic or repetitive*: giống làm từ khuôn, ít khác biệt giữa các video, "không có mạch truyện".
  2. *Unsatisfying or off-putting*: thiếu mạch truyện / tiến trình logic, dựa nặng vào khuôn chung hoặc chủ đề thao túng cảm xúc, **bắt chước định dạng khác đến mức lẫn lộn**, hình / lời dẫn gây hiểu lầm.
  3. *AI personas related to sensitive topics*: nội dung "presents itself as a human expert providing advice to viewers on topics such as health, legal issues, **finances**, or politics" — ví dụ "AI podcast hosts offering financial guidance".
- **Xét theo cả kênh**: người duyệt xem chủ đề chính, video nhiều view nhất, mới nhất, chiếm nhiều thời gian xem, metadata, mục "About"; vi phạm có thể mất kiếm tiền **toàn kênh**. Ngưỡng "quá nhiều" không được định nghĩa.
- **Reused content**: không kiếm tiền khi chủ yếu đọc lại tài liệu không phải mình viết, ghép nội dung người khác không có bình luận / biến đổi đáng kể — áp dụng **kể cả khi có phép** của tác giả gốc.
- Giọng TTS tự thân **không** bị cấm; vấn đề là hàng loạt, khuôn mẫu, thiếu giá trị (nhiều nguồn tổng hợp đồng ý, ví dụ [Metricool](https://metricool.com/youtube-ai-content-rules-monetization/)).

**Việc kênh này cần làm** (suy ra từ chính sách, không phải danh sách chính thức):

1. Mỗi video một **luận điểm riêng có mạch truyện**: hook → bối cảnh → giải thích → ví dụ → nghiên cứu (dẫn nguồn thật: tên tác giả, năm) → cách tránh → kết. Kịch bản do người duyệt và sửa, không đăng thẳng bản Claude sinh. Giữ bản nháp / ghi chú nghiên cứu làm bằng chứng tác giả.
2. **Không để mọi video giống nhau**: đổi bố cục cảnh, nhạc nền, ví dụ, nhịp; intro / outro giống nhau thì được ("the bulk of the content differs").
3. Nhịp đăng vừa phải (vd. 1–3 video/tuần) — đăng dồn hàng chục video na ná dễ bị coi là "content farm" (suy luận).
4. Nhân vật người que là **hoạt hình rõ ràng**, không phải "chuyên gia người thật". Không đặt tên / dựng hình nhân vật kiểu "Dr. X – financial advisor"; lời dẫn kiểu người kể chuyện / giải thích khái niệm, không xưng là chuyên gia tư vấn.
5. Trang "About" và mô tả nói rõ: kênh giáo dục về tâm lý học hành vi; lời đọc dùng giọng tổng hợp (TTS); kịch bản do người biên soạn có dùng công cụ AI hỗ trợ.
6. Tiêu đề / thumbnail khớp nội dung (không câu view gây hiểu lầm — nhóm 2).
7. Không dùng chủ đề gây sốc / thao túng cảm xúc lặp lại.

### 3.2 Công khai nội dung "altered or synthetic"

Theo [Help 14328491](https://support.google.com/youtube/answer/14328491): phải bật nhãn khi nội dung **thực tế** có thể gây nhầm: người thật nói / làm điều không có, sửa cảnh quay sự kiện / nơi chốn thật, tạo cảnh thực tế chưa từng xảy ra, nhạc AI là trọng tâm. **Miễn**: nội dung rõ ràng phi thực tế, **hoạt hình hoàn toàn**, dùng AI cho dàn ý / kịch bản / thumbnail / tiêu đề / infographic / phụ đề, nhân bản giọng của chính mình để lồng tiếng. Trang không nói thẳng về giọng TTS không phải của chủ kênh; âm thanh AI (không phải nhạc) có thể được YouTube tự gắn nhãn trong mô tả mở rộng. Công khai **không** làm giảm phân phối hay kiếm tiền; không công khai lặp lại có thể bị gắn nhãn, gỡ, hoặc đình chỉ YPP.

→ Với video người que + giọng Kokoro: về nguyên tắc **không bắt buộc** bật nhãn (hoạt hình, giọng không giả người thật). Khuyến nghị: không bật nhãn trừ khi video có cảnh trông thực tế; nhưng **ghi rõ trong mô tả / About** là giọng tổng hợp (minh bạch, và đáp ứng điều kiện của StyleTTS2 nếu có dùng). **Tuyệt đối không** dùng giọng mô phỏng người nổi tiếng / nhà đầu tư thật (Buffett, Munger…) — vừa phải bật nhãn vừa vướng chính sách mạo danh và nhóm 3.

### 3.3 Lưu ý riêng cho nội dung tài chính / đầu tư

- Định vị: **giáo dục tâm lý học hành vi** (thiên kiến, cảm xúc khi đầu tư), không phải tư vấn đầu tư.
- Không nói "mua / bán mã X", không dự đoán giá, không hứa lợi nhuận, không "tín hiệu", không quảng bá coin / sàn / khoá học không rõ ràng — tránh vướng chính sách lừa đảo / nội dung gây hại và nhóm "AI persona tư vấn tài chính".
- Ví dụ cổ phiếu nên dùng mã giả / công ty giả ("Stock A", "Company B") hoặc dữ kiện lịch sử có nguồn.
- Dẫn nghiên cứu có tên tác giả, năm, link trong mô tả (Kahneman & Tversky 1979, Shefrin & Statman 1985…).
- Miễn trừ trách nhiệm ở **cả cuối video (chữ trên hình 2–3 giây) và mô tả**, ví dụ:

  > *This video is for educational and entertainment purposes only and is not financial, investment, or legal advice. I am not a licensed financial advisor. Examples are simplified and hypothetical. Do your own research and consider consulting a qualified professional before making financial decisions.*

  (Thêm câu *"Narration uses a synthetic (text-to-speech) voice."* nếu muốn gộp minh bạch giọng.)
- Nếu sau này có link tiếp thị liên kết / tài trợ: bật hộp "Includes paid promotion" trên YouTube và ghi rõ trong mô tả (yêu cầu của YouTube và luật quảng cáo nước người xem, ví dụ FTC ở Mỹ).
- Nội dung tài chính thường được nhà quảng cáo trả giá cao nhưng cũng bị soi kỹ hơn; giữ tiêu đề không giật gân ("You Will Get RICH…").

---

## 4. Rủi ro bản quyền khi "làm giống" một kênh khác

**Không được bảo hộ** (tự do học theo): ý tưởng, chủ đề, khái niệm, phương pháp, phong cách chung — luật Mỹ 17 U.S.C. §102(b) loại trừ "idea, procedure, process, system, method of operation, concept, principle, or discovery" ([Cornell LII](https://www.law.cornell.edu/uscode/text/17/102)); luật Việt Nam cũng có nguyên tắc tương tự (Luật SHTT, Điều 15 không bảo hộ ý tưởng, quy trình, khái niệm — nhớ theo nội dung luật, chưa mở lại hôm nay). Cụ thể: định dạng "hoạt hình người que giải thích tâm lý", cấu trúc hook → giải thích → ví dụ, nhịp cắt nhanh, chữ to bật lên, dùng SFX pop/whoosh — đều là kỹ thuật chung.

**Được bảo hộ** (không được chép): kịch bản / lời cụ thể của họ (kể cả **dịch sang tiếng Anh** — bản dịch là tác phẩm phái sinh, vừa vi phạm bản quyền vừa trúng "reused content"), hình vẽ nhân vật cụ thể, thiết kế thumbnail cụ thể, nhạc / SFX họ làm hoặc mua giấy phép, đoạn video, bố cục cảnh chép từng khung. Tên kênh, logo, nhân vật đặc trưng còn có thể vướng nhãn hiệu và chính sách **mạo danh** của YouTube ([Impersonation policy](https://support.google.com/youtube/answer/2801947)).

**Ranh giới thực tế cho repo này:**
1. `nq phan-tich` chỉ được rút ra **số liệu cấu trúc** (độ dài cảnh, mật độ chữ, kiểu chuyển cảnh, tỉ lệ các phần) — không lưu / tái dùng lời, hình, nhạc của họ. Bản chép lời (faster-whisper) chỉ để phân tích nhịp, không đưa vào kịch bản; nên xoá sau khi phân tích hoặc giữ ngoài git.
2. Chủ đề trùng (vd. "loss aversion") là bình thường, nhưng **ví dụ, câu chuyện, câu đùa, thứ tự lập luận phải tự viết**; nguồn nghiên cứu lấy từ tài liệu gốc chứ không lấy qua video họ.
3. Nhân vật người que **tự thiết kế** (tên, màu, đạo cụ, nét riêng), không giống nhân vật của họ đến mức nhận ra.
4. Không dùng tên / tiêu đề / thumbnail na ná để người xem nhầm là cùng kênh (nhóm 2 "imitate other formats so they feel interchangeable" + mạo danh).
5. Kênh tham khảo là tiếng Việt, kênh mình tiếng Anh: khác ngôn ngữ **không** làm việc chép lời trở thành hợp pháp.
6. Bị khiếu nại bản quyền (copyright strike) thì 3 cảnh cáo trong 90 ngày là mất kênh — rủi ro lớn hơn nhiều so với lợi ích chép.

---

## Nguồn chính

- Kokoro: https://github.com/hexgrad/kokoro · https://huggingface.co/hexgrad/Kokoro-82M · https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md · https://pypi.org/project/kokoro/ · https://github.com/hexgrad/misaki
- Piper: https://github.com/OHF-Voice/piper1-gpl · docs/API_PYTHON.md · docs/COMMERCIAL_USE.md · docs/CLI.md · https://pypi.org/project/piper-tts/ · https://huggingface.co/rhasspy/piper-voices
- Chatterbox: https://github.com/resemble-ai/chatterbox · StyleTTS2: https://github.com/yl4579/StyleTTS2 · XTTS-v2: https://huggingface.co/coqui/XTTS-v2 · F5-TTS: https://github.com/SWivid/F5-TTS · KittenTTS: https://github.com/KittenML/KittenTTS
- Tổng hợp mô hình 2026: https://www.cartesia.ai/learn/open-source-tts · https://www.yaps.ai/blog/best-local-tts-models
- YouTube: https://support.google.com/youtube/answer/1311392 · https://support.google.com/youtube/answer/14328491 · https://support.google.com/youtube/answer/3376882 · https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/ · https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update/
- Âm thanh: https://freesound.org/help/faq/ · https://incompetech.com/music/royalty-free/faq.html · https://pixabay.com/service/license/ · https://www.zapsplat.com/faq-category/license-and-usage/ · https://licenseorg.com/guide/music-audio/sonniss · https://kenney.nl/assets
- Bản quyền: https://www.law.cornell.edu/uscode/text/17/102
