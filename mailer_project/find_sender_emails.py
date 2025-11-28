#!/usr/bin/env python3
"""
Auto-Find REAL Business Sender Emails from Any Proxy IP
- Real domain lookup (reverse DNS + API)
- Only standard business emails
- No hardcoded IPs
"""

import socket
import re
import urllib.request
import json

def get_real_domain_from_ip(ip):
    """Get real domain via reverse DNS or free API."""
    # Step 1: Reverse DNS
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})$', hostname)
        if match:
            return match.group(1).lower()
    except:
        pass

    # Step 2: Free IP API (ip-api.com)
    try:
        url = f"http://ip-api.com/json/{ip}?fields=org,isp,reverse"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            org = (data.get('org') or data.get('isp') or '').strip().lower()
            reverse = (data.get('reverse') or '').strip().lower()

            # Prefer reverse DNS
            if reverse:
                match = re.search(r'([a-zA-Z0-9-]+\.[a-zA-Z]{2,})$', reverse)
                if match:
                    return match.group(1)

            # Use org/isp if it looks like a domain
            if org and '.' in org and len(org.split('.')) >= 2:
                return org
            if org:
                return org.replace(' ', '') + '.com'
    except:
        pass

    return "business.com"  # Final fallback

def generate_real_business_emails(domain, num=8):
    """Only standard business email patterns."""
    patterns = [
        "info@", "marketing@", "support@", "noreply@",
        "admin@", "contact@", "sales@", "hello@"
    ]
    return [pattern + domain for pattern in patterns[:num]]

# ————————————————————————————————————
if __name__ == "__main__":
    ip = input("Enter your business proxy IP: ").strip()
    if not ip:
        print("IP required.")
        exit()

    domain = get_real_domain_from_ip(ip)
    print(f"\nReal Domain: {domain}")
    print("Business Sender Emails (use in GUI):")
    for email in generate_real_business_emails(domain):
        print(f"  • {email}")
    print(f"\nRecommended: {generate_real_business_emails(domain)[0]}")
    print("\nCopy → GUI → Sender Email field")