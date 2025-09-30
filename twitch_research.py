# ============================================================================
# SCRIPT 1: WebSocket Message Interceptor
# Capture et analyse tous les messages WebSocket de Twitch
# ============================================================================

import websocket
import json
import time
import threading
from datetime import datetime

class TwitchWebSocketInterceptor:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.messages_log = []
        self.ws = None
        
    def on_message(self, ws, message):
        timestamp = datetime.now().isoformat()
        try:
            parsed = json.loads(message)
            self.messages_log.append({
                'timestamp': timestamp,
                'raw': message,
                'parsed': parsed,
                'type': parsed.get('type', 'unknown')
            })
            print(f"[{timestamp}] Type: {parsed.get('type', 'unknown')}")
            print(f"Message: {message[:200]}...")
            print("-" * 50)
        except json.JSONDecodeError:
            print(f"[{timestamp}] Non-JSON message: {message}")
            
    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")
        
    def on_open(self, ws):
        print("WebSocket connection opened")
        
    def start_monitoring(self):
        """Lance l'interception des messages WebSocket"""
        # URL observée dans tes DevTools
        ws_url = "wss://hermes.twitch.tv/v1?clientId=kimne78kx3ncx6brgo4mv6wki5h1ko"
        
        self.ws = websocket.WebSocketApp(ws_url,
                                       on_open=self.on_open,
                                       on_message=self.on_message,
                                       on_error=self.on_error,
                                       on_close=self.on_close)
        
        # Headers observés
        self.ws.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://www.twitch.tv'
        }
        
        self.ws.run_forever()
        
    def save_logs(self, filename):
        """Sauvegarde les logs pour analyse"""
        with open(filename, 'w') as f:
            json.dump(self.messages_log, f, indent=2)
        print(f"Logs sauvegardés dans {filename}")

# ============================================================================
# SCRIPT 2: Topic Discovery Tool
# Teste différents topics de subscription
# ============================================================================

import uuid
import requests

class TwitchTopicTester:
    def __init__(self, channel_name, channel_id):
        self.channel_name = channel_name
        self.channel_id = channel_id
        
    def test_subscription_topics(self):
        """Teste différents topics possibles"""
        possible_topics = [
            f"viewcount.{self.channel_id}",
            f"video-playback-by-id.{self.channel_id}",
            f"broadcast-settings-update.{self.channel_id}",
            f"channel-bits-events-v2.{self.channel_id}",
            f"following.{self.channel_id}",
            f"presence.{self.channel_id}",
            f"viewer-heartbeat.{self.channel_id}",
            f"stream-state.{self.channel_id}",
            f"live-status.{self.channel_id}"
        ]
        
        for topic in possible_topics:
            print(f"Testing topic: {topic}")
            success = self.test_single_topic(topic)
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
            print("-" * 50)
            time.sleep(2)  # Éviter le rate limiting
            
    def test_single_topic(self, topic):
        """Teste un topic spécifique"""
        try:
            ws_url = "wss://hermes.twitch.tv/v1?clientId=kimne78kx3ncx6brgo4mv6wki5h1ko"
            
            def on_message(ws, message):
                print(f"Response for {topic}: {message}")
                return True
                
            def on_error(ws, error):
                print(f"Error for {topic}: {error}")
                return False
                
            ws = websocket.WebSocketApp(ws_url,
                                      on_message=on_message,
                                      on_error=on_error)
            
            def send_subscription():
                time.sleep(1)  # Attendre la connexion
                subscribe_msg = {
                    "type": "subscribe",
                    "id": str(uuid.uuid4()),
                    "subscribe": {
                        "id": str(uuid.uuid4()),
                        "type": "pubsub",
                        "pubsub": {
                            "topic": topic
                        }
                    },
                    "timestamp": datetime.now().isoformat() + "Z"
                }
                ws.send(json.dumps(subscribe_msg))
                time.sleep(5)  # Attendre la réponse
                ws.close()
            
            # Lancer la subscription dans un thread
            threading.Thread(target=send_subscription, daemon=True).start()
            ws.run_forever()
            return True
            
        except Exception as e:
            print(f"Exception testing {topic}: {e}")
            return False

# ============================================================================
# SCRIPT 3: Authentication Token Analyzer  
# Analyse les tokens et headers nécessaires
# ============================================================================

try:
    import tls_client
    HAS_TLS_CLIENT = True
