#!/usr/bin/env python3
"""
ULTIMATE PERSONALIZED EMAIL MAILER (Full - With Enrich & Auto-SMTP)
- Auto-detects SMTP from proxy
- Enrich recipient (name, company, domain)
- SOCKS5 routing
- Multi-threaded + delay
- QR + Logo
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
from email.utils import formataddr
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re
from io import BytesIO
import sys
import json

# --------------------------------------------------------------
# 1. CONFIGURATION — EDIT ONLY THIS SECTION
# --------------------------------------------------------------
BASE_DIR = Path(__file__).parent

# --- PATHS ---
HTML_LETTER_PATH = BASE_DIR / "letters" / "welcome.html"
CSV_LIST_PATH    = BASE_DIR / "lists" / "subscribers.csv"
ATTACHMENT_PATHS = [
    # BASE_DIR / "attachments" / "brochure.pdf",
]

# --- TOGGLE FEATURES ---
ENABLE_ATTACHMENTS = True
ENABLE_QR_CODE     = True

# --- EMAIL SETTINGS ---
EMAIL_SUBJECT = "Exclusive Update for {{name}} at {{company}}"
SENDER_EMAIL  = "your@gmail.com"

# --- PROXY (SOCKS5) ---
PROXY_HOST = ""          # e.g., "62.106.66.109"
PROXY_PORT = 1080
PROXY_USER = ""
PROXY_PASS = ""

# --- SMTP (Auto-Detected from Proxy if Empty) ---
SMTP_HOST = ""           # Leave empty to auto-detect
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""

# --- TRACKING & QR ---
TRACKING_BASE_URL = "https://yourdomain.com/track"

# --- SENDING ---
DELAY_BETWEEN_EMAILS = 1.5
MAX_THREADS = 5
BATCH_SIZE = 0  # 0 = all

# --- DIRECTORIES ---
LOG_DIR     = BASE_DIR / "logs"
QR_DIR      = BASE_DIR / "qr_codes"
LOGO_CACHE  = BASE_DIR / "logo_cache"
LOG_DIR.mkdir(exist_ok=True)
QR_DIR.mkdir(exist_ok=True)
LOGO_CACHE.mkdir(exist_ok=True)

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"sent_{datetime.now():%Y-%m-%d}.log"),
        logging.StreamHandler()
    ]
)

# --------------------------------------------------------------
# AUTO-DETECT SMTP FROM PROXY
# --------------------------------------------------------------
if PROXY_HOST and not SMTP_HOST:
    SMTP_HOST = f"mail.{PROXY_HOST}"
    SMTP_USER = PROXY_USER or SMTP_USER
    SMTP_PASS = PROXY_PASS or SMTP_PASS
    logging.info(f"Auto-set SMTP to {SMTP_HOST} from proxy")

# --------------------------------------------------------------
# 2. ENRICH RECIPIENT FUNCTION (FIXED - MISSING IN YOUR VERSION)
# --------------------------------------------------------------
def enrich_recipient(email: str) -> Dict[str, str]:
    """Auto-detect full_name, company, domain, username from email."""
    match = re.match(r"(.+)@(.+)", email)
    if not match:
        return {"email": email, "full_name": "Unknown", "company": "Unknown", "domain": "", "username": ""}

    username, domain = match.groups()
    username = username.lower().replace(".", " ").replace("_", " ").strip()

    # Full name: Capitalize words
    name_words = username.split()
    full_name = " ".join(word.capitalize() for word in name_words)
    if len(name_words) == 1 and name_words[0] in {"john", "bob", "alice", "mary"}:
        full_name = f"{full_name} {full_name.capitalize()}"

    # Company: Domain without TLD
    company_match = re.match(r"([^.]+)", domain)
    company = company_match.group(1).capitalize() if company_match else domain.capitalize()

    return {
        "email": email,
        "full_name": full_name,
        "company": company,
        "domain": domain,
        "username": username
    }

# --------------------------------------------------------------
# 3. HELPERS
# --------------------------------------------------------------
def random_sender_name() -> str:
    first = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer"]
    last = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson"]
    return f"{random.choice(first)} {random.choice(last)}"

def get_domain_logo(domain: str) -> Path:
    cache_file = LOGO_CACHE / f"{domain}.png"
    if cache_file.exists():
        return cache_file
    url = f"https://logo.clearbit.com/{domain}?size=100"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            with open(cache_file, "wb") as f:
                f.write(r.content)
            return cache_file
    except:
        pass
    return None

def generate_qr(data: str) -> Path:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_path = QR_DIR / f"qr_{int(time.time()*1000)}.png"
    with open(qr_path, "wb") as f:
        f.write(buffer.getvalue())
    return qr_path

def attach_files(msg: EmailMessage, files: List[Path]):
    for p in files:
        if not p.exists():
            continue
        mime_map = {".pdf": ("application", "pdf"), ".png": ("image", "png"), ".jpg": ("image", "jpeg")}
        main, sub = mime_map.get(p.suffix.lower(), ("application", "octet-stream"))
        msg.add_attachment(p.read_bytes(), maintype=main, subtype=sub, filename=p.name)

# --------------------------------------------------------------
# 4. SEND ONE EMAIL
# --------------------------------------------------------------
def send_single_email(recipient: Dict[str, str]):
    try:
        email = recipient["email"]
        full_name = recipient["full_name"]
        first_name = full_name.split()[0]
        username = recipient["username"]
        domain = recipient["domain"]
        company = recipient["company"]

        sender_name = random_sender_name()
        logo_path = get_domain_logo(domain) if domain else None
        qr_path = generate_qr(f"{TRACKING_BASE_URL}?email={email}") if ENABLE_QR_CODE else None

        # Load HTML
        html_body = HTML_LETTER_PATH.read_text(encoding="utf-8")

        # Replace placeholders
        now = datetime.now()
        replacements = {
            "{{name}}": first_name,
            "{{full_name}}": full_name,
            "{{email}}": email,
            "{{username}}": username,
            "{{company}}": company,
            "{{domain}}": domain,
            "{{date}}": now.strftime("%B %d, %Y"),
            "{{time}}": now.strftime("%I:%M %p"),
            "{{sender_name}}": sender_name,
            "{{qr_code}}": f'<img src="cid:qr_code" alt="Scan" width="150"/>' if qr_path else "",
            "{{company_logo}}": f'<img src="cid:company_logo" alt="{company}" width="100"/>' if logo_path else ""
        }
        for ph, val in replacements.items():
            html_body = html_body.replace(ph, val)

        # Subject
        subject = EMAIL_SUBJECT
        for ph, val in replacements.items():
            if ph not in ["{{qr_code}}", "{{company_logo}}"]:
                subject = subject.replace(ph, val)

        # Plain text
        plain_body = re.sub(r"<[^>]+>", "", html_body)

        # Build message
        msg = EmailMessage()
        msg["From"] = formataddr((sender_name, SENDER_EMAIL))
        msg["To"] = formataddr((full_name, email))
        msg["Subject"] = subject

        msg.set_content(plain_body)
        msg.add_alternative(html_body, subtype="html")

        # Embed QR + Logo
        if qr_path and qr_path.exists():
            with open(qr_path, "rb") as f:
                msg.get_payload()[1].add_related(f.read(), 'image', 'png', cid="qr_code")
        if logo_path and logo_path.exists():
            with open(logo_path, "rb") as f:
                msg.get_payload()[1].add_related(f.read(), 'image', 'png', cid="company_logo")

        # Attachments
        if ENABLE_ATTACHMENTS:
            for p in ATTACHMENT_PATHS:
                if p.exists():
                    mime_map = {".pdf": ("application", "pdf"), ".png": ("image", "png"), ".jpg": ("image", "jpeg")}
                    main, sub = mime_map.get(p.suffix.lower(), ("application", "octet-stream"))
                    msg.add_attachment(p.read_bytes(), maintype=main, subtype=sub, filename=p.name)

        # Send
        context = ssl.create_default_context()
        original_socket = None
        if PROXY_HOST:
            import socks
            socks.set_default_proxy(socks.SOCKS5, PROXY_HOST, PROXY_PORT, True, PROXY_USER or None, PROXY_PASS or None)
            import socket
            original_socket = socket.socket
            socket.socket = socks.socksocket

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()

        if original_socket:
            import socket
            socket.socket = original_socket

        logging.info(f"SUCCESS → {email} | {full_name} @ {company} | From: {sender_name}")
        return True

    except Exception as e:
        logging.error(f"FAILED → {email} | {e}")
        return False

# --------------------------------------------------------------
# 5. MAIN CAMPAIGN
# --------------------------------------------------------------
def send_campaign():
    logging.info("Starting campaign...")

    if not HTML_LETTER_PATH.exists():
        logging.error(f"Missing HTML: {HTML_LETTER_PATH}")
        return
    if not CSV_LIST_PATH.exists():
        logging.error(f"Missing CSV: {CSV_LIST_PATH}")
        return

    recipients = []
    with open(CSV_LIST_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip()
            if email:
                recipients.append(enrich_recipient(email))  # FIXED - Now defined

    if BATCH_SIZE > 0:
        recipients = recipients[:BATCH_SIZE]

    logging.info(f"Loaded {len(recipient)} recipients. Threads: {MAX_THREADS}")

    success = 0
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(send_single_email, r) for r in recipients]
        for f in as_completed(futures):
            if f.result():
                success += 1
            time.sleep(DELAY_BETWEEN_EMAILS)

    logging.info(f"COMPLETE: {success}/{len(recipient)} sent.")

# --------------------------------------------------------------
# 6. TEST MODE (From GUI)
# --------------------------------------------------------------
if len(sys.argv) > 1 and sys.argv[1] == "--test-email":
    test_email = sys.argv[2]
    recipient = enrich_recipient(test_email)  # FIXED - Now defined
    send_single_email(recipient)
    logging.info("Test complete.")
    sys.exit(0)

# --------------------------------------------------------------
# 7. RUN
# --------------------------------------------------------------
if __name__ == "__main__":
    send_campaign()