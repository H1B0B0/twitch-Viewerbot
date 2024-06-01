import os
import sys
import shutil
import requests
import subprocess
import webbrowser
import customtkinter
import platform
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from threading import Thread
from tkinter import messagebox
from dotenv import load_dotenv
from tkinter import filedialog
from viewer_bot import ViewerBot
from urllib.parse import urlparse
from flask import Flask, request, redirect

current_path = Path(__file__).resolve().parent
ICON = current_path/"interface_assets"/"R.ico"
THEME = current_path/"interface_assets"/"purple.json"

SLIDER_MIN = 1000
SLIDER_MAX = 10000

app = Flask(__name__)
current_path = Path(__file__).resolve().parent

# Get the base path (directory of the .exe when compiled, directory of the script otherwise)
base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

# Try to load .env file from base path
if not load_dotenv(os.path.join(base_path, 'twitchbot', '.env')):
    # If loading .env file from base path failed, try to load it from script directory
    if not load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')):
        # If loading .env file from script directory also failed, display an error
        print("Error: .env file not found")

# Get the credentials from .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SERVER_ID = os.getenv('SERVER_ID')
ROLE_ID = os.getenv('ROLE_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Auto-update system
GITHUB_REPO_API = 'https://api.github.com/repos/H1B0B0/twitch-Viewerbot/releases/latest'
response = requests.get(GITHUB_REPO_API)
data = response.json()

# Get the current version of the app
current_version = '2.0.2'

# Check if a new version is available
if data['tag_name'] > current_version:
    # Download the new version
    download_url = data['assets'][1]['browser_download_url']
    response = requests.get(download_url, stream=True)
    with open('new_version.exe', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    # If old_version.exe exists, remove it
    if os.path.exists('old_version.exe'):
        os.remove('old_version.exe')

    # Replace the current executable with the new one
    os.rename(sys.argv[0], 'old_version.exe')
    os.rename('new_version.exe', sys.argv[0])

    # Show a message to the user
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Update", "The application has been updated. It will now restart.")
    root.destroy()  # Destroy the main window

    # Relaunch the application
    subprocess.Popen([sys.argv[0]])

    # Close the current application
    sys.exit()

class ViewerBotGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Viewerbot")
        customtkinter.set_appearance_mode("System")
        if platform.system() == "Windows":
            self.wm_iconbitmap(ICON)
        customtkinter.set_default_color_theme(THEME)
        self.nb_requests = 0
        self.slider = 0
        self.nb_of_proxies = 0
        self.nb_of_proxies_alive = 0
        self.message_gived = False
        self.logged_in = False
        self.browser = None
        self.nb_threads_entry = None
        self.channel_name_entry = None
        self.status_label = None
        self.total_label = None
        self.alive_label = None
        self.name_label = None
        self.segemented_button_var = None
        self.timeout = None
        self.nb_requests_label = None
        self.proxies_label = None
        self.threads = []
        self.segemented_button = None
        self.active_threads_label = None
        
        @app.route('/')
        def index():
            url = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify+role_connections.write+guilds+guilds.members.read'
            return redirect(url, code=302)

        @app.route('/callback')
        def callback():
            code = request.args.get('code')
            data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'scope': 'identify guilds'
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
            response.raise_for_status()
            token = response.json()['access_token']
            print(f"Access token: {token}")
            headers = {
                'Authorization': f'Bearer {token}'
            }
            response = requests.get('https://discord.com/api/users/@me', headers=headers)
            response.raise_for_status()
            user_id = response.json()['id']  # Get the user's ID
            response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
            response.raise_for_status()
            guilds = response.json()
            guild_ids = [guild['id'] for guild in guilds]
            if SERVER_ID in guild_ids:
                headers = {
                        'Authorization': f'Bot {BOT_TOKEN}'  # Use Bot token here
                    }
                response = requests.get(f'https://discord.com/api/guilds/{SERVER_ID}/members/{user_id}', headers=headers)  # Use the user's ID here
                response.raise_for_status()
                roles = response.json()['roles']
                if ROLE_ID in roles:
                    self.label.destroy()
                    self.login_button.destroy()
                    font = ("Helvetica", 15)
                    # Label for number of threads
                    nb_threads_label = customtkinter.CTkLabel(self, text="Number of threads:", font=font)
                    nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
                    
                    # Entry for number of threads
                    self.nb_threads_entry = customtkinter.CTkEntry(self)
                    self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
                    
                    # Label for Twitch channel name
                    channel_name_label = customtkinter.CTkLabel(self, text="Twitch channel name or url:", font=font)
                    channel_name_label.grid(column=0, row=1, padx=10, pady=10)
                    
                    # Entry for Twitch channel name
                    self.channel_name_entry = customtkinter.CTkEntry(self)
                    self.channel_name_entry.grid(column=1, row=1, padx=10, pady=10)

                    # Label for proxy type
                    proxy_type = customtkinter.CTkLabel(self, text="Proxy type", font=font)
                    proxy_type.grid(column=0, row=2, columnspan=2, padx=10, pady=0)

                    # select proxy type
                    self.segemented_button_var = customtkinter.StringVar(value="http")
                    self.segemented_button = customtkinter.CTkSegmentedButton(self, values=["http", "socks4", "socks5", "all"], variable=self.segemented_button_var, font=font)
                    self.segemented_button.grid(column=0, row=3, columnspan=2, padx=10, pady=5)

                    self.slider = customtkinter.CTkSlider(self, from_=SLIDER_MIN, to=SLIDER_MAX, command=self.slider_event)
                    self.slider.set(SLIDER_MAX)
                    self.slider.grid(column=0, row=5, columnspan=2, padx=10, pady=0)

                    # Label for timeout
                    self.timeout = customtkinter.CTkLabel(self, text=f"timeout: {int(self.slider.get())}", font=font)
                    self.timeout.grid(column=0, row=4, columnspan=2, padx=10, pady=0)
                    
                    # Button to start the bot
                    start_button = customtkinter.CTkButton(self, text="Start bot", font=font)
                    start_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10, sticky='ew')
                    start_button.configure(command=lambda: self.start_bot(start_button))
                    
                    self.nb_requests_label = customtkinter.CTkLabel(self, text="Number of requests: 0", font=font)
                    self.nb_requests_label.grid(column=0, row=7, columnspan=2, padx=10, pady=2)

                    self.active_threads_label = customtkinter.CTkLabel(self, text="Active threads: 0", font=font)
                    self.active_threads_label.grid(column=0, row=8, columnspan=2, padx=10, pady=2)
                    # Label for status
                    self.status_label = customtkinter.CTkLabel(self, text="Status: Stopped", font=font)
                    self.status_label.grid(column=0, row=9, columnspan=2, padx=10, pady=2)

                    # Label for the proxy states
                    self.proxies_label = customtkinter.CTkLabel(self, text="proxy states", font=font)
                    self.proxies_label.grid(column=0, columnspan=2, row=10, padx=10, pady=2)

                    # Label for the proxy states
                    self.total_label = customtkinter.CTkLabel(self, text=f"Total:{self.nb_of_proxies}", font=font)
                    self.total_label.grid(column=0, row=11, padx=10, pady=2, sticky="w")

                    # Label for the proxy states
                    self.alive_label = customtkinter.CTkLabel(self, text=f"Alive:{self.nb_of_proxies_alive}", font=font)
                    self.alive_label.grid(column=1, row=11, padx=10, pady=2, sticky="e")

                    # Label
                    self.name_label = customtkinter.CTkLabel(self, text="Coded by HIBOBO", font=font)
                    self.name_label.grid(column=0, columnspan=2, row=12, padx=10, pady=2)
                    
                    # Variables for status and threads
                    self.status = "Stopped"
                    self.show_dialog()
                    return """
                        <html>
                            <head>
                                <style>
                                    body, html {
                                        margin: 0;
                                        padding: 0;
                                        height: 100%;
                                        width: 100%;
                                        overflow: hidden;  # Prevents scrollbars from appearing
                                    }
                                    #canvas3d {
                                        width: 100%;
                                        height: 100%;
                                    }
                                </style>
                            </head>
                            <body>
                                <canvas id="canvas3d"></canvas>
                                <script type="module">
                                    import { Application } from 'https://cdn.skypack.dev/@splinetool/runtime';

                                    const canvas = document.getElementById('canvas3d');
                                    const app = new Application(canvas);
                                    app.load('https://prod.spline.design/5-w0xw-yuEOQ4-0Q/scene.splinecode');
                                </script>
                            </body>
                        </html>
                        """
                else:
                    dialog = customtkinter.CTk()
                    dialog.title("Subscribe to the bot")
                    label = customtkinter.CTkLabel(dialog, text="You are in the server, but you are not subscribed.\n Please subscribe to access the bot.\n If you are already subscribed, please contact the owner.\n")
                    label.pack(pady=10, padx=10)
                    link = customtkinter.CTkButton(dialog, text="Subscribe", command=lambda: open_link(dialog))
                    link.pack(pady=10, padx=10)
                    dialog.mainloop()
                    return """
                        <html>
                            <head>
                                <style>
                                    body {
                                        font-family: Arial, sans-serif;
                                        background-color: #f0f0f0;
                                        color: #333;
                                        padding: 30px;
                                    }
                                    .message {
                                        font-size: 24px;
                                        font-weight: bold;
                                        color: #FF0000;  # Red text
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="message">You are not subscribed</div>
                            </body>
                        </html>
                        """
            else:
                dialog = customtkinter.CTk()
                dialog.title("Join the server")
                label = customtkinter.CTkLabel(dialog, text="You are not in the server.\n Please join the server to access the bot.\n If you are already in the server, please contact the owner.\n")
                label.pack(pady=10, padx=10)
                link = customtkinter.CTkButton(dialog, text="Join", command=lambda: open_link_discord(dialog))
                link.pack(pady=10, padx=10)
                dialog.mainloop()
                return """
                    <html>
                        <head>
                            <style>
                                body {
                                    font-family: Arial, sans-serif;
                                    background-color: #f0f0f0;
                                    color: #333;
                                    padding: 30px;
                                }
                                .message {
                                    font-size: 24px;
                                    font-weight: bold;
                                    color: #FF0000;  # Red text
                                }   
                            </style>
                        </head>
                        <body>
                            <div class="message">You are not in the server</div>
                        </body>
                    </html>
                    """

        def run_flask():
            app.run(debug=True, use_reloader=False)

        def open_browser():
            self.browser = webbrowser.open('http://localhost:5000')

        def open_link(dialog):
            self.browser = webbrowser.open('https://www.patreon.com/hibo/membership')
            dialog.destroy()

        def open_link_discord(dialog):
            self.browser = webbrowser.open('https://discord.gg/EDQ8ayhjDp')
            dialog.destroy()

        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        font = ("Helvetica", 15)

        self.label = customtkinter.CTkLabel(self, text="Please login to access the bot", font=font)
        self.label.pack(pady=10, padx=10)
        self.login_button = customtkinter.CTkButton(self, text="Login", command=open_browser, font=font)
        self.login_button.pack(pady=10, padx=10)
                

    def slider_event(self, value):
        self.timeout.configure(text=f"timeout: {int(self.slider.get())}")
        
    def start_bot(self, button=object()):
        if self.status == "Stopped":
            button.configure(command=lambda: self.stop_bot(button), text="Stop bot")
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            channel_input = self.channel_name  # This should be the input from the user
            # Parse the input as a URL
            parsed_url = urlparse(channel_input)

            # If the input is a URL, extract the username from the path
            if parsed_url.netloc == 'www.twitch.tv':
                self.channel_name = parsed_url.path.lstrip('/')
            else:
                # If the input is not a URL, assume it's a username
                self.channel_name = channel_input
            self.bot = ViewerBot(nb_of_threads, self.channel_name, self.proxylist, self.proxy_imported, self.slider.get(), type_of_proxy=self.segemented_button_var)
            self.thread = Thread(target=self.bot.main)
            self.after(200, self.configure_label)
            self.after(200, self.proxies_number)
            self.thread.daemon = True
            self.thread.start()
            # Change status and disable/enable buttons
            self.status = "Running"
            self.nb_threads_entry.configure(state="disabled")
            self.channel_name_entry.configure(state="disabled")
            self.segemented_button.configure(state="disabled")
            self.slider.configure(state="disabled")
            # Update status label and buttons
            self.status_label.configure(text=f"Status: {self.status}")
            # Append thread to list of threads
            self.threads.append(self.thread)
        
    def stop_bot(self, button=object()):
        if self.status == "Running":
            button.configure(command=lambda: self.start_bot(button), text="Start bot")
            # Change status and disable/enable buttons
            self.status = "Stopped"
            self.nb_threads_entry.configure(state="normal")
            self.channel_name_entry.configure(state="normal")
            self.segemented_button.configure(state="normal")
            self.slider.configure(state="normal")
            # Update status label and buttons
            self.status_label.configure(text=f"Status: {self.status}")
            self.bot.stop()

    def configure_label(self):
        self.nb_requests_label.configure(text=f"Number of requests: {self.bot.nb_requests}")
        self.active_threads_label.configure(text=f"Active threads: {self.bot.active_threads}")
        try:
            alive_text = f"Alive: {len(self.bot.proxies)}"
            self.alive_label.configure(text=alive_text)
            if len(self.bot.proxies) < 50 and self.bot.proxyrefreshed==True:
                self.bot.proxyrefreshed=False
            if len(self.bot.proxies) < 50 and self.bot.proxy_imported==False and self.bot.proxyrefreshed==False:
                self.bot.get_proxies()
                self.bot.proxyrefreshed=True
                self.proxies_number()
            elif not self.message_gived and len(self.bot.proxies) < 100 and self.bot.proxy_imported==True:
                messagebox.showwarning(title="Warning", 
                                       message="Your proxies are expired or of poor quality,\n you need to import a better list or switch to automatic mode")
                self.message_gived=True
        except:
            pass
        self.update_idletasks()
        self.after(200, self.configure_label)
        
    def proxies_number(self):
        try:
            total_text = f"Total: {len(self.bot.proxies)}"
            self.total_label.configure(text=total_text)  # Use the 'text' attribute to update label text
            self.update_idletasks()
        except:
            self.after(200, self.proxies_number)

    def show_dialog(self):
        font = ("Helvetica", 15)
        self.proxylist = []
        # create new window for the parameters
        self.dialog = customtkinter.CTkToplevel(self)
        self.dialog.title("Parameters")
        # Button for import proxy list
        open_file_button = customtkinter.CTkButton(self.dialog, text="import your proxy list", font=font)
        open_file_button.grid(column=1, row=1, padx=10, pady=10)
        open_file_button.configure(command=self.on_open_file) 

        scraped_button = customtkinter.CTkButton(self.dialog, text="scraped automatically proxy", font=font)
        scraped_button.grid(column=1, row=2, padx=10, pady=10)
        scraped_button.configure(command=self.scraped_proxy) 

        self.dialog.protocol("WM_DELETE_WINDOW", self.scraped_proxy)
        # center the parameters window about the object
        self.dialog.update_idletasks()
        self.wait_window(self.dialog)
        
    def scraped_proxy(self):
        self.proxylist = None
        self.proxy_imported = False
        self.dialog.destroy()

    # validation button
    def on_open_file(self):
        file_path = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])
        for path in file_path:
            with open(path, 'r') as f:
                for line in f:
                    self.proxylist.append(line.strip())
        self.proxy_imported = True
        if self.proxylist == []:
            self.proxylist = None
            self.proxy_imported = False
            messagebox.showwarning(title="WARNING", message="No proxy imported, the proxy list is empty. Proxies gonna be scraped.")
        # close the parameters window
        self.dialog.destroy()                 

if __name__ == "__main__":
    app = ViewerBotGUI()
    app.mainloop()