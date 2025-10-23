#!/usr/bin/env python3
"""
Command-line tool for managing access codes
Usage: python access_code_cli.py [command] [options]
"""

import sys
import argparse
from datetime import datetime, timedelta
from server_auth import AccessCodeManager

def create_code(args):
    """Create a new access code"""
    code_manager = AccessCodeManager()
    
    # Parse expiry
    expires_days = None
    if args.expires:
        if args.expires == 'never':
            expires_days = None
        else:
            try:
                expires_days = int(args.expires)
            except ValueError:
                print(f"Error: Invalid expiry value '{args.expires}'. Use a number or 'never'")
                return
    
    # Parse max uses
    max_uses = None
    if args.uses:
        if args.uses == 'unlimited':
            max_uses = None
        else:
            try:
                max_uses = int(args.uses)
            except ValueError:
                print(f"Error: Invalid uses value '{args.uses}'. Use a number or 'unlimited'")
                return
    
    # Get admin key
    admin_key = args.admin_key or input("Enter admin key: ")
    
    try:
        # Create the code
        code = code_manager.generate_access_code(
            name=args.name,
            features=args.features.split(',') if args.features else ['basic_patching'],
            expires_days=expires_days,
            max_uses=max_uses,
            admin_key=admin_key
        )
        
        print(f"Access code created: {code}")
        print(f"Name: {args.name}")
        print(f"Features: {', '.join(args.features.split(',') if args.features else ['basic_patching'])}")
        print(f"Expires: {expires_days or 'Never'} days")
        print(f"Max uses: {max_uses or 'Unlimited'}")
        print("Note: This code is encrypted and hidden from regular users")
        
    except PermissionError as e:
        print(f"Error: {e}")
        print("Admin authentication required to create access codes")

def list_codes(args):
    """List access codes"""
    code_manager = AccessCodeManager()
    
    # Get admin key if provided
    admin_key = args.admin_key if hasattr(args, 'admin_key') else None
    
    codes = code_manager.list_access_codes(admin_key)
    
    if not codes:
        print("No access codes found.")
        return
    
    if admin_key:
        print(f"All Access Codes ({len(codes)} total) - Admin View:")
    else:
        print(f"Public Access Codes ({len(codes)} total) - User View:")
    print("-" * 80)
    
    for code, data in codes.items():
        expires = "Never" if not data.get("expires_at") else "Expired" if data["expires_at"] < time.time() else "Valid"
        max_uses = "∞" if not data.get("max_uses") else str(data["max_uses"])
        visibility = "Public" if data.get("public", False) else "Private"
        
        print(f"Code: {code}")
        print(f"  Name: {data['name']}")
        print(f"  Uses: {data['used_count']}/{max_uses}")
        print(f"  Status: {expires}")
        print(f"  Features: {', '.join(data['features'])}")
        if admin_key:
            print(f"  Visibility: {visibility}")
        print()

def revoke_code(args):
    """Revoke an access code"""
    code_manager = AccessCodeManager()
    
    if code_manager.revoke_access_code(args.code):
        print(f"Code {args.code} has been revoked.")
    else:
        print(f"Code {args.code} not found.")

def status_code(args):
    """Get status of a specific code"""
    code_manager = AccessCodeManager()
    codes = code_manager.list_access_codes()
    
    if args.code not in codes:
        print(f"Code {args.code} not found.")
        return
    
    data = codes[args.code]
    current_time = time.time()
    
    print(f"Code Status: {args.code}")
    print("-" * 40)
    print(f"Name: {data['name']}")
    print(f"Features: {', '.join(data['features'])}")
    print(f"Used: {data['used_count']}/{data.get('max_uses', '∞')}")
    
    if data.get('expires_at'):
        if current_time > data['expires_at']:
            print("Status: EXPIRED")
        else:
            days_remaining = int((data['expires_at'] - current_time) / (24 * 3600))
            print(f"Status: Valid ({days_remaining} days remaining)")
    else:
        print("Status: Never expires")
    
    if data.get('max_uses') and data['used_count'] >= data['max_uses']:
        print("Usage: EXHAUSTED")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Access Code Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new access code (requires admin key)')
    create_parser.add_argument('name', help='Name/description of the code')
    create_parser.add_argument('--expires', help='Expiry in days (or "never")', default='never')
    create_parser.add_argument('--uses', help='Maximum uses (or "unlimited")', default='unlimited')
    create_parser.add_argument('--features', help='Comma-separated features', default='basic_patching')
    create_parser.add_argument('--admin-key', help='Admin key for authentication')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List access codes (admin key shows all)')
    list_parser.add_argument('--admin-key', help='Admin key to see all codes')
    
    # Revoke command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke an access code')
    revoke_parser.add_argument('code', help='Code to revoke')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get status of a code')
    status_parser.add_argument('code', help='Code to check')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Import time for status checking
    global time
    import time
    
    if args.command == 'create':
        create_code(args)
    elif args.command == 'list':
        list_codes(args)
    elif args.command == 'revoke':
        revoke_code(args)
    elif args.command == 'status':
        status_code(args)

if __name__ == '__main__':
    main()
