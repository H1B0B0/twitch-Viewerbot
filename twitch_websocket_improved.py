import websocket
import json
import time
import threading
import uuid
import tls_client
from datetime import datetime, timezone

def get_channel_id(channel_name):
    """Récupère l'ID du channel à partir de son nom avec tls_client"""
    try:
        session = tls_client.Session(client_identifier="chrome_120")

        # Méthode 1: GraphQL API
        headers = {
            'Client-ID': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'Content-Type': 'application/json'
        }

        graphql_query = {
            "query": f"query {{user(login:\"{channel_name}\"){{id}}}}"
        }

        response = session.post(
            'https://gql.twitch.tv/gql',
            headers=headers,
            json=graphql_query
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('data', {}).get('user', {}).get('id'):
                channel_id = data['data']['user']['id']
                print(f"Channel ID trouvé via GraphQL: {channel_id}")
                return channel_id

        # Méthode 2: Scraping de la page
        print("GraphQL échoué, essai via scraping...")
        response = session.get(f'https://www.twitch.tv/{channel_name}')

        if response.status_code == 200:
            import re
            match = re.search(r'"channelID":"(\d+)"', response.text)
            if match:
                channel_id = match.group(1)
                print(f"Channel ID trouvé via scraping: {channel_id}")
                return channel_id

        print(f"Impossible de trouver l'ID du channel")
    except Exception as e:
        print(f"Erreur récupération channel ID: {e}")

    return None

def test_ping_format(channel_name):
    messages_log = []

    # Récupérer l'ID du channel
    channel_id = get_channel_id(channel_name)
    if not channel_id:
        print(f"Impossible de récupérer l'ID pour {channel_name}")
        return

    print(f"Channel ID: {channel_id}")

    def on_message(ws, message):
        timestamp = datetime.now().isoformat()
        try:
            parsed = json.loads(message)
            messages_log.append({'timestamp': timestamp, 'raw': message, 'parsed': parsed})
            print(f"[{timestamp}] Type: {parsed.get('type', 'unknown')}")
            print(f"Message: {message}")
            print("-" * 80)
            
            if parsed.get('type') == 'welcome':
                print("Welcome recu - Envoi subscription au format ViewerBot...")

                # Topics qui fonctionnent (sans auth)
                working_topics = [
                    f"video-playback-by-id.{channel_id}",
                    f"video-playback.{channel_name}"
                ]

                for topic in working_topics:
                    subscribe_message = {
                        "type": "subscribe",
                        "id": str(uuid.uuid4()),
                        "subscribe": {
                            "id": str(uuid.uuid4()),
                            "type": "pubsub",
                            "pubsub": {
                                "topic": topic
                            }
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
                    }

                    ws.send(json.dumps(subscribe_message))
                    print(f"Subscribe envoye pour topic: {topic}")
                    time.sleep(0.5)

                print("Souscriptions terminées - En attente de notifications...")
                # Pas besoin d'envoyer de keepalive client, le serveur s'en charge

        except json.JSONDecodeError:
            print(f"[{timestamp}] Non-JSON: {message}")

    def on_error(ws, error):
        print(f"WebSocket error: {error}")
        
    def on_close(ws, close_status_code, close_msg):
        print(f"Connexion fermee: {close_status_code} - {close_msg}")
        
        with open(f'viewbot_test_{channel_name}.json', 'w') as f:
            json.dump(messages_log, f, indent=2)
        print("Logs sauves")
        
    def on_open(ws):
        print("WebSocket ouvert - En attente du welcome...")
        
    ws_url = "wss://hermes.twitch.tv/v1?clientId=kimne78kx3ncx6brgo4mv6wki5h1ko"
    
    ws = websocket.WebSocketApp(ws_url,
                               on_open=on_open,
                               on_message=on_message,
                               on_error=on_error,
                               on_close=on_close)
    
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("Arret demande")
        ws.close()

test_ping_format("mexic_original")