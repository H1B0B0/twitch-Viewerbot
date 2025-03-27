#!/usr/bin/env python3
import socket
import subprocess
import platform
import os
import sys
import requests
import argparse

def check_port_open(port):
    """Check if a port is open on the local machine"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

def get_public_ip():
    """Get public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except Exception as e:
        return f"Error getting public IP: {e}"

def check_dns(domain):
    """Check if domain resolves properly"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error running command: {e}"

def main():
    parser = argparse.ArgumentParser(description="Network Diagnostics Tool")
    parser.add_argument('--domain', help='Domain name to check')
    args = parser.parse_args()
    
    print("=== Network Diagnostics ===")
    
    # Check local network
    print("\n=== Local Network ===")
    print(f"Hostname: {socket.gethostname()}")
    try:
        print(f"Local IP: {socket.gethostbyname(socket.gethostname())}")
    except socket.gaierror:
        print("Local IP: Unable to determine")
    
    # Check ports
    print("\n=== Port Status ===")
    print(f"Port 80 (HTTP): {'Open' if check_port_open(80) else 'Closed'}")
    print(f"Port 443 (HTTPS): {'Open' if check_port_open(443) else 'Closed'}")
    print(f"Port 3001 (Dev): {'Open' if check_port_open(3001) else 'Closed'}")
    
    # Check public IP
    print("\n=== Public IP ===")
    public_ip = get_public_ip()
    print(f"Public IP: {public_ip}")
    
    # Check DNS if domain provided
    if args.domain:
        print(f"\n=== DNS for {args.domain} ===")
        ip = check_dns(args.domain)
        if ip:
            print(f"Resolves to: {ip}")
            if ip == public_ip:
                print("✅ Domain correctly points to your public IP")
            else:
                print("❌ Domain does NOT point to your public IP")
        else:
            print(f"❌ Domain {args.domain} does not resolve to an IP address")
    
    # Run platform-specific checks
    print("\n=== Platform-specific checks ===")
    system = platform.system().lower()
    
    if system == 'linux':
        print("-- Checking firewall status --")
        print(run_command("sudo iptables -L | grep -E '(DROP|REJECT|443|80)'"))
        
        print("\n-- Network interfaces --")
        print(run_command("ip addr | grep -E 'inet '"))
        
        print("\n-- Active connections --")
        print(run_command("netstat -tulpn | grep -E ':(80|443|3001)'"))
        
    elif system == 'windows':
        print("-- Checking firewall status --")
        print(run_command("netsh advfirewall show allprofiles state"))
        
        print("\n-- Network interfaces --")
        print(run_command("ipconfig /all | findstr IPv4"))
        
        print("\n-- Active connections --")
        print(run_command("netstat -ano | findstr :443"))
        
    print("\n=== Recommendations ===")
    print("1. Ensure your domain points to your server's public IP address")
    print("2. Check if your router has port forwarding enabled for ports 80 and 443")
    print("3. Make sure your firewall allows incoming connections on ports 80 and 443")
    print(f"4. Try accessing the server by IP directly: https://{public_ip}")
    print("5. For local network access, ensure the domain is in your hosts file")

if __name__ == "__main__":
    main()
