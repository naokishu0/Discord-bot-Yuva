import os
import discord
from discord.ext import commands, tasks
import asyncio
import aiohttp
import json
import sqlite3
import random
from datetime import datetime, timedelta
import requests
import youtube_dl
from discord import FFmpegPCMAudio, FFmpegOpusAudio
import re

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=['.', '!'], intents=intents, help_command=None)

# Token
TOKEN = "MTQ0OTc1NTE3OTA3NDE5NTU4OQ.GKzUTt.Fcv4m4pY4HO-9sowJFRIzUuyZIs_6GW6apRU1A"

# Rol ID'leri
EKIP_ROLE_ID = 1460458108181545022
YETKILI_ROLE_ID = 1461144641792508089

# Owner ID (senin Discord ID'n)
OWNER_ID = 144758869337518082  # Buraya kendi ID'ni koy

# Joy FM Radio URL
JOY_FM_URL = "https://playerservices.streamtheworld.com/api/livestream-redirect/JOY_FMAAC.aac"

# Database setup
def init_db():
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, balance INTEGER DEFAULT 1000, 
                  xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, warnings INTEGER DEFAULT 0)''')
    
    # Giveaways table
    c.execute('''CREATE TABLE IF NOT EXISTS giveaways
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, message_id INTEGER, channel_id INTEGER,
                  prize TEXT, end_time DATETIME, winner_count INTEGER, creator_id INTEGER,
                  active INTEGER DEFAULT 1)''')
    
    # Tickets table
    c.execute('''CREATE TABLE IF NOT EXISTS tickets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, channel_id INTEGER,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP, closed INTEGER DEFAULT 0)''')
    
    # Welcome/Leave settings
    c.execute('''CREATE TABLE IF NOT EXISTS guild_settings
                 (guild_id INTEGER PRIMARY KEY, welcome_channel INTEGER, leave_channel INTEGER,
                  welcome_message TEXT, leave_message TEXT, ticket_category INTEGER)''')
    
    # Command usage
    c.execute('''CREATE TABLE IF NOT EXISTS command_usage
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, user_id INTEGER, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Helper functions
def log_command(command_name, user_id):
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO command_usage (command, user_id) VALUES (?, ?)",
              (command_name, user_id))
    conn.commit()
    conn.close()

def is_admin():
    def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id == OWNER_ID
    return commands.check(predicate)

def is_owner():
    def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

# Bot events
@bot.event
async def on_ready():
    print(f'''
    🏠 YUVA BOT ONLINE!
    ==================
    🤖 Bot: {bot.user}
    📊 Sunucular: {len(bot.guilds)}
    👥 Kullanıcılar: {len(bot.users)}
    🏓 Ping: {round(bot.latency * 1000)}ms
    
    🎯 Özellikler:
    ✅ Giriş/Çıkış Sistemi
    ✅ Ticket Sistemi
    ✅ Çekiliş Sistemi
    ✅ Müzik Sistemi (Joy FM)
    ✅ Moderasyon
    ✅ Rol Yönetimi
    ''')
    
    # Status rotation
    activities = [
        discord.Game("Yuva Sunucusunu Koruyor 🏠"),
        discord.Activity(type=discord.ActivityType.watching, name="Yuva Üyelerini"),
        discord.Activity(type=discord.ActivityType.listening, name="Joy FM 📻"),
        discord.Game(".yardım | Yuva Bot")
    ]
    
    while True:
        for activity in activities:
            await bot.change_presence(activity=activity, status=discord.Status.online)
            await asyncio.sleep(60)

