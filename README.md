# Jokeman – Advanced SOCKS5 Email Sender (Full GUI)

Anonymous bulk email tool that routes **every email through a SOCKS5 proxy**  
(Tor · residential proxies · any SOCKS5 service).

Works perfectly with Gmail, Outlook, Yahoo, custom SMTP.  
Full drag-and-drop GUI, HTML templates, attachments, logging, QR backup.

### Features
- Full SOCKS5 support (PySocks)
- Unlimited sender accounts & proxies
- Drag & drop files/folders into the window
- HTML letters (local + remote images)
- Personalisation with `{{name}}`, `{{email}}`, etc.
- Random delays between emails
- Detailed logs + QR code config backup
- Runs on Windows · macOS · Linux

### One-command installation & launch

Open Terminal / PowerShell and paste this single line:

```bash
git clone https://github.com/GulfGate231/Jokeman.git && cd Jokeman/mailer_project && pip install -r requirements.txt && python gui_mailer.py
