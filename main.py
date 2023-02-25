import requests
from streamlink import Streamlink
import sys
import time
import random
from random import shuffle
from fake_useragent import UserAgent
import linecache
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from tkinter import ttk
import requests

channel_url = ""
proxies_file = "good_proxy.txt"
processes = []

all_proxies = []
nb_of_proxies = 0

# Session creating for request
ua = UserAgent()
session = Streamlink()
session.set_option("http-headers", {'User-Agent': ua.random, "Client-ID": "ewvlchtxgqq88ru9gmfp1gmyt6h2b93"})

class ViewerBot:
    def __init__(self, nb_of_threads, proxies_file, channel_name):
        self.nb_of_threads = nb_of_threads
        self.proxies_file = proxies_file
        self.channel_name = channel_name


    def print_exception(self):
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


    def get_proxies(self):
        # Reading the list of proxies
        global nb_of_proxies
        try:
            with open(self.proxies_file) as f:
                lines = [line.rstrip("\n") for line in f]
        except IOError as e:
            print("An error has occurred while trying to read the list of proxies: %s" % e.strerror)
            sys.exit(1)

        nb_of_proxies = len(lines)
        return lines



    def get_url(self):
        url = ""
        try:
            streams = session.streams(self.channel_url)
            try:
                url = streams['audio_only'].url
                print(f"URL : {url[:30]}...\n")
            except:
                url = streams['worst'].url
                print(f"URL : {url[:30]}...\n")

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
                    print(f"Sent HEAD request with {current_proxy['http']} | {response.status_code} | {response.request} | {response}")
                    proxy_data['time'] = time.time()
                    all_proxies[current_index] = proxy_data
            except:
                print("Connection Error!")

        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def stop(self):
        sys.exit()

    def mainmain(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name
        proxies = self.get_proxies()

        for p in proxies:
            all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

        shuffle(all_proxies)
        list_of_all_proxies = all_proxies
        current_proxy_index = 0

        while True:
            try:
                for i in range(0, max_nb_of_threads):
                    threaded = Thread(target=self.open_url, args=(all_proxies[random.randrange(len(all_proxies))]))
                    threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                    threaded.start()
            except:
                self.print_exception()
            shuffle(all_proxies)

        
class ViewerBotGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ViewerBot")

        self.window.tk.call("source", "azure.tcl")
        self.window.tk.call("set_theme", "dark")
        self.window.wm_iconbitmap('R.ico')
        
        # Label for number of threads
        nb_threads_label = ttk.Label(self.window, text="Number of threads:")
        nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
        
        # Entry for number of threads
        self.nb_threads_entry = ttk.Entry(self.window, width=10)
        self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
        
        # Label for proxy file
        proxy_file_label = ttk.Label(self.window, text="Proxy file:")
        proxy_file_label.grid(column=0, row=1, padx=10, pady=10)
        
        # Button to select proxy file
        self.proxy_file_button = ttk.Button(self.window, style="Accent.TButton",text="Select file", command=self.select_proxy_file)
        self.proxy_file_button.grid(column=1, row=1, padx=10, pady=10)
        
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
        
    def select_proxy_file(self):
        self.proxy_file = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=[("Text Files", "*.txt")])
        
    def start_bot(self):
        if self.status == "Stopped":
            global max_nb_of_threads
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            self.bot = ViewerBot(nb_of_threads, self.proxy_file, self.channel_name)
            ViewerBot(nb_of_threads, self.proxy_file, self.channel_name)
            ViewerBot(nb_of_threads, self.proxy_file, self.channel_name)
            self.thread = Thread(target=self.bot.mainmain)
            self.thread.daemon = True
            self.thread.start()

            max_nb_of_threads = nb_of_threads
            max_nb_of_threads = int(max_nb_of_threads)
            max_nb_of_threads = max_nb_of_threads*10
            # Change status and disable/enable buttons
            self.status = "Running"
            self.proxy_file_button.config(state="disabled")
            self.nb_threads_entry.config(state="disabled")
            self.channel_name_entry.config(state="disabled")
            self.window.update()
            
            # Update status label and buttons
            status_label = ttk.Label(self.window, text="Status: Running")
            status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
            
            start_button = self.window.nametowidget("start_button")
            start_button.config(state="disabled")
            
            stop_button = self.window.nametowidget("stop_button")
            stop_button.config(state="normal")
            
            # Append thread to list of threads
            self.threads.append(self.thread)
            
        
    def stop_bot(self):
        if self.status == "Running":
            # Change status and disable/enable buttons
            self.status = "Stopped"
            self.proxy_file_button.config(state="normal")
            self.nb_threads_entry.config(state="normal")
            self.channel_name_entry.config(state="normal")
            self.window.update()

            
            # Update status label and buttons
            status_label = ttk.Label(self.window, text="Status: Stopped")
            status_label.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
            
            
            # Stop all threads
            for thread in self.threads:
                thread.stop()

            self.bot.stop()
            

            

if __name__ == '__main__':
    ViewerBotGUI = ViewerBotGUI()