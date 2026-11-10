# Giọng mẫu

**Hiện chưa cần dùng thư mục này.**

Động cơ giọng mặc định **Kokoro-82M** (Apache-2.0) dùng các **giọng có sẵn** trong mô hình — không cần tệp ghi âm mẫu. Chọn giọng ở `config.yaml`:

```yaml
tts:
  kokoro: {giong: am_michael, toc_do: 1.0, ma_ngon_ngu: a}   # a = American English
```

Muốn đổi giọng, đổi `giong` sang giọng khác Kokoro có sẵn (danh sách trong tài liệu của mô hình), dựng nháp thử một đoạn rồi mới dùng cho cả video. Nên nghe thử `af_heart` (nữ, tác giả chấm A), `am_fenrir`, `am_puck` (nam, ngang `am_michael`) trước khi chốt — xem chú thích trong `config.yaml` và [docs/03](../docs/03-GIONG-DOC-NHAC-GIAY-PHEP.md). Piper (dự phòng) cũng dùng mô hình giọng có sẵn (`tts.piper.mo_hinh`, mặc định `en_US-norman-medium` — được dùng thương mại; **không** dùng `en_US-ryan-*`, `lessac`, `amy`).

## Để dành cho sau này

Thư mục này để dành nếu sau này dùng mô hình **nhân bản giọng** (cần vài chục giây ghi âm mẫu). Khi đó:

- **Chỉ dùng giọng mình có quyền**: giọng của chính mình, hoặc người đã đồng ý bằng văn bản cho dùng trên kênh có kiếm tiền.
- **Không** nhân bản giọng người nổi tiếng, giọng lấy từ video / kênh khác.
- Kiểm giấy phép của mô hình nhân bản: nhiều mô hình phổ biến (vd. XTTS-v2, F5-TTS) có giấy phép **phi thương mại** — không dùng cho kênh bật kiếm tiền.
- Thêm động cơ mới là việc của code (`nguoique/giong.py`) và phải theo `docs/00-HOP-DONG.md`.
- Tệp ghi âm mẫu là dữ liệu cá nhân — cân nhắc không đưa lên git công khai.
