#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import subprocess
import threading
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"

# Default config
DEFAULT_CONFIG = {
    "ENABLE_ROTATION": False,
    "SINGLE_SMTP_HOST": "smtp.gmail.com",
    "SINGLE_SMTP_PORT": 587,
    "SINGLE_SMTP_USER": "",
    "SINGLE_SMTP_PASS": "",
    "SINGLE_SMTP_NAME": "Alex Rivera",

    "HTML_LETTER_PATH": "letters/template.html",
    "CSV_LIST_PATH": "lists/contacts.csv",
    "ATTACHMENT_PATHS": [],

    "EMAIL_SUBJECT": "Hey {{name}}, quick note from {{sender}}",
    "MAX_THREADS": 5,
    "DELAY_RANGE_MIN": 14,
    "DELAY_RANGE_MAX": 42,
    "WARMUP_FIRST_30": True,
    "ENABLE_QR_CODE": False,
    "ENABLE_ATTACHMENTS": True,
    "ENABLE_PIXEL": False
}

class MailerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Elite Inbox Mailer 2025 - Config Panel")
        self.root.geometry("920x760")
        self.root.configure(padx=20, pady=20)
        self.config = DEFAULT_CONFIG.copy()
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        # === TAB 1: SMTP Settings ===
        tab_smtp = ttk.Frame(nb)
        nb.add(tab_smtp, text="SMTP Settings")

        ttk.Label(tab_smtp, text="SMTP Mode:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,5))
        self.rot_var = tk.BooleanVar(value=self.config["ENABLE_ROTATION"])
        ttk.Checkbutton(tab_smtp, text="Enable SMTP Rotation (multiple accounts)", variable=self.rot_var,
                        command=self.toggle_rotation).pack(anchor="w", padx=20)

        # Single SMTP (always visible)
        single_frame = ttk.LabelFrame(tab_smtp, text="Single SMTP Account (used when rotation OFF)")
        single_frame.pack(fill="x", pady=10, padx=10)

        rows = [
    ("SMTP Host", "SINGLE_SMTP_HOST", False),
    ("SMTP Port", "SINGLE_SMTP_PORT", False),
    ("SMTP User (email)", "SINGLE_SMTP_USER", False),
    ("SMTP Password", "SINGLE_SMTP_PASS", True),
    ("Display Name", "SINGLE_SMTP_NAME", False),
]
        self.single_vars = {}
        for label, key, password in rows:
            row = ttk.Frame(single_frame)
            row.pack(fill="x", pady=4, padx=10)
            ttk.Label(row, text=label + ":", width=18).pack(side="left")
            var = tk.StringVar(value=str(self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=50, show="*" if password else "")
            entry.pack(side="left", padx=5, expand=True, fill="x")
            self.single_vars[key] = var

        # === TAB 2: Paths & Attachments ===
        tab_paths = ttk.Frame(nb)
        nb.add(tab_paths, text="Paths & Attachments")

        path_frame = ttk.LabelFrame(tab_paths, text="Files")
        path_frame.pack(fill="x", pady=10, padx=10)

        paths = [
            ("HTML Template", "HTML_LETTER_PATH", "*.html"),
            ("CSV Contacts", "CSV_LIST_PATH", "*.csv"),
        ]
        self.path_vars = {}
        for label, key, ext in paths:
            row = ttk.Frame(path_frame)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":", width=16).pack(side="left")
            var = tk.StringVar(value=str(BASE_DIR / self.config[key]))
            entry = ttk.Entry(row, textvariable=var, width=60)
            entry.pack(side="left", padx=5, expand=True, fill="x")
            btn = ttk.Button(row, text="Browse", command=lambda k=key, v=var, e=ext: self.browse_file(v, e))
            btn.pack(side="right")
            self.path_vars[key] = var

        # Attachments
        attach_frame = ttk.LabelFrame(tab_paths, text="Attachments (PDF, HTML, EML, SVG)")
        attach_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.attach_listbox = tk.Listbox(attach_frame, height=8)
        self.attach_listbox.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)
        btns = ttk.Frame(attach_frame)
        btns.pack(side="right", padx=10, pady=10)
        ttk.Button(btns, text="Add File", command=self.add_attachment).pack(pady=5, fill="x")
        ttk.Button(btns, text="Remove", command=self.remove_attachment).pack(pady=5, fill="x")
        ttk.Button(btns, text="Clear All", command=lambda: self.config.update({"ATTACHMENT_PATHS": []}) or self.update_attach_list()).pack(pady=5, fill="x")

        # === TAB 3: Campaign Settings ===
        tab_settings = ttk.Frame(nb)
        nb.add(tab_settings, text="Campaign")

        self.setting_vars = {}
        settings = [
            ("Subject Line", "EMAIL_SUBJECT"),
            ("Max Threads", "MAX_THREADS", int),
            ("Delay Min (sec)", "DELAY_RANGE_MIN", float),
            ("Delay Max (sec)", "DELAY_RANGE_MAX", float),
        ]
        for label, key, typ in settings:
            row = ttk.Frame(tab_settings)
            row.pack(fill="x", pady=6, padx=20)
            ttk.Label(row, text=label + ":", width=18).pack(side="left")
            var = tk.StringVar(value=str(self.config[key]))
            ttk.Entry(row, textvariable=var, width=40).pack(side="left", padx=5)
            self.setting_vars[key] = (var, typ)

        # Toggles
        toggles_frame = ttk.LabelFrame(tab_settings, text="Features")
        toggles_frame.pack(fill="x", pady=10, padx=20)
        toggles = [
            ("Warmup first 30 emails", "WARMUP_FIRST_30"),
            ("Enable QR Code", "ENABLE_QR_CODE"),
            ("Enable Attachments", "ENABLE_ATTACHMENTS"),
            ("Enable Tracking Pixel", "ENABLE_PIXEL"),
        ]
        self.toggle_vars = {}
        for text, key in toggles:
            var = tk.BooleanVar(value=self.config[key])
            ttk.Checkbutton(toggles_frame, text=text, variable=var).pack(anchor="w", padx=20, pady=3)
            self.toggle_vars[key] = var

        # === Buttons ===
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="Save Config", command=self.save_config).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Load Config", command=self.load_config).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Test Email", command=self.test_email).grid(row=0, column=2, padx=10)
        ttk.Button(btn_frame, text="LAUNCH CAMPAIGN", style="Accent.TButton", command=self.launch_mailer).grid(row=0, column=3, padx=10)

        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#0066cc", font=("Arial", 10, "bold"))

        self.status = ttk.Label(self.root, text="Ready", foreground="green", font=("Arial", 11))
        self.status.pack(pady=5)

        self.update_attach_list()

    def toggle_rotation(self):
        state = "normal" if self.rot_var.get() else "disabled"
        # You can expand this later to show rotating accounts list if needed

    def browse_file(self, var, ext):
        path = filedialog.askopenfilename(filetypes=[("Files", ext)])
        if path:
            var.set(path)

    def add_attachment(self):
        paths = filedialog.askopenfilenames(filetypes=[("All Supported", "*.pdf *.html *.eml *.svg *.png *.jpg")])
        if paths:
            current = self.config.get("ATTACHMENT_PATHS", [])
            self.config["ATTACHMENT_PATHS"] = list(current) + list(paths)
            self.update_attach_list()

    def remove_attachment(self):
        sel = self.attach_listbox.curselection()
        if sel:
            idx = sel[0]
            paths = self.config.get("ATTACHMENT_PATHS", [])
            del paths[idx]
            self.config["ATTACHMENT_PATHS"] = paths
            self.update_attach_list()

    def update_attach_list(self):
        self.attach_listbox.delete(0, tk.END)
        for p in self.config.get("ATTACHMENT_PATHS", []):
            self.attach_listbox.insert(tk.END, Path(p).name)

    def save_config(self):
        try:
            # Save paths
            for key, var in self.path_vars.items():
                path = Path(var.get())
                self.config[key] = path.relative_to(BASE_DIR).as_posix() if path.is_absolute() else path.as_posix()

            # Save single SMTP
            for key, var in self.single_vars.items():
                self.config[key] = var.get().strip()

            # Save toggles & settings
            self.config["ENABLE_ROTATION"] = self.rot_var.get()
            for key, var in self.toggle_vars.items():
                self.config[key] = var.get()
            for key, (var, typ) in self.setting_vars.items():
                val = var.get().strip()
                self.config[key] = typ(val) if val else DEFAULT_CONFIG[key]

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)

            self.status.config(text="Config saved successfully!", foreground="green")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.config.update(loaded)

                # Restore GUI
                self.rot_var.set(self.config.get("ENABLE_ROTATION", False))
                for key, var in self.single_vars.items():
                    var.set(self.config.get(key, ""))
                for key, var in self.path_vars.items():
                    var.set(str(BASE_DIR / self.config.get(key, "")))
                for key, var in self.toggle_vars.items():
                    var.set(self.config.get(key, True))
                for key, (var, _) in self.setting_vars.items():
                    var.set(str(self.config.get(key, "")))

                self.update_attach_list()
                self.status.config(text="Config loaded!", foreground="green")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load config:\n{e}")

    def test_email(self):
        self.save_config()
        email = simpledialog.askstring("Test Email", "Enter your email to receive test:")
        if not email or "@" not in email:
            return
        threading.Thread(target=self._run_test, args=(email,), daemon=True).start()

    def _run_test(self, email):
        self.status.config(text="Sending test email...", foreground="blue")
        self.root.update()
        try:
            result = subprocess.run([
                "python3", "send_via_socks5.py", "--test", email
            ], capture_output=True, text=True, timeout=90)
            if result.returncode == 0:
                self.status.config(text="Test email sent!", foreground="green")
            else:
                self.status.config(text="Test failed", foreground="red")
                messagebox.showerror("Test Failed", result.stderr or "Unknown error")
        except subprocess.TimeoutExpired:
            self.status.config(text="Test timed out", foreground="red")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def launch_mailer(self):
        if not messagebox.askyesno("Launch Campaign", "Start sending to all contacts?"):
            return
        self.save_config()
        threading.Thread(target=self._run_mailer, daemon=True).start()

    def _run_mailer(self):
        self.status.config(text="Campaign running...", foreground="blue")
        self.root.update()
        try:
            proc = subprocess.Popen(["python3", "send_via_socks5.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate(timeout=3600)
            if proc.returncode == 0:
                self.status.config(text="Campaign completed!", foreground="green")
            else:
                self.status.config(text="Campaign failed", foreground="red")
                messagebox.showerror("Error", stderr or "Unknown error")
        except Exception as e:
            self.status.config(text="Error during campaign", foreground="red")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MailerGUI(root)
    root.mainloop()
