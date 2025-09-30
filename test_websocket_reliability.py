import websocket
import json
import time
import threading
import uuid
import tls_client
from datetime import datetime, timezone

def get_channel_id(channel_name):
    """Récupère l'ID du channel"""
    try:
        session = tls_client.Session(client_identifier="chrome_120")
        headers = {'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko', 'Content-Type': 'application/json'}
        graphql_query = {"query": f'query {{user(login:"{channel_name}"){{id}}}}'}
        response = session.post('https://gql.twitch.tv/gql', headers=headers, json=graphql_query)

        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('user', {}).get('id'):
                return data['data']['user']['id']
    except Exception as e:
        print(f"Erreur: {e}")
    return None

class WebSocketReliabilityTest:
    def __init__(self, channel_name, test_duration=300, num_concurrent_connections=10, auto_reconnect=True):
        self.channel_name = channel_name
        self.channel_id = None
        self.test_duration = test_duration
        self.num_concurrent_connections = num_concurrent_connections
        self.auto_reconnect = auto_reconnect
        self.stats = {
            'connexions_tentees': 0,
            'connexions_reussies': 0,
            'subscriptions_reussies': 0,
            'notifications_recues': 0,
            'keepalives_recus': 0,
            'erreurs': [],
            'disconnections': 0,
            'reconnections': 0,
            'temps_connexion_total': 0,
            'debut_test': None,
            'fin_test': None,
            'notifications_par_connexion': {}
        }
        self.connexion_debut = {}
        self.running = True
        self.lock = threading.Lock()

    def test(self):
        """Lance le test de fiabilité agressif avec connexions multiples"""
        print(f"=== Test de fiabilité WebSocket AGRESSIF ===")
        print(f"Channel: {self.channel_name}")
        print(f"Durée: {self.test_duration}s")
        print(f"Connexions simultanées: {self.num_concurrent_connections}")
        print(f"Auto-reconnexion: {'OUI' if self.auto_reconnect else 'NON'}")
        print("=" * 40)

        # Récupérer l'ID du channel
        self.channel_id = get_channel_id(self.channel_name)
        if not self.channel_id:
            print("Impossible de récupérer l'ID du channel")
            return

        print(f"Channel ID: {self.channel_id}\n")

        self.stats['debut_test'] = time.time()

        # Timer pour arrêter le test
        def stop_test():
            time.sleep(self.test_duration)
            self.running = False
            print("\n[TEST] Durée écoulée, arrêt du test...")

        threading.Thread(target=stop_test, daemon=True).start()

        # Lancer plusieurs connexions en parallèle
        threads = []
        for i in range(self.num_concurrent_connections):
            t = threading.Thread(target=self.run_test, args=(i,), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.1)  # Petit délai entre chaque connexion

        # Attendre la fin du test
        for t in threads:
            t.join()

        self.stats['fin_test'] = time.time()

        # Afficher les résultats
        self.print_results()

    def run_test(self, conn_id):
        """Exécute le test WebSocket pour une connexion"""
        messages_log = []

        def on_message(ws, message):
            try:
                parsed = json.loads(message)
                messages_log.append({'timestamp': datetime.now().isoformat(), 'parsed': parsed})

                msg_type = parsed.get('type', 'unknown')

                if msg_type == 'welcome':
                    with self.lock:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Welcome reçu")
                        self.stats['connexions_reussies'] += 1
                        self.connexion_debut[conn_id] = time.time()
                        self.stats['notifications_par_connexion'][conn_id] = 0

                    # S'abonner aux topics
                    topics = [
                        f"video-playback-by-id.{self.channel_id}",
                        f"video-playback.{self.channel_name}"
                    ]

                    for topic in topics:
                        subscribe_msg = {
                            "type": "subscribe",
                            "id": str(uuid.uuid4()),
                            "subscribe": {
                                "id": str(uuid.uuid4()),
                                "type": "pubsub",
                                "pubsub": {"topic": topic}
                            },
                            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                        }
                        ws.send(json.dumps(subscribe_msg))

                elif msg_type == 'subscribeResponse':
                    result = parsed.get('subscribeResponse', {}).get('result')
                    if result == 'ok':
                        with self.lock:
                            self.stats['subscriptions_reussies'] += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Subscription OK")
                    else:
                        error = parsed.get('subscribeResponse', {}).get('error', 'unknown')
                        with self.lock:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Subscription erreur: {error}")
                            self.stats['erreurs'].append(f"Conn #{conn_id} Subscription error: {error}")

                elif msg_type == 'notification':
                    with self.lock:
                        self.stats['notifications_recues'] += 1
                        self.stats['notifications_par_connexion'][conn_id] = self.stats['notifications_par_connexion'].get(conn_id, 0) + 1
                    pubsub_data = json.loads(parsed['notification']['pubsub'])
                    viewers = pubsub_data.get('viewers', 'N/A')
                    if self.stats['notifications_recues'] % 10 == 0:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Notification #{self.stats['notifications_recues']} - Viewers: {viewers}")

                elif msg_type == 'keepalive':
                    with self.lock:
                        self.stats['keepalives_recus'] += 1

            except json.JSONDecodeError:
                with self.lock:
                    self.stats['erreurs'].append(f"Conn #{conn_id} JSON decode error")
            except Exception as e:
                with self.lock:
                    self.stats['erreurs'].append(f"Conn #{conn_id} error: {str(e)}")

        def on_error(ws, error):
            with self.lock:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Erreur WebSocket: {error}")
                self.stats['erreurs'].append(f"Conn #{conn_id}: {str(error)}")

        def on_close(ws, close_status_code, close_msg):
            with self.lock:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Fermée ({close_status_code} - {close_msg})")
                self.stats['disconnections'] += 1

                if conn_id in self.connexion_debut:
                    duree = time.time() - self.connexion_debut[conn_id]
                    self.stats['temps_connexion_total'] += duree

            # Sauvegarder les logs
            with open(f'reliability_test_{self.channel_name}_conn{conn_id}_{int(time.time())}.json', 'w') as f:
                json.dump(messages_log, f, indent=2)

            # Auto-reconnexion si activée et test en cours
            if self.auto_reconnect and self.running:
                time.sleep(2)  # Attendre 2s avant de reconnecter
                with self.lock:
                    self.stats['reconnections'] += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Reconnexion...")
                # Relancer une nouvelle connexion
                self.run_test(conn_id)

        def on_open(ws):
            with self.lock:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Ouverte")
                self.stats['connexions_tentees'] += 1

        ws_url = "wss://hermes.twitch.tv/v1?clientId=kimne78kx3ncx6brgo4mv6wki5h1ko"

        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        try:
            ws.run_forever()
        except KeyboardInterrupt:
            print(f"\n[TEST] Conn #{conn_id}: Arrêt demandé")
        except Exception as e:
            with self.lock:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Conn #{conn_id}: Exception: {e}")
                self.stats['erreurs'].append(f"Conn #{conn_id} run_forever error: {str(e)}")

    def print_results(self):
        """Affiche les résultats du test agressif"""
        print("\n" + "=" * 50)
        print("=== Résultats du test AGRESSIF ===")
        print("=" * 50)

        duree_test = self.stats['fin_test'] - self.stats['debut_test'] if self.stats['fin_test'] else 0

        print(f"\n📊 Configuration:")
        print(f"  - Durée du test: {duree_test:.1f}s")
        print(f"  - Connexions simultanées: {self.num_concurrent_connections}")
        print(f"  - Auto-reconnexion: {'✓' if self.auto_reconnect else '✗'}")

        print(f"\n🔗 Connexions:")
        print(f"  - Tentées: {self.stats['connexions_tentees']}")
        print(f"  - Réussies: {self.stats['connexions_reussies']}")
        print(f"  - Reconnexions: {self.stats['reconnections']}")
        print(f"  - Taux de succès: {self.stats['connexions_reussies']/max(self.stats['connexions_tentees'],1)*100:.1f}%")

        print(f"\n📡 Subscriptions:")
        print(f"  - Réussies: {self.stats['subscriptions_reussies']}/{self.num_concurrent_connections * 2}")
        print(f"  - Taux: {self.stats['subscriptions_reussies']/(self.num_concurrent_connections * 2)*100:.1f}%")

        print(f"\n📨 Messages reçus:")
        print(f"  - Notifications: {self.stats['notifications_recues']}")
        print(f"  - Keepalives: {self.stats['keepalives_recus']}")

        if self.stats['notifications_recues'] > 0 and duree_test > 0:
            freq = duree_test / self.stats['notifications_recues']
            rate = self.stats['notifications_recues'] / duree_test * 60
            print(f"  - Fréquence: 1 notification toutes les {freq:.1f}s")
            print(f"  - Débit: {rate:.1f} notifications/min")

        # Statistiques par connexion
        if self.stats['notifications_par_connexion']:
            print(f"\n📊 Distribution par connexion:")
            for conn_id, count in sorted(self.stats['notifications_par_connexion'].items()):
                print(f"  - Conn #{conn_id}: {count} notifications")

        print(f"\n💪 Stabilité:")
        print(f"  - Disconnections: {self.stats['disconnections']}")
        print(f"  - Temps connexion cumulé: {self.stats['temps_connexion_total']:.1f}s")
        if duree_test > 0 and self.num_concurrent_connections > 0:
            uptime = (self.stats['temps_connexion_total'] / (duree_test * self.num_concurrent_connections)) * 100
            print(f"  - Uptime moyen: {uptime:.1f}%")

        if self.stats['erreurs']:
            print(f"\n❌ Erreurs ({len(self.stats['erreurs'])}):")
            for err in self.stats['erreurs'][:10]:
                print(f"  - {err}")
            if len(self.stats['erreurs']) > 10:
                print(f"  ... et {len(self.stats['erreurs']) - 10} autres")

        # Évaluation finale
        print("\n" + "=" * 50)
        success_rate = self.stats['connexions_reussies'] / max(self.stats['connexions_tentees'], 1)
        sub_rate = self.stats['subscriptions_reussies'] / max(self.num_concurrent_connections * 2, 1)

        if (success_rate >= 0.9 and
            sub_rate >= 0.9 and
            self.stats['notifications_recues'] > 100):
            print("✓✓✓ Test EXCELLENT - Système très robuste sous charge")
        elif (success_rate >= 0.7 and
              sub_rate >= 0.7 and
              self.stats['notifications_recues'] > 50):
            print("✓✓ Test RÉUSSI - Système stable sous charge")
        elif self.stats['notifications_recues'] > 10:
            print("✓ Test ACCEPTABLE - Quelques problèmes sous charge")
        else:
            print("✗ Test ÉCHOUÉ - Système instable sous charge")
        print("=" * 50)

if __name__ == "__main__":
    # Test agressif : 10 connexions simultanées pendant 5 minutes avec auto-reconnexion
    test = WebSocketReliabilityTest(
        channel_name="m_noko12",
        test_duration=300,  # 5 minutes
        num_concurrent_connections=10,  # 10 connexions simultanées
        auto_reconnect=True  # Reconnexion automatique en cas de déconnexion
    )
    test.test()
