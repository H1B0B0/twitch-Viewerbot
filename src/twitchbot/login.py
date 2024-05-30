import os
import platform
import threading
import webbrowser
import customtkinter
import requests
from flask import Flask, request, redirect
from pathlib import Path
from main import ViewerBotGUI
from dotenv import load_dotenv

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

ICON = current_path/"interface_assets"/"R.ico"
THEME = current_path/"interface_assets"/"purple.json"

@app.route('/')
def index():
    url = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify+role_connections.write+guilds+guilds.join+guilds.members.read'
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
    if response.status_code == 401:
        dialog = customtkinter.CTk()
        label = customtkinter.CTkLabel(root, text="You are not in the server.\n Please join the server to access the bot.\n If you are already in the server, please contact the owner.\n")
        label.pack()
        link = customtkinter.CTkButton(root, text="Join", command=open_link_discord)
        link.pack()
        dialog.mainloop()
    response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
    response.raise_for_status()
    guilds = response.json()
    for guild in guilds:
        if guild['id'] == SERVER_ID:
            headers = {
                'Authorization': f'Bot {BOT_TOKEN}'  # Use Bot token here
            }
            response = requests.get(f'https://discord.com/api/guilds/{SERVER_ID}/members/{user_id}', headers=headers)  # Use the user's ID here
            response.raise_for_status()
            roles = response.json()['roles']
            print(roles)
            if ROLE_ID in roles:
                open_bot()
            else:
                dialog = customtkinter.CTk()
                label = customtkinter.CTkLabel(root, text="You are in the server, but you are not subscribed.\n Please subscribe to access the bot.\n If you are already subscribed, please contact the owner.\n")
                label.pack()
                link = customtkinter.CTkButton(root, text="Subscribe", command=open_link)
                link.pack()
                dialog.mainloop()
    return 'Done'

def open_bot():
    root.destroy()
    flask_thread.join()
    app = ViewerBotGUI()
    app.mainloop()

def run_flask():
    app.run(debug=True, use_reloader=False)

def open_browser():
    webbrowser.open('http://localhost:5000')

def open_link():
    webbrowser.open('https://www.patreon.com/hibo/membership')

def open_link_discord():
    webbrowser.open('https://discord.gg/EDQ8ayhjDp')

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    root = customtkinter.CTk()
    if platform.system() == "Windows":
            root.wm_iconbitmap(ICON)
    customtkinter.set_default_color_theme(THEME)
    root.title("Login with Discord")
    root.geometry("300x100")
    frame = customtkinter.CTkFrame(root)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    label = customtkinter.CTkLabel(frame, text="Click the button below to login with Discord")
    label.place(relx=0.5, rely=0.3, anchor='center')
    button = customtkinter.CTkButton(frame, text="Login with Discord", command=open_browser)
    button.place(relx=0.5, rely=0.7, anchor='center')
    button.pack()
    root.mainloop()