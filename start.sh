#!/bin/bash

echo "🏠 YUVA BOT BAŞLATILIYOR..."
echo "=========================="

# Virtual environment aktif et
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment aktif edildi"
else
    echo "❌ Virtual environment bulunamadı! Önce install.sh çalıştırın."
    exit 1
fi

# Python ve paket kontrolü
python3 -c "import discord" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Discord.py bulunamadı! Paketleri yüklüyor..."
    pip install -r requirements.txt
fi

# FFmpeg kontrolü
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg bulunamadı! Lütfen FFmpeg'i yükleyin:"
    echo "sudo apt install ffmpeg"
    exit 1
fi

# Bot'u başlat
echo "🤖 Yuva Bot başlatılıyor..."
echo ""

python3 bot.py