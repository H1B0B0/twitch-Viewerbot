import requests
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging

class TwitchPlayerAnalyzer:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.captured_requests = []
        self.player_sources = []
        
    def setup_selenium(self):
        """Configure Selenium pour capturer le trafic réseau"""
        chrome_options = Options()
        chrome_options.add_argument("--enable-network-service-logging")
        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Configuration moderne pour les logs réseau
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        return webdriver.Chrome(options=chrome_options)
        
    def analyze_player_traffic(self, duration_minutes=3):
        """Analyse le trafic généré par le player pendant X minutes"""
        print(f"Démarrage analyse trafic player pour {self.channel_name}")
        
        driver = self.setup_selenium()
        
        try:
            # Aller sur la page Twitch
            driver.get(f"https://www.twitch.tv/{self.channel_name}")
            
            # Attendre le chargement
            time.sleep(5)
            
            # Capturer le trafic pendant la durée spécifiée
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            print(f"Capture du trafic pendant {duration_minutes} minutes...")
            
            while time.time() < end_time:
                # Récupérer les logs réseau
                logs = driver.get_log('performance')
                
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        
                        if message['message']['method'] in ['Network.requestWillBeSent', 'Network.responseReceived']:
                            self.process_network_event(message['message'])
                            
                    except Exception as e:
                        continue
                
                time.sleep(1)
                
        finally:
            driver.quit()
            
        # Analyser les résultats
        self.analyze_captured_requests()
        
    def process_network_event(self, event):
        """Traite un événement réseau capturé"""
        if event['method'] == 'Network.requestWillBeSent':
            request = event['params']['request']
            url = request['url']
            
            # Filtrer les requêtes intéressantes
            interesting_patterns = [
                'api.twitch.tv',
                'gql.twitch.tv', 
                'usher.ttvnw.net',
                'pubsub-edge.twitch.tv',
                'video-weaver',
                'heartbeat',
                'analytics',
                'viewer',
                'telemetry'
            ]
            
            if any(pattern in url for pattern in interesting_patterns):
                self.captured_requests.append({
                    'timestamp': time.time(),
                    'type': 'request',
                    'url': url,
                    'method': request.get('method', 'GET'),
                    'headers': request.get('headers', {}),
                    'postData': request.get('postData', '')
                })
                
                print(f"Requête capturée: {request['method']} {url}")
                
    def analyze_captured_requests(self):
        """Analyse les requêtes capturées pour identifier les patterns"""
        print(f"\n=== ANALYSE DE {len(self.captured_requests)} REQUÊTES ===")
        
        # Grouper par domaine
        domains = {}
        for req in self.captured_requests:
            domain = re.search(r'https?://([^/]+)', req['url'])
            if domain:
                domain = domain.group(1)
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(req)
        
        # Analyser chaque domaine
        for domain, requests in domains.items():
            print(f"\n--- {domain} ({len(requests)} requêtes) ---")
            
            # Patterns d'URLs uniques
            url_patterns = set()
            for req in requests:
                # Simplifier l'URL pour voir les patterns
                simplified = re.sub(r'\d+', '{ID}', req['url'])
                simplified = re.sub(r'[a-f0-9]{8,}', '{HASH}', simplified)
                url_patterns.add(simplified)
            
            for pattern in sorted(url_patterns):
                print(f"  Pattern: {pattern}")
                
        # Chercher des endpoints de viewer tracking
        self.find_viewer_tracking_endpoints()
        
    def find_viewer_tracking_endpoints(self):
        """Recherche spécifiquement les endpoints de tracking des viewers"""
        print(f"\n=== ENDPOINTS DE TRACKING POTENTIELS ===")
        
        tracking_keywords = ['viewer', 'view', 'watch', 'heartbeat', 'ping', 'analytics', 'telemetry', 'segment']
        
        for req in self.captured_requests:
            url_lower = req['url'].lower()
            
            if any(keyword in url_lower for keyword in tracking_keywords):
                print(f"\n🎯 ENDPOINT INTÉRESSANT:")
                print(f"   URL: {req['url']}")
                print(f"   Méthode: {req['method']}")
                
                if req.get('postData'):
                    print(f"   Data: {req['postData'][:200]}...")
                    
                # Analyser les headers
                important_headers = ['authorization', 'client-id', 'x-device-id', 'user-agent']
                for header in important_headers:
                    if header in req['headers']:
                        print(f"   {header}: {req['headers'][header]}")
        
    def extract_player_javascript(self):
        """Extrait et analyse le code JavaScript du player"""
        print(f"\n=== EXTRACTION CODE PLAYER ===")
        
        try:
            # Récupérer la page principale
            response = requests.get(f"https://www.twitch.tv/{self.channel_name}")
            
            # Chercher les références aux fichiers JS du player
            js_patterns = [
                r'https://player\.twitch\.tv/[^"]+\.js',
                r'https://static\.twitchcdn\.net/[^"]+player[^"]+\.js'
            ]
            
            js_urls = set()
            for pattern in js_patterns:
                matches = re.findall(pattern, response.text)
                js_urls.update(matches)
            
            print(f"Fichiers JS du player trouvés: {len(js_urls)}")
            
            # Analyser chaque fichier
            for url in js_urls:
                self.analyze_player_js(url)
                
        except Exception as e:
            print(f"Erreur extraction JS: {e}")
            
    def analyze_player_js(self, js_url):
        """Analyse un fichier JavaScript du player"""
        try:
            response = requests.get(js_url)
            js_content = response.text
            
            # Rechercher des patterns spécifiques
            search_patterns = [
                r'viewer.*count',
                r'heartbeat.*\w+',
                r'analytics?.*send',
                r'telemetry.*\w+',
                r'websocket.*connect',
                r'api\.twitch\.tv[^"\']+',
                r'gql\.twitch\.tv[^"\']+',
                r'pubsub[^"\']*'
            ]
            
            findings = []
            for pattern in search_patterns:
                matches = re.findall(pattern, js_content, re.IGNORECASE)
                if matches:
                    findings.extend(matches)
            
            if findings:
                print(f"\n📁 {js_url}")
                for finding in findings[:10]:  # Limiter à 10 résultats
                    print(f"   {finding}")
                    
        except Exception as e:
            print(f"Erreur analyse {js_url}: {e}")
            
    def run_full_analysis(self):
        """Lance l'analyse complète"""
        print(f"=== ANALYSE COMPLÈTE DU PLAYER TWITCH ===")
        print(f"Channel: {self.channel_name}")
        
        # 1. Analyser le trafic réseau
        self.analyze_player_traffic(duration_minutes=2)
        
        # 2. Extraire et analyser le code JS
        self.extract_player_javascript()
        
        # 3. Sauvegarder les résultats
        self.save_results()
        
    def save_results(self):
        """Sauvegarde les résultats de l'analyse"""
        results = {
            'channel': self.channel_name,
            'timestamp': time.time(),
            'captured_requests': self.captured_requests,
            'analysis_summary': self.generate_summary()
        }
        
        filename = f'twitch_player_analysis_{self.channel_name}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\n📄 Résultats sauvés dans: {filename}")
        
    def generate_summary(self):
        """Génère un résumé de l'analyse"""
        domains = set()
        tracking_urls = []
        
        for req in self.captured_requests:
            domain = re.search(r'https?://([^/]+)', req['url'])
            if domain:
                domains.add(domain.group(1))
                
            if any(keyword in req['url'].lower() for keyword in ['viewer', 'heartbeat', 'analytics']):
                tracking_urls.append(req['url'])
        
        return {
            'total_requests': len(self.captured_requests),
            'unique_domains': list(domains),
            'potential_tracking_urls': tracking_urls
        }

# Utilisation
if __name__ == "__main__":
    analyzer = TwitchPlayerAnalyzer("m_noko12")
    analyzer.run_full_analysis()