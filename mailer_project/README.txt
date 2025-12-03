══════════════════════════════════════════════════════════
           ELITE INBOX MAILER 2025 – FULL FEATURES GUIDE
══════════════════════════════════════════════════════════
Author: IDEYWITHU | Built for invisibility & domination

1. MAIN SCRIPT TO RUN
   → python3 gui_mailer.py
   Opens the full elite GUI (best & only way to use)

2. CORE FILES & FOLDERS
   gui_mailer.py           → Full GUI + config manager
   send_via_socks5.py      → Core engine (rotating SMTP + proxies + bounce handling)
   config.json             → Auto-saved settings (SMTP, delays, features)
   blacklist.txt           → Auto-created: hard bounces & complaints
   proxies.txt             → One SOCKS5 proxy per line (ip:port or ip:port:user:pass)

   FOLDERS:
   letters/      → Your HTML templates (template.html)
   lists/        → contacts.csv (email column required)
   attachments/  → PDF, HTML, EML, SVG, PNG, JPG (all supported)
   qr/           → Auto-generated QR codes
   logs/         → Full send log + blacklist updates
   cache/        → Company logos from Clearbit

3. NEW FEATURES (ELITE TIER)
   • Optional SMTP Rotation (single or multiple accounts)
   • Full bounce handling (hard/soft/complaints) → auto-blacklist
   • Full attachment support: PDF, HTML, EML, SVG (inline or attached)
   • Inline SVG support (use {{inline_svg}} in HTML)
   • Company logo auto-embed (Clearbit)
   • QR code per recipient (optional)
   • Human-like delays + warmup (first 30 emails extra slow)
   • Clean headers: Message-ID, List-Unsubscribe, Reply-To
   • 1×1 tracking pixel (optional, only if you own domain)
   • Blacklist system (blacklist.txt auto-updated)
   • Zero spoofing (From = real authenticated email)

4. HOW TO SET UP (30 seconds)
   1. Run: python3 gui_mailer.py
   2. SMTP Settings tab:
      • Leave "Enable Rotation" OFF → use single Gmail/Outlook
      • Fill: your.email@gmail.com + 16-char App Password
   3. Paths tab:
      • Select your HTML template (letters/template.html)
      • Select your list (lists/contacts.csv)
      • Drag files into Attachments box (PDF, SVG, etc.)
   4. Campaign tab:
      • Subject line with {{name}}, {{company}}
      • Max Threads: 3–8 (safe)
      • Enable Attachments: ON
   5. Click "Save Config" → "LAUNCH CAMPAIGN"

5. PERSONALIZATION TAGS (use in your HTML)
   {{name}}         → Full name (John Doe)
   {{first_name}}   → First name (John)
   {{email}}        → Full email
   {{company}}      → Guessed company (Google, Microsoft, etc.)
   {{domain}}       → Domain only (gmail.com)
   {{inline_svg}}   → For inline SVG attachments (filename must contain "inline")

   Example:
   <img src="cid:company_logo" width="110">
   <img src="cid:qr_code" width="160">
   {{inline_svg}}

6. ATTACHMENTS — FULLY SUPPORTED
   • PDF contracts, brochures
   • HTML files (as attachment)
   • EML (previous emails)
   • SVG (inline or attached)
   • PNG/JPG logos
   Just drop files into attachments/ folder or drag into GUI

7. BOUNCE HANDLING (Enterprise Grade)
   • Hard bounces (550, user unknown) → auto-blacklisted
   • Complaints & abuse reports → auto-blacklisted
   • Soft bounces → retried next run
   • blacklist.txt created automatically

8. PROXIES (SOCKS5 ONLY)
   Create proxies.txt:
   185.246.86.136:1080
   45.89.123.45:1080:user:pass
   102.33.44.55:1080
   → One proxy per thread → perfect reputation isolation

9. TEST EMAIL
   In GUI → Click "Test Email" → enter your email
   Or command line:
   python3 send_via_socks5.py --test youremail@gmail.com

10. ONE-CLICK UPDATE TO LATEST VERSION (2025+)
    Run this single command anytime:
```bash
rm -rf ~/Jokeman-main && curl -L https://github.com/GulfGate231/Jokeman/archive/refs/heads/main.zip -o Jokeman.zip && unzip -o Jokeman.zip && cd Jokeman-main/mailer_project && pip3 install -r requirements.txt --upgrade && python3 gui_mailer.py

11. QUICK START CHECKLIST
[ ] Run gui_mailer.py
[ ] Add your Gmail + App Password
[ ] Put template.html in letters/
[ ] Put contacts.csv in lists/
[ ] Add attachments (optional)
[ ] Set subject with {{name}}
[ ] Click LAUNCH CAMPAIGN
PRO TIPS FOR 99% PRIMARY INBOX
• Use warmed-up Gmail/Outlook (50–100 sent before bulk)
• Residential or mobile SOCKS5 proxies
• Random delay 14–42 seconds
• Never spoof From address
• Include List-Unsubscribe
• Use real display name
• Keep volume under 200/day per account

══════════════════════════════════════════════════════════
Use responsibly. Stay in Primary. Stay invisible.
– IDEYWITH | 2025 JOKE MAN MAILER
══════════════════════════════════════════════════════════
