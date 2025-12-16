# PowerShell 腳本: 安全地從 WSL2 複製專案到 Windows
# 使用方式: 在 Windows PowerShell 中執行此腳本

Write-Host "🔧 WSL2 → Windows 專案複製工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 設定路徑
$WSL_PATH = "\\wsl$\Ubuntu\root\project\citizenApp\src\main\js\citizen-portal"
$WINDOWS_PATH = "C:\AndroidProjects\citizen-portal"

Write-Host "📂 來源: $WSL_PATH" -ForegroundColor Yellow
Write-Host "📂 目標: $WINDOWS_PATH" -ForegroundColor Yellow
Write-Host ""

# 確認是否繼續
$confirm = Read-Host "是否繼續? (y/n)"
if ($confirm -ne "y") {
    Write-Host "❌ 取消操作" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📁 建立目標資料夾..." -ForegroundColor Green
New-Item -ItemType Directory -Path $WINDOWS_PATH -Force | Out-Null

Write-Host "📋 複製必要檔案 (排除 node_modules 等)..." -ForegroundColor Green
Write-Host ""

# 要複製的資料夾清單
$folders = @(
    "src",
    "public",
    "android",
    "ios"
)

# 要複製的檔案清單
$files = @(
    "package.json",
    "package-lock.json",
    "vite.config.js",
    "index.html",
    "capacitor.config.json",
    "README.md",
    "MOBILE_APP_GUIDE.md",
    "QUICK_START.md"
)

# 複製資料夾
foreach ($folder in $folders) {
    $sourcePath = Join-Path $WSL_PATH $folder
    $destPath = Join-Path $WINDOWS_PATH $folder

    if (Test-Path $sourcePath) {
        Write-Host "  📂 複製 $folder..." -ForegroundColor Cyan

        try {
            # 使用 robocopy 複製,排除問題檔案
            $exclude = @(
                "node_modules",
                ".git",
                "dist",
                ".vite",
                ".gradle",
                "build",
                "Pods",
                ".DS_Store"
            )

            $excludeArgs = $exclude | ForEach-Object { "/XD", $_ }

            robocopy $sourcePath $destPath /E /NFL /NDL /NJH /NJS /nc /ns /np $excludeArgs | Out-Null

            if ($LASTEXITCODE -le 7) {
                Write-Host "     ✓ 完成" -ForegroundColor Green
            } else {
                Write-Host "     ⚠ 警告: 部分檔案可能未複製 (代碼: $LASTEXITCODE)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "     ✗ 錯誤: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⊘ 跳過 $folder (不存在)" -ForegroundColor Gray
    }
}

Write-Host ""

# 複製檔案
foreach ($file in $files) {
    $sourcePath = Join-Path $WSL_PATH $file
    $destPath = Join-Path $WINDOWS_PATH $file

    if (Test-Path $sourcePath) {
        Write-Host "  📄 複製 $file..." -ForegroundColor Cyan
        try {
            Copy-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "     ✓ 完成" -ForegroundColor Green
        } catch {
            Write-Host "     ✗ 錯誤: $_" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "✅ 複製完成!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 下一步:" -ForegroundColor Yellow
Write-Host "1. 開啟 Android Studio"
Write-Host "2. File → Open"
Write-Host "3. 選擇: $WINDOWS_PATH\android"
Write-Host "4. 等待 Gradle 同步"
Write-Host "5. 如果 Gradle 同步失敗:"
Write-Host "   - Settings → Build Tools → Gradle → Gradle JDK → 選擇 'jbr-17'"
Write-Host "   - Build → Clean Project"
Write-Host "   - File → Invalidate Caches → Restart"
Write-Host ""

# 詢問是否開啟 Android Studio
$openStudio = Read-Host "要現在開啟 Android Studio 嗎? (y/n)"
if ($openStudio -eq "y") {
    $studioPath = "C:\Program Files\Android\Android Studio\bin\studio64.exe"
    $projectPath = Join-Path $WINDOWS_PATH "android"

    if (Test-Path $studioPath) {
        Write-Host "🚀 啟動 Android Studio..." -ForegroundColor Green
        Start-Process -FilePath $studioPath -ArgumentList $projectPath
    } else {
        Write-Host "⚠ 找不到 Android Studio,請手動開啟" -ForegroundColor Yellow
        Write-Host "   預設路徑: $studioPath" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🎉 完成!" -ForegroundColor Green