# Giriş/Çıkış Sistemi
@bot.event
async def on_member_join(member):
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("SELECT welcome_channel, welcome_message FROM guild_settings WHERE guild_id = ?", 
              (member.guild.id,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        channel = bot.get_channel(result[0])
        if channel:
            # ErensiBot tarzı hoş geldin mesajı
            embed = discord.Embed(
                title="🎉 Hoş Geldin!",
                description=f"**{member.mention}** Yuva'ya hoş geldin! 🏠",
                color=0x00ff88,
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.add_field(name="👤 Kullanıcı", value=f"{member.name}#{member.discriminator}", inline=True)
            embed.add_field(name="🆔 ID", value=member.id, inline=True)
            embed.add_field(name="📅 Hesap Oluşturma", value=member.created_at.strftime("%d.%m.%Y"), inline=True)
            embed.add_field(name="👥 Üye Sayısı", value=f"Yuva'da şimdi **{member.guild.member_count}** kişi var!", inline=False)
            
            embed.set_footer(text=f"Yuva • {member.guild.name}", icon_url=member.guild.icon.url if member.guild.icon else None)
            
            # Hoş geldin resmi (ErensiBot tarzı)
            file = discord.File("welcome_template.png", filename="welcome.png") if os.path.exists("welcome_template.png") else None
            if file:
                embed.set_image(url="attachment://welcome.png")
            
            await channel.send(f"Hoş geldin {member.mention}! 🎊 @Mami029 seninle birlikte Yuva'da şeninle birlikte **{member.guild.member_count}** kişi olduk.", 
                             embed=embed, file=file)

@bot.event
async def on_member_remove(member):
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("SELECT leave_channel FROM guild_settings WHERE guild_id = ?", (member.guild.id,))
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        channel = bot.get_channel(result[0])
        if channel:
            embed = discord.Embed(
                title="😢 Görüşürüz!",
                description=f"**{member.name}#{member.discriminator}** Yuva'dan ayrıldı...",
                color=0xff4444,
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.add_field(name="👥 Kalan Üye", value=f"Yuva'da şimdi **{member.guild.member_count}** kişi kaldı.", inline=False)
            embed.set_footer(text=f"Yuva • {member.guild.name}")
            
            await channel.send(f"Yuva Sunucumuzdan ayrıldığın için üzgünüz. Sen gidince **{member.guild.member_count}** kişi kaldık.", embed=embed)

# OWNER KOMUTU
@bot.command(name='owner')
@is_owner()
async def owner(ctx):
    embed = discord.Embed(
        title="👑 Bot Sahibi",
        description="Bu bot **Yuva** sunucusu için özel olarak kodlanmıştır.",
        color=0xffd700
    )
    
    owner = bot.get_user(OWNER_ID)
    if owner:
        embed.add_field(name="👤 Sahip", value=f"{owner.mention}", inline=True)
        embed.add_field(name="🏠 Sunucu", value="Yuva Discord", inline=True)
        embed.add_field(name="🤖 Bot", value=bot.user.mention, inline=True)
        embed.set_thumbnail(url=owner.avatar.url if owner.avatar else owner.default_avatar.url)
    
    embed.add_field(name="📊 İstatistikler", 
                   value=f"**Sunucular:** {len(bot.guilds)}\n**Kullanıcılar:** {len(bot.users)}\n**Ping:** {round(bot.latency * 1000)}ms", 
                   inline=False)
    
    await ctx.send(embed=embed)
    log_command('owner', ctx.author.id)

# ROL YÖNETİMİ
@bot.command(name='ekip')
@is_admin()
async def ekip(ctx, user_id: int):
    try:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)
        member = ctx.guild.get_member(user_id)
        
        if not member:
            return await ctx.send("❌ Bu kullanıcı sunucuda bulunamadı!")
        
        role = ctx.guild.get_role(EKIP_ROLE_ID)
        if not role:
            return await ctx.send("❌ Ekip rolü bulunamadı!")
        
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="🔴 Ekip Rolü Kaldırıldı",
                description=f"**{member.mention}** kullanıcısından **{role.name}** rolü kaldırıldı.",
                color=0xff4444
            )
        else:
            await member.add_roles(role)
            embed = discord.Embed(
                title="🟢 Ekip Rolü Verildi",
                description=f"**{member.mention}** kullanıcısına **{role.name}** rolü verildi.",
                color=0x00ff88
            )
        
        embed.add_field(name="👤 Kullanıcı", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="🛡️ Yetkili", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await ctx.send(embed=embed)
        log_command('ekip', ctx.author.id)
        
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

@bot.command(name='yetkili')
@is_admin()
async def yetkili(ctx, user_id: int):
    try:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)
        member = ctx.guild.get_member(user_id)
        
        if not member:
            return await ctx.send("❌ Bu kullanıcı sunucuda bulunamadı!")
        
        role = ctx.guild.get_role(YETKILI_ROLE_ID)
        if not role:
            return await ctx.send("❌ Yetkili rolü bulunamadı!")
        
        if role in member.roles:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="🔴 Yetkili Rolü Kaldırıldı",
                description=f"**{member.mention}** kullanıcısından **{role.name}** rolü kaldırıldı.",
                color=0xff4444
            )
        else:
            await member.add_roles(role)
            embed = discord.Embed(
                title="🟢 Yetkili Rolü Verildi",
                description=f"**{member.mention}** kullanıcısına **{role.name}** rolü verildi.",
                color=0x00ff88
            )
        
        embed.add_field(name="👤 Kullanıcı", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="🛡️ Yetkili", value=ctx.author.mention, inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await ctx.send(embed=embed)
        log_command('yetkili', ctx.author.id)
        
    except Exception as e:
        await ctx.send(f"❌ Hata: {e}")

# MODERASYON KOMUTLARI (Sadece Adminler)
@bot.command(name='ban')
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    if member == ctx.author:
        return await ctx.send("❌ Kendinizi banlayamazsınız!")
    
    if member.top_role >= ctx.author.top_role and ctx.author.id != OWNER_ID:
        return await ctx.send("❌ Bu kullanıcıyı banlamak için yeterli yetkiniz yok!")
    
    try:
        # DM gönder
        dm_embed = discord.Embed(
            title="🔨 Yuva'dan Banlandınız",
            description=f"**Sebep:** {reason}",
            color=0xff0000
        )
        dm_embed.add_field(name="🛡️ Yetkili", value=f"{ctx.author.name}#{ctx.author.discriminator}", inline=True)
        dm_embed.set_footer(text="Yuva Discord Sunucusu")
        
        try:
            await member.send(embed=dm_embed)
        except:
            pass
        
        await member.ban(reason=f"Yetkili: {ctx.author} | Sebep: {reason}")
        
        embed = discord.Embed(
            title="🔨 Kullanıcı Banlandı",
            description=f"**{member}** Yuva'dan banlandı!",
            color=0xff0000
        )
        embed.add_field(name="🛡️ Yetkili", value=ctx.author.mention, inline=True)
        embed.add_field(name="📝 Sebep", value=reason, inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await ctx.send(embed=embed)
        log_command('ban', ctx.author.id)
        
    except Exception as e:
        await ctx.send(f"❌ Ban işlemi başarısız: {e}")

@bot.command(name='kick')
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="Sebep belirtilmedi"):
    if member == ctx.author:
        return await ctx.send("❌ Kendinizi atamazsınız!")
    
    try:
        await member.kick(reason=f"Yetkili: {ctx.author} | Sebep: {reason}")
        
        embed = discord.Embed(
            title="👢 Kullanıcı Atıldı",
            description=f"**{member}** Yuva'dan atıldı!",
            color=0xff9900
        )
        embed.add_field(name="🛡️ Yetkili", value=ctx.author.mention, inline=True)
        embed.add_field(name="📝 Sebep", value=reason, inline=True)
        
        await ctx.send(embed=embed)
        log_command('kick', ctx.author.id)
        
    except Exception as e:
        await ctx.send(f"❌ Kick işlemi başarısız: {e}")

@bot.command(name='temizle', aliases=['clear', 'sil'])
@is_admin()
async def temizle(ctx, miktar: int = 5):
    if miktar > 100:
        return await ctx.send("❌ En fazla 100 mesaj silebilirsiniz!")
    
    deleted = await ctx.channel.purge(limit=miktar + 1)
    
    embed = discord.Embed(
        title="🗑️ Mesajlar Temizlendi",
        description=f"**{len(deleted) - 1}** mesaj silindi.",
        color=0x00ff88
    )
    embed.add_field(name="🛡️ Yetkili", value=ctx.author.mention, inline=True)
    
    msg = await ctx.send(embed=embed)
    await asyncio.sleep(5)
    await msg.delete()
    log_command('temizle', ctx.author.id)

# ÇEKİLİŞ SİSTEMİ
@bot.command(name='çekiliş', aliases=['giveaway'])
@is_admin()
async def cekilis(ctx, süre, kazanan_sayısı: int, *, ödül):
    # Süre parse et (örn: 1h, 30m, 1d)
    time_regex = re.match(r"(\d+)([smhd])", süre.lower())
    if not time_regex:
        return await ctx.send("❌ Geçersiz süre formatı! Örnek: `1h`, `30m`, `1d`")
    
    amount, unit = time_regex.groups()
    amount = int(amount)
    
    if unit == 's':
        delta = timedelta(seconds=amount)
    elif unit == 'm':
        delta = timedelta(minutes=amount)
    elif unit == 'h':
        delta = timedelta(hours=amount)
    elif unit == 'd':
        delta = timedelta(days=amount)
    
    end_time = datetime.now() + delta
    
    embed = discord.Embed(
        title="🎉 ÇEKİLİŞ BAŞLADI!",
        description=f"**Ödül:** {ödül}\n**Kazanan Sayısı:** {kazanan_sayısı}\n**Süre:** {süre}",
        color=0xffd700,
        timestamp=end_time
    )
    
    embed.add_field(name="📝 Katılım", value="🎁 Emojisine tıklayarak katılabilirsiniz!", inline=False)
    embed.add_field(name="⏰ Bitiş", value=f"<t:{int(end_time.timestamp())}:R>", inline=True)
    embed.add_field(name="👑 Düzenleyen", value=ctx.author.mention, inline=True)
    embed.set_footer(text="Çekiliş biter")
    
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎁")
    
    # Veritabanına kaydet
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO giveaways (message_id, channel_id, prize, end_time, winner_count, creator_id) VALUES (?, ?, ?, ?, ?, ?)",
              (message.id, ctx.channel.id, ödül, end_time, kazanan_sayısı, ctx.author.id))
    conn.commit()
    conn.close()
    
    log_command('çekiliş', ctx.author.id)

# Çekiliş kontrol task'ı
@tasks.loop(minutes=1)
async def check_giveaways():
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM giveaways WHERE active = 1 AND end_time <= ?", (datetime.now(),))
    expired_giveaways = c.fetchall()
    
    for giveaway in expired_giveaways:
        giveaway_id, message_id, channel_id, prize, end_time, winner_count, creator_id, active = giveaway
        
        channel = bot.get_channel(channel_id)
        if not channel:
            continue
            
        try:
            message = await channel.fetch_message(message_id)
            reaction = discord.utils.get(message.reactions, emoji="🎁")
            
            if reaction and reaction.count > 1:  # Bot'un reaction'ı hariç
                users = [user async for user in reaction.users() if not user.bot]
                
                if len(users) >= winner_count:
                    winners = random.sample(users, min(winner_count, len(users)))
                    
                    embed = discord.Embed(
                        title="🎊 ÇEKİLİŞ BİTTİ!",
                        description=f"**Ödül:** {prize}",
                        color=0x00ff88
                    )
                    
                    winner_mentions = [winner.mention for winner in winners]
                    embed.add_field(name="🏆 Kazananlar", value="\n".join(winner_mentions), inline=False)
                    embed.add_field(name="🎁 Katılımcı Sayısı", value=len(users), inline=True)
                    
                    await channel.send(f"🎉 Tebrikler {', '.join(winner_mentions)}! **{prize}** kazandınız!", embed=embed)
                else:
                    embed = discord.Embed(
                        title="😔 Çekiliş İptal",
                        description=f"**{prize}** çekilişi yeterli katılımcı olmadığı için iptal edildi.",
                        color=0xff4444
                    )
                    await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="😔 Çekiliş İptal",
                    description=f"**{prize}** çekilişi katılımcı olmadığı için iptal edildi.",
                    color=0xff4444
                )
                await channel.send(embed=embed)
                
        except Exception as e:
            print(f"Çekiliş hatası: {e}")
        
        # Çekilişi pasif yap
        c.execute("UPDATE giveaways SET active = 0 WHERE id = ?", (giveaway_id,))
    
    conn.commit()
    conn.close()

