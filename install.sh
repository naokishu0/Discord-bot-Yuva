#!/bin/bash

echo "🏠 YUVA BOT KURULUM BAŞLATIYOR..."
echo "=================================="

# Sistem güncellemesi
echo "📦 Sistem güncelleniyor..."
sudo apt update && sudo apt upgrade -y

# Gerekli paketleri yükle
echo "🔧 Gerekli paketler yükleniyor..."
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# FFmpeg kontrolü
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg kurulumu başarısız!"
    exit 1
fi

# Virtual environment oluştur
echo "🐍 Python virtual environment oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate

# Python paketlerini yükle
echo "📥 Python paketleri yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

# Başlatma scriptini çalıştırılabilir yap
chmod +x start.sh

echo ""
echo "🎉 KURULUM TAMAMLANDI!"
echo "======================"
echo ""
echo "🚀 Bot'u başlatmak için: ./start.sh"
echo "📖 Detaylar için: README.md dosyasını okuyun"
echo ""
echo "🏠 Yuva Bot hazır!"