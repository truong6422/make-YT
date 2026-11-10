---
description: Cài đặt lần đầu trên máy chạy (Python, ffmpeg, giọng đọc) và tự kiểm — người dùng không phải gõ gì
---

Người dùng KHÔNG gõ lệnh tay. Bạn tự chạy, tự xử lý lỗi.

1. Chạy `powershell -ExecutionPolicy Bypass -File setup.ps1`. Nếu nó cài Python/ffmpeg rồi yêu cầu mở lại PowerShell: tự làm mới PATH (`$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`) rồi chạy lại setup.ps1.
2. Chạy `.venv\Scripts\python -m nguoique kiem-tra`. Mục nào THIẾU → làm theo cách sửa ghi bên cạnh, chạy lại kiem-tra.
3. Chạy `.venv\Scripts\python -m pytest -q`. Test hỏng → sửa code (không sửa test cho qua nếu code sai), chạy lại.
4. Chạy thử nháp: `.venv\Scripts\python -m nguoique moi thu-nghiem` (bỏ qua nếu đã có) rồi `.venv\Scripts\python -m nguoique lam thu-nghiem --nhap`.
5. Báo người dùng ngắn gọn: cài xong chưa, MP4 thử nằm ở đâu, điều gì còn phải để ý (driver NVIDIA cũ, NVENC lỗi → đã lùi libx264…).

Chỉ hỏi người dùng khi cần quyền quản trị / khởi động lại máy. Không commit.