# TICKET SİSTEMİ
@bot.command(name='ticket')
async def ticket(ctx):
    # Mevcut ticket kontrolü
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("SELECT channel_id FROM tickets WHERE user_id = ? AND closed = 0", (ctx.author.id,))
    existing = c.fetchone()
    
    if existing:
        channel = bot.get_channel(existing[0])
        if channel:
            return await ctx.send(f"❌ Zaten açık bir ticket'ınız var: {channel.mention}")
    
    # Yeni ticket oluştur
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="🎫 Tickets")
    
    if not category:
        category = await guild.create_category("🎫 Tickets")
    
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    # Admin rollerini ekle
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    channel = await guild.create_text_channel(
        f"ticket-{ctx.author.name}",
        category=category,
        overwrites=overwrites
    )
    
    embed = discord.Embed(
        title="🎫 Ticket Oluşturuldu",
        description=f"Merhaba {ctx.author.mention}! Ticket'ınız oluşturuldu.",
        color=0x00ff88
    )
    embed.add_field(name="📝 Açıklama", value="Sorununuzu detaylı bir şekilde açıklayın. Yetkili ekibimiz en kısa sürede size yardımcı olacak.", inline=False)
    embed.add_field(name="🔒 Kapatma", value="Ticket'ı kapatmak için `.kapat` komutunu kullanın.", inline=False)
    embed.set_footer(text="Yuva Destek Sistemi")
    
    await channel.send(embed=embed)
    
    # Veritabanına kaydet
    c.execute("INSERT INTO tickets (user_id, channel_id) VALUES (?, ?)", (ctx.author.id, channel.id))
    conn.commit()
    conn.close()
    
    await ctx.send(f"✅ Ticket oluşturuldu: {channel.mention}")
    log_command('ticket', ctx.author.id)

