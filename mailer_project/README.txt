══════════════════════════════════════════════════════════
           JOKEMAN MAILER – FULL FUNCTIONS & FEATURES GUIDE
══════════════════════════════════════════════════════════

1. MAIN SCRIPT TO RUN
   → python3 gui_mailer.py
   This opens the full drag & drop GUI (best way)

2. CORE FILES & WHAT THEY DO
   gui_mailer.py          → Main GUI + sending engine
   send_via_socks5.py     → Core sending function (SOCKS5 + SMTP)
   find_sender_emails.py  → Auto-grab sender emails from text/files
   editor.html            → Built-in HTML letter editor (double-click to open)
   config.json            → Stores all your senders & proxies (auto-created)

3. HOW TO ADD SMTP + SOCKS5 PROXY (First time setup)
   In GUI → Click "Add Sender" → Fill:
   • Sender Name        : Anything (e.g. "Gmail 1")
   • SMTP Server         : smtp.gmail.com / smtp-mail.outlook.com / etc.
   • Port                : 587 (TLS) or 465 (SSL)
   • Email               : yourreal@gmail.com
   • Password            : App Password (Gmail) or real password
   • SOCKS5 Proxy Host   : 127.0.0.1          ← Tor
                         : or 123.45.67.89    ← paid/residential proxy
   • SOCKS5 Port         : 9050 (Tor) or 1080 (most proxies)
   → Click "Save & Test" → Green = working!

   You can add unlimited senders & proxies → it rotates automatically.

4. FOLDERS – WHERE TO PUT YOUR STUFF
   letters/               → Put your HTML templates here (.html files)
   lists/                → One recipient per line OR Name,Email
   attachments/           → Files to attach OR drag directly into GUI

   Example list (lists/subscribers.txt):
   John Doe,john@gmail.com
   Mary Smith,mary@yahoo.com

5. PERSONALIZATION TAGS (Auto-replace in HTML letters)
   {{name}}           → Full name (John Doe)
   {{first_name}}     → First name only (John)
   {{email}}          → Full email
   {{username}}       → Part before @ (john)
   {{domain}}         → Part after @ (gmail.com)
   {{company}}        → Guessed company from domain (Google, Yahoo, Microsoft, etc.)
   {{date}}           → Today’s date (November 30, 2025)
   {{year}}           → 2025

   Example in HTML:
   Dear {{first_name}} from {{company}},

6. AUTO-GRAB COMMANDS (Copy-paste into letter)
   These are the exact codes used by the mailer to extract data:

   Full name:           {{name}}
   First name:          {{first_name}}
   Full email:          {{email}}
   Username:            {{username}}
   Domain:              {{domain}}
   Company guess:       {{company}}
   Today's date:        {{date}}
   Current year:        {{year}}

7. HOW TO USE find_sender_emails.py (Grab emails from any text)
   Put any text file with emails in the main folder → Run:
   python3 find_sender_emails.py input.txt
   → Creates found_emails.txt with clean list (one email per line)

   Example:
   python3 find_sender_emails.py messy_dump.txt

8. HOW TO USE send_via_socks5.py (Direct command-line send)
   python3 send_via_socks5.py \
     --smtp smtp.gmail.com \
     --port 587 \
     --email you@gmail.com \
     --password "apppassword123" \
     --proxy 127.0.0.1:9050 \
     --to recipient@gmail.com \
     --subject "Test" \
     --html letters/welcome.html \
     --attach attachments/contract.pdf

9. BUILT-IN HTML EDITOR
   Double-click editor.html → Opens in browser
   Write or paste HTML → Save → It appears instantly in GUI dropdown

10. LOGS & BACKUPS
   logs/                  → Every sent email logged with timestamp
   qr_codes/              → Click "Backup Config" → QR code of all settings

11. QUICK START CHECKLIST
   [ ] Run: python3 gui_mailer.py
   [ ] Add at least one sender + proxy
   [ ] Put HTML in letters/
   [ ] Put list in lists/
   [ ] Drag attachments or use folder
   [ ] Select everything → Click START

12. PRO TIPS
   • Use Gmail App Passwords (not real password)
   • Tor = 127.0.0.1:9050 (run Tor Browser in background)
   • Random delay 15–60 seconds avoids spam flags
   • Never commit real config.json to GitHub!

You now own one of the most powerful anonymous bulk mailers on the planet.
Use responsibly. Stay invisible.

– IDEYWITH231
══════════════════════════════════════════════════════════
