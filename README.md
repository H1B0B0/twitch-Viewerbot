# Twitch Viewer Bot

A modern web application for generating Twitch views using proxies, built with a Flask backend and React frontend.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Installation [DEV]](#installation-dev)
- [Usage [DEV]](#usage-dev)
- [How to use with macOS](#how-to-use-with-macos)
- [Screenshots](#screenshots)
- [License](#license)
- [Warning](#warning)

## Features

- 🚀 Multi-threading system supporting up to 1000 simultaneous threads
- 🔄 Automatic proxy rotation and management
- 🌐 Support for HTTP, SOCKS4, and SOCKS5 proxies
- 📊 Real-time statistics dashboard
- 🔒 SSL/HTTPS support
- 📱 Responsive web interface

## Requirements

- Python 3.9+
- Modern web browser
- Internet connection
- (Optional) Custom proxy list

## 💻 Installation

1. Download the executable.
2. Launch the application.
3. Login / Register.
4. Configure your settings.
5. Start the bot.

## Installation [DEV]

1. Clone the repository:
   ```shell
   git clone https://github.com/H1B0B0/twitch-Viewerbot.git
   ```
2. Navigate into the folder:
   ```shell
   cd twitch-Viewerbot
   ```
3. Install the required Python packages:
   ```shell
   pip install -r requirements.txt
   ```

## Usage [DEV]

1. Open your web browser and navigate to `http://localhost:3000`.
2. Enter the number of threads you want to run.
3. Enter the name of the Twitch channel you want to generate views for.
4. (Optional) Upload your custom proxy list.
5. Click the "Start bot" button to start generating views.

## How to use with macOS

1. Download the application from the [release page](https://github.com/H1B0B0/twitch-Viewerbot/releases).
   ![macOS version](./images/macos_file.png)
2. When you try to open the application, macOS will block it because it is not from an identified developer.
   ![macOS block message](./images/macos_block.png)
3. Open `Settings` and go to `Security & Privacy`. Under the `Security` tab, you will see a message about the blocked application. Click `Open Anyway`.
   ![Enable macOS application](images/enable_macos.png)
4. Confirm that you want to open the application by clicking `Open Anyway` in the dialog that appears.
   ![Execute the app](./images/use_macos.png)
5. The application will now open, and you can start using it. Enjoy 🚀

## 📸 Screenshots

![Screenshot 1](https://github.com/user-attachments/assets/c292df62-3bde-4240-93c3-a83f573af90e)
![Screenshot 2](https://github.com/user-attachments/assets/ff64062e-7b30-4b14-9faf-0f798197222f)
![Screenshot 3](https://github.com/user-attachments/assets/349d778e-310a-4899-9667-8e1da2893fa8)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Warning

⚠ This code is for educational purposes only ⚠
