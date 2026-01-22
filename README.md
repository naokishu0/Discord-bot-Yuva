# 🏠 Yuva Bot - Tam Özellikli Discord Botu

**Yuva** Discord sunucusu için özel olarak kodlanmış, ErensiBot ve Marpel Bot özelliklerini içeren gelişmiş Discord botu.

## 🎯 Özellikler

### 👑 **Sahip Komutları**
- `!owner` - Bot sahibi bilgileri

### 🛡️ **Admin Komutları (Sadece Adminler)**
- `!ekip <user_id>` - Ekip rolü ver/kaldır (ID: 1460458108181545022)
- `!yetkili <user_id>` - Yetkili rolü ver/kaldır (ID: 1461144641792508089)
- `!ban <@kullanıcı> [sebep]` - Kullanıcı banla
- `!kick <@kullanıcı> [sebep]` - Kullanıcı at
- `!temizle <sayı>` - Mesaj sil (max 100)

### 🎉 **Çekiliş Sistemi**
- `!çekiliş <süre> <kazanan_sayısı> <ödül>` - Çekiliş başlat
- **Süre formatları:** `1h` (1 saat), `30m` (30 dakika), `1d` (1 gün)
- **Örnek:** `!çekiliş 2h 3 Discord Nitro`
- Otomatik kazanan seçimi ve duyuru

### 🎫 **Ticket Sistemi**
- `!ticket` - Yeni destek ticket'ı oluştur
- `!kapat` - Ticket'ı kapat (sahip veya admin)
- Otomatik kategori oluşturma
- Yetki yönetimi

### 🎵 **Müzik Sistemi (Joy FM)**
- `!katıl <kanal_id>` - Sesli kanala katıl ve Joy FM çal
- `!dur` - Müziği durdur ve kanaldan ayrıl
- **Joy FM** canlı yayın desteği
- FFmpeg tabanlı ses sistemi

### 🎊 **Giriş/Çıkış Sistemi (ErensiBot Tarzı)**
- Otomatik hoş geldin mesajları (embed + resim)
- Otomatik ayrılma mesajları
- Üye sayısı takibi
- Özelleştirilebilir kanallar

### ⚙️ **Ayar Komutları**
- `!hoşgeldin-ayarla <#kanal>` - Hoş geldin kanalı belirle
- `!görüşürüz-ayarla <#kanal>` - Ayrılma kanalı belirle

## 📦 Kurulum

### **Raspberry Pi'de Kurulum:**

```bash
# 1. Dosyaları indir
git clone https://github.com/[repo]/YuvaBot
cd YuvaBot

# 2. Kurulum scriptini çalıştır
chmod +x install.sh
./install.sh

# 3. Bot'u başlat
./start.sh
```

### **Manuel Kurulum:**

```bash
# Sistem paketleri
sudo apt update
sudo apt install python3 python3-pip python3-venv ffmpeg git -y

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Python paketleri
pip install -r requirements.txt

# Bot'u çalıştır
python3 bot.py
```

## 🔧 Yapılandırma

### **Bot Token:**
`bot.py` dosyasında TOKEN değişkenini güncelleyin:
```python
TOKEN = "your_bot_token_here"
```

### **Rol ID'leri:**
```python
EKIP_ROLE_ID = 1460458108181545022      # Ekip rolü
YETKILI_ROLE_ID = 1461144641792508089   # Yetkili rolü
OWNER_ID = your_discord_id              # Sahip ID'si
```

### **Joy FM URL:**
Radyo URL'si otomatik olarak ayarlanmıştır. Değiştirmek için:
```python
JOY_FM_URL = "https://playerservices.streamtheworld.com/api/livestream-redirect/JOY_FMAAC.aac"
```

## 🎮 Kullanım Örnekleri

### **Çekiliş Başlatma:**
```
!çekiliş 1h 2 Discord Nitro
!çekiliş 30m 1 Steam Oyunu
!çekiliş 1d 5 Özel Rol
```

### **Rol Yönetimi:**
```
!ekip 123456789012345678
!yetkili 987654321098765432
```

### **Müzik Sistemi:**
```
!katıl 1234567890123456789  # Sesli kanal ID'si
!dur                        # Müziği durdur
```

### **Ticket Sistemi:**
```
!ticket                     # Yeni ticket aç
!kapat                      # Ticket'ı kapat
```

## 🗄️ Veritabanı

Bot SQLite kullanır ve şu tabloları oluşturur:

- **users** - Kullanıcı bilgileri, bakiye, XP
- **giveaways** - Çekiliş bilgileri
- **tickets** - Ticket kayıtları
- **guild_settings** - Sunucu ayarları
- **command_usage** - Komut kullanım istatistikleri

