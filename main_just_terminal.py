import os
import sys
import time
import random
import requests
import linecache
from random import shuffle
from threading import Thread, Lock
from streamlink import Streamlink
from fake_useragent import UserAgent


channel_url = ""
processes = []

all_proxies = []
nb_of_proxies = 0
MAX_THREADS = 200
lock = Lock()


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
    def __init__(self, nb_of_threads, channel_name):
        self.nb_of_threads = nb_of_threads
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
                    print(f"Sent HEAD request with {current_proxy['http']} | {response.status_code} | {response.request} | {response}")
                    proxy_data['time'] = time.time()
                    all_proxies[current_index] = proxy_data
            except:
                print("Connection Error!")
                if proxy_data in all_proxies:
                    all_proxies.remove(proxy_data)

        except (KeyboardInterrupt, SystemExit):
            sys.exit()


    def stop(self):
        for thread in processes:
            thread.join()
        sys.exit()


    def mainmain(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name

        while True:
            proxies = self.get_proxies()

            for p in proxies:
                all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                threaded = Thread(target=self.open_url, args=(all_proxies[random.randrange(len(all_proxies))],))
                threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                threaded.start()

            shuffle(all_proxies)

if __name__ == '__main__':

    nb_of_threads = int(input("Enter the number of threads: "))
    channel_name = input("Enter the name of the Twitch channel: ")
    bot = ViewerBot(nb_of_threads=nb_of_threads, channel_name=channel_name)
    bot.mainmain()
