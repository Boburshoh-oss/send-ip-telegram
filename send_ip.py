#!/usr/bin/env python3
"""
Jetson qurilmasi ishga tushganda IP manzilni Telegram guruhiga yuboradi.
Boot vaqtida IP address ni Telegram bot orqali yuboruvchi script.
"""
import socket
import subprocess
import urllib.request
import urllib.parse
import json
import time

# -----------------------------------------------
# SOZLAMALAR — o'zingizning qiymatlaringizni kiriting
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather dan olingan token
CHAT_ID   = "YOUR_CHAT_ID_HERE"     # Guruh yoki shaxsiy chat ID
# -----------------------------------------------


def get_ip_addresses():
    """Barcha loopback bo'lmagan IPv4 manzillarni qaytaradi."""
    ips = {}
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                parts = line.split()
                ip = parts[1].split("/")[0]
                if ip != "127.0.0.1":
                    iface = ""
                    for p in parts:
                        if p not in ("inet", parts[1]):
                            iface = p
                    ips[ip] = iface
    except Exception:
        pass

    if not ips:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips[s.getsockname()[0]] = "default"
            s.close()
        except Exception:
            pass

    return ips


def send_telegram_message(text):
    """Telegram botiga xabar yuboradi."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }).encode()

    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main():
    # Tarmoq tayyor bo'lishini kutish (max 60 sekund)
    for _ in range(30):
        ips = get_ip_addresses()
        if ips:
            break
        time.sleep(2)

    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    if ips:
        ip_lines = "\n".join(f"  <b>{ip}</b>" for ip in ips)
        message = (
            f"Jetson qurilmasi ishga tushdi!\n\n"
            f"Hostname: <b>{hostname}</b>\n"
            f"IP manzil(lar):\n{ip_lines}"
        )
    else:
        message = (
            f"Jetson qurilmasi ishga tushdi!\n\n"
            f"Hostname: <b>{hostname}</b>\n"
            f"IP manzil aniqlanmadi."
        )

    send_telegram_message(message)


if __name__ == "__main__":
    main()
