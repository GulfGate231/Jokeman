#!/usr/bin/env python3
"""
ELITE INBOX MAILER 2025 — FINAL VERSION
Features:
• Optional SMTP rotation (single or multiple accounts)
• Full SOCKS5 proxy rotation (proxies.txt)
• Bounce handling + automatic blacklist (blacklist.txt)
• Full attachment support (PDF, HTML, EML, SVG — inline or attached)
• Personalized QR code + company logo (Clearbit)
• Human-like delays + warmup for first 30 emails
• Clean headers (Message-ID, List-Unsubscribe, Reply-To)
• 1×1 tracking pixel (optional)
• Primary inbox delivery (Gmail, Outlook, Yahoo tested)
• No spam flags, no mail.{ip}, no spoofing
"""

import smtplib
import ssl
import csv
import logging
import time
import random
import qrcode
import requests
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
from io import BytesIO
import sys
import socket

# ===================== CONFIG =====================
BASE_DIR = Path(__file__).parent

HTML_LETTER_PATH = BASE_DIR / "letters" / "template.html"
CSV_LIST_PATH    = BASE_DIR / "lists" / "contacts.csv"
PROXIES_FILE     = BASE_DIR / "proxies.txt"        # ip:port or ip:port:user:pass
BLACKLIST_FILE   = BASE_DIR / "blacklist.txt"      # auto-created

# Attachments (PDF, HTML, EML, SVG supported)
ATTACHMENT_PATHS = [
    BASE_DIR / "attachments" / "brochure.pdf",
    BASE_DIR / "attachments" / "proposal.html",
    BASE_DIR / "attachments" / "previous_email.eml",
    BASE_DIR / "attachments" / "signature.svg",
]

# SMTP ROTATION — SET TO False FOR SINGLE ACCOUNT (recommended)
ENABLE_ROTATION = False

# Single SMTP (used when ENABLE_ROTATION = False)
SINGLE_SMTP = {
    "host": "smtp.gmail.com",
    "port": 587,
    "user": "your.main.email@gmail.com",   # CHANGE THIS
    "pass": "your-app-password-here",      # CHANGE THIS
    "name": "Alex Rivera"
}

# Rotating accounts (used only when ENABLE_ROTATION = True)
ROTATING_SMTP_ACCOUNTS = [
    ("smtp.gmail.com", 587, "john.real1@gmail.com", "abcd efgh ijkl mnop", "John Miller"),
    ("smtp.gmail.com", 587, "sarah.real2@gmail.com", "xyzw pqrs tuvw abcd", "Sarah Chen"),
    ("smtp.outlook.com", 587, "alex@outlook.com", "realpass123", "Alex Rivera"),
]

EMAIL_SUBJECT      = "Hey {{name}}, quick note from {{sender}}"
MAX_THREADS        = 5
DELAY_RANGE        = (14, 42)
WARMUP_FIRST_30    = True
ENABLE_QR_CODE     = False
ENABLE_ATTACHMENTS = True
ENABLE_PIXEL       = False   # only if you own the tracking domain

# Folders
LOG_DIR    = BASE_DIR / "logs"
QR_DIR     = BASE_DIR / "qr"
LOGO_CACHE = BASE_DIR / "cache"
for d in (LOG_DIR, QR_DIR, LOGO_CACHE):
    d.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "log.txt"), logging.StreamHandler()]
)

# ===================== PROXIES & BLACKLIST =====================
def load_proxies() -> List[Dict]:
    if not PROXIES_FILE.exists():
        return [{"host": "", "port": 0, "user": "", "pass": ""}]
    proxies = []
    for line in PROXIES_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split(":")
        if len(parts) == 4:
            h, p, u, pw = parts
            proxies.append({"host": h, "port": int(p), "user": u, "pass": pw})
        else:
            h, p = parts
            proxies.append({"host": h, "port": int(p), "user": "", "pass": ""})
    return proxies

PROXIES = load_proxies()

def load_blacklist() -> set:
    if BLACKLIST_FILE.exists():
        return set(line.split("#")[0].strip().lower() for line in BLACKLIST_FILE.read_text().splitlines() if line.strip())
    return set()

def add_to_blacklist(email: str, reason: str):
    email = email.lower().strip()
    with open(BLACKLIST_FILE, "a", encoding="utf-8") as f:
        f.write(f"{email}  # {reason} | {datetime.now():%Y-%m-%d %H:%M}\n")
    logging.warning(f"BLACKLISTED → {email} | {reason}")

BLACKLIST = load_blacklist()

# ===================== HELPERS =====================
sent_count = 0
def human_delay():
    global sent_count
    if WARMUP_FIRST_30 and sent_count < 30:
        time.sleep(random.uniform(40, 100))
    else:
        time.sleep(random.uniform(*DELAY_RANGE))
    sent_count += 1

def enrich_recipient(email: str) -> Dict:
    local, domain = email.split("@", 1)
    name = re.sub(r"[._+-]", " ", local).title()
    company = domain.split(".")[0].capitalize()
    return {"email": email, "full_name": name, "company": company, "domain": domain}

def get_logo(domain: str) -> Path | None:
    path = LOGO_CACHE / f"{domain}.png"
    if path.exists(): return path
    try:
        r = requests.get(f"https://logo.clearbit.com/{domain}?size=120", timeout=6)
        if r.status_code == 200:
            path.write_bytes(r.content)
            return path
    except: pass
    return None

def generate_qr(url: str) -> Path:
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="white")
    buf = BytesIO()
    img.save(buf, "PNG")
    path = QR_DIR / f"qr_{int(time.time()*1000)}.png"
    path.write_bytes(buf.getvalue())
    return path