except ImportError:
    HAS_TLS_CLIENT = False

class TwitchAuthAnalyzer:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        
    def analyze_required_auth(self):
        """Analyse l'authentification requise pour Twitch"""
        print("=== ANALYSE D'AUTHENTIFICATION TWITCH ===")
        
        # Test 1: Récupération de tokens depuis différents endpoints
        self.test_token_endpoints()
        
        # Test 2: Analyse des cookies de session
        self.analyze_session_cookies()
        
        # Test 3: Test des headers requis
        self.test_required_headers()
        
    def test_token_endpoints(self):
        """Teste différents endpoints pour récupérer des tokens"""
        print("\n1. TEST DES ENDPOINTS DE TOKENS")
        
        endpoints = [
            "https://api.twitch.tv/helix/users",
            "https://gql.twitch.tv/gql", 
            "https://www.twitch.tv/api/viewer/token",
            "https://passport.twitch.tv/userinfo",
            f"https://www.twitch.tv/{self.channel_name}"
        ]
        
        headers = {
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if HAS_TLS_CLIENT:
            session = tls_client.Session(client_identifier="chrome_120")
            session.headers.update(headers)
            client_type = "tls_client"
        else:
            session = requests.Session()
            session.headers.update(headers)
            client_type = "requests"
            
        print(f"Utilisation de: {client_type}")
        
        for endpoint in endpoints:
            try:
                print(f"\nTesting: {endpoint}")
                response = session.get(endpoint, timeout=10)
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
                # Chercher des tokens dans la réponse
                if 'token' in response.text.lower():
                    print("⚠️  Token trouvé dans la réponse!")
                    
                if 'auth' in response.text.lower():
                    print("⚠️  Auth trouvé dans la réponse!")
                    
            except Exception as e:
                print(f"Erreur: {e}")
                
    def analyze_session_cookies(self):
        """Analyse les cookies de session requis"""
        print("\n2. ANALYSE DES COOKIES DE SESSION")
        
        try:
            if HAS_TLS_CLIENT:
                session = tls_client.Session(client_identifier="chrome_120")
            else:
                session = requests.Session()
                
            # Visiter la page principale
            response = session.get(f"https://www.twitch.tv/{self.channel_name}")
            
            print("Cookies reçus:")
            for cookie in session.cookies:
                print(f"  {cookie.name}: {cookie.value[:50]}...")
                
            # Vérifier les cookies critiques
            critical_cookies = ['auth-token', 'twilight-user', 'persistent', 'api_token']
            for cookie_name in critical_cookies:
                if cookie_name in [c.name for c in session.cookies]:
                    print(f"✅ Cookie critique trouvé: {cookie_name}")
                else:
                    print(f"❌ Cookie critique manquant: {cookie_name}")
                    
        except Exception as e:
            print(f"Erreur analyse cookies: {e}")
            
    def test_required_headers(self):
        """Teste quels headers sont requis"""
        print("\n3. TEST DES HEADERS REQUIS")
        
        base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        optional_headers = {
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'Authorization': 'Bearer test',
            'X-Device-Id': str(uuid.uuid4()),
            'Accept': 'application/json',
            'Origin': 'https://www.twitch.tv',
            'Referer': f'https://www.twitch.tv/{self.channel_name}'
        }
        
        # Test avec headers minimaux
        print("Test avec headers minimaux...")
        self.test_headers_combination(base_headers)
        
        # Test avec tous les headers
        print("Test avec tous les headers...")
        all_headers = {**base_headers, **optional_headers}
        self.test_headers_combination(all_headers)
        
        # Test en retirant un header à la fois
        for header_name in optional_headers:
            test_headers = {**base_headers}
            for k, v in optional_headers.items():
                if k != header_name:
                    test_headers[k] = v
            print(f"Test sans {header_name}...")
            self.test_headers_combination(test_headers)
            
    def test_headers_combination(self, headers):
        """Teste une combinaison de headers"""
        try:
            response = requests.get(f"https://api.twitch.tv/helix/users?login={self.channel_name}", 
                                  headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ Succès")
            else:
                print(f"  ❌ Échec: {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ Erreur: {e}")

# ============================================================================
# SCRIPT 4: Viewer Count Monitor
# Surveille les changements de viewcount en temps réel
# ============================================================================

class ViewerCountMonitor:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.viewer_counts = []
        
    def monitor_viewer_count(self, duration_minutes=10):
        """Surveille le viewcount pendant X minutes"""
        print(f"Monitoring viewer count for {self.channel_name} pendant {duration_minutes} minutes...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            try:
                count = self.get_current_viewer_count()
                timestamp = datetime.now().isoformat()
                
                self.viewer_counts.append({
                    'timestamp': timestamp,
                    'count': count
                })
                
                print(f"[{timestamp}] Viewers: {count}")
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Erreur monitoring: {e}")
                time.sleep(10)
                
        self.analyze_viewer_patterns()
        
    def get_current_viewer_count(self):
        """Récupère le viewcount actuel"""
        try:
            # Méthode 1: API Twitch
            headers = {
                'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(f"https://api.twitch.tv/helix/streams?user_login={self.channel_name}", 
                                  headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    return data['data'][0].get('viewer_count', 0)
            
            # Méthode 2: Scraping de la page
            page_response = requests.get(f"https://www.twitch.tv/{self.channel_name}")
            if page_response.status_code == 200:
                import re
                match = re.search(r'"viewersCount":(\d+)', page_response.text)
                if match:
                    return int(match.group(1))
                    
            return 0
            
        except Exception as e:
            print(f"Erreur récupération viewcount: {e}")
            return 0
            
    def analyze_viewer_patterns(self):
        """Analyse les patterns de viewcount"""
        print("\n=== ANALYSE DES PATTERNS ===")
        
        if len(self.viewer_counts) < 2:
            print("Pas assez de données pour analyser")
            return
            
        # Calculer les variations
        variations = []
        for i in range(1, len(self.viewer_counts)):
            prev_count = self.viewer_counts[i-1]['count']
            curr_count = self.viewer_counts[i]['count']
            variation = curr_count - prev_count
            variations.append(variation)
            
        # Statistiques
        avg_count = sum(vc['count'] for vc in self.viewer_counts) / len(self.viewer_counts)
        max_count = max(vc['count'] for vc in self.viewer_counts)
        min_count = min(vc['count'] for vc in self.viewer_counts)
        
        print(f"Viewcount moyen: {avg_count:.1f}")
        print(f"Viewcount max: {max_count}")
        print(f"Viewcount min: {min_count}")
        print(f"Variation moyenne: {sum(variations)/len(variations):.1f}")
        print(f"Plus grande augmentation: {max(variations)}")
        print(f"Plus grande diminution: {min(variations)}")

# ============================================================================
# SCRIPT D'UTILISATION PRINCIPAL
# ============================================================================

def main():
    channel_name = input("Nom du channel Twitch à analyser: ").strip()
    
    print("\n=== OUTILS D'ANALYSE TWITCH ===")
    print("1. Intercepter les messages WebSocket")
    print("2. Tester les topics de subscription") 
    print("3. Analyser l'authentification")
    print("4. Monitorer le viewcount")
    print("5. Tout exécuter")
    
    choice = input("\nChoisir une option (1-5): ").strip()
    
    if choice == "1":
        interceptor = TwitchWebSocketInterceptor(channel_name)
        print("Démarrage de l'interception... (Ctrl+C pour arrêter)")
        try:
            interceptor.start_monitoring()
        except KeyboardInterrupt:
            interceptor.save_logs(f"twitch_messages_{channel_name}.json")
            
    elif choice == "2":
        channel_id = input("ID du channel (si connu, sinon laisser vide): ").strip()
        if not channel_id:
            print("Récupération de l'ID du channel...")
            # Ici tu peux utiliser ta fonction get_channel_id()
            channel_id = "123456"  # Placeholder
            
        tester = TwitchTopicTester(channel_name, channel_id)
        tester.test_subscription_topics()
        
    elif choice == "3":
        analyzer = TwitchAuthAnalyzer(channel_name)
        analyzer.analyze_required_auth()
        
    elif choice == "4":
        duration = int(input("Durée de monitoring en minutes (défaut: 10): ") or "10")
        monitor = ViewerCountMonitor(channel_name)
        monitor.monitor_viewer_count(duration)
        
    elif choice == "5":
        print("Exécution complète...")
        # Exécuter tous les tests
        analyzer = TwitchAuthAnalyzer(channel_name)
        analyzer.analyze_required_auth()
        
        monitor = ViewerCountMonitor(channel_name)
        monitor.monitor_viewer_count(5)  # 5 minutes
        
if __name__ == "__main__":
    main()