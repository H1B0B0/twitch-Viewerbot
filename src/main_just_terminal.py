import sys
import time
import random
import requests
import datetime
from random import shuffle
from threading import Thread, Lock
from streamlink import Streamlink
from fake_useragent import UserAgent


channel_url = ""
processes = []

all_proxies = []
nb_of_proxies = 0
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
        self.request_count = 0  # initialize the counter variable

    def get_proxies(self):
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
                        s.head(current_url, proxies=current_proxy, headers=headers, timeout=10)
                        self.request_count += 1  # increment the counter variable
                    proxy_data['time'] = time.time()
                    all_proxies[current_index] = proxy_data
            except:
                pass

        except (KeyboardInterrupt):
            sys.exit()


    def stop(self):
        for thread in processes:
            thread.join()
        sys.exit()


    def main(self):
        self.channel_url = "https://www.twitch.tv/" + self.channel_name
        print(f"Number of requests sent: {self.request_count}", end="", flush=True)  # initial print statement
        proxies = self.get_proxies()
        start = datetime.datetime.now()
        while True:
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            for p in proxies:
                all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                threaded = Thread(target=self.open_url, args=(all_proxies[random.randrange(len(all_proxies))],))
                threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                # print the request count
                print(f"\rNumber of requests sent: {self.request_count}", end="", flush=True)
                threaded.start()

            if elapsed_seconds >= 300:
                start = datetime.datetime.now()
                proxies = self.get_proxies()
                elapsed_seconds = 0  # reset elapsed time

            shuffle(all_proxies)


if __name__ == '__main__':

    nb_of_threads = int(input("Enter the number of threads: "))
    channel_name = input("Enter the name of the Twitch channel: ")
    bot = ViewerBot(nb_of_threads=nb_of_threads, channel_name=channel_name)
    bot.main()
