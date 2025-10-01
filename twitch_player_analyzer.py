import requests
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging
import sys

class TwitchPlayerAnalyzer:
    def __init__(self, channel_name, log_file='twitch_analysis_detailed.log'):
        self.channel_name = channel_name
        self.captured_requests = []
        self.player_sources = []
        self.request_id_map = {}  # Pour mapper request_id aux données
        self.log_file = open(log_file, 'w', encoding='utf-8')

    def log(self, message):
        """Log vers fichier et console"""
        # Remplacer les emojis problématiques pour la console Windows
        safe_message = message.encode('ascii', errors='ignore').decode('ascii')
        if safe_message.strip():  # Si il reste du texte après suppression des emojis
            print(safe_message)
        # Garder les emojis dans le fichier
        self.log_file.write(message + '\n')
        self.log_file.flush()
        
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
        self.log(f"Démarrage analyse trafic player pour {self.channel_name}")

        driver = self.setup_selenium()

        try:
            # Aller sur la page Twitch
            driver.get(f"https://www.twitch.tv/{self.channel_name}")

            # Attendre le chargement
            time.sleep(5)

            # Capturer le trafic pendant la durée spécifiée
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)

            self.log(f"Capture du trafic pendant {duration_minutes} minutes...")
            
            while time.time() < end_time:
                # Récupérer les logs réseau
                logs = driver.get_log('performance')

                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        method = message['message']['method']

                        if method in ['Network.requestWillBeSent', 'Network.responseReceived', 'Network.loadingFinished']:
                            self.process_network_event(message['message'], driver)

                    except Exception as e:
                        continue

                time.sleep(1)
                
        finally:
            driver.quit()
            
        # Analyser les résultats
        self.analyze_captured_requests()
        
    def process_network_event(self, event, driver):
        """Traite un événement réseau capturé"""
        method = event['method']
        params = event['params']

        if method == 'Network.requestWillBeSent':
            request = params['request']
            request_id = params['requestId']
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
                'telemetry',
                'integrity'
            ]

            if any(pattern in url for pattern in interesting_patterns):
                self.request_id_map[request_id] = {
                    'timestamp': time.time(),
                    'url': url,
                    'method': request.get('method', 'GET'),
                    'headers': request.get('headers', {}),
                    'postData': request.get('postData', ''),
                    'response_body': None
                }

                self.log(f"\n{'='*80}")
                self.log(f"🔵 REQUÊTE: {request['method']} {url}")

                # Afficher les headers importants
                important_headers = ['authorization', 'client-id', 'x-device-id', 'device-id', 'user-agent']
                for header_name in important_headers:
                    header_value = request.get('headers', {}).get(header_name)
                    if header_value:
                        self.log(f"   📋 {header_name}: {header_value[:100]}...")

                # Afficher le body pour les POST
                if request.get('postData'):
                    self.log(f"\n   📤 REQUEST BODY:")
                    try:
                        body_json = json.loads(request['postData'])
                        self.log(json.dumps(body_json, indent=6, ensure_ascii=False))
                    except:
                        self.log(f"   {request['postData'][:500]}...")

        elif method == 'Network.responseReceived':
            request_id = params['requestId']
            response = params['response']

            if request_id in self.request_id_map:
                self.request_id_map[request_id]['response_headers'] = response.get('headers', {})
                self.request_id_map[request_id]['status'] = response.get('status')

        elif method == 'Network.loadingFinished':
            request_id = params['requestId']

            if request_id in self.request_id_map:
                try:
                    # Récupérer le body de la réponse
                    response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    body = response_body.get('body', '')

                    self.request_id_map[request_id]['response_body'] = body

                    # Afficher la réponse
                    if body:
                        self.log(f"\n   📥 RESPONSE BODY:")
                        try:
                            body_json = json.loads(body)
                            self.log(json.dumps(body_json, indent=6, ensure_ascii=False))
                        except:
                            self.log(f"   {body[:500]}...")

                    # Ajouter à captured_requests
                    self.captured_requests.append(self.request_id_map[request_id])

                except Exception as e:
                    # Certaines requêtes n'ont pas de body accessible
                    pass
                
    def analyze_captured_requests(self):
        """Analyse les requêtes capturées pour identifier les patterns"""
        self.log(f"\n=== ANALYSE DE {len(self.captured_requests)} REQUÊTES ===")

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
            self.log(f"\n--- {domain} ({len(requests)} requêtes) ---")

            # Patterns d'URLs uniques
            url_patterns = set()
            for req in requests:
                # Simplifier l'URL pour voir les patterns
                simplified = re.sub(r'\d+', '{ID}', req['url'])
                simplified = re.sub(r'[a-f0-9]{8,}', '{HASH}', simplified)
                url_patterns.add(simplified)

            for pattern in sorted(url_patterns):
                self.log(f"  Pattern: {pattern}")

        # Chercher des endpoints de viewer tracking
        self.find_viewer_tracking_endpoints()
        
    def find_viewer_tracking_endpoints(self):
        """Recherche spécifiquement les endpoints de tracking des viewers"""
        self.log(f"\n=== ENDPOINTS DE TRACKING POTENTIELS ===")

        tracking_keywords = ['viewer', 'view', 'watch', 'heartbeat', 'ping', 'analytics', 'telemetry', 'segment']

        for req in self.captured_requests:
            url_lower = req['url'].lower()

            if any(keyword in url_lower for keyword in tracking_keywords):
                self.log(f"\n🎯 ENDPOINT INTÉRESSANT:")
                self.log(f"   URL: {req['url']}")
                self.log(f"   Méthode: {req['method']}")

                if req.get('postData'):
                    self.log(f"   Data: {req['postData'][:200]}...")

                # Analyser les headers
                important_headers = ['authorization', 'client-id', 'x-device-id', 'user-agent']
                for header in important_headers:
                    if header in req['headers']:
                        self.log(f"   {header}: {req['headers'][header]}")
        
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
        self.log(f"=== ANALYSE COMPLÈTE DU PLAYER TWITCH ===")
        self.log(f"Channel: {self.channel_name}")

        # 1. Analyser le trafic réseau (30 secondes suffisent pour capturer les requêtes initiales)
        self.analyze_player_traffic(duration_minutes=0.5)

        # 2. Sauvegarder les résultats
        self.save_results()

        # 3. Fermer le fichier de log
        self.log_file.close()

    def save_results(self):
        """Sauvegarde les résultats de l'analyse"""
        results = {
            'channel': self.channel_name,
            'timestamp': time.time(),
            'captured_requests': self.captured_requests,
            'analysis_summary': self.generate_summary()
        }

        filename = f'twitch_player_analysis_{self.channel_name}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.log(f"\n📄 Résultats sauvés dans: {filename}")
        
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
    analyzer = TwitchPlayerAnalyzer("neko_chad_")
    analyzer.run_full_analysis()