@bot.command(name='kapat')
async def kapat(ctx):
    if not ctx.channel.name.startswith('ticket-'):
        return await ctx.send("❌ Bu komut sadece ticket kanallarında kullanılabilir!")
    
    # Ticket sahibi veya admin kontrolü
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM tickets WHERE channel_id = ? AND closed = 0", (ctx.channel.id,))
    result = c.fetchone()
    
    if not result:
        return await ctx.send("❌ Bu ticket bulunamadı!")
    
    ticket_owner_id = result[0]
    
    if ctx.author.id != ticket_owner_id and not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Bu ticket'ı sadece sahibi veya adminler kapatabilir!")
    
    embed = discord.Embed(
        title="🔒 Ticket Kapatılıyor",
        description="Bu ticket 10 saniye içinde kapatılacak...",
        color=0xff4444
    )
    embed.add_field(name="🛡️ Kapatan", value=ctx.author.mention, inline=True)
    
    await ctx.send(embed=embed)
    
    # Ticket'ı kapat
    c.execute("UPDATE tickets SET closed = 1 WHERE channel_id = ?", (ctx.channel.id,))
    conn.commit()
    conn.close()
    
    await asyncio.sleep(10)
    await ctx.channel.delete()
    log_command('kapat', ctx.author.id)

# MÜZİK SİSTEMİ (Joy FM)
@bot.command(name='katıl')
@is_admin()
async def katil(ctx, channel_id: int):
    try:
        channel = bot.get_channel(channel_id)
        
        if not channel or not isinstance(channel, discord.VoiceChannel):
            return await ctx.send("❌ Geçersiz sesli kanal ID'si!")
        
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        
        voice_client = await channel.connect()
        
        embed = discord.Embed(
            title="🎵 Sesli Kanala Katıldım",
            description=f"**{channel.name}** kanalına katıldım!",
            color=0x00ff88
        )
        embed.add_field(name="📻 Radyo", value="Joy FM çalmaya başlıyor...", inline=False)
        
        await ctx.send(embed=embed)
        
        # Joy FM çal
        try:
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            
            voice_client.play(FFmpegPCMAudio(JOY_FM_URL, **ffmpeg_options))
            
            embed = discord.Embed(
                title="📻 Joy FM Çalıyor",
                description="Artık Joy FM dinliyorsunuz! 🎶",
                color=0x00ff88
            )
            embed.set_footer(text="Durdurmak için .dur komutunu kullanın")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Radyo çalma hatası: {e}")
        
        log_command('katıl', ctx.author.id)
        
    except Exception as e:
        await ctx.send(f"❌ Sesli kanala katılma hatası: {e}")

