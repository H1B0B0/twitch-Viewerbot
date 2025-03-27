# Twitch Viewer Bot

A modern web application for generating Twitch views using proxies, built with a Flask backend and React frontend.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Standard Installation](#standard-installation)
  - [Development Installation](#development-installation)
  - [Server Installation](#server-installation)
- [Usage](#usage)
  - [For End Users](#for-end-users)
  - [For Developers](#for-developers)
  - [For Server Deployment](#for-server-deployment)
- [macOS Installation Guide](#macos-installation-guide)
- [Screenshots](#screenshots)
- [License](#license)
- [Disclaimer](#disclaimer)

## Features

- 🚀 Multi-threading system supporting up to 1000 simultaneous threads
- 🔄 Automatic proxy rotation and management
- 🌐 Support for HTTP, SOCKS4, and SOCKS5 proxies
- 📊 Real-time statistics dashboard
- 🔒 SSL/HTTPS support with Let's Encrypt integration
- 📱 Responsive web interface
- 🖥️ Remote access support via server edition

## Requirements

- Python 3.9+
- Modern web browser
- Internet connection
- (Optional) Custom proxy list
- (For server edition) Domain name pointing to your server
- (For server edition) Certbot installed for Let's Encrypt certificates

## Installation

### Standard Installation

1. Download the executable from the [releases page](https://github.com/H1B0B0/twitch-Viewerbot/releases)
2. Launch the application
3. Login or register an account
4. Configure your settings
5. Start the bot

### Development Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/H1B0B0/twitch-Viewerbot.git
   ```

2. Navigate to the project directory:

   ```shell
   cd twitch-Viewerbot
   ```

3. Install the required Python packages:

   ```shell
   pip install -r requirements.txt
   ```

4. Build the static Frontend:

   **Windows**

   ```shell
   ./build.ps1
   ```

   **Linux / macOS**

   ```shell
   ./build.sh
   ```

5. Launch the backend:
   ```shell
   python ./backend/main.py --dev
   ```

### Server Installation

To deploy the application on a server with remote access:

1. Install Certbot for Let's Encrypt:

   ```shell
   # Debian/Ubuntu
   sudo apt-get update
   sudo apt-get install certbot

   # CentOS/RHEL
   sudo yum install certbot
   ```

2. Make sure your domain points to your server and ports 80 and 443 are open

3. Launch the application with domain and email arguments:

   ```shell
   sudo python ./backend/main.py --domain yourdomain.com --email your@email.com --no-browser
   ```

4. The application will automatically obtain Let's Encrypt certificates

5. Access the application securely at https://yourdomain.com

## Usage

### For End Users

1. Open your web browser and navigate to `https://velbots.shop`
2. Enter the number of threads you want to run
3. Enter the name of the Twitch channel you want to generate views for
4. (Optional) Upload your custom proxy list
5. Click the "Start bot" button to begin generating views

### For Developers

- The `--dev` flag enables development mode
- Check the console for logs and debugging information
- Frontend code is located in the `frontend` directory
- Backend API endpoints are defined in `backend/main.py`

### For Server Deployment

- Use the `--domain` parameter to specify your domain name
- Use the `--email` parameter to provide an email for Let's Encrypt registration
- Use the `--renew` flag to force certificate renewal
- Use the `--no-browser` flag to prevent the application from opening a browser
- Run the application with sudo or as root to bind to port 443

## macOS Installation Guide

1. Download the application from the [release page](https://github.com/H1B0B0/twitch-Viewerbot/releases)

   ![macOS version](./images/macos_file.png)

2. If macOS blocks the application, open **System Settings** and go to **Privacy & Security**

   ![macOS block message](./images/macos_block.png)

3. Under the **Security** tab, locate the message about the blocked application and click **Open Anyway**

   ![Enable macOS application](images/enable_macos.png)

4. Confirm that you want to open the application by clicking **Open Anyway** in the dialog

   ![Execute the app](./images/use_macos.png)

5. The application will now launch and is ready to use 🚀

## Screenshots

![Dashboard View](https://github.com/user-attachments/assets/c292df62-3bde-4240-93c3-a83f573af90e)
![Statistics Panel](https://github.com/user-attachments/assets/ff64062e-7b30-4b14-9faf-0f798197222f)
![Configuration Screen](https://github.com/user-attachments/assets/349d778e-310a-4899-9667-8e1da2893fa8)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

⚠️ **This tool is provided for educational purposes only** ⚠️

Using this software to artificially inflate viewer counts may violate Twitch's Terms of Service. The developers are not responsible for any consequences resulting from the misuse of this application.
