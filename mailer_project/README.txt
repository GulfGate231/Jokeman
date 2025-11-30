═══════════════════════════════════════════════════════════
  Advanced SOCKS5 Email Sender with Full GUI
           (Tor / Residential Proxies / Any SMTP)
                Built By IDEYWITHU
═══════════════════════════════════════════════════════════

What this program actually does
────────────────────────────────────────────────────
This is a complete bulk/mail-merge email tool that forces EVERY single email
through a SOCKS5 proxy (Tor, Luminati, 911.re, Sock5 residential pools, etc.).
That means:
• Your real IP is hidden
• You can rotate thousands of proxies if you want
• Gmail / Outlook / Yahoo / custom SMTP — all work the same
• Full drag & drop GUI — no command-line needed after first setup
• Send personalised HTML emails with attachments to thousands of recipients

Perfect for newsletters, outreach, notifications — while staying anonymous.

Features in detail
──────────────────
✓ Send through any SOCKS5 proxy → 127.0.0.1:9050 (Tor) or any paid proxy
✓ Unlimited sender accounts (add as many as you want in config)
✓ Load recipient lists → just one email per line in /lists/yourlist.txt
✓ HTML email templates → put your .html files in /letters folder (images auto embedded or remote)
✓ Attachments → drag & drop files or whole folders into the window
✓ Random delay between emails (avoids spam filters)
✓ Rotate proxies automatically if you put multiple in config
✓ Full logging → every sent email is saved in /logs with timestamp
✓ QR code backup of your entire config (scan with phone if you lose the file)
✓ Works on Windows, macOS and Linux without changing anything

Folder structure explained
──────────────────────────
attachments/      → put files here OR drag them directly into the GUI
letters/          → your HTML templates (example_letter.html etc.)
lists/            → your recipient lists (one email per line)
logs/             → automatically created — every sent mail is logged here
qr_codes/         → your config backup as QR code (super useful)
config.json       → created on first run — contains all your settings

First-time installation (30 seconds)
────────────────────────────────────
1. Install Python from https://python.org (tick “Add to PATH”)
2. Unzip this folder anywhere
3. Open terminal / command prompt in this folder
4. Run once:
   pip install -r requirements.txt
   (this installs only 4 small packages — works on Windows & Mac)

How to run the program
──────────────────────
Just double-click run.bat (Windows)  
or in terminal type:
   python gui_mailer.py

First start — quick setup wizard
────────────────────────────────
When you run it the first time:
1. Click “Add Sender” → fill in:
   • SMTP server (gmail.com, smtp-mail.outlook.com, etc.)
   • Port (587 or 465)
   • Your email + password/app-password
   • SOCKS5 proxy host & port (example: 127.0.0.1   9050 for Tor)
2. Click “Save & Test Connection” — it will tell you instantly if it works
3. (Optional) Add more sender accounts or more proxies for rotation

How to send a real campaign
───────────────────────────
1. Put your HTML letter in /letters (you can use images with normal <img src="…">)
2. Put your recipient list in /lists (one email per line, or name,email if you want personalisation)
3. Put attachments in /attachments folder or just drag them into the window
4. Choose your sender account, letter, list, delay range
5. Click START → watch the log in real time

Personalisation example
───────────────────────
If your list is:
John,john@gmail.com
Mary,mary@yahoo.com

and your letter contains  {{name}}  then it will become “Dear John”, “Dear Mary” automatically.

Safety & best practices
───────────────────────
• Use app-passwords (Gmail) or OAuth if possible
• Never upload config.json with real passwords to GitHub
• Test with 5–10 recipients first
• Start with 15–60 second random delay
• For maximum anonymity → run Tor Browser in background (it listens on 9050)

That’s it — you now have a full-featured, anonymous bulk mailer that looks professional and is extremely hard to trace.

Enjoy and stay safe!


Questions? Message the original author
