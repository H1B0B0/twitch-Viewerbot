import os
import requests
import webbrowser
import customtkinter
import platform
from pathlib import Path
from threading import Thread
from tkinter import messagebox
from dotenv import load_dotenv
from tkinter import filedialog
from viewer_bot import ViewerBot
from flask import Flask, request, redirect

current_path = Path(__file__).resolve().parent
ICON = current_path/"interface_assets"/"R.ico"
THEME = current_path/"interface_assets"/"purple.json"

SLIDER_MIN = 1000
SLIDER_MAX = 10000

app = Flask(__name__)
current_path = Path(__file__).resolve().parent

# Load .env file
load_dotenv()

# Get the credentials from .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SERVER_ID = os.getenv('SERVER_ID')
ROLE_ID = os.getenv('ROLE_ID')
BOT_TOKEN = os.getenv('BOT_TOKEN')

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
                    # Label for number of threads
                    nb_threads_label = customtkinter.CTkLabel(self, text="Number of threads:")
                    nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
                    
                    # Entry for number of threads
                    self.nb_threads_entry = customtkinter.CTkEntry(self)
                    self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
                    
                    # Label for Twitch channel name
                    channel_name_label = customtkinter.CTkLabel(self, text="Twitch channel name:")
                    channel_name_label.grid(column=0, row=1, padx=10, pady=10)
                    
                    # Entry for Twitch channel name
                    self.channel_name_entry = customtkinter.CTkEntry(self)
                    self.channel_name_entry.grid(column=1, row=1, padx=10, pady=10)

                    # Label for proxy type
                    proxy_type = customtkinter.CTkLabel(self, text="Proxy type")
                    proxy_type.grid(column=0, row=2, columnspan=2, padx=10, pady=0)

                    # select proxy type
                    self.segemented_button_var = customtkinter.StringVar(value="http")
                    self.segemented_button = customtkinter.CTkSegmentedButton(self, values=["http", "socks4", "socks5", "all"], variable=self.segemented_button_var)
                    self.segemented_button.grid(column=0, row=3, columnspan=2, padx=10, pady=5)

                    self.slider = customtkinter.CTkSlider(self, from_=SLIDER_MIN, to=SLIDER_MAX, command=self.slider_event)
                    self.slider.set(SLIDER_MAX)
                    self.slider.grid(column=0, row=5, columnspan=2, padx=10, pady=0)

                    # Label for timeout
                    self.timeout = customtkinter.CTkLabel(self, text=f"timeout: {int(self.slider.get())}")
                    self.timeout.grid(column=0, row=4, columnspan=2, padx=10, pady=0)
                    
                    # Button to start the bot
                    start_button = customtkinter.CTkButton(self, text="Start bot")
                    start_button.grid(column=0, row=6, padx=10, pady=10)
                    start_button.configure(command=self.start_bot)
                    
                    # Button to stop the bot
                    stop_button = customtkinter.CTkButton(self, text="Stop", state="normal")
                    stop_button.grid(column=1, row=6, padx=10, pady=10)
                    stop_button.configure(command=self.stop_bot)
                    
                    self.nb_requests_label = customtkinter.CTkLabel(self, text="Number of requests: 0")
                    self.nb_requests_label.grid(column=0, row=7, columnspan=2, padx=10, pady=2)
                    # Label for status
                    self.status_label = customtkinter.CTkLabel(self, text="Status: Stopped")
                    self.status_label.grid(column=0, row=8, columnspan=2, padx=10, pady=2)

                    # Label for the proxy states
                    self.proxies_label = customtkinter.CTkLabel(self, text="proxy states")
                    self.proxies_label.grid(column=0, columnspan=2, row=9, padx=10, pady=2)

                    # Label for the proxy states
                    self.total_label = customtkinter.CTkLabel(self, text=f"Total:{self.nb_of_proxies}")
                    self.total_label.grid(column=0, row=10, padx=10, pady=2, sticky="w")

                    # Label for the proxy states
                    self.alive_label = customtkinter.CTkLabel(self, text=f"Alive:{self.nb_of_proxies_alive}")
                    self.alive_label.grid(column=1, row=10, padx=10, pady=2, sticky="e")

                    # Label
                    self.name_label = customtkinter.CTkLabel(self, text="Coded by HIBOBO")
                    self.name_label.grid(column=0, columnspan=2, row=11, padx=10, pady=2)
                    
                    # Variables for status and threads
                    self.status = "Stopped"
                    self.show_dialog()
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
                                        color: #008000;  # Green text
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="message">You are logged in</div>
                            </body>
                        </html>
                        """
                else:
                    dialog = customtkinter.CTkInputDialog()
                    dialog.title("Subscribe to the bot")
                    label = customtkinter.CTkLabel(dialog, text="You are in the server, but you are not subscribed.\n Please subscribe to access the bot.\n If you are already subscribed, please contact the owner.\n")
                    label.pack(pady=10, padx=10)
                    link = customtkinter.CTkButton(dialog, text="Subscribe", command=open_link)
                    link.pack(pady=10, padx=10)
                    dialog.mainloop()
            else:
                dialog = customtkinter.CTkInputDialog()
                dialog.title("Join the server")
                label = customtkinter.CTkLabel(dialog, text="You are not in the server.\n Please join the server to access the bot.\n If you are already in the server, please contact the owner.\n")
                label.pack(pady=10, padx=10)
                link = customtkinter.CTkButton(dialog, text="Join", command=open_link_discord)
                link.pack(pady=10, padx=10)
                dialog.mainloop()

        def run_flask():
            app.run(debug=True, use_reloader=False)

        def open_browser():
            self.browser = webbrowser.open('http://localhost:5000')

        def open_link():
            self.browser = webbrowser.open('https://www.patreon.com/hibo/membership')

        def open_link_discord():
            self.browser = webbrowser.open('https://discord.gg/EDQ8ayhjDp')

        if __name__ == '__main__':
            flask_thread = Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()

            self.label = customtkinter.CTkLabel(self, text="Please login to access the bot")
            self.label.pack(pady=10, padx=10)
            self.login_button = customtkinter.CTkButton(self, text="Login", command=open_browser)
            self.login_button.pack(pady=10, padx=10)
                

    def slider_event(self, value):
        self.timeout.configure(text=f"timeout: {int(self.slider.get())}")
        
    def start_bot(self):
        if self.status == "Stopped":
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
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
        
    def stop_bot(self):
        if self.status == "Running":
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
        self.proxylist = []
        # create new window for the parameters
        self.dialog = customtkinter.CTkToplevel(self)
        self.dialog.title("Parameters")
        # Button for import proxy list
        open_file_button = customtkinter.CTkButton(self.dialog, text="import your proxy list")
        open_file_button.grid(column=1, row=1, padx=10, pady=10)
        open_file_button.configure(command=self.on_open_file) 

        scraped_button = customtkinter.CTkButton(self.dialog, text="scraped automatically proxy")
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