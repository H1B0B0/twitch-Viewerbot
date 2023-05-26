import os
import time
import random
import customtkinter
import tkinter as tk
import datetime
import requests
from random import shuffle
from threading import Thread
from tkinter import filedialog
from streamlink import Streamlink
from fake_useragent import UserAgent


class ViewerBot:
    def __init__(self, nb_of_threads, channel_name, label,proxylist, type_of_proxy , proxy_imported, timeout, stop=False):
        self.nb_of_threads = nb_of_threads
        self.channel_name = channel_name
        self.nb_requests = 0
        self.nb_requests_label = label
        self.stop_event = stop
        self.proxylist = proxylist
        self.all_proxies = []
        self.proxyrefreshed = True
        self.type_of_proxy = type_of_proxy.get()
        self.proxy_imported = proxy_imported
        self.timeout = timeout

    def create_session(self):
        # Session creating for request
        self.ua = UserAgent()
        self.session = Streamlink()
        self.session.set_option("http-headers", {
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua.random,
            "Client-ID": "ewvlchtxgqq88ru9gmfp1gmyt6h2b93",
            "Referer": "https://www.google.com/"
        })
        return self.session

    def get_proxies(self):
        if self.proxylist == None or self.proxyrefreshed == False: 
            try:
                response = requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol={self.type_of_proxy}&timeout={self.timeout}&country=all&ssl=all&anonymity=all")
                if response.status_code == 200:
                    lines = response.text.split("\n")
                    lines = [line.strip() for line in lines if line.strip()]
                    return lines
                self.proxyrefreshed = True
            except:
                pass
        else :
            return self.proxylist

    def get_url(self):
        try:
            streams = self.session.streams(self.channel_url)
            try:
                url = streams['audio_only'].url
            except:
                url = streams['worst'].url
        except:
            pass
        try: 
            return url
        except:
            exit()
    

    def open_url(self, proxy_data):
            headers = {'User-Agent': self.ua.random}
            current_index = self.all_proxies.index(proxy_data)

            if proxy_data['url'] == "":
                proxy_data['url'] = self.get_url()
            current_url = proxy_data['url']
            username = proxy_data.get('username')
            password = proxy_data.get('password')
            if username and password:
                current_proxy = {"http": f"{username}:{password}@{proxy_data['proxy']}", "https": f"{username}:{password}@{proxy_data['proxy']}"}
            else:
                current_proxy = {"http": proxy_data['proxy'], "https": proxy_data['proxy']}

            try:
                if time.time() - proxy_data['time'] >= random.randint(1, 5):
                    current_proxy = {"http": proxy_data['proxy'], "https": proxy_data['proxy']}
                    with requests.Session() as s:
                        response = s.head(current_url, proxies=current_proxy, headers=headers, timeout=(self.timeout/1000))
                    self.nb_requests += 1
                    proxy_data['time'] = time.time()
                    self.all_proxies[current_index] = proxy_data
            except:
                pass

    def stop(self):
        self.stop_event = True

    def main(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name

        proxies = self.get_proxies()
        start = datetime.datetime.now()
        self.create_session()
        while not self.stop_event:
            proxies = self.get_proxies()
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()
            
            for p in proxies:
                self.all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                self.threaded = Thread(target=self.open_url, args=(self.all_proxies[random.randrange(len(self.all_proxies))],))
                self.threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                self.threaded.start()

            if elapsed_seconds >= 300 and self.proxy_imported == False:
                start = datetime.datetime.now()
                proxies = self.get_proxies()
                elapsed_seconds = 0  # reset elapsed time
                self.proxyrefreshed = False

            self.nb_requests_label.configure(text=f"Number of requests: {self.nb_requests}")


        
class ViewerBotGUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")
        self.title("Viewerbot")
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.wm_iconbitmap(f"{self.current_dir}/R.ico")
        self.nb_requests = 0
        self.slider = 0
        
        # Label for number of threads
        nb_threads_label = customtkinter.CTkLabel(self, text="Number of threads:")
        nb_threads_label.grid(column=0, row=0, padx=10, pady=10)
        
        # Entry for number of threads
        self.nb_threads_entry = customtkinter.CTkEntry(self)
        self.nb_threads_entry.grid(column=1, row=0, padx=10, pady=10)
        
        # Label for Twitch channel name
        channel_name_label = customtkinter.CTkLabel(self, text="Twitch channel name:")
        channel_name_label.grid(column=0, row=2, padx=10, pady=10)
        
        # Entry for Twitch channel name
        self.channel_name_entry = customtkinter.CTkEntry(self)
        self.channel_name_entry.grid(column=1, row=2, padx=10, pady=10)

        # Label for proxy type
        proxy_type = customtkinter.CTkLabel(self, text="Proxy type")
        proxy_type.grid(column=0, row=3, columnspan=2, padx=10, pady=0)

        # select proxy type
        self.segemented_button_var = customtkinter.StringVar(value="http")
        self.segemented_button = customtkinter.CTkSegmentedButton(self, values=["http", "socks4", "socks5", "all"], variable=self.segemented_button_var)
        self.segemented_button.grid(column=0, row=4, columnspan=2, padx=10, pady=5)

        self.slider = customtkinter.CTkSlider(self, from_=1000, to=10000, command=self.slider_event)
        self.slider.grid(column=0, row=6, columnspan=2, padx=10, pady=0)

        # Label for timeout
        self.timeout = customtkinter.CTkLabel(self, text=f"timeout: {int(self.slider.get())}")
        self.timeout.grid(column=0, row=5, columnspan=2, padx=10, pady=0)
        
        # Button to start the bot
        start_button = customtkinter.CTkButton(self, text="Start bot")
        start_button.grid(column=0, row=7, padx=10, pady=10)
        start_button.configure(command=self.start_bot)
        
        # Button to stop the bot
        stop_button = customtkinter.CTkButton(self, text="Stop", state="normal")
        stop_button.grid(column=1, row=7, padx=10, pady=10)
        stop_button.configure(command=self.stop_bot)
        
        self.nb_requests_label = customtkinter.CTkLabel(self, text="Number of requests: 0")
        self.nb_requests_label.grid(column=0, row=8, columnspan=2, padx=10, pady=2)
        # Label for status
        status_label = customtkinter.CTkLabel(self, text="Status: Stopped")
        status_label.grid(column=0, row=9, columnspan=2, padx=10, pady=2)
        
        # Variables for status and threads
        self.status = "Stopped"
        self.threads = []

        self.show_dialog()

    def slider_event(self, value):
        self.timeout.configure(text=f"timeout: {int(self.slider.get())}")
        
    def start_bot(self):
        if self.status == "Stopped":
            nb_of_threads = self.nb_threads_entry.get()
            self.channel_name = self.channel_name_entry.get()
            self.bot = ViewerBot(nb_of_threads, self.channel_name, self.nb_requests_label , self.proxylist, self.segemented_button_var, self.proxy_imported, self.slider.get())
            self.thread = Thread(target=self.bot.main)
            self.thread.daemon = True
            self.thread.start()
            # Change status and disable/enable buttons
            self.status = "Running"
            self.nb_threads_entry.configure(state="disabled")
            self.channel_name_entry.configure(state="disabled")
            self.segemented_button.configure(state="disabled")
            self.slider.configure(state="disabled")
            
            # Update status label and buttons
            status_label = customtkinter.CTkLabel(self, text="Status: Running")
            status_label.grid(column=0, row=9, columnspan=2, padx=10, pady=10)
            
            # Append thread to list of threads
            self.threads.append(self.thread)
            self.nb_requests = 0
            self.nb_requests_label.configure(text=f"Number of requests: {self.nb_requests}")
            
        
    def stop_bot(self):
        if self.status == "Running":
            # Change status and disable/enable buttons
            self.status = "Stopped"
            self.nb_threads_entry.configure(state="normal")
            self.channel_name_entry.configure(state="normal")
            self.segemented_button.configure(state="normal")
            self.slider.configure(state="normal")

            
            # Update status label and buttons
            status_label = customtkinter.CTkLabel(self, text="Status: Stopped")
            status_label.grid(column=0, row=9, columnspan=2, padx=10, pady=10)

            self.bot.stop()

    def show_dialog(self):

        self.proxylist = []

        # create new window for the parameters
        self.dialog = customtkinter.CTkToplevel(self)
        self.dialog.title("Parameters")
        self.dialog.iconbitmap(f"{self.current_dir}/R.ico")

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
        
        # close the parameters window
        self.dialog.destroy()


                      

if __name__ == '__main__':
    app = ViewerBotGUI()
    app.mainloop()