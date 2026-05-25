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
BOT_TOKEN = "8892459100:AAEQ3N62bLATXa8XdxnNL0cwYWqt7tW0sLs"   # @BotFather dan olingan token
CHAT_ID   = "-1003786945587"     # Guruh yoki shaxsiy chat ID
# -----------------------------------------------


# Virtual/Docker interfeyslarini filtrlash uchun prefix va nom ro'yxati
VIRTUAL_IFACE_PREFIXES = ("docker", "br-", "veth", "virbr", "lxc", "lxd", "flannel", "cni", "dummy")
VIRTUAL_IP_PREFIXES = ("172.17.", "172.18.", "172.19.", "172.20.", "10.0.2.")


def is_virtual_iface(iface, ip):
    """Interfeys yoki IP virtual/Docker ekanligini tekshiradi."""
    if iface.startswith(VIRTUAL_IFACE_PREFIXES):
        return True
    if ip.startswith(VIRTUAL_IP_PREFIXES):
        return True
    return False


def get_ip_addresses():
    """Haqiqiy (loopback va virtual bo'lmagan) IPv4 manzillarni qaytaradi."""
    ips = {}
    iface = None
    try:
        result = subprocess.run(
            ["ip", "-4", "addr", "show"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            # Interfeys nomini ol
            if line and not line[0].isspace():
                parts = line.split()
                if len(parts) >= 2:
                    iface = parts[1].rstrip(":")
            line = line.strip()
            if line.startswith("inet "):
                parts = line.split()
                ip = parts[1].split("/")[0]
                if ip == "127.0.0.1":
                    continue
                if iface and is_virtual_iface(iface, ip):
                    continue
                ips[ip] = iface or ""
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
    # Tarmoq tayyor bo'lishini kutish (max 120 sekund)
    # Faqat haqiqiy (virtual bo'lmagan) IP topilsa to'xtatamiz
    for _ in range(60):
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

    # DNS tayyor bo'lmasa retry (max 30 urinish, har 5 sekund)
    for attempt in range(30):
        try:
            send_telegram_message(message)
            break
        except Exception:
            if attempt < 29:
                time.sleep(5)
            else:
                raise


if __name__ == "__main__":
    main()