## 🔒 Güvenlik

### **Yetki Sistemi:**
- **Owner:** Tüm komutlara erişim
- **Admin:** Moderasyon ve yönetim komutları
- **Kullanıcı:** Temel komutlar (ticket, vb.)

### **Rol Koruması:**
- Sadece adminler rol verebilir
- Kendi rolünden yüksek role sahip kullanıcıları banlayamaz
- Otomatik yetki kontrolü

## 📊 Özellik Detayları

### **Giriş/Çıkış Sistemi:**
- ErensiBot tarzı embed mesajları
- Kullanıcı avatarı ve bilgileri
- Üye sayısı güncellemesi
- Özelleştirilebilir mesajlar

### **Çekiliş Sistemi:**
- Emoji tabanlı katılım (🎁)
- Otomatik kazanan seçimi
- Çoklu kazanan desteği
- Zaman tabanlı bitiş

### **Ticket Sistemi:**
- Otomatik kanal oluşturma
- Yetki tabanlı erişim
- Admin bildirimleri
- Temiz kapatma sistemi

### **Müzik Sistemi:**
- Joy FM canlı yayın
- FFmpeg tabanlı ses
- Otomatik yeniden bağlanma
- Sesli kanal yönetimi

## 🚀 Performans

### **Sistem Gereksinimleri:**
- **Python 3.7+**
- **FFmpeg** (müzik için)
- **2GB RAM** (önerilen)
- **İnternet bağlantısı**

### **Optimizasyonlar:**
- Async/await kullanımı
- Veritabanı connection pooling
- Bellek yönetimi
- Hata yakalama

## 🔄 Otomatik Başlatma

### **Systemd Servisi:**
```bash
sudo nano /etc/systemd/system/yuva-bot.service
```

```ini
[Unit]
Description=Yuva Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/YuvaBot
ExecStart=/home/pi/YuvaBot/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable yuva-bot
sudo systemctl start yuva-bot
```

### **Crontab:**
```bash
crontab -e
# Ekle:
@reboot cd /home/pi/YuvaBot && ./start.sh
```

## 🛠️ Sorun Giderme

### **FFmpeg Hatası:**
```bash
sudo apt install ffmpeg
# veya
sudo apt update && sudo apt install ffmpeg
```

### **Discord.py Hatası:**
```bash
pip install --upgrade discord.py[voice]
```

### **Yetki Hatası:**
```bash
chmod +x install.sh start.sh
```

### **Token Hatası:**
- Discord Developer Portal'dan yeni token alın
- Bot'u sunucuya davet edin (tüm yetkilerle)

## 📞 Destek

### **Log Kontrolü:**
```bash
# Bot loglarını görüntüle
tail -f yuva_bot.log

# Sistem logları
journalctl -u yuva-bot -f
```

### **Veritabanı Yedekleme:**
```bash
cp yuva_bot.db yuva_bot_backup.db
```

## 🎯 Gelecek Özellikler

- [ ] Web dashboard
- [ ] Ekonomi sistemi genişletme
- [ ] Müzik playlist sistemi
- [ ] Otomatik moderasyon
- [ ] Seviye sistemi
- [ ] Özel komut oluşturma

---

## 📋 Komut Listesi

| Kategori | Komut | Açıklama | Yetki |
|----------|-------|----------|-------|
| **Sahip** | `!owner` | Bot sahibi bilgileri | Owner |
| **Rol** | `!ekip <id>` | Ekip rolü ver/al | Admin |
| **Rol** | `!yetkili <id>` | Yetkili rolü ver/al | Admin |
| **Mod** | `!ban <@user>` | Kullanıcı banla | Admin |
| **Mod** | `!kick <@user>` | Kullanıcı at | Admin |
| **Mod** | `!temizle <sayı>` | Mesaj sil | Admin |
| **Çekiliş** | `!çekiliş <süre> <sayı> <ödül>` | Çekiliş başlat | Admin |
| **Ticket** | `!ticket` | Ticket oluştur | Herkes |
| **Ticket** | `!kapat` | Ticket kapat | Sahip/Admin |
| **Müzik** | `!katıl <id>` | Sesli kanala katıl | Admin |
| **Müzik** | `!dur` | Müziği durdur | Admin |
| **Ayar** | `!hoşgeldin-ayarla <#kanal>` | Hoş geldin kanalı | Admin |
| **Ayar** | `!görüşürüz-ayarla <#kanal>` | Ayrılma kanalı | Admin |
| **Genel** | `!yardım` | Komut listesi | Herkes |

---

*🏠 Yuva Bot v2.0 - Özel olarak Yuva Discord sunucusu için kodlandı*