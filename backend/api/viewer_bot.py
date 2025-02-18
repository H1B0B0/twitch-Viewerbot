import sys
import time
import random
import logging
import requests
import datetime
from threading import Thread
from streamlink import Streamlink
from threading import Semaphore
from rich.console import Console
from fake_useragent import UserAgent

# Add this near the top of the file, after imports
logging.getLogger("urllib3").setLevel(logging.ERROR)

console = Console()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    def __init__(self, nb_of_threads, channel_name, proxy_file=None, proxy_imported=False, timeout=10000, type_of_proxy="http"):
        self.proxy_imported = proxy_imported
        self.proxy_file = proxy_file
        self.nb_of_threads = int(nb_of_threads)
        self.channel_name = channel_name
        self.request_count = 0  # Total requests
        self.all_proxies = []
        self.processes = []
        self.proxyrefreshed = False
        self.channel_url = "https://www.twitch.tv/" + self.channel_name
        self.thread_semaphore = Semaphore(int(nb_of_threads))  # Semaphore to control thread count
        self.active_threads = 0
        self.should_stop = False
        self.timeout = (5, 10)  # (connect timeout, read timeout)
        self.type_of_proxy = type_of_proxy
        self.proxies = []  # Add this to store proxies only once
        self.request_per_second = 0  # Add counter for requests per second
        self.requests_in_current_second = 0
        self.last_request_time = time.time()
        logging.debug(f"Type of proxy: {self.type_of_proxy}")
        logging.debug(f"Timeout: {self.timeout}")
        logging.debug(f"Proxy imported: {self.proxy_imported}")
        logging.debug(f"Proxy file: {self.proxy_file}")
        logging.debug(f"Number of threads: {self.nb_of_threads}")
        logging.debug(f"Channel name: {self.channel_name}")

    def get_proxies(self):
        # Fetch proxies from an API or use the provided proxy list
        if self.proxyrefreshed == False: 
            if self.proxy_file:
                try:
                    with open(self.proxy_file, 'r') as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                        self.proxyrefreshed = True
                        logging.debug(f"Proxies loaded from file: {lines}")
                        return lines
                except FileNotFoundError:
                    logging.error(f"Proxy file {self.proxy_file} not found.")
                    sys.exit(1)
            else:
                try:
                    response = requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol={self.type_of_proxy}&timeout={self.timeout}&country=all&ssl=all&anonymity=all")
                    if response.status_code == 200:
                        lines = response.text.split("\n")
                        lines = [line.strip() for line in lines if line.strip()]
                        self.proxyrefreshed = True
                        logging.debug(f"Proxies fetched from API: {lines}")
                        return lines
                except Exception as e:
                    logging.error(f"Error fetching proxies: {e}")
                    if len(response.text) == "":
                        console.print("Limit of proxy retrieval reached. Retry later", style="bold red")
                        return []
    
    def get_url(self):
        url = ""
        try:
            streams = session.streams(self.channel_url)
            try:
                url = streams['audio_only'].url
            except KeyError:
                url = streams['worst'].url
        except Exception as e:
            logging.error(f"Error getting stream URL: {e}")
        logging.debug(f"Stream URL: {url}")
        return url

    def stop(self):
        console.print("[bold red]Bot has been stopped[/bold red]")        
        self.should_stop = True # Set the flag to stop the bot
        self.active_threads = 0  # Reset active threads count
        self.all_proxies = []  # Clear proxies list
        self.should_stop = True  # Reset the flag
        logging.debug("Bot stopped")

    def open_url(self, proxy_data):
        self.active_threads += 1
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
                        self.request_count += 1
                        logging.debug(f"Request sent using proxy {current_proxy}")
                    proxy_data['time'] = time.time()
                    self.all_proxies[current_index] = proxy_data
            except Exception as e:
                logging.error(f"Error sending request: {e}")
            finally:
                self.active_threads -= 1
                self.thread_semaphore.release()  # Release the semaphore

        except (KeyboardInterrupt, SystemExit):
            self.should_stop = True
            logging.debug("Bot interrupted by user")

    def main(self):
        start = datetime.datetime.now()
        proxies = self.get_proxies()
        
        # Initialize all_proxies only once
        self.all_proxies = [{'proxy': p, 'time': time.time(), 'url': ""} for p in proxies]
        logging.debug(f"Initial proxies: {self.all_proxies}")
        
        while True:
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            for i in range(0, int(self.nb_of_threads)):
                acquired = self.thread_semaphore.acquire()
                if acquired:
                    threaded = Thread(target=self.open_url, args=(self.all_proxies[random.randrange(len(self.all_proxies))],))
                    threaded.daemon = True
                    threaded.start()

            if elapsed_seconds >= 300 and self.proxy_imported == False:
                # Refresh the proxies after 300 seconds (5 minutes)
                start = datetime.datetime.now()
                self.proxyrefreshed = False
                proxies = self.get_proxies()
                # Update all_proxies with new proxies
                self.all_proxies = [{'proxy': p, 'time': time.time(), 'url': ""} for p in proxies]
                logging.debug(f"Proxies refreshed: {self.all_proxies}")
                elapsed_seconds = 0

            if self.should_stop:
                logging.debug("Stopping main loop")
                sys.exit()
