# 完整複製專案到 Windows (包含 node_modules)
# 解決 Capacitor plugins 找不到的問題

Write-Host "🔧 完整專案複製工具" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

$WSL_PATH = "\\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal"
$WINDOWS_PATH = "E:\code\AndroidStudioProjects\citizen-portal"

Write-Host "📂 來源: $WSL_PATH" -ForegroundColor Yellow
Write-Host "📂 目標: $WINDOWS_PATH" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  注意: 這會包含 node_modules,可能需要 5-10 分鐘" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "是否繼續? (y/n)"
if ($confirm -ne "y") {
    Write-Host "❌ 取消操作" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📁 建立目標目錄..." -ForegroundColor Green
New-Item -ItemType Directory -Path $WINDOWS_PATH -Force | Out-Null

Write-Host "📋 複製專案檔案 (這可能需要幾分鐘)..." -ForegroundColor Green
Write-Host ""

# 使用 robocopy 複製,排除不必要的檔案
$excludeDirs = @(
    ".git",
    "dist",
    ".vite",
    ".gradle",
    "build",
    "Pods"
)

$excludeFiles = @(
    "*.log",
    ".DS_Store"
)

$excludeDirArgs = $excludeDirs | ForEach-Object { "/XD", $_ }
$excludeFileArgs = $excludeFiles | ForEach-Object { "/XF", $_ }

# 執行 robocopy
robocopy $WSL_PATH $WINDOWS_PATH /E /MT:8 /R:0 /W:0 /NP $excludeDirArgs $excludeFileArgs

$exitCode = $LASTEXITCODE

if ($exitCode -le 7) {
    Write-Host ""
    Write-Host "✅ 複製完成!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 複製統計:" -ForegroundColor Cyan
    Write-Host "  - 包含完整 node_modules (Capacitor plugins 已包含)" -ForegroundColor White
    Write-Host "  - 已排除 .git, dist, .vite 等臨時檔案" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 下一步:" -ForegroundColor Yellow
    Write-Host "1. 在 Android Studio: File → Close Project" -ForegroundColor White
    Write-Host "2. File → Open" -ForegroundColor White
    Write-Host "3. 選擇: $WINDOWS_PATH\android" -ForegroundColor White
    Write-Host "4. 等待 Gradle 同步完成" -ForegroundColor White
    Write-Host "5. 點擊 Run (▶️)" -ForegroundColor White
    Write-Host ""

    $openStudio = Read-Host "要現在開啟 Android Studio 嗎? (y/n)"
    if ($openStudio -eq "y") {
        $studioPath = "C:\Program Files\Android\Android Studio\bin\studio64.exe"
        if (Test-Path $studioPath) {
            Write-Host "🚀 啟動 Android Studio..." -ForegroundColor Green
            Start-Process -FilePath $studioPath -ArgumentList "$WINDOWS_PATH\android"
        } else {
            Write-Host "⚠️  找不到 Android Studio,請手動開啟" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host ""
    Write-Host "❌ 複製時發生錯誤 (代碼: $exitCode)" -ForegroundColor Red
    Write-Host "請檢查路徑是否正確" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 完成!" -ForegroundColor Green
