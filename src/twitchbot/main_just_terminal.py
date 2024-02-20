import os
import sys
import argparse
import time
import random
import requests
import datetime
from random import shuffle
from threading import Thread
from streamlink import Streamlink
from fake_useragent import UserAgent
from threading import Semaphore

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
    def __init__(self, nb_of_threads, channel_name, proxy_file=None, proxy_imported=False):
        self.proxy_imported = proxy_imported
        self.proxy_file = proxy_file
        self.nb_of_threads = nb_of_threads
        self.channel_name = channel_name
        self.request_count = 0  # initialize the counter variable
        self.all_proxies = []
        self.processes = []
        self.proxyrefreshed = False
        self.channel_url = "https://www.twitch.tv/" + self.channel_name
        self.thread_semaphore = Semaphore(int(nb_of_threads))  # Semaphore to control thread count

    def get_proxies(self):
        # Fetch proxies from an API or use the provided proxy list
        if self.proxyrefreshed == False: 
            if self.proxy_file:
                try:
                    with open(self.proxy_file, 'r') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                        self.proxyrefreshed = True
                        return lines
                except FileNotFoundError:
                    print(f"Proxy file {self.proxy_file} not found.")
                    sys.exit(1)
            else:
                try:
                    response = requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all")
                    if response.status_code == 200:
                        lines = []
                        lines = response.text.split("\n")
                        lines = [line.strip() for line in lines if line.strip()]
                        self.proxyrefreshed = True
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
            headers = {'User-Agent': ua.random}
            current_index = self.all_proxies.index(proxy_data)

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
                    self.all_proxies[current_index] = proxy_data
            except:
                pass
            finally:
                self.thread_semaphore.release()  # Release the semaphore

        except (KeyboardInterrupt):
            sys.exit()

    def stop(self):
        for thread in self.processes:
            thread.join()
        sys.exit()

    def main(self):
        print(f"Number of requests sent: {self.request_count}", end="", flush=True)  # initial print statement
        proxies = self.get_proxies()
        start = datetime.datetime.now()
        while True:
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            for p in proxies:
                self.all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                self.thread_semaphore.acquire()  # Acquire the semaphore
                threaded = Thread(target=self.open_url, args=(self.all_proxies[random.randrange(len(self.all_proxies))],))
                threaded.daemon = True  # This thread dies when main thread (only non-daemon thread) exits.
                # print the request count
                print(f"\rNumber of requests sent: {self.request_count}", end="", flush=True)
                threaded.start()

            if elapsed_seconds >= 300 and self.proxy_imported == False:
                # Refresh the proxies after 300 seconds (5 minutes)
                start = datetime.datetime.now()
                self.proxyrefreshed = False
                proxies = self.get_proxies()
                elapsed_seconds = 0  # Reset elapsed time

            shuffle(self.all_proxies)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-threads', type=int, help='Number of threads')
    parser.add_argument('-twitchname', type=str, help='Twitch channel name')
    parser.add_argument('-proxyfile', type=str, help='File containing list of proxies')
    args = parser.parse_args()

    nb_of_threads = args.threads if args.threads else int(input("Enter the number of threads: "))
    channel_name = args.twitchname if args.twitchname else input("Enter the name of the Twitch channel: ")
    proxy_file = args.proxyfile if args.proxyfile else input("Do you wan't to use a proxy file? (y/n): ")

    if proxy_file.lower().startswith('y'):
        proxy_file = args.proxyfile if args.proxyfile else input("Enter the path of the proxy file: ")
        proxy_imported = True
    else:
        proxy_file = None
    bot = ViewerBot(nb_of_threads=nb_of_threads, channel_name=channel_name, proxy_file=proxy_file, proxy_imported=proxy_imported)
    bot.main()
