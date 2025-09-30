import sys
import time
import logging
import requests
import datetime
import json
import uuid
import websocket
from threading import Thread
from threading import Semaphore
from rich.console import Console
from fake_useragent import UserAgent
from urllib.parse import urlparse

# Try to import tls_client for better fingerprinting
try:
    import tls_client
    HAS_TLS_CLIENT = True
except ImportError:
    HAS_TLS_CLIENT = False
    logging.warning("tls_client not available, using requests (may be detected)")

# Add this near the top of the file, after imports
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("websocket").setLevel(logging.ERROR)

console = Console()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Session creating for request
ua = UserAgent()

class ViewerBot:
    def __init__(self, nb_of_threads, channel_name, proxy_file=None, proxy_imported=False, timeout=10000, type_of_proxy="http"):
        self.proxy_imported = proxy_imported
        self.proxy_file = proxy_file
        self.nb_of_threads = int(nb_of_threads)
        self.channel_name = self.extract_channel_name(channel_name)
        self.channel_id = None  # Will be fetched from Twitch API
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
        self.active_websockets = []  # Track active websocket connections
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

    def get_channel_id(self):
        """Récupère l'ID du channel depuis l'API Twitch avec tls_client en priorité"""
        try:
            # Method 1: Try with tls_client (preferred method)
            if HAS_TLS_CLIENT:
                try:
                    s = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)
                    s.headers.update({
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': 'https://www.twitch.tv/',
                        'Origin': 'https://www.twitch.tv',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                    })
                    
                    # First visit Twitch main page to establish session
                    session_resp = s.get("https://www.twitch.tv")
                    logging.debug(f"TLS client session request status: {session_resp.status_code}")
                    
                    # Try Helix API first
                    helix_url = f"https://api.twitch.tv/helix/users?login={self.channel_name}"
                    response = s.get(helix_url)
                    
                    logging.debug(f"TLS client Helix API status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('data') and len(data['data']) > 0:
                            self.channel_id = data['data'][0]['id']
                            logging.debug(f"Retrieved channel ID from Helix API with tls_client: {self.channel_id}")
                            return self.channel_id
                    
                    # If Helix fails, try GraphQL API (Twitch's internal API)
                    gql_url = "https://gql.twitch.tv/gql"
                    gql_headers = s.headers.copy()
                    gql_headers.update({
                        'Content-Type': 'application/json',
                    })
                    
                    gql_query = {
                        "query": f"query {{user(login: \"{self.channel_name}\") {{id displayName}}}}",
                        "variables": {}
                    }
                    
                    gql_response = s.post(gql_url, headers=gql_headers, json=gql_query)
                    logging.debug(f"TLS client GraphQL API status: {gql_response.status_code}")
                    
                    if gql_response.status_code == 200:
                        gql_data = gql_response.json()
                        if gql_data.get('data', {}).get('user', {}).get('id'):
                            self.channel_id = gql_data['data']['user']['id']
                            logging.debug(f"Retrieved channel ID from GraphQL API with tls_client: {self.channel_id}")
                            return self.channel_id
                    
                    # If APIs fail, try scraping the channel page
                    page_response = s.get(f'https://www.twitch.tv/{self.channel_name}')
                    if page_response.status_code == 200:
                        import re
                        # Look for channel data in the page
                        patterns = [
                            rf'"channelID":"(\d+)"',
                            rf'"id":"(\d+)".*?"login":"{re.escape(self.channel_name)}"',
                            rf'channel.*?id["\']:\s*"?(\d+)"?',
                            rf'"targetID":"(\d+)"'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, page_response.text, re.IGNORECASE)
                            if match:
                                self.channel_id = match.group(1)
                                logging.debug(f"Retrieved channel ID from page scraping with tls_client: {self.channel_id}")
                                return self.channel_id
                                
                except Exception as e:
                    logging.debug(f"tls_client method failed: {e}")
            
            # Method 2: Fallback to requests
            try:
                headers = {
                    'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'https://www.twitch.tv/{self.channel_name}',
                }
                
                # Try Helix API
                url = f"https://api.twitch.tv/helix/users?login={self.channel_name}"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data') and len(data['data']) > 0:
                        self.channel_id = data['data'][0]['id']
                        logging.debug(f"Retrieved channel ID from Helix API with requests: {self.channel_id}")
                        return self.channel_id
                
                logging.warning("Helix API failed with requests, trying page scraping")
                
                # Alternative: scraper la page Twitch
                page_response = requests.get(f'https://www.twitch.tv/{self.channel_name}', 
                                           headers={'User-Agent': headers['User-Agent']})
                if page_response.status_code == 200:
                    import re
                    # Chercher l'ID dans le HTML de la page
                    patterns = [
                        rf'"channelID":"(\d+)"',
                        rf'"id":"(\d+)".*?"login":"{re.escape(self.channel_name)}"',
                        rf'channel.*?id["\']:\s*"?(\d+)"?'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, page_response.text, re.IGNORECASE)
                        if match:
                            self.channel_id = match.group(1)
                            logging.debug(f"Retrieved channel ID via scraping with requests: {self.channel_id}")
                            return self.channel_id
                
            except Exception as e:
                logging.debug(f"Requests fallback failed: {e}")
            
            logging.error("Could not retrieve channel ID with any method")
            return None
            
        except Exception as e:
            logging.error(f"Error getting channel ID: {e}")
            return None

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
    
    def create_websocket_connection(self, proxy_data):
        """Crée une connexion websocket vers Twitch Hermes"""
        try:
            proxy_type, proxy_address = proxy_data['proxy']
            
            # Configuration du proxy pour websocket
            proxy_host, proxy_port = proxy_address.split(':')[:2]
            
            # URL de connexion Hermes
            ws_url = "wss://hermes.twitch.tv/v1?clientId=kimne78kx3ncx6brgo4mv6wki5h1ko"
            
            # Créer la websocket avec proxy
            if proxy_type in ["socks4", "socks5"]:
                # Pour SOCKS, utiliser un autre paramètre
                ws = websocket.WebSocket(
                    sslopt={"cert_reqs": 0},
                    sockopt=[(websocket.socket.SOL_SOCKET, websocket.socket.SO_REUSEADDR, 1)]
                )
            else:
                # Pour HTTP proxy
                ws = websocket.WebSocket(
                    http_proxy_host=proxy_host,
                    http_proxy_port=int(proxy_port),
                    sslopt={"cert_reqs": 0}
                )
            
            # Headers pour la connexion
            headers = {
                'User-Agent': ua.random,
                'Origin': 'https://www.twitch.tv'
            }
            
            # Connexion
            ws.connect(ws_url, header=headers, timeout=10)
            
            # Message de subscription au topic video-playback (fonctionne sans auth)
            subscribe_message = {
                "type": "subscribe",
                "id": str(uuid.uuid4()),
                "subscribe": {
                    "id": str(uuid.uuid4()),
                    "type": "pubsub",
                    "pubsub": {
                        "topic": f"video-playback-by-id.{self.channel_id}"
                    }
                },
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            }
            
            ws.send(json.dumps(subscribe_message))
            logging.debug(f"Sent subscription message via proxy {proxy_address}")
            
            return ws
            
        except Exception as e:
            logging.error(f"Error creating websocket connection: {e}")
            return None

    def maintain_websocket(self, proxy_data):
        """Maintient une connexion websocket active"""
        self.active_threads += 1
        ws = None
        
        try:
            ws = self.create_websocket_connection(proxy_data)
            if not ws:
                return
            
            self.active_websockets.append(ws)

            while not self.should_stop:
                try:
                    # Pas besoin d'envoyer de keepalive - le serveur les envoie automatiquement
                    # Écouter les messages entrants (avec timeout ultra court pour être plus réactif)
                    ws.settimeout(0.5)  # Réduit de 1.0 à 0.5 secondes
                    try:
                        result = ws.recv()
                        if result:
                            logging.debug(f"Received: {result[:100]}...")  # Log first 100 chars
                            # Compter les notifications comme des requêtes réussies
                            parsed = json.loads(result)
                            if parsed.get('type') == 'notification':
                                self.request_count += 1
                    except websocket.WebSocketTimeoutException:
                        pass  # Timeout normal, continuer

                    # Pause minimale pour être plus agressif
                    time.sleep(0.01)  # Réduit de 0.1 à 0.01 secondes
                    
                except websocket.WebSocketConnectionClosedException:
                    logging.warning(f"WebSocket connection closed for proxy {proxy_data['proxy'][1]}")
                    # Tentative de reconnexion automatique (mode agressif)
                    if not self.should_stop:
                        logging.info(f"Attempting auto-reconnect for proxy {proxy_data['proxy'][1]}...")
                        time.sleep(2)  # Petite pause avant reconnexion
                        ws = self.create_websocket_connection(proxy_data)
                        if ws:
                            self.active_websockets.append(ws)
                            logging.info(f"Successfully reconnected proxy {proxy_data['proxy'][1]}")
                            continue  # Reprendre la boucle
                    break
                except Exception as e:
                    logging.error(f"Error in websocket loop: {e}")
                    # Tentative de reconnexion automatique (mode agressif)
                    if not self.should_stop:
                        logging.info(f"Attempting auto-reconnect after error for proxy {proxy_data['proxy'][1]}...")
                        time.sleep(2)
                        ws = self.create_websocket_connection(proxy_data)
                        if ws:
                            self.active_websockets.append(ws)
                            logging.info(f"Successfully reconnected proxy {proxy_data['proxy'][1]}")
                            continue
                    break

        except Exception as e:
            logging.error(f"Error maintaining websocket: {e}")
        finally:
            if ws:
                try:
                    ws.close()
                    if ws in self.active_websockets:
                        self.active_websockets.remove(ws)
                except:
                    pass
            self.active_threads -= 1
            self.thread_semaphore.release()

    def stop(self):
        console.print("[bold red]Bot has been stopped[/bold red]")
        self.update_status('stopping', 'Stopping bot...')
        self.should_stop = True
        
        # Fermer toutes les connexions websocket actives
        for ws in self.active_websockets:
            try:
                ws.close()
            except:
                pass
        self.active_websockets.clear()
        
        for thread in self.processes:
            if thread.is_alive():
                thread.join(timeout=1)
        
        # Vider la liste des threads
        self.processes.clear()
        self.active_threads = 0
        self.all_proxies = []
        self.update_status('stopped', 'Bot has been stopped')
        logging.debug("Bot stopped and all threads cleaned up")

    def main(self):
        self.update_status('starting', 'Starting bot...', startup_progress=0)
        
        # Récupérer l'ID du channel
        self.update_status('starting', 'Getting channel information...', startup_progress=20)
        if not self.get_channel_id():
            self.update_status('error', 'Could not get channel ID. Stopping bot.')
            return
        
        start = datetime.datetime.now()
        proxies = self.get_proxies()
        logging.debug(f"Proxies: {proxies}")
        
        if not proxies:
            self.update_status('error', 'No proxies available. Stopping bot.')
            self.should_stop = True
            return

        # Initialize all_proxies only once
        self.all_proxies = [{'proxy': p, 'time': time.time()} for p in proxies]
        
        self.processes = []
        
        self.update_status('running', 'Bot is now running with WebSocket connections (AGGRESSIVE MODE)',
                          proxy_count=len(self.all_proxies),
                          startup_progress=100)

        # Mode agressif : démarrer TOUTES les connexions immédiatement
        logging.info(f"AGGRESSIVE MODE: Starting {self.nb_of_threads} connections immediately")
        for i in range(0, min(int(self.nb_of_threads), len(self.all_proxies))):
            acquired = self.thread_semaphore.acquire(blocking=False)
            if acquired and len(self.all_proxies) > 0:
                proxy_data = self.all_proxies[i % len(self.all_proxies)]
                threaded = Thread(target=self.maintain_websocket, args=(proxy_data,))
                self.processes.append(threaded)
                threaded.daemon = True
                threaded.start()
                time.sleep(0.05)  # Délai minimal entre chaque démarrage
            elif acquired:
                self.thread_semaphore.release()

        while not self.should_stop:
            if len(self.all_proxies) == 0:
                console.print("[bold red]No proxies available. Stopping bot.[/bold red]")
                break

            elapsed_seconds = (datetime.datetime.now() - start).total_seconds()

            # Vérifier et créer de nouvelles connexions si nécessaire (mode agressif)
            active_count = sum(1 for t in self.processes if t.is_alive())
            if active_count < int(self.nb_of_threads):
                needed = int(self.nb_of_threads) - active_count
                logging.info(f"AGGRESSIVE MODE: Spawning {needed} additional connections")
                for i in range(needed):
                    acquired = self.thread_semaphore.acquire(blocking=False)
                    if acquired and len(self.all_proxies) > 0:
                        proxy_data = self.all_proxies[i % len(self.all_proxies)]
                        threaded = Thread(target=self.maintain_websocket, args=(proxy_data,))
                        self.processes.append(threaded)
                        threaded.daemon = True
                        threaded.start()
                    elif acquired:
                        self.thread_semaphore.release()

            # Attendre avant de vérifier à nouveau (mode agressif)
            time.sleep(2)  # Réduit à 2 secondes pour vérifier plus souvent

            if elapsed_seconds >= 300 and self.proxy_imported == False:
                # Refresh the proxies after 300 seconds (5 minutes)
                start = datetime.datetime.now()
                self.proxyrefreshed = False
                proxies = self.get_proxies()
                # Update all_proxies with new proxies
                self.all_proxies = [{'proxy': p, 'time': time.time()} for p in proxies]
                logging.debug(f"Proxies refreshed: {self.all_proxies}")
                elapsed_seconds = 0

            if self.should_stop:
                logging.debug("Stopping main loop")
                break

        for t in self.processes:
            t.join()
        console.print("[bold red]Bot main loop ended[/bold red]")