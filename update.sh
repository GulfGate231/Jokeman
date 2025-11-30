#!/bin/bash
cd "$(dirname "$(find ~ -name gui_mailer.py -print -quit 2>/dev/null)")" 2>/dev/null || { echo "Mailer not found! Run fresh install first."; exit 1; }
echo "Updating Jokeman Mailer to latest version..."
git pull origin main
pip3 install -r requirements.txt --upgrade >/dev/null 2>&1
echo "Updated! Launching..."
python3 gui_mailer.py
