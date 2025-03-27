# Server Setup Guide for Twitch Viewer Bot

This guide explains how to set up the Twitch Viewer Bot on a server with HTTPS support using Let's Encrypt certificates.

## Prerequisites

- A server with a public IP address
- A domain name pointing to your server
- Root or sudo access on your server
- Python 3.9+ installed
- Ports 80 and 443 open in your firewall

## Step 1: Install Required Software

First, install the required software on your server:

```bash
# For Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv certbot

# For CentOS/RHEL
sudo yum install python3 python3-pip certbot
```

## Step 2: Set Up the Project

1. Clone the repository:

```bash
git clone https://github.com/H1B0B0/twitch-Viewerbot.git
cd twitch-Viewerbot
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create the certificates directory:

```bash
mkdir -p backend/certs
```

## Step 3: Obtain Let's Encrypt Certificates

Let's Encrypt certificates can be obtained manually using certbot:

```bash
# Make sure port 80 is available (stop any web servers)
sudo systemctl stop apache2    # If you use Apache
sudo systemctl stop nginx      # If you use Nginx

# Obtain the certificate
sudo certbot certonly --standalone -d yourdomain.com
```

This will generate certificates at `/etc/letsencrypt/live/yourdomain.com/`.

## Step 4: Copy Certificates to the Application

Copy the Let's Encrypt certificates to the application directory:

```bash
# Create the certs directory if it doesn't exist
mkdir -p backend/certs

# Copy the certificates (use your domain name)
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem backend/certs/yourdomain.com.cert
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem backend/certs/yourdomain.com.key
```

## Step 5: Run the Application

Now you can run the application with HTTPS support:

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run the application with domain information
sudo ./venv/bin/python backend/main.py --domain yourdomain.com --email your@email.com --no-browser --dev
```

The `--dev` flag bypasses authentication for testing. For production, set up a JWT_SECRET in your environment variables:

```bash
# Create a .env file in the backend directory
echo "JWT_SECRET=your_secure_random_string" > backend/.env

# Then run without the --dev flag
sudo ./venv/bin/python backend/main.py --domain yourdomain.com --email your@email.com --no-browser
```

## Troubleshooting

### Certificate Not Found

If the application can't find your certificates, check:

1. The certificates are in the correct location (`backend/certs/`)
2. The certificate files have the correct names:

   - For certificates: `yourdomain.com.cert` or `fullchain.pem`
   - For private keys: `yourdomain.com.key` or `privkey.key`

3. The permissions allow the application to read the files:
   ```bash
   sudo chmod 644 backend/certs/yourdomain.com.cert
   sudo chmod 600 backend/certs/yourdomain.com.key
   ```

### Port 80/443 Already in Use

If ports 80 or 443 are already in use, you need to stop the services using them:

```bash
# Find services using port 80/443
sudo lsof -i :80
sudo lsof -i :443

# Stop the services (example for Apache)
sudo systemctl stop apache2
```

### ERR_CONNECTION_REFUSED Error

If you get "ERR_CONNECTION_REFUSED" when trying to access your server, check:

1. **Check if the server is running:**

   ```bash
   ps aux | grep python
   ```

2. **Verify the domain points to your server's public IP:**

   ```bash
   # Install dig if needed
   sudo apt install dnsutils

   # Check what IP your domain resolves to
   dig +short yourdomain.com

   # Compare with your public IP
   curl https://api.ipify.org
   ```

3. **Check if ports are open on your server:**

   ```bash
   # Install netstat if needed
   sudo apt install net-tools

   # Check listening ports
   sudo netstat -tulpn | grep -E ':80|:443'
   ```

4. **Verify firewall settings:**

   ```bash
   # For UFW
   sudo ufw status

   # For iptables
   sudo iptables -L

   # Allow ports if needed
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

5. **Check port forwarding on your router:**

   - Log into your router's admin panel
   - Look for port forwarding or virtual server settings
   - Ensure ports 80 and 443 are forwarded to your server's internal IP

6. **Run the diagnostic script:**
   ```bash
   python backend/network_check.py --domain yourdomain.com
   ```

### Private/Local Domains

If you're using a private domain (like example.private.local):

1. **For local network access only:**

   - Add the domain to your hosts file on client machines:

   ```
   192.168.1.x  yourdomain.private.local
   ```

2. **For public access:**
   - Use a public domain instead
   - Or set up Split DNS with a local DNS server

### Certificate Works But Site Inaccessible

If your certificates are valid but the site is still inaccessible:

1. **Check application logs:**

   ```bash
   # View the last 50 lines of the log
   tail -n 50 application.log
   ```

2. **Test HTTPS locally on the server:**

   ```bash
   curl -k https://localhost
   ```

3. **Check if certificates are properly set up:**
   ```bash
   # Test the certificate configuration
   sudo openssl s_client -connect localhost:443
   ```

## Running as a Service

For production deployments, you should run the application as a service:

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/twitchbot.service
```

2. Add the following content:

```ini
[Unit]
Description=Twitch Viewer Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/twitch-Viewerbot
ExecStart=/path/to/twitch-Viewerbot/venv/bin/python /path/to/twitch-Viewerbot/backend/main.py --domain yourdomain.com --email your@email.com --no-browser
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable twitchbot
sudo systemctl start twitchbot
```

4. Check service status:

```bash
sudo systemctl status twitchbot
```
