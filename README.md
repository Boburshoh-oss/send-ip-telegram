# Jetson Boot IP Reporter — Telegram

NVIDIA Jetson qurilmasi har ishga tushganda IP manzilini Telegram guruhiga yuboruvchi Python skript va systemd servisi.

## Umumiy Ko'rinish

```
Jetson ishga tushadi
       │
       ▼
network-online.target tayyor bo'ladi
       │
       ▼
send-ip.service ishga tushadi
       │
       ▼
send_ip.py IP manzil(lar)ni aniqlaydi
       │
       ▼
Telegram botiga xabar yuboradi
```

## Talablar

- NVIDIA Jetson (yoki istalgan Linux qurilmasi)
- Python 3.6+
- Internet ulanishi
- Telegram bot tokeni (`@BotFather` orqali olingan)

## O'rnatish

### 1. Telegram Bot Yaratish

1. Telegramda `@BotFather` ni toping
2. `/newbot` buyrug'ini yuboring
3. Bot uchun nom va username bering
4. Olingan **token** ni saqlang

### 2. Chat ID Aniqlash

Bot qo'shilgan guruh uchun chat ID ni aniqlash:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates"
```
Javobdagi `chat.id` ni oling. Guruh bo'lsa, `-100` prefiksi bilan supergroup ID bo'ladi.

### 3. Skriptni Sozlash

`send_ip.py` faylini oching va qiymatlarni o'zgartiring:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather dan olingan token
CHAT_ID   = "YOUR_CHAT_ID_HERE"     # Guruh yoki shaxsiy chat ID
```

### 4. Skriptni Deploy Qilish

```bash
# Skriptni nusxalash
sudo cp send_ip.py /usr/local/bin/send_ip.py
sudo chmod +x /usr/local/bin/send_ip.py

# Servisi nusxalash
sudo cp send-ip.service /etc/systemd/system/send-ip.service

# Servisi yoqish va ishga tushirish
sudo systemctl daemon-reload
sudo systemctl enable send-ip.service
sudo systemctl start send-ip.service
```

### 5. Tekshirish

```bash
# Servis holatini ko'rish
sudo systemctl status send-ip.service

# Skriptni qo'lda sinab ko'rish
python3 /usr/local/bin/send_ip.py

# Loglarni ko'rish
sudo journalctl -u send-ip.service -f
```

## Fayl Tuzilmasi

```
send-ip-telegram/
├── send_ip.py        # Asosiy Python skript
├── send-ip.service   # systemd servis unit fayli
└── README.md         # Ushbu fayl
```

## Xabar Namunasi

Qurilma ishga tushganda Telegram guruhiga quyidagi xabar keladi:

```
Jetson qurilmasi ishga tushdi!

Hostname: jetson-nano
IP manzil(lar):
  192.168.1.105
  10.0.0.2
```

## Muammolar va Yechimlar

| Muammo | Yechim |
|--------|--------|
| `HTTP 400: chat not found` | Chat ID ni tekshiring, minus belgisi kerak |
| `HTTP 403: Forbidden` | Bot guruhga qo'shilganligini tekshiring |
| `group upgraded to supergroup` | Yangi supergroup ID ni oling (`migrate_to_chat_id`) |
| IP aniqlanmadi | `network-online.target` ishlaganligini tekshiring |

## Litsenziya

MIT License
