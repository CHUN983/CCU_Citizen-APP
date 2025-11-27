#!/bin/bash
cd /root/project/citizenApp/src/main/js/citizen-portal

echo "🔨 Building Vue app..."
npm run build

if [ $? -eq 0 ]; then
    echo ""
    echo "🔄 Syncing to Android platform..."
    npx cap sync
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Build and sync complete!"
        echo ""
        echo "📱 Next steps:"
        echo "1. Open Windows File Explorer"
        echo "2. Navigate to: \\\\wsl\$\\Ubuntu\\root\\project\\citizenApp\\src\\main\\js\\citizen-portal\\android"
        echo "3. Right-click and open with Android Studio"
        echo "4. Wait for Gradle sync to complete"
        echo "5. Click the Run button (▶️) to launch the app"
        echo ""
        echo "🚀 Or use this command in Windows PowerShell:"
        echo "   cd \\\\wsl\$\\Ubuntu\\root\\project\\citizenApp\\src\\main\\js\\citizen-portal\\android"
        echo "   & \"E:\\program_file\\Android\\Android Studio\\bin\\studio64.exe\" ."
    else
        echo "❌ Capacitor sync failed!"
        exit 1
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