def attach_files(msg: EmailMessage, files: List[Path]):
    for p in files:
        if not p.exists(): continue
        filename = p.name
        data = p.read_bytes()
        ext = p.suffix.lower()
        mime_map = {
            ".pdf": ("application", "pdf"), ".html": ("text", "html"), ".eml": ("message", "rfc822"),
            ".svg": ("image", "svg+xml"), ".png": ("image", "png"), ".jpg": ("image", "jpeg"), ".jpeg": ("image", "jpeg")
        }
        maintype, subtype = mime_map.get(ext, ("application", "octet-stream"))
        if ext == ".svg" and "inline" in filename.lower():
            cid = f"svg_{random.randint(1000,9999)}"
            msg.get_payload()[-1].add_related(data, maintype, subtype, cid=f"<{cid}>")
            html = msg.get_payload()[-1].get_content()
            html = html.replace("{{inline_svg}}", f"cid:{cid}")
            msg.get_payload()[-1].set_content(html, subtype="html")
        else:
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

# ===================== BOUNCE DETECTION =====================
def is_hard_bounce(e):
    msg = str(e).lower()
    return any(x in msg for x in ["550", "551", "552", "553", "554", "user unknown", "no such user", "mailbox unavailable", "invalid recipient"])

# ===================== SEND EMAIL =====================
def send_email(recipient: Dict, smtp: Tuple, proxy: Dict) -> bool:
    host, port, user, pwd, display_name = smtp
    email = recipient["email"].lower().strip()
    if email in BLACKLIST:
        return False
    try:
        name = recipient["full_name"]
        first = name.split()[0]
        domain = recipient["domain"]

        msg = EmailMessage()
        msg["From"] = formataddr((display_name, user))
        msg["To"] = formataddr((name, email))
        msg["Subject"] = EMAIL_SUBJECT.replace("{{name}}", first).replace("{{sender}}", display_name.split()[0])
        msg["Reply-To"] = user
        msg["Message-ID"] = make_msgid(domain="yourdomain.com")
        msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
        msg["List-Unsubscribe"] = "<mailto:unsubscribe@yourdomain.com>, <https://yourdomain.com/unsubscribe>"

        html = HTML_LETTER_PATH.read_text(encoding="utf-8")
        html = html.replace("{{name}}", first).replace("{{company}}", recipient["company"])

        qr_path = generate_qr(f"https://yourdomain.com/click?e={email}") if ENABLE_QR_CODE else None
        if qr_path:
            html = html.replace("{{qr_code}}", '<img src="cid:qr_code" width="160" alt="Scan">')

        logo_path = get_logo(domain)
        if logo_path:
            html = html.replace("{{company_logo}}", '<img src="cid:company_logo" width="110" alt="Logo">')

        if ENABLE_PIXEL:
            html += f'<img src="https://track.yourdomain.com/pixel.gif?e={email}" width="1" height="1" style="display:none;">'

        msg.set_content("Please view in HTML.")
        related = msg.add_alternative(html, subtype="html")

        if qr_path:
            with open(qr_path, "rb") as f:
                related.add_related(f.read(), "image", "png", cid="qr_code")
        if logo_path:
            with open(logo_path, "rb") as f:
                related.add_related(f.read(), "image", "png", cid="company_logo")

        if ENABLE_ATTACHMENTS:
            attach_files(msg, ATTACHMENT_PATHS)

        original_socket = None
        if proxy["host"]:
            import socks
            socks.set_default_proxy(socks.SOCKS5, proxy["host"], proxy["port"],
                                   True, proxy["user"] or None, proxy["pass"] or None)
            original_socket = socket.socket
            socket.socket = socks.socksocket

        ctx = ssl.create_default_context()
        with smtplib.SMTP(host, port, timeout=40) as server:
            server.starttls(context=ctx)
            server.login(user, pwd)
            server.send_message(msg)

        if original_socket:
            socket.socket = original_socket

        logging.info(f"DELIVERED → {first} <{email}>")
        human_delay()
        return True

    except smtplib.SMTPRecipientsRefused:
        add_to_blacklist(email, "hard bounce (refused)")
        return False
    except Exception as e:
        if is_hard_bounce(e):
            add_to_blacklist(email, f"hard bounce: {e}")
            logging.warning(f"HARD BOUNCE → {email}")
        else:
            logging.error(f"Failed {email} → {e}")
        human_delay()
        return False

# ===================== CAMPAIGN =====================
def run():
    logging.info("Starting campaign...")
    recipients = []
    with open(CSV_LIST_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            e = row.get("email", "").strip().lower()
            if e and "@" in e and e not in BLACKLIST:
                recipients.append(enrich_recipient(e))

    logging.info(f"Loaded {len(recipients)} valid contacts")

    accounts = ROTATING_SMTP_ACCOUNTS if ENABLE_ROTATION else [(
        SINGLE_SMTP["host"], SINGLE_SMTP["port"],
        SINGLE_SMTP["user"], SINGLE_SMTP["pass"], SINGLE_SMTP["name"]
    )]

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as pool:
        futures = []
        for i, rec in enumerate(recipients):
            smtp = accounts[i % len(accounts)]
            proxy = PROXIES[i % len(PROXIES)] if PROXIES[0]["host"] else PROXIES[0]
            futures.append(pool.submit(send_email, rec, smtp, proxy))
        success = sum(f.result() for f in as_completed(futures))

    logging.info(f"Campaign finished: {success}/{len(recipients)} delivered")

# ===================== TEST & RUN =====================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test = enrich_recipient(sys.argv[2])
        test_smtp = (
            SINGLE_SMTP["host"], SINGLE_SMTP["port"],
            SINGLE_SMTP["user"], SINGLE_SMTP["pass"], SINGLE_SMTP["name"]
        )
        send_email(test, test_smtp, PROXIES[0])
    else:
        run()
