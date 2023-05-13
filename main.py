import os
import time
import random
import sv_ttk
import datetime
import requests
import tkinter as tk
from tkinter import ttk
from random import shuffle
from threading import Thread
from tkinter import filedialog
from streamlink import Streamlink
from fake_useragent import UserAgent

channel_url = ""
processes = []

nb_of_proxies = 0

# Session creating for request
ua = UserAgent()
session = Streamlink()
session.set_option("http-headers", {
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": ua.random,
    "Client-ID": "ewvlchtxgqq88ru9gmfp1gmyt6h2b93",
    "Referer": "https://www.google.com/"
})

class ViewerBot:
    def __init__(self, nb_of_threads, channel_name, label,proxylist, stop=False):
        self.nb_of_threads = nb_of_threads
        self.channel_name = channel_name
        self.nb_requests = 0
        self.nb_requests_label = label
        self.stop_event = stop
        self.proxylist = proxylist
        self.all_proxies = []

    def get_proxies(self):
        if self.proxylist == None : 
            try:
                response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    lines = [line.strip() for line in lines if line.strip()]
                    return lines
            except:
                pass
        else :
            return self.proxylist

    def get_url(self):
        url = ""
        try:
            streams = session.streams(self.channel_url)
            try:
                url = streams['audio_only'].url
            except:
                url = streams['worst'].url
        except:
            pass
        return url
    

    def open_url(self, proxy_data):
        try:
            headers = {'User-Agent': ua.random}
            current_index = self.all_proxies.index(proxy_data)

            if proxy_data['url'] == "":
                proxy_data['url'] = self.get_url()
            current_url = proxy_data['url']
            try:
                if time.time() - proxy_data['time'] >= random.randint(1, 5):
                    current_proxy = {"http": proxy_data['proxy'], "https": proxy_data['proxy']}
                    with requests.Session() as s:
                        response = s.head(current_url, proxies=current_proxy, headers=headers, timeout=10)
                    self.nb_requests += 1
                    self.nb_requests_label.config(text=f"Number of requests: {self.nb_requests}")
                    proxy_data['time'] = time.time()
                    self.all_proxies[current_index] = proxy_data
            except:
                pass
        except (KeyboardInterrupt):
            pass

    def stop(self):
        self.stop_event = True

    def main(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name

        proxies = self.get_proxies()
        start = datetime.datetime.now()
        while not self.stop_event:
            proxies = self.get_proxies()
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            for p in proxies:
                self.all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                self.threaded = Thread(target=self.open_url, args=(self.all_proxies[random.randrange(len(self.all_proxies))],))
                self.threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                self.threaded.start()

            if elapsed_seconds >= 300:
                start = datetime.datetime.now()
                proxies = self.get_proxies()
                elapsed_seconds = 0  # reset elapsed time

            shuffle(self.all_proxies)

        
class ViewerBotGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ViewerBot")
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        now = datetime.datetime.now()
        hour = now.hour
        if hour >= 19: 
            sv_ttk.set_theme("dark")
        else:
            sv_ttk.set_theme("light")
        self.window.wm_iconbitmap(f"{self.current_dir}/R.ico")
        self.nb_requests_label = ttk.Label(self.window, text="Number of requests: 0")
        self.nb_requests_label.grid(column=0, row=5, columnspan=2, padx=10, pady=10)
        self.nb_requests = 0
        
        # Label for number of threads
        nb_threads_label = ttk.Label(self.window, text="Number of threads:")
        nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
        
        # Entry for number of threads
        self.nb_threads_entry = ttk.Entry(self.window, width=10)
        self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
        
        
        # Label for Twitch channel name
        channel_name_label = ttk.Label(self.window, text="Twitch channel name:")
        channel_name_label.grid(column=0, row=2, padx=10, pady=10)
        
        # Entry for Twitch channel name
        self.channel_name_entry = ttk.Entry(self.window, width=20)
        self.channel_name_entry.grid(column=1, row=2, padx=10, pady=10)
        
        # Button to start the bot
        start_button = ttk.Button(self.window, text="Start bot")
        start_button.grid(column=0, row=3, padx=10, pady=10)
        start_button.config(command=self.start_bot)
        
        # Button to stop the bot
        stop_button = ttk.Button(self.window, text="Stop", state="normal")
        stop_button.grid(column=1, row=3, padx=10, pady=10)
        stop_button.config(command=self.stop_bot)
        
        # Label for status
        status_label = ttk.Label(self.window, text="Status: Stopped")
        status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
        
        # Variables for status and threads
        self.status = "Stopped"
        self.threads = []

        self.show_dialog()
        
        self.window.mainloop()
        
    def start_bot(self):
        if self.status == "Stopped":
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            self.bot = ViewerBot(nb_of_threads, self.channel_name, self.nb_requests_label , self.proxylist)
            self.thread = Thread(target=self.bot.main)
            self.thread.daemon = True
            self.thread.start()
            # Change status and disable/enable buttons
            self.status = "Running"
            self.nb_threads_entry.config(state="disabled")
            self.channel_name_entry.config(state="disabled")
            self.window.update()
            
            # Update status label and buttons
            status_label = ttk.Label(self.window, text="Status: Running")
            status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
            
            # Append thread to list of threads
            self.threads.append(self.thread)
            self.nb_requests = 0
            self.nb_requests_label.config(text=f"Number of requests: {self.nb_requests}")
            
        
    def stop_bot(self):
        if self.status == "Running":
            # Change status and disable/enable buttons
            self.status = "Stopped"
            self.nb_threads_entry.config(state="normal")
            self.channel_name_entry.config(state="normal")
            self.window.update()

            
            # Update status label and buttons
            status_label = ttk.Label(self.window, text="Status: Stopped")
            status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

            self.bot.stop()

    def show_dialog(self):

        self.proxylist = []

        # create new window for the parameters
        self.dialog = tk.Toplevel(self.window)
        self.dialog.title("Parameters")
        self.dialog.iconbitmap(f"{self.current_dir}/R.ico")

        # Button for import proxy list
        open_file_button = ttk.Button(self.dialog, text="import your proxy list (only http)")
        open_file_button.grid(column=1, row=1, padx=10, pady=10)
        open_file_button.config(command=self.on_open_file) 

        scraped_button = ttk.Button(self.dialog, text="scraped automatically proxy")
        scraped_button.grid(column=1, row=2, padx=10, pady=10)
        scraped_button.config(command=self.scraped_proxy) 


        self.dialog.protocol("WM_DELETE_WINDOW", self.scraped_proxy)
        # center the parameters window about the self.window window
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = self.window.winfo_x() + (self.window.winfo_width() - width) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - height) // 2
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.window.wait_window(self.dialog)
        
    def scraped_proxy(self):
        self.proxylist = None

        self.dialog.destroy()
        
        
    # validation button
    def on_open_file(self):

        
        file_path = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt")])


        for path in file_path:
            with open(path, 'r') as f:
                for line in f:
                    self.proxylist.append(line.strip())
        
        # close the parameters window
        self.dialog.destroy()


                      

if __name__ == '__main__':
    ViewerBotGUI = ViewerBotGUI()