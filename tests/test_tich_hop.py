"""Tích hợp: `nq dung <du-an> --nhap` với giọng gia-lap ra MP4 đúng thời lượng (cần ffmpeg + ffprobe)."""

import json
import shutil
import subprocess

import pytest
import yaml

from nguoique.cli import main
from nguoique.dong_thoi_gian import lap_dong_thoi_gian
from nguoique.giong import tao_giong_du_an
from nguoique.kichban import nap_kich_ban

from conftest import ghi_kich_ban, kb_toi_gian

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="cần ffmpeg + ffprobe trong PATH",
)


def _ffprobe(tep):
    kq = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,duration",
         "-of", "json", str(tep)],
        capture_output=True, check=True, timeout=60,
    )
    return json.loads(kq.stdout.decode("utf-8"))


def test_dung_nhap_hai_canh_ra_mp4(ch, tmp_path):
    tep_ch = tmp_path / "config-test.yaml"
    tep_ch.write_text(yaml.safe_dump(ch, allow_unicode=True), encoding="utf-8")

    thu_muc = tmp_path / "du-an" / "thu"
    ghi_kich_ban(thu_muc, kb_toi_gian(so_canh=2, loi=True))

    ma = main(["--cau-hinh", str(tep_ch), "dung", str(thu_muc), "--nhap"])
    assert ma == 0

    mp4 = thu_muc / "thu.mp4"
    srt = thu_muc / "thu.srt"
    assert mp4.is_file() and mp4.stat().st_size > 0
    assert srt.is_file() and "-->" in srt.read_text(encoding="utf-8")

    # thời lượng mong đợi: dựng lại dòng thời gian từ bộ đệm giọng (không đọc lại)
    kb = nap_kich_ban(thu_muc / "kich-ban.json", ch)
    giong = tao_giong_du_an(kb, thu_muc / "build", ch)
    assert set(giong) == {"c01", "c02"}
    _ds, tong = lap_dong_thoi_gian(kb, giong, ch)

    tt = _ffprobe(mp4)
    video = [s for s in tt["streams"] if s.get("codec_type") == "video"]
    am = [s for s in tt["streams"] if s.get("codec_type") == "audio"]
    assert len(video) == 1 and len(am) == 1
    assert (int(video[0]["width"]), int(video[0]["height"])) == (640, 360)
    assert float(video[0]["duration"]) == pytest.approx(round(tong * 15) / 15.0, abs=0.1)
    assert float(tt["format"]["duration"]) == pytest.approx(tong, abs=0.2)
