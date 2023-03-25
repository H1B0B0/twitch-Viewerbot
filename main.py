import os
import sys
import time
import random
import requests
import linecache
import tkinter as tk
from tkinter import ttk
from random import shuffle
from threading import Thread
from streamlink import Streamlink
from fake_useragent import UserAgent



channel_url = ""
processes = []

all_proxies = []
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
    def __init__(self, nb_of_threads, channel_name, label, stop=False):
        self.nb_of_threads = nb_of_threads
        self.channel_name = channel_name
        self.nb_requests = 0
        self.nb_requests_label = label
        self.stop_event = stop



    def print_exception(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


    def get_proxies(self):
        while True:
            try:
                response = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    lines = [line.strip() for line in lines if line.strip()]
                    return lines
            except:
                pass


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
            global all_proxies
            headers = {'User-Agent': ua.random}
            current_index = all_proxies.index(proxy_data)

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
                    all_proxies[current_index] = proxy_data
            except:
                if proxy_data in all_proxies:
                    all_proxies.remove(proxy_data)

        except (KeyboardInterrupt, SystemExit):
            pass


    def stop(self):
        self.stop_event = True


    def mainmain(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name

        while not self.stop_event:
            proxies = self.get_proxies()

            for p in proxies:
                all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                self.threaded = Thread(target=self.open_url, args=(all_proxies[random.randrange(len(all_proxies))],))
                self.threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                self.threaded.start()

            shuffle(all_proxies)

        
class ViewerBotGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ViewerBot")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        theme_file = os.path.join(current_dir, "azure_theme", "azure.tcl")
        self.window.tk.call("source", theme_file)
        self.window.tk.call("set_theme", "dark")
        self.window.wm_iconbitmap(f"{current_dir}/R.ico")
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
        start_button = ttk.Button(self.window, style="Accent.TButton",text="Start bot")
        start_button.grid(column=0, row=3, padx=10, pady=10)
        start_button.config(command=self.start_bot)
        
        # Button to stop the bot
        stop_button = ttk.Button(self.window, style="Accent.TButton",text="Stop", state="normal")
        stop_button.grid(column=1, row=3, padx=10, pady=10)
        stop_button.config(command=self.stop_bot)
        
        # Label for status
        status_label = ttk.Label(self.window, text="Status: Stopped")
        status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
        
        # Variables for status and threads
        self.status = "Stopped"
        self.threads = []
        
        self.window.mainloop()
        
    def start_bot(self):
        if self.status == "Stopped":
            global max_nb_of_threads
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            self.bot = ViewerBot(nb_of_threads, self.channel_name, self.nb_requests_label , )
            self.thread = Thread(target=self.bot.mainmain)
            self.thread.daemon = True
            self.thread.start()
            max_nb_of_threads = nb_of_threads
            max_nb_of_threads = int(max_nb_of_threads)
            max_nb_of_threads = max_nb_of_threads*10
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
                      

if __name__ == '__main__':
    ViewerBotGUI = ViewerBotGUI()