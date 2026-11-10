"""Chạy `python -m nguoique ...` (tương đương lệnh `nq ...`)."""

import sys

for _luong in (sys.stdout, sys.stderr):
    try:
        _luong.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from .cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
