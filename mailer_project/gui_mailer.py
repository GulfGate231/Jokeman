#!/usr/bin/env python3
"""
ULTIMATE MAILER GUI - FULLY FIXED
- All tabs
- Save/Load config.json
- Test email
- Launch mailer
- SOCKS5 ready
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import subprocess
import threading
from pathlib import Path

# --------------------------------------------------------------
# CONFIG DEFAULTS
# --------------------------------------------------------------
DEFAULT_CONFIG = {
    "HTML_LETTER_PATH": "letters/welcome.html",
    "CSV_LIST_PATH": "lists/subscribers.csv",
    "ATTACHMENT_PATHS": [],
    "ENABLE_ATTACHMENTS": True,
    "ENABLE_QR_CODE": True,
    "EMAIL_SUBJECT": "Exclusive Update for {{name}} at {{company}}",
    "SENDER_EMAIL": "your@gmail.com",
    "SMTP_HOST": "smtp.gmail.com",
    "SMTP_PORT": 587,
    "SMTP_USER": "your@gmail.com",
    "SMTP_PASS": "your-app-password",
    "PROXY_HOST": "",
    "PROXY_PORT": 1080,
    "PROXY_USER": "",
    "PROXY_PASS": "",
    "TRACKING_BASE_URL": "https://yourdomain.com/track",
    "DELAY_BETWEEN_EMAILS": 1.5,
    "MAX_THREADS": 5,
    "BATCH_SIZE": 0
}

CONFIG_FILE = Path("config.json")
BASE_DIR = Path(__file__).parent

# --------------------------------------------------------------
# GUI APP
# --------------------------------------------------------------
class MailerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Mailer Config Panel")
        self.root.geometry("850x720")
        self.root.configure(padx=20, pady=20)

        self.config = DEFAULT_CONFIG.copy()

        self.create_widgets()  # MUST come before load_config
        self.load_config()     # Now safe

    def create_widgets(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        # === TAB 1: Paths ===
        tab1 = ttk.Frame(nb)
        nb.add(tab1, text="Paths")

        self.path_vars = {}
        paths = [
            ("HTML Letter", "HTML_LETTER_PATH", "file", "*.html"),
            ("CSV List", "CSV_LIST_PATH", "file", "*.csv"),
        ]
        for label, key, ftype, ext in paths:
            row = ttk.Frame(tab1)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":", width=20).pack(side="left")
            var = tk.StringVar(value=str(BASE_DIR / self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=50)
            entry.pack(side="left", padx=5, expand=True, fill="x")
            btn = ttk.Button(row, text="Browse", command=lambda k=key, v=var, t=ftype, e=ext: self.browse_file(k, v, t, e))
            btn.pack(side="right")
            self.path_vars[key] = var

        # Attachments
        row = ttk.Frame(tab1)
        row.pack(fill="x", pady=10)
        ttk.Label(row, text="Attachments:", width=20).pack(side="left")
        self.attach_listbox = tk.Listbox(row, height=4)
        self.attach_listbox.pack(side="left", padx=5, expand=True, fill="x")
        btn_frame = ttk.Frame(row)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="+", width=3, command=self.add_attachment).pack()
        ttk.Button(btn_frame, text="-", width=3, command=self.remove_attachment).pack()
        self.update_attachment_list()

        # === TAB 2: Toggles ===
        tab2 = ttk.Frame(nb)
        nb.add(tab2, text="Toggles")

        self.toggle_vars = {}
        toggles = [
            ("Enable Attachments", "ENABLE_ATTACHMENTS"),
            ("Enable QR Code", "ENABLE_QR_CODE"),
        ]
        for label, key in toggles:
            var = tk.BooleanVar(value=self.config[key])
            chk = ttk.Checkbutton(tab2, text=label, variable=var)
            chk.pack(anchor="w", pady=5)
            self.toggle_vars[key] = var

        # === TAB 3: Email & SMTP ===
        tab3 = ttk.Frame(nb)
        nb.add(tab3, text="Email & SMTP")

        entries = [
            ("Subject", "EMAIL_SUBJECT", False),
            ("Sender Email", "SENDER_EMAIL", False),
            ("SMTP Host", "SMTP_HOST", False),
            ("SMTP Port", "SMTP_PORT", False),
            ("SMTP User", "SMTP_USER", False),
            ("SMTP Pass", "SMTP_PASS", True),
        ]
        self.entry_vars = {}
        for label, key, is_pass in entries:
            row = ttk.Frame(tab3)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":", width=15).pack(side="left")
            var = tk.StringVar(value=str(self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=50, show="*" if is_pass else "")
            entry.pack(side="left", padx=5, expand=True, fill="x")
            self.entry_vars[key] = var

        # === TAB 4: Proxy & Tracking ===
        tab4 = ttk.Frame(nb)
        nb.add(tab4, text="Proxy & Tracking")

        proxy_entries = [
            ("Proxy Host", "PROXY_HOST", False),
            ("Proxy Port", "PROXY_PORT", False),
            ("Proxy User", "PROXY_USER", False),
            ("Proxy Pass", "PROXY_PASS", True),
            ("Tracking URL", "TRACKING_BASE_URL", False),
        ]
        for label, key, is_pass in proxy_entries:
            row = ttk.Frame(tab4)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":", width=15).pack(side="left")
            var = tk.StringVar(value=str(self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=50, show="*" if is_pass else "")
            entry.pack(side="left", padx=5, expand=True, fill="x")
            self.entry_vars[key] = var

        # === TAB 5: Sending ===
        tab5 = ttk.Frame(nb)
        nb.add(tab5, text="Sending")

        send_opts = [
            ("Delay (sec)", "DELAY_BETWEEN_EMAILS", float),
            ("Max Threads", "MAX_THREADS", int),
            ("Batch Size", "BATCH_SIZE", int),
        ]
        for label, key, typ in send_opts:
            row = ttk.Frame(tab5)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":", width=15).pack(side="left")
            var = tk.StringVar(value=str(self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=20)
            entry.pack(side="left", padx=5)
            self.entry_vars[key] = var
            self.entry_vars[f"{key}_type"] = typ

        # === Buttons ===
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Save Config", command=self.save_config).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Load Config", command=self.load_config).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Test Email", command=self.test_email).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Launch Mailer", command=self.launch_mailer).grid(row=0, column=3, padx=5)

        # === Status ===
        self.status = ttk.Label(self.root, text="Ready", foreground="green")
        self.status.pack(pady=5)

    def browse_file(self, key, var, ftype, ext):
        if ftype == "file":
            path = filedialog.askopenfilename(filetypes=[(ext[1:], ext)])
        else:
            path = filedialog.askdirectory()
        if path:
            var.set(path)

    def add_attachment(self):
        path = filedialog.askopenfilename()
        if path:
            self.config["ATTACHMENT_PATHS"].append(path)
            self.update_attachment_list()

    def remove_attachment(self):
        sel = self.attach_listbox.curselection()
        if sel:
            idx = sel[0]
            del self.config["ATTACHMENT_PATHS"][idx]
            self.update_attachment_list()

    def update_attachment_list(self):
        self.attach_listbox.delete(0, tk.END)
        for p in self.config["ATTACHMENT_PATHS"]:
            self.attach_listbox.insert(tk.END, Path(p).name)

    def save_config(self):
        try:
            # Update from GUI
            for key, var in self.path_vars.items():
                self.config[key] = Path(var.get()).relative_to(BASE_DIR).as_posix()
            self.config["ATTACHMENT_PATHS"] = [
                Path(p).relative_to(BASE_DIR).as_posix() for p in self.config["ATTACHMENT_PATHS"]
            ]
            for key, var in self.toggle_vars.items():
                self.config[key] = var.get()
            for key, var in self.entry_vars.items():
                if "_type" not in key:
                    typ = self.entry_vars.get(f"{key}_type", str)
                    val = var.get()
                    self.config[key] = typ(val) if typ != str else val

            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=2)
            self.status.config(text="Config saved!", foreground="green")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    loaded = json.load(f)
                self.config.update(loaded)

                for key, var in self.path_vars.items():
                    var.set(str(BASE_DIR / self.config.get(key, "")))
                for key, var in self.toggle_vars.items():
                    var.set(self.config.get(key, True))
                for key, var in self.entry_vars.items():
                    if "_type" not in key:
                        var.set(str(self.config.get(key, "")))
                self.update_attachment_list()
                self.status.config(text="Config loaded!", foreground="green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {e}")
        else:
            self.status.config(text="No config.json", foreground="orange")

    def test_email(self):
        self.save_config()
        email = simpledialog.askstring("Test Email", "Your email:")
        if not email:
            return
        threading.Thread(target=self._run_test, args=(email,), daemon=True).start()

    def _run_test(self, email):
        try:
            self.status.config(text="Sending test...", foreground="blue")
            self.root.update()
            result = subprocess.run([
                "python3", "send_via_socks5.py", "--test-email", email
            ], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.status.config(text="Test sent!", foreground="green")
            else:
                self.status.config(text="Test failed", foreground="red")
                messagebox.showerror("Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def launch_mailer(self):
        self.save_config()
        if messagebox.askyesno("Launch", "Start campaign?"):
            threading.Thread(target=self._run_mailer, daemon=True).start()

    def _run_mailer(self):
        try:
            self.status.config(text="Running...", foreground="blue")
            self.root.update()
            result = subprocess.run(["python3", "send_via_socks5.py"], capture_output=True, text=True)
            if result.returncode == 0:
                self.status.config(text="Complete!", foreground="green")
            else:
                self.status.config(text="Failed", foreground="red")
                messagebox.showerror("Error", result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --------------------------------------------------------------
# Run
# --------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MailerGUI(root)
    root.mainloop()