@bot.command(name='dur')
@is_admin()
async def dur(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        
        embed = discord.Embed(
            title="⏹️ Müzik Durduruldu",
            description="Sesli kanaldan ayrıldım ve müzik durduruldu.",
            color=0xff4444
        )
        await ctx.send(embed=embed)
        log_command('dur', ctx.author.id)
    else:
        await ctx.send("❌ Herhangi bir sesli kanalda değilim!")

# AYARLAR
@bot.command(name='hoşgeldin-ayarla')
@is_admin()
async def hosgeldin_ayarla(ctx, channel: discord.TextChannel):
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    
    c.execute("INSERT OR REPLACE INTO guild_settings (guild_id, welcome_channel) VALUES (?, ?)",
              (ctx.guild.id, channel.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Hoş Geldin Kanalı Ayarlandı",
        description=f"Hoş geldin mesajları artık {channel.mention} kanalında gönderilecek.",
        color=0x00ff88
    )
    await ctx.send(embed=embed)
    log_command('hoşgeldin-ayarla', ctx.author.id)

@bot.command(name='görüşürüz-ayarla')
@is_admin()
async def gorusuruz_ayarla(ctx, channel: discord.TextChannel):
    conn = sqlite3.connect('yuva_bot.db')
    c = conn.cursor()
    
    c.execute("INSERT OR REPLACE INTO guild_settings (guild_id, leave_channel) VALUES (?, ?)",
              (ctx.guild.id, channel.id))
    conn.commit()
    conn.close()
    
    embed = discord.Embed(
        title="✅ Görüşürüz Kanalı Ayarlandı",
        description=f"Ayrılma mesajları artık {channel.mention} kanalında gönderilecek.",
        color=0x00ff88
    )
    await ctx.send(embed=embed)
    log_command('görüşürüz-ayarla', ctx.author.id)

# YARDIM KOMUTU
@bot.command(name='yardım', aliases=['help', 'komutlar'])
async def yardim(ctx):
    embed = discord.Embed(
        title="🏠 Yuva Bot - Komut Listesi",
        description="Yuva Discord sunucusu için özel bot!",
        color=0x00ff88
    )
    
    embed.add_field(
        name="👑 Sahip Komutları",
        value="`!owner` - Bot sahibi bilgileri",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Admin Komutları",
        value="`!ekip <user_id>` - Ekip rolü ver/al\n`!yetkili <user_id>` - Yetkili rolü ver/al\n`!ban <@kullanıcı> [sebep]` - Kullanıcı banla\n`!kick <@kullanıcı> [sebep]` - Kullanıcı at\n`!temizle <sayı>` - Mesaj sil",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Çekiliş Sistemi",
        value="`!çekiliş <süre> <kazanan_sayısı> <ödül>` - Çekiliş başlat\nÖrnek: `!çekiliş 1h 2 Nitro`",
        inline=False
    )
    
    embed.add_field(
        name="🎫 Ticket Sistemi",
        value="`!ticket` - Yeni ticket oluştur\n`!kapat` - Ticket'ı kapat",
        inline=False
    )
    
    embed.add_field(
        name="🎵 Müzik Sistemi",
        value="`!katıl <kanal_id>` - Sesli kanala katıl ve Joy FM çal\n`!dur` - Müziği durdur ve ayrıl",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Ayarlar",
        value="`!hoşgeldin-ayarla <#kanal>` - Hoş geldin kanalı ayarla\n`!görüşürüz-ayarla <#kanal>` - Ayrılma kanalı ayarla",
        inline=False
    )
    
    embed.set_footer(text="Yuva Bot v2.0 • Özel olarak kodlandı")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)
    log_command('yardım', ctx.author.id)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="🚫 Yetki Hatası",
            description="Bu komutu kullanmak için yeterli yetkiniz yok!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="🚫 Erişim Reddedildi",
            description="Bu komutu kullanma yetkiniz yok!",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Eksik Argüman",
            description=f"Gerekli argüman eksik: `{error.param.name}`\nYardım için: `!yardım`",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ Beklenmeyen Hata",
            description="Bir hata oluştu! Lütfen daha sonra tekrar deneyin.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        print(f"Error: {error}")

# Initialize and run
if __name__ == "__main__":
    init_db()
    bot.start_time = datetime.now()
    
    # Çekiliş kontrol task'ını başlat
    check_giveaways.start()
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Yuva Bot başlatılamadı: {e}")