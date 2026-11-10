# setup.ps1 - cai dat nguoique tren Windows (Acer Aspire 7, GTX 1650 4GB)
#
# Cach chay (mo PowerShell tai thu muc repo):
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#   powershell -ExecutionPolicy Bypass -File setup.ps1 -DongCo kokoro
#   powershell -ExecutionPolicy Bypass -File setup.ps1 -DongCo piper -BoQuaTaiMoHinh
#
# Cac buoc: Python 3.11 + ffmpeg (winget) -> .venv -> torch CUDA (neu dung Kokoro)
#           -> pip install -e ".[may-chu,phan-tich,<dong co>]" -> espeak-ng + spaCy en_core_web_sm (Kokoro)
#           -> tai mo hinh + font -> nq kiem-tra
#
# Tep nay chi dung ky tu ASCII (PowerShell 5.1 doc sai UTF-8 khong BOM).

param(
    [ValidateSet("kokoro", "piper", "tat-ca")]
    [string]$DongCo = "tat-ca",
    [switch]$BoQuaTaiMoHinh
)

$ErrorActionPreference = "Continue"   # pip ghi canh bao ra stderr; khong de PS coi la loi
Set-Location -Path $PSScriptRoot

# torch cu126: co ban cho Python 3.11 / Windows, ho tro GTX 1650 (Turing, sm_75).
# Can driver NVIDIA >= 528 (CUDA 12.x). Driver cu hon: doi sang https://download.pytorch.org/whl/cu118
$TorchIndex = "https://download.pytorch.org/whl/cu126"

function Write-Step([string]$msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Warn([string]$msg) { Write-Host "CANH BAO: $msg" -ForegroundColor Yellow }
function Stop-IfFailed([string]$msg) {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "LOI: $msg (ma thoat $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
}

# ------------------------------------------------------------ 1. Python 3.11 va ffmpeg
Write-Step "Kiem tra Python 3.11 va ffmpeg"

function Test-Python311 {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 --version *> $null
        if ($LASTEXITCODE -eq 0) { return "py" }
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $v = (& python --version 2>&1 | Out-String)
        if ($v -match "Python 3\.11\.") { return "python" }
    }
    return $null
}

$PyBoot = Test-Python311
$CoFfmpeg = [bool](Get-Command ffmpeg -ErrorAction SilentlyContinue)
$DaCaiMoi = $false

if (-not $PyBoot -or -not $CoFfmpeg) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Host "LOI: khong co winget. Cai 'App Installer' tu Microsoft Store, hoac tu cai Python 3.11 va ffmpeg roi chay lai." -ForegroundColor Red
        exit 1
    }
}

if (-not $PyBoot) {
    Write-Host "Chua co Python 3.11 -> cai qua winget..."
    winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    Stop-IfFailed "cai Python 3.11 qua winget"
    $DaCaiMoi = $true
} else {
    Write-Host "Python 3.11: OK ($PyBoot)"
}

if (-not $CoFfmpeg) {
    Write-Host "Chua co ffmpeg -> cai qua winget (Gyan.FFmpeg)..."
    winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    Stop-IfFailed "cai ffmpeg qua winget"
    $DaCaiMoi = $true
} else {
    Write-Host "ffmpeg: OK"
}

if ($DaCaiMoi) {
    Write-Host ""
    Write-Host "Da cai xong phan mem moi. HAY DONG PowerShell, MO LAI (de nhan PATH moi) roi chay lai:" -ForegroundColor Green
    Write-Host "  powershell -ExecutionPolicy Bypass -File setup.ps1 -DongCo $DongCo"
    exit 0
}

# ------------------------------------------------------------ 2. .venv
Write-Step "Tao moi truong ao .venv"
$Py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    if ($PyBoot -eq "py") { & py -3.11 -m venv .venv } else { & python -m venv .venv }
    Stop-IfFailed "tao .venv"
} else {
    Write-Host ".venv da co, dung lai."
}

& $Py -m pip install --upgrade pip
Stop-IfFailed "nang cap pip"

$CanKokoro = ($DongCo -eq "kokoro" -or $DongCo -eq "tat-ca")
$CanPiper = ($DongCo -eq "piper" -or $DongCo -eq "tat-ca")

# ------------------------------------------------------------ 3. torch CUDA (truoc khi cai kokoro de pip khong keo ban CPU)
if ($CanKokoro) {
    Write-Step "Cai torch ban CUDA ($TorchIndex)"
    & $Py -m pip install torch --index-url $TorchIndex
    Stop-IfFailed "cai torch CUDA. Thu doi TorchIndex sang cu118 trong setup.ps1"
    & $Py -c "import torch; print('torch', torch.__version__, 'cuda:', torch.cuda.is_available())"
    Stop-IfFailed "kiem tra torch"
}

