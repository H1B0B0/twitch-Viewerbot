import signal
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
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
import logging
from urllib3 import PoolManager
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

# Add this near the top of the file, after imports
logging.getLogger("urllib3").setLevel(logging.ERROR)

console = Console()


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
        self.nb_requests = 0  # Total requests
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
        print(f"Type of proxy: {self.type_of_proxy}")
        print(f"Timeout: {self.timeout}")
        print(f"Proxy imported: {self.proxy_imported}")
        print(f"Proxy file: {self.proxy_file}")
        print(f"Number of threads: {self.nb_of_threads}")
        print(f"Channel name: {self.channel_name}")

        # Configure connection pooling
        self.pool_connections = min(100, max(nb_of_threads, 10))  # Scale with thread count, min 10, max 100
        self.pool_maxsize = min(100, max(nb_of_threads, 10))     # Same as connections
        
        # Configure retries with more specific settings
        self.retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_redirect=False,
            raise_on_status=False,
            connect=3,
            read=3
        )
        
        # Create a session with proper pooling
        self.session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            max_retries=self.retry_strategy,
            pool_block=False  # Don't block when pool is full
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

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
                    response = requests.get(f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol={self.type_of_proxy}&timeout={self.timeout}&country=all&ssl=all&anonymity=all")
                    if response.status_code == 200:
                        lines = []
                        lines = response.text.split("\n")
                        lines = [line.strip() for line in lines if line.strip()]
                        self.proxyrefreshed = True
                        return lines
                except:
                    if len(response.text) == "":
                        console.print("Limit of proxy retrieval reached. Retry later", style="bold red")
                        return []
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

    def stop(self):
        console.print("[bold red]Bot has been stopped[/bold red]")        
        self.should_stop = True # Set the flag to stop the bot
        self.active_threads = 0  # Reset active threads count
        self.all_proxies = []  # Clear proxies list
        self.session.close()  # Properly close the session when stopping
    
    def update_display(self):
        with Live(console=console, refresh_per_second=10) as live:
            while True:
                table = Table(show_header=False, show_edge=False)
                table.add_column(justify="right")
                table.add_column(justify="left")
                
                text = Text(f"Number of requests sent: {self.nb_requests}")
                text.stylize("bold magenta")
                table.add_row(text, Spinner("aesthetic"))
                
                active_threads_text = Text(f"Active threads: {self.active_threads}")
                active_threads_text.stylize("bold cyan")  # add style to the active threads text
                table.add_row(active_threads_text, Spinner("aesthetic"))  # display the number of active threads
                
                live.update(table)
                if self.should_stop:
                    sys.exit()
    
    def open_url(self, proxy_data):
        self.active_threads += 1
        try:
            headers = {
                'User-Agent': ua.random,
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            current_index = self.all_proxies.index(proxy_data)

            if proxy_data['url'] == "":
                proxy_data['url'] = self.get_url()
            current_url = proxy_data['url']
            
            try:
                if time.time() - proxy_data['time'] >= random.randint(1, 5):
                    current_proxy = {
                        "http": proxy_data['proxy'],
                        "https": proxy_data['proxy']
                    }
                    
                    # Use head request with specific options
                    response = self.session.head(
                        current_url,
                        proxies=current_proxy,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=False,
                        verify=False  # Disable SSL verification for proxies
                    )
                    
                    if response.status_code == 200:
                        self.nb_requests += 1
                        self.requests_in_current_second += 1
                        proxy_data['time'] = time.time()
                        self.all_proxies[current_index] = proxy_data
                    
            except requests.exceptions.RequestException:
                # Remove failed proxy from the list
                if proxy_data in self.all_proxies:
                    self.all_proxies.remove(proxy_data)
            finally:
                self.active_threads -= 1
                self.thread_semaphore.release()
        
        except (KeyboardInterrupt, SystemExit):
            self.should_stop = True

    def main(self):
        start = datetime.datetime.now()
        proxies = self.get_proxies()

        # Start a separate thread for updating the display
        self.display_thread = Thread(target=self.update_display)
        self.display_thread.daemon = True
        self.display_thread.start()
        
        while not self.should_stop:  # Changed condition to check should_stop flag
            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            for p in proxies:
                if self.should_stop:  # Check should_stop before adding proxies
                    break
                self.all_proxies.append({'proxy': p, 'time': time.time(), 'url': ""})

            for i in range(0, int(self.nb_of_threads)):
                if self.should_stop:  # Check should_stop before starting new threads
                    break
                acquired = self.thread_semaphore.acquire()  # Acquire the semaphore with a timeout
                if acquired:
                    threaded = Thread(target=self.open_url, args=(self.all_proxies[random.randrange(len(self.all_proxies))],))
                    threaded.daemon = True
                    threaded.start()

            if elapsed_seconds >= 300 and self.proxy_imported == False and not self.should_stop:
                # Refresh the proxies after 300 seconds (5 minutes)
                start = datetime.datetime.now()
                self.proxyrefreshed = False
                proxies = self.get_proxies()
                elapsed_seconds = 0  # Reset elapsed time

            if self.should_stop:
                break

            time.sleep(0.1)  # Add small sleep to prevent CPU overuse

