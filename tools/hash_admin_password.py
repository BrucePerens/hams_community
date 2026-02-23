#!/usr/bin/env python3
import sys
import os
import getpass
try:
    from passlib.context import CryptContext
except ImportError:
    print("[!] Please install passlib first: pip install passlib")
    sys.exit(1)

def main():
    print("====================================")
    print("     Odoo Admin Password Hasher     ")
    print("====================================")
    pwd = getpass.getpass("Enter new admin password: ")
    pwd2 = getpass.getpass("Confirm password: ")
    if pwd != pwd2:
        print("[!] Passwords do not match!")
        sys.exit(1)
        
    # Odoo 19 utilizes pbkdf2_sha512 natively
    ctx = CryptContext(schemes=["pbkdf2_sha512"])
    hashed = ctx.hash(pwd)
    
    # Resolve the absolute path to deploy/.env based on this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.abspath(os.path.join(script_dir, '..', 'deploy', '.env'))
    
    print(f"\n[*] Generated Hash: {hashed}")
    print(f"[*] Updating {env_path}...")
    
    if not os.path.exists(env_path):
        print(f"[!] Warning: {env_path} does not exist. Creating it.")
        lines = []
    else:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    updated = False
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            # Safely replace the target line while preserving the rest of the vault
            if line.startswith('ODOO_ADMIN_PASSWORD='):
                f.write(f"ODOO_ADMIN_PASSWORD={hashed}\n")
                updated = True
            else:
                f.write(line)
        
        # If the key wasn't found in the existing file, append it
        if not updated:
            f.write(f"ODOO_ADMIN_PASSWORD={hashed}\n")
            
    print("\n[+] Success! The .env file has been automatically updated with the new hashed password.")
    print("[*] Remember to recreate your Docker containers or restart the Odoo service for the hook to apply it.")

if __name__ == '__main__':
    main()
