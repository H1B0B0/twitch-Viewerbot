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
from urllib.parse import urlparse

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

class ViewerBot_Stability:
    def __init__(self, nb_of_threads, channel_name, proxy_file=None, proxy_imported=False, timeout=10000, type_of_proxy="http"):
        self.proxy_imported = proxy_imported
        self.proxy_file = proxy_file
        self.nb_of_threads = int(nb_of_threads)
        self.channel_name = self.extract_channel_name(channel_name)
        self.request_count = 0  # Total requests
        self.all_proxies = []
        self.processes = []
        self.proxyrefreshed = False
        self.channel_url = "https://www.twitch.tv/" + self.channel_name
        self.thread_semaphore = Semaphore(int(nb_of_threads))  # Semaphore to control thread count
        self.active_threads = 0
        self.should_stop = False
        self.timeout = timeout
        self.type_of_proxy = type_of_proxy
        self.proxies = []  # Add this to store proxies only once
        self.request_per_second = 0  # Add counter for requests per second
        self.requests_in_current_second = 0
        self.last_request_time = time.time()
        self.min_proxy_threshold = 0.3  # 30% of thread count minimum threshold
        self.status = {
            'state': 'initialized',  # Current state of the bot
            'message': 'Bot initialized',  # Status message
            'proxy_count': 0,  # Number of proxies currently loaded
            'proxy_loading_progress': 0,  # Progress when loading proxies (0-100)
            'startup_progress': 0  # Overall startup progress (0-100)
        }
        logging.debug(f"Type of proxy: {self.type_of_proxy}")
        logging.debug(f"Timeout: {self.timeout}")
        logging.debug(f"Proxy imported: {self.proxy_imported}")
        logging.debug(f"Proxy file: {self.proxy_file}")
        logging.debug(f"Number of threads: {self.nb_of_threads}")
        logging.debug(f"Channel name: {self.channel_name}")

    def extract_channel_name(self, input_str):
        """Extrait le nom de la chaîne d'une URL Twitch ou retourne le nom directement"""
        if "twitch.tv/" in input_str:
            # Extraire le nom de la chaîne de l'URL
            parts = input_str.split("twitch.tv/")
            channel = parts[1].split("/")[0].split("?")[0]  # Gérer les paramètres d'URL potentiels
            return channel.lower()
        return input_str.lower()

    def update_status(self, state, message, proxy_count=None, proxy_loading_progress=None, startup_progress=None):
        self.status.update({
            'state': state,
            'message': message,
            **(({'proxy_count': proxy_count} if proxy_count is not None else {})),
            **(({'proxy_loading_progress': proxy_loading_progress} if proxy_loading_progress is not None else {})),
            **(({'startup_progress': startup_progress} if startup_progress is not None else {}))
        })
        logging.info(f"Status updated: {self.status}")

    def get_proxies(self):
        self.update_status('loading_proxies', 'Starting proxy collection...')
        
        if not self.proxyrefreshed:
            if self.proxy_file:
                try:
                    self.update_status('loading_proxies', 'Loading proxies from file...')
                    with open(self.proxy_file, 'r') as f:
                        lines = [self.extract_ip_port(line.strip()) for line in f.readlines() if line.strip()]
                        self.proxyrefreshed = True
                        self.update_status('proxies_loaded', f'Loaded {len(lines)} proxies from file', proxy_count=len(lines))
                        return lines
                except FileNotFoundError:
                    self.update_status('error', 'Proxy file not found')
                    logging.error(f"Proxy file {self.proxy_file} not found.")
                    sys.exit(1)
            else:
                try:
                    self.update_status('loading_proxies', 'Fetching proxies from API...')
                    
                    # Debug: Print current proxy type
                    logging.debug(f"Fetching proxies with type: {self.type_of_proxy}")
                    
                    url = "https://api.proxyscrape.com/v4/free-proxy-list/get"
                    params = {
                        'request': 'display_proxies',
                        'proxy_format': 'protocolipport',
                        'format': 'text',
                        'protocol': self.type_of_proxy,
                        'timeout': self.timeout
                    }
                    
                    headers = {
                        'User-Agent': ua.random
                    }
                    
                    # Debug: Log request details
                    logging.debug(f"Request URL: {url}")
                    logging.debug(f"Request params: {params}")
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    
                    # Debug: Log response details
                    logging.debug(f"Response status code: {response.status_code}")
                    logging.debug(f"Response headers: {response.headers}")
                    
                    if response.status_code == 200:
                        # Debug: Log first few lines of response
                        logging.debug(f"First 100 chars of response: {response.text[:100]}")
                        
                        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
                        proxies = []
                        
                        # Debug: Log number of lines found
                        logging.debug(f"Found {len(lines)} proxy lines")
                        
                        for idx, line in enumerate(lines):
                            try:
                                if '://' in line:
                                    # Line already has protocol
                                    proxy_data = self.extract_ip_port(line)
                                else:
                                    # Add default http:// if no protocol specified
                                    proxy_data = self.extract_ip_port(f"http://{line}")
                                
                                # Filter by proxy type if specified
                                if self.type_of_proxy == 'all' or proxy_data[0] == self.type_of_proxy:
                                    proxies.append(proxy_data)
                                
                                # Update progress
                                progress = int((idx + 1) / len(lines) * 100)
                                if progress % 10 == 0:
                                    self.update_status(
                                        'loading_proxies',
                                        f'Processing proxies... {progress}%',
                                        proxy_loading_progress=progress
                                    )
                            except Exception as e:
                                logging.error(f"Error processing proxy line '{line}': {e}")
                                continue
                        
                        if proxies:
                            self.proxyrefreshed = True
                            self.update_status(
                                'proxies_loaded',
                                f'Successfully loaded {len(proxies)} proxies',
                                proxy_count=len(proxies),
                                proxy_loading_progress=100
                            )
                            # Debug: Log first few proxies
                            logging.debug(f"First 5 proxies: {proxies[:5]}")
                            return proxies
                        
                        logging.error("No valid proxies found in response")
                    else:
                        logging.error(f"API request failed with status code: {response.status_code}")
                    
                    # Si aucun proxy n'est trouvé, essayer une source de secours
                    backup_response = requests.get(
                        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
                    )
                    if backup_response.status_code == 200:
                        proxies = [
                            self.extract_ip_port(f"http://{line.strip()}")
                            for line in backup_response.text.splitlines()
                            if line.strip()
                        ]
                        if proxies:
                            self.proxyrefreshed = True
                            self.update_status(
                                'proxies_loaded',
                                f'Loaded {len(proxies)} proxies from backup source',
                                proxy_count=len(proxies),
                                proxy_loading_progress=100
                            )
                            return proxies
                    
                    self.update_status('error', 'Failed to fetch proxies from both sources')
                    return []
                        
                except Exception as e:
                    error_msg = f"Error fetching proxies: {str(e)}"
                    logging.error(error_msg)
                    self.update_status('error', error_msg)
                    return []

    def extract_ip_port(self, proxy):
        try:
            # Gérer les formats avec protocole
            if '://' in proxy:
                parsed = urlparse(proxy)
                protocol = parsed.scheme
                proxy_address = parsed.netloc
                # Gérer le cas où il y a des credentials
                if '@' in proxy_address:
                    proxy_address = proxy_address.split('@')[1]
            else:
                protocol = self.type_of_proxy
                proxy_address = proxy

            return (protocol, proxy_address)
        except Exception as e:
            logging.error(f"Error parsing proxy {proxy}: {e}")
            return (self.type_of_proxy, proxy)  # Fallback to raw format
    
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
        self.update_status('stopping', 'Stopping bot...')
        self.should_stop = True
        
        for thread in self.processes:
            if thread.is_alive():
                thread.join(timeout=1)
        
        # Vider la liste des threads
        self.processes.clear()
        self.active_threads = 0
        self.all_proxies = []
        self.update_status('stopped', 'Bot has been stopped')
        logging.debug("Bot stopped and all threads cleaned up")

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
                    proxy_type, proxy_address = proxy_data['proxy']
                    proxies = self.configure_proxies(proxy_type, proxy_address)
                    
                    start_time = time.time()
                    with requests.Session() as s:
                        s.head(current_url, proxies=proxies, headers=headers, timeout=10)
                        response_time = int((time.time() - start_time) * 1000)  # Convert to ms
                        self.request_count += 1
                        
                        # Update proxy metrics
                        if 'success_count' not in proxy_data:
                            proxy_data['success_count'] = 0
                        proxy_data['success_count'] += 1
                        proxy_data['response_time'] = response_time
                        logging.debug(f"Request successful using proxy {proxies}, response time: {response_time}ms")
                        
                    proxy_data['time'] = time.time()
                    self.all_proxies[current_index] = proxy_data
            except Exception as e:
                # Update failure count
                if 'failure_count' not in proxy_data:
                    proxy_data['failure_count'] = 0
                proxy_data['failure_count'] += 1
                self.all_proxies[current_index] = proxy_data
                logging.error(f"Error sending request: {e}")
            finally:
                self.active_threads -= 1
                self.thread_semaphore.release()  # Release the semaphore

        except (KeyboardInterrupt, SystemExit):
            self.should_stop = True
            logging.debug("Bot interrupted by user")

    def configure_proxies(self, proxy_type, proxy_address):
        # Split the proxy address to extract IP, port, username, and password
        parts = proxy_address.split(':')
        ip = parts[0]
        port = parts[1]
        username = parts[2] if len(parts) > 2 else None
        password = parts[3] if len(parts) > 3 else None
    
        if username and password:
            credentials = f"{username}:{password}@"
        else:
            credentials = ""
    
        if proxy_type in ["socks4", "socks5"]:
            return {"http": f"{proxy_type}://{credentials}{ip}:{port}",
                    "https": f"{proxy_type}://{credentials}{ip}:{port}"}
        else:  # Default to HTTP
            return {"http": f"http://{credentials}{ip}:{port}",
                    "https": f"http://{credentials}{ip}:{port}"}

    def sort_proxies_by_quality(self):
        """Sort proxies by their success rate and response time"""
        logging.debug("Sorting proxies by quality...")
        
        # Calculate score for each proxy based on success rate and response time
        for proxy in self.all_proxies:
            if 'success_count' not in proxy:
                proxy['success_count'] = 0
            if 'failure_count' not in proxy:
                proxy['failure_count'] = 0
            if 'response_time' not in proxy:
                proxy['response_time'] = 1000  # Default high response time
                
            total_attempts = proxy['success_count'] + proxy['failure_count']
            if total_attempts > 0:
                success_rate = proxy['success_count'] / total_attempts
            else:
                success_rate = 0
                
            # Calculate score (higher is better)
            proxy['score'] = success_rate * (1000 / max(proxy['response_time'], 1))
        
        # Sort by score in descending order
        self.all_proxies.sort(key=lambda x: x.get('score', 0), reverse=True)
        logging.debug(f"Proxies sorted. Top 3 scores: {[p.get('score', 0) for p in self.all_proxies[:3]]}")
        
    def remove_bad_proxies(self):
        """Remove proxies that have consistently failed"""
        initial_count = len(self.all_proxies)
        logging.debug(f"Checking for bad proxies. Initial count: {initial_count}")
        
        # Remove proxies with high failure rate (over 5 failures and success rate < 20%)
        self.all_proxies = [p for p in self.all_proxies if not (
            p.get('failure_count', 0) > 5 and 
            p.get('success_count', 0) / max(p.get('failure_count', 1) + p.get('success_count', 0), 1) < 0.2
        )]
        
        removed_count = initial_count - len(self.all_proxies)
        if removed_count > 0:
            logging.info(f"Removed {removed_count} bad proxies. Remaining: {len(self.all_proxies)}")
            
        # Check if we have enough proxies left
        min_required = int(self.nb_of_threads * self.min_proxy_threshold)
        if len(self.all_proxies) < min_required:
            logging.warning(f"Proxy count ({len(self.all_proxies)}) below threshold ({min_required}). Attempting to refresh proxies.")
            self.proxyrefreshed = False
            new_proxies = self.get_proxies()
            if new_proxies:
                # Add new proxies to the pool
                new_proxy_data = [{'proxy': p, 'time': time.time(), 'url': "", 'success_count': 0, 'failure_count': 0, 'response_time': 1000} for p in new_proxies]
                self.all_proxies.extend(new_proxy_data)
                logging.info(f"Added {len(new_proxy_data)} new proxies. New total: {len(self.all_proxies)}")
        
        return len(self.all_proxies)

    def main(self):
        self.update_status('starting', 'Starting bot...', startup_progress=0)
        start = datetime.datetime.now()
        last_proxy_maintenance = time.time()
        proxies = self.get_proxies()
        
        if not proxies:
            self.update_status('error', 'No proxies available. Stopping bot.')
            self.should_stop = True
            return

        # Initialize all_proxies with quality metrics
        self.all_proxies = [{'proxy': p, 'time': time.time(), 'url': "", 
                            'success_count': 0, 'failure_count': 0, 'response_time': 1000} 
                           for p in proxies]
        
        # Number of threads should be at most the number of available proxies
        thread_count = min(self.nb_of_threads, len(self.all_proxies))
        self.thread_semaphore = Semaphore(thread_count)  # Update semaphore with actual thread count
        
        logging.info(f"Starting bot with {thread_count} threads using {len(self.all_proxies)} unique proxies")
        
        self.processes = []
        
        self.update_status('running', 'Bot is now running', 
                          proxy_count=len(self.all_proxies), 
                          startup_progress=100)
        
        # Track which proxies are currently in use
        in_use_proxies = set()
        
        # Track which proxies were recently used and their last usage time
        proxy_usage_history = {}
        # Track the cycle count to ensure all proxies get used
        cycle_count = 0
        
        while True:
            if len(self.all_proxies) == 0:
                console.print("[bold red]No proxies available. Stopping bot.[/bold red]")
                break

            # Perform proxy maintenance every 30 seconds
            if time.time() - last_proxy_maintenance > 30:
                self.sort_proxies_by_quality()
                self.remove_bad_proxies()
                # Don't clear in_use_proxies here anymore
                last_proxy_maintenance = time.time()
                # Reset usage cycle periodically to refresh distribution
                cycle_count += 1
                if cycle_count >= 5:  # Reset after 5 maintenance cycles
                    proxy_usage_history.clear()
                    cycle_count = 0
                    logging.debug("Resetting proxy usage history to ensure diversity")

            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            # Get available proxies, prioritizing those that haven't been used recently
            current_time = time.time()
            available_proxies = []
            unused_proxies = []
            recently_used = []
            
            for proxy in self.all_proxies:
                proxy_key = self.proxy_to_key(proxy['proxy'])
                # Skip currently in-use proxies
                if proxy_key in in_use_proxies:
                    continue
                    
                # Categorize proxies by usage recency
                last_used = proxy_usage_history.get(proxy_key, 0)
                if last_used == 0:  # Never used in this cycle
                    unused_proxies.append(proxy)
                else:
                    # Consider a proxy "recently used" if it was used in the last 5 seconds
                    time_since_use = current_time - last_used
                    if time_since_use < 5:
                        recently_used.append((proxy, time_since_use))
                    else:
                        available_proxies.append((proxy, time_since_use))
            
            # Sort available proxies by time since last use (oldest first)
            available_proxies.sort(key=lambda x: x[1], reverse=True)
            available_proxies = [p[0] for p in available_proxies]
            
            # Prioritize unused proxies, then add older used proxies
            prioritized_proxies = unused_proxies + available_proxies
            
            # If we're severely limited on proxies, allow recently used ones too
            if len(prioritized_proxies) < thread_count * 0.5:
                recently_used.sort(key=lambda x: x[1], reverse=True)  # Oldest first
                prioritized_proxies.extend([p[0] for p in recently_used])
                
            # Log proxy distribution stats
            logging.debug(f"Proxy distribution: {len(unused_proxies)} unused, {len(available_proxies)} available, {len(recently_used)} recent")
                
            # Launch threads for prioritized proxies up to the thread limit
            launched_threads = 0
            for proxy_data in prioritized_proxies:
                if launched_threads >= thread_count:
                    break
                    
                acquired = self.thread_semaphore.acquire(blocking=False)
                if not acquired:
                    break  # No more semaphores available
                    
                proxy_key = self.proxy_to_key(proxy_data['proxy'])
                in_use_proxies.add(proxy_key)
                proxy_usage_history[proxy_key] = current_time
                
                # Create thread for this proxy
                threaded = Thread(target=self.open_url_with_tracking, 
                                 args=(proxy_data, proxy_key, in_use_proxies))
                self.processes.append(threaded)
                threaded.daemon = True
                threaded.start()
                launched_threads += 1
                
            # Log how many threads we launched this cycle
            if launched_threads > 0:
                logging.debug(f"Launched {launched_threads} threads this cycle")
                
            # If we couldn't launch enough threads, we need more proxies
            if launched_threads < thread_count * 0.7 and len(self.all_proxies) >= thread_count:
                logging.warning(f"Only launched {launched_threads}/{thread_count} threads. Proxy diversity might be limited.")

            # Proxy refresh logic (same as before)
            if elapsed_seconds >= 300 and self.proxy_imported == False:
                # Refresh proxies code...
                pass

            # Small sleep to prevent CPU overload but allow for quick thread turnover
            time.sleep(0.05)

            if self.should_stop:
                logging.debug("Stopping main loop")
                # Release all remaining semaphores
                for _ in range(thread_count):
                    try:
                        self.thread_semaphore.release()
                    except ValueError:
                        pass  # Ignore if already released
                break

        for t in self.processes:
            t.join()
        console.print("[bold red]Bot main loop ended[/bold red]")

    # Helper method to generate a unique key for each proxy
    def proxy_to_key(self, proxy):
        return f"{proxy[0]}:{proxy[1]}"  # protocol:ip:port

    # Modified version of open_url that tracks when a proxy is finished being used
    def open_url_with_tracking(self, proxy_data, proxy_key, in_use_set):
        self.active_threads += 1
        try:
            headers = {'User-Agent': ua.random}
            
            try:
                # Find the proxy in the list (it might have moved due to sorting)
                try:
                    current_index = self.all_proxies.index(proxy_data)
                except ValueError:
                    # Proxy no longer in list, abort this thread
                    logging.debug(f"Proxy {proxy_key} no longer in list, aborting thread")
                    return
                    
                if proxy_data['url'] == "":
                    proxy_data['url'] = self.get_url()
                current_url = proxy_data['url']
                
                # Always try to use the proxy regardless of time since last use
                # This ensures all proxies get used
                proxy_type, proxy_address = proxy_data['proxy']
                proxies = self.configure_proxies(proxy_type, proxy_address)
                
                start_time = time.time()
                with requests.Session() as s:
                    s.head(current_url, proxies=proxies, headers=headers, timeout=10)
                    response_time = int((time.time() - start_time) * 1000)  # Convert to ms
                    self.request_count += 1
                    
                    # Update proxy metrics
                    if 'success_count' not in proxy_data:
                        proxy_data['success_count'] = 0
                    proxy_data['success_count'] += 1
                    proxy_data['response_time'] = response_time
                    logging.debug(f"Request successful using proxy {proxy_key}, response time: {response_time}ms")
                    
                proxy_data['time'] = time.time()
                self.all_proxies[current_index] = proxy_data
            except Exception as e:
                # Update failure count
                if 'failure_count' not in proxy_data:
                    proxy_data['failure_count'] = 0
                proxy_data['failure_count'] += 1
                
                # Try to update the proxy in the list
                try:
                    current_index = self.all_proxies.index(proxy_data)
                    self.all_proxies[current_index] = proxy_data
                except ValueError:
                    # Proxy no longer in list
                    pass
                    
                logging.error(f"Error sending request with proxy {proxy_key}: {e}")
            finally:
                # Mark this proxy as no longer in use
                if proxy_key in in_use_set:
                    in_use_set.remove(proxy_key)
                self.active_threads -= 1
                self.thread_semaphore.release()  # Release the semaphore

        except (KeyboardInterrupt, SystemExit):
            self.should_stop = True
            logging.debug("Bot interrupted by user")
