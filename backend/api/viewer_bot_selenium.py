#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitch Viewer Bot avec Selenium - Contourne les détections d'Août 2025
Utilise de vrais browsers headless avec device fingerprinting authentique
"""

import sys
import time
import random
import logging
import requests
import datetime
from threading import Thread, Semaphore
from rich.console import Console
from fake_useragent import UserAgent
from urllib.parse import urlparse

# Selenium imports
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("❌ Error: Selenium not installed!")
    print("Run: pip install undetected-chromedriver selenium")
    sys.exit(1)

# Disable urllib3 warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.getLogger("urllib3").setLevel(logging.ERROR)

console = Console()
ua = UserAgent()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ViewerBotSelenium:
    """
    Bot de viewers Twitch utilisant Selenium pour simuler de vrais viewers.
    Contourne les détections d'Août 2025 avec:
    - Device fingerprinting authentique
    - Interactions player réelles
    - Timing humain
    - Cookies et sessions valides
    """
    
    def __init__(self, nb_of_threads, channel_name, proxy_file=None, 
                 proxy_imported=False, timeout=10000, type_of_proxy="http",
                 headless=True):
        self.proxy_imported = proxy_imported
        self.proxy_file = proxy_file
        self.nb_of_threads = int(nb_of_threads)
        self.channel_name = self.extract_channel_name(channel_name)
        self.request_count = 0
        self.all_proxies = []
        self.drivers = []  # Liste des drivers Selenium actifs
        self.processes = []  # Pour compatibilité avec l'ancien code
        self.proxyrefreshed = False
        self.channel_url = f"https://www.twitch.tv/{self.channel_name}"
        self.thread_semaphore = Semaphore(int(nb_of_threads))
        self.active_threads = 0
        self.should_stop = False
        self.timeout = timeout
        self.type_of_proxy = type_of_proxy
        self.headless = headless
        self.viewer_count = 0
        self.request_per_second = 0
        self.requests_in_current_second = 0
        self.last_request_time = time.time()
        
        self.status = {
            'state': 'initialized',
            'message': 'Bot initialized with Selenium',
            'proxy_count': 0,
            'proxy_loading_progress': 0,
            'startup_progress': 0,
            'active_viewers': 0
        }
        
        logging.info(f"🚀 Twitch Viewer Bot Selenium initialized")
        logging.info(f"📺 Channel: {self.channel_name}")
        logging.info(f"🧵 Threads: {self.nb_of_threads}")
        logging.info(f"🔒 Headless: {self.headless}")
        logging.info(f"🌐 Proxy type: {self.type_of_proxy}")
        logging.debug(f"Timeout: {self.timeout}")
        logging.debug(f"Proxy imported: {self.proxy_imported}")
        logging.debug(f"Proxy file: {self.proxy_file}")

    def extract_channel_name(self, input_str):
        """Extrait le nom de la chaîne d'une URL Twitch"""
        if "twitch.tv/" in input_str:
            parts = input_str.split("twitch.tv/")
            channel = parts[1].split("/")[0].split("?")[0]
            return channel.lower()
        return input_str.lower()

    def update_status(self, state, message, proxy_count=None, proxy_loading_progress=None, startup_progress=None):
        """Met à jour le statut du bot (compatible avec l'ancien format)"""
        self.status.update({
            'state': state,
            'message': message,
            **(({'proxy_count': proxy_count} if proxy_count is not None else {})),
            **(({'proxy_loading_progress': proxy_loading_progress} if proxy_loading_progress is not None else {})),
            **(({'startup_progress': startup_progress} if startup_progress is not None else {}))
        })
        logging.info(f"Status updated: {self.status}")

    def get_proxies(self):
        """Charge les proxies depuis un fichier ou une API (compatible avec l'ancien bot)"""
        self.update_status('loading_proxies', 'Starting proxy collection...')
        
        if not self.proxyrefreshed:
            if self.proxy_file:
                try:
                    self.update_status('loading_proxies', 'Loading proxies from file...')
                    with open(self.proxy_file, 'r') as f:
                        lines = [self.extract_ip_port(line.strip()) 
                                for line in f.readlines() if line.strip()]
                        self.proxyrefreshed = True
                        self.update_status(
                            'proxies_loaded', 
                            f'Loaded {len(lines)} proxies from file',
                            proxy_count=len(lines)
                        )
                        return lines
                except FileNotFoundError:
                    self.update_status('error', 'Proxy file not found')
                    logging.error(f"Proxy file {self.proxy_file} not found.")
                    sys.exit(1)
            else:
                # Récupérer les proxies depuis l'API comme l'ancien bot
                try:
                    self.update_status('loading_proxies', 'Fetching proxies from API...')
                    
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
                    
                    logging.debug(f"Request URL: {url}")
                    logging.debug(f"Request params: {params}")
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    
                    logging.debug(f"Response status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        logging.debug(f"First 100 chars of response: {response.text[:100]}")
                        
                        lines = [line.strip() for line in response.text.splitlines() if line.strip()]
                        proxies = []
                        
                        logging.debug(f"Found {len(lines)} proxy lines")
                        
                        for idx, line in enumerate(lines):
                            try:
                                if '://' in line:
                                    proxy_data = self.extract_ip_port(line)
                                else:
                                    proxy_data = self.extract_ip_port(f"http://{line}")
                                
                                # Filter by proxy type
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
                            logging.debug(f"First 5 proxies: {proxies[:5]}")
                            return proxies
                        
                        logging.error("No valid proxies found in response")
                    else:
                        logging.error(f"API request failed with status code: {response.status_code}")
                    
                    # Backup source si échec
                    backup_response = requests.get(
                        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                        timeout=10
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
        
        return []

    def extract_ip_port(self, proxy):
        """Parse le format du proxy"""
        try:
            if '://' in proxy:
                parsed = urlparse(proxy)
                protocol = parsed.scheme
                proxy_address = parsed.netloc
                if '@' in proxy_address:
                    proxy_address = proxy_address.split('@')[1]
            else:
                protocol = self.type_of_proxy
                proxy_address = proxy
            return (protocol, proxy_address)
        except Exception as e:
            logging.error(f"Error parsing proxy {proxy}: {e}")
            return (self.type_of_proxy, proxy)

    def create_driver(self, proxy_data=None):
        """
        Crée un driver Chrome avec undetected-chromedriver
        pour éviter la détection par Twitch
        """
        try:
            options = uc.ChromeOptions()
            
            # Options pour éviter la détection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-setuid-sandbox')
            
            # Randomize window size (fingerprinting)
            width = random.choice([1366, 1920, 1440, 1600])
            height = random.choice([768, 1080, 900, 1200])
            options.add_argument(f'--window-size={width},{height}')
            
            # Headless mode
            if self.headless:
                options.add_argument('--headless=new')
            
            # Random User-Agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Audio settings (mute for performance)
            options.add_argument('--mute-audio')
            
            # Proxy configuration
            if proxy_data and proxy_data[0] != 'direct':
                proxy_type, proxy_address = proxy_data
                if proxy_type in ['http', 'https']:
                    options.add_argument(f'--proxy-server=http://{proxy_address}')
                elif proxy_type == 'socks5':
                    options.add_argument(f'--proxy-server=socks5://{proxy_address}')
                elif proxy_type == 'socks4':
                    options.add_argument(f'--proxy-server=socks4://{proxy_address}')
            
            # Créer le driver avec undetected-chromedriver
            # Force version 140 pour matcher Chrome 140.0.7339.128
            driver = uc.Chrome(options=options, version_main=140)
            
            # Set timeouts
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            return driver
            
        except Exception as e:
            logging.error(f"Error creating Chrome driver: {e}")
            return None

    def simulate_human_behavior(self, driver):
        """
        Simule un comportement humain sur Twitch pour éviter la détection
        - Interactions avec le player
        - Mouvements de souris aléatoires
        - Scroll
        """
        try:
            # Attendre que la page charge
            time.sleep(random.uniform(2, 5))
            
            # Scroll aléatoire
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Essayer de cliquer sur le player pour démarrer la lecture
            try:
                # Chercher le bouton play ou le player
                player_selectors = [
                    'button[data-a-target="player-play-pause-button"]',
                    'button[aria-label="Play"]',
                    'video',
                    '.video-player'
                ]
                
                for selector in player_selectors:
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        if element:
                            # Simuler un mouvement de souris vers l'élément
                            driver.execute_script("arguments[0].scrollIntoView();", element)
                            time.sleep(random.uniform(0.3, 0.8))
                            
                            # Essayer de cliquer
                            try:
                                element.click()
                                logging.debug("✅ Clicked on player element")
                                break
                            except:
                                # Utiliser JavaScript si le clic normal échoue
                                driver.execute_script("arguments[0].click();", element)
                                logging.debug("✅ Clicked on player via JS")
                                break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Could not interact with player: {e}")
            
            # Simuler quelques interactions aléatoires
            actions = [
                lambda: driver.execute_script("window.scrollBy(0, -200);"),
                lambda: time.sleep(random.uniform(1, 3)),
                lambda: driver.execute_script("window.scrollBy(0, 100);"),
            ]
            
            for _ in range(random.randint(1, 3)):
                random.choice(actions)()
                time.sleep(random.uniform(0.5, 2))
            
            return True
            
        except Exception as e:
            logging.debug(f"Error in simulate_human_behavior: {e}")
            return False

    def open_url_selenium(self, proxy_data, viewer_id):
        """
        Ouvre Twitch dans un browser Selenium et simule un vrai viewer
        """
        driver = None
        self.active_threads += 1
        
        try:
            proxy_type, proxy_address = proxy_data
            logging.info(f"🌐 Viewer #{viewer_id}: Starting with proxy {proxy_address}")
            
            # Créer le driver
            driver = self.create_driver(proxy_data)
            if not driver:
                logging.error(f"❌ Viewer #{viewer_id}: Failed to create driver")
                self.active_threads -= 1
                self.thread_semaphore.release()
                return
            
            self.drivers.append(driver)
            
            # Naviguer vers la chaîne Twitch
            try:
                logging.info(f"📺 Viewer #{viewer_id}: Opening {self.channel_url}")
                driver.get(self.channel_url)
            except WebDriverException as e:
                # Erreur de connexion proxy
                if "ERR_TUNNEL_CONNECTION_FAILED" in str(e) or "ERR_PROXY_CONNECTION_FAILED" in str(e):
                    logging.warning(f"❌ Viewer #{viewer_id}: Proxy connection failed - {proxy_address}")
                    # Retirer le proxy mort de la liste
                    try:
                        proxy_to_remove = [p for p in self.all_proxies if p['proxy'] == proxy_data]
                        if proxy_to_remove:
                            self.all_proxies.remove(proxy_to_remove[0])
                            logging.info(f"🗑️ Removed dead proxy: {proxy_address}")
                    except Exception:
                        pass
                    raise  # Re-raise pour cleanup
                else:
                    raise
            
            # Attendre que la page charge
            time.sleep(random.uniform(3, 6))
            
            # Accepter les cookies si nécessaire
            try:
                cookie_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        'button[data-a-target="consent-banner-accept"]'))
                )
                cookie_button.click()
                logging.debug(f"✅ Viewer #{viewer_id}: Accepted cookies")
                time.sleep(1)
            except TimeoutException:
                logging.debug(f"⏭️ Viewer #{viewer_id}: No cookie banner found")
            except Exception as e:
                logging.debug(f"⏭️ Viewer #{viewer_id}: Cookie banner error: {e}")
            
            # Simuler un comportement humain
            self.simulate_human_behavior(driver)
            
            self.viewer_count += 1
            self.request_count += 1
            logging.info(f"✅ Viewer #{viewer_id}: Active! Total viewers: {self.viewer_count}")
            
            # Garder le viewer actif pendant un certain temps
            watch_duration = random.randint(60, 300)  # 1-5 minutes
            logging.info(f"⏱️ Viewer #{viewer_id}: Watching for {watch_duration}s")
            
            start_time = time.time()
            while time.time() - start_time < watch_duration and not self.should_stop:
                # Simuler quelques interactions pendant le viewing
                if random.random() < 0.3:  # 30% de chance toutes les 30s
                    self.simulate_human_behavior(driver)
                time.sleep(30)
            
            logging.info(f"👋 Viewer #{viewer_id}: Leaving after {int(time.time() - start_time)}s")
            
        except WebDriverException as e:
            if "ERR_TUNNEL_CONNECTION_FAILED" in str(e) or "ERR_PROXY_CONNECTION_FAILED" in str(e):
                logging.error(f"❌ Viewer #{viewer_id}: Proxy error - {proxy_address} (removed from pool)")
            else:
                logging.error(f"❌ Viewer #{viewer_id}: WebDriver error - {str(e)[:100]}")
        except Exception as e:
            logging.error(f"❌ Viewer #{viewer_id}: Error - {str(e)[:100]}")
        finally:
            # Fermer le driver
            if driver:
                try:
                    driver.quit()
                    if driver in self.drivers:
                        self.drivers.remove(driver)
                    if self.viewer_count > 0:
                        self.viewer_count -= 1
                    logging.debug(f"🔚 Viewer #{viewer_id}: Driver closed")
                except Exception as e:
                    logging.debug(f"Error closing driver: {e}")
            
            self.active_threads -= 1
            self.thread_semaphore.release()

    def stop(self):
        """Arrête tous les viewers et ferme les drivers"""
        console.print("[bold red]Bot has been stopped[/bold red]")
        self.update_status('stopping', 'Stopping bot...')
        self.should_stop = True
        
        # Attendre que les threads se terminent
        for thread in self.processes:
            if thread.is_alive():
                thread.join(timeout=1)
        
        # Fermer tous les drivers Selenium
        logging.info(f"Closing {len(self.drivers)} active drivers...")
        for driver in self.drivers[:]:
            try:
                driver.quit()
            except:
                pass
        
        # Cleanup
        self.drivers.clear()
        self.processes.clear()
        self.active_threads = 0
        self.all_proxies = []
        self.viewer_count = 0
        self.update_status('stopped', 'Bot has been stopped')
        logging.debug("Bot stopped and all threads cleaned up")

    def main(self):
        """Fonction principale du bot (compatible avec l'ancien format)"""
        self.update_status('starting', 'Starting bot...', startup_progress=0)
        start = datetime.datetime.now()
        
        console.print("[bold cyan]🚀 Twitch Viewer Bot with Selenium[/bold cyan]")
        console.print(f"[cyan]Channel: {self.channel_name}[/cyan]")
        console.print(f"[cyan]Max viewers: {self.nb_of_threads}[/cyan]")
        
        # Charger les proxies
        proxies = self.get_proxies()
        logging.debug(f"Proxies: {proxies}")
        
        if not proxies:
            # Mode sans proxy en secours
            console.print("[bold yellow]⚠️ No proxies available. Running in DIRECT mode (no proxy)[/bold yellow]")
            console.print("[bold yellow]⚠️ This is NOT recommended for production![/bold yellow]")
            proxies = [('direct', 'no-proxy')]
        
        # Initialize all_proxies pour compatibilité
        self.all_proxies = [{'proxy': p, 'time': time.time(), 'url': ""} for p in proxies]
        
        logging.info(f"📊 Loaded {len(proxies)} proxies")
        
        self.update_status('running', 'Bot is now running', 
                          proxy_count=len(self.all_proxies), 
                          startup_progress=100)
        
        viewer_id = 0
        
        try:
            while True:
                # Vérifier s'il reste des proxies
                if len(self.all_proxies) == 0:
                    console.print("[bold red]⚠️ All proxies failed. Switching to DIRECT mode...[/bold red]")
                    # Mode secours sans proxy
                    self.all_proxies = [{'proxy': ('direct', 'no-proxy'), 'time': time.time(), 'url': ""}]
                
                elapsed_seconds = (datetime.datetime.now() - start).total_seconds()
                
                # Démarrer les viewers progressivement (gradual join)
                for i in range(self.nb_of_threads):
                    if self.should_stop:
                        break
                    
                    if len(self.all_proxies) == 0:
                        break
                    
                    acquired = self.thread_semaphore.acquire(blocking=False)
                    if acquired:
                        # Sélectionner un proxy aléatoire
                        proxy_dict = random.choice(self.all_proxies)
                        proxy = proxy_dict['proxy']
                        
                        viewer_id += 1
                        
                        thread = Thread(
                            target=self.open_url_selenium, 
                            args=(proxy, viewer_id),
                            daemon=True
                        )
                        self.processes.append(thread)
                        thread.start()
                        
                        # Délai entre les lancements (gradual join)
                        time.sleep(random.uniform(2, 5))
                
                # Refresh proxies toutes les 5 minutes si mode API
                if elapsed_seconds >= 300 and self.proxy_imported == False and self.proxy_file is None:
                    start = datetime.datetime.now()
                    self.proxyrefreshed = False
                    proxies = self.get_proxies()
                    if proxies:
                        self.all_proxies = [{'proxy': p, 'time': time.time(), 'url': ""} for p in proxies]
                        logging.debug(f"Proxies refreshed: {self.all_proxies}")
                    elapsed_seconds = 0
                
                if self.should_stop:
                    logging.debug("Stopping main loop")
                    # Relâcher tous les sémaphores restants
                    for _ in range(self.nb_of_threads):
                        try:
                            self.thread_semaphore.release()
                        except ValueError:
                            pass
                    break
                
                # Attendre un peu avant de reboucler
                time.sleep(10)
                
        except KeyboardInterrupt:
            console.print("\n[bold red]⚠️ Interrupted by user[/bold red]")
            self.stop()
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/bold red]")
            logging.error(f"Main loop error: {e}")
        finally:
            # Attendre que tous les threads se terminent
            for t in self.processes:
                t.join()
            self.stop()
        
        console.print("[bold red]Bot main loop ended[/bold red]")


# Test standalone
if __name__ == "__main__":
    # Test avec un vrai channel en live
    # Mode NON-headless pour voir ce qui se passe
    bot = ViewerBotSelenium(
        nb_of_threads=5,  # 1 seul viewer pour tester
        channel_name="mmigo8",  # Remplace par un channel en LIVE
        headless=False,  # ⚠️ FENÊTRE VISIBLE pour debug
        type_of_proxy="http"
    )
    
    try:
        bot.main()
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        bot.stop()


# Alias pour compatibilité avec l'ancien code
ViewerBot = ViewerBotSelenium