# ------------------------------------------------------------ 4. goi nguoique
$Extras = @("may-chu", "phan-tich")
if ($CanKokoro) { $Extras += "kokoro" }
if ($CanPiper) { $Extras += "piper" }
$Spec = ".[" + ($Extras -join ",") + "]"
Write-Step "pip install -e `"$Spec`""
& $Py -m pip install -e $Spec
Stop-IfFailed "cai goi nguoique $Spec"

# ------------------------------------------------------------ 5. espeak-ng + spaCy (cho Kokoro)
# Kokoro (misaki) dung espeak-ng de doc TU LA (ten rieng, tu ngoai tu dien). Neu espeak-ng khong nap
# duoc, misaki chi canh bao "EspeakFallback not Enabled" va BO QUA tu la -> video mat chu. Vi vay
# cai ban he thong (README kokoro khuyen tren Windows): thu winget truoc, khong duoc thi tai .msi
# tu GitHub releases va cai im lang. Loi o buoc nay chi canh bao (espeakng-loader co the da du).
function Test-Espeak {
    return (Test-Path "C:\Program Files\eSpeak NG\espeak-ng.exe") -or [bool](Get-Command espeak-ng -ErrorAction SilentlyContinue)
}

function Install-EspeakMsi {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $rel = Invoke-RestMethod -Uri "https://api.github.com/repos/espeak-ng/espeak-ng/releases/latest" -Headers @{ "User-Agent" = "nguoique-setup" }
        $msi = @($rel.assets | Where-Object { $_.name -like "*.msi" })
        $chon = @($msi | Where-Object { $_.name -match "x64|X64" })
        if ($chon.Count -eq 0) { $chon = $msi }
        if ($chon.Count -eq 0) { Write-Warn "ban phat hanh espeak-ng moi nhat khong co tep .msi"; return $false }
        $tep = Join-Path $env:TEMP $chon[0].name
        Write-Host "Tai $($chon[0].browser_download_url) ..."
        Invoke-WebRequest -Uri $chon[0].browser_download_url -OutFile $tep -UseBasicParsing
        $p = Start-Process msiexec.exe -ArgumentList @("/i", "`"$tep`"", "/qn", "/norestart") -Wait -PassThru -Verb RunAs
        return ($p.ExitCode -eq 0)
    } catch {
        Write-Warn "cai espeak-ng tu .msi loi: $($_.Exception.Message)"
        return $false
    }
}

if ($CanKokoro) {
    Write-Step "espeak-ng (doc tu la cho Kokoro)"
    if (Test-Espeak) {
        Write-Host "espeak-ng: OK"
    } else {
        $DaCai = $false
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install -e --id eSpeak-NG.eSpeak-NG --accept-source-agreements --accept-package-agreements
            $DaCai = ($LASTEXITCODE -eq 0) -or (Test-Espeak)
        }
        if (-not $DaCai) {
            Write-Host "winget khong cai duoc espeak-ng -> thu tep .msi tu GitHub..."
            $DaCai = (Install-EspeakMsi) -or (Test-Espeak)
        }
        if ($DaCai) {
            Write-Host "espeak-ng: da cai"
        } else {
            Write-Warn "chua cai duoc espeak-ng. Tai tay tep .msi tai https://github.com/espeak-ng/espeak-ng/releases roi chay lai setup.ps1"
        }
    }

    # misaki tai mo hinh spaCy en_core_web_sm luc chay lan dau; tai truoc de chay offline duoc
    Write-Step "Mo hinh spaCy en_core_web_sm (misaki can)"
    & $Py -c "import en_core_web_sm" *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "en_core_web_sm: OK"
    } else {
        & $Py -m spacy download en_core_web_sm
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "khong tai duoc en_core_web_sm (ma $LASTEXITCODE). Lan dau chay Kokoro se tu tai (can mang)."
        }
    }
}

# ------------------------------------------------------------ 6. tai mo hinh + font
if (-not $BoQuaTaiMoHinh) {
    Write-Step "Tai font"
    & $Py -m nguoique tai-mo-hinh font
    Stop-IfFailed "tai font"
    if ($CanPiper) {
        Write-Step "Tai mo hinh Piper"
        & $Py -m nguoique tai-mo-hinh piper
        Stop-IfFailed "tai mo hinh Piper"
    }
    if ($CanKokoro) {
        Write-Step "Tai mo hinh Kokoro (lan dau ~330MB tu Hugging Face)"
        & $Py -m nguoique tai-mo-hinh kokoro
        Stop-IfFailed "tai mo hinh Kokoro"
    }
} else {
    Write-Host "Bo qua tai mo hinh (-BoQuaTaiMoHinh)."
}

# ------------------------------------------------------------ 7. kiem tra
Write-Step "nq kiem-tra"
& $Py -m nguoique kiem-tra
Stop-IfFailed "nq kiem-tra bao loi (xem chi tiet o tren)"

Write-Host ""
Write-Host "XONG. Kich hoat moi truong: .\.venv\Scripts\Activate.ps1  (sau do dung lenh: nq ...)" -ForegroundColor Green
Write-Host "Mo may chu giong (cua so rieng): nq may-chu"
