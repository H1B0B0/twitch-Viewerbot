from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from threading import Thread

# Update the import to use relative import
from .viewer_bot import ViewerBot

bot_api = Blueprint('bot_api', __name__)
active_bots = {}

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class BotManager:
    def __init__(self):
        self.bot = None
        self.stats = {
            'requests': 0,
            'active_threads': 0,
            'total_proxies': 0,
            'alive_proxies': 0
        }
        self.is_running = False
        self.last_channel = None  # Ajouter cette ligne

    def start_bot(self, channel_name, threads, proxy_file=None, timeout=1000, proxy_type="http"):
        if self.is_running:
            return False
        
        self.bot = ViewerBot(
            nb_of_threads=threads,
            channel_name=channel_name,
            proxy_file=proxy_file,
            proxy_imported=bool(proxy_file),
            timeout=timeout,
            type_of_proxy=proxy_type
        )
        
        def run_bot():
            self.is_running = True
            self.bot.main()
        
        self.bot_thread = Thread(target=run_bot)
        self.bot_thread.daemon = True
        self.bot_thread.start()
        self.last_channel = channel_name  # Sauvegarder le nom du canal
        return True

    def stop_bot(self):
        if self.bot and self.is_running:
            self.bot.stop()
            self.is_running = False
            return True
        return False

    def get_stats(self):
        if self.bot:
            return {
                'requests': self.bot.request_count,
                'active_threads': self.bot.active_threads,
                'total_proxies': len(self.bot.all_proxies),
                'alive_proxies': self.stats['alive_proxies'],
                'is_running': self.is_running,
                'channel_name': self.last_channel,
                'config': {
                    'threads': self.bot.nb_of_threads,
                    'timeout': self.bot.timeout,
                    'proxy_type': self.bot.type_of_proxy,
                }
            }
        return self.stats

bot_manager = BotManager()

@bot_api.route('/start', methods=['POST', 'OPTIONS'])
def start_bot():
    if request.method == 'OPTIONS':
        return '', 204
        
    channel_name = request.form.get('channelName')
    threads = int(request.form.get('threads', 100))
    timeout = int(request.form.get('timeout', 1000))
    proxy_type = request.form.get('proxyType', 'http')
    proxy_file_path = None

    if 'proxyFile' in request.files:
        file = request.files['proxyFile']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            proxy_file_path = filepath

    if not channel_name:
        return jsonify({'error': 'Channel name is required'}), 400

    success = bot_manager.start_bot(
        channel_name=channel_name,
        threads=threads,
        proxy_file=proxy_file_path,
        timeout=timeout,
        proxy_type=proxy_type
    )

    if proxy_file_path and os.path.exists(proxy_file_path):
        os.remove(proxy_file_path)
    
    if success:
        return jsonify({'message': 'Bot started successfully'})
    return jsonify({'error': 'Bot is already running'}), 400

@bot_api.route('/stop', methods=['POST'])
def stop_bot():
    success = bot_manager.stop_bot()
    if success:
        return jsonify({'message': 'Bot stopped successfully'})
    return jsonify({'error': 'No bot is running'}), 400

@bot_api.route('/stats', methods=['GET'])
def get_stats():
    stats = bot_manager.get_stats()
    return jsonify({
        'active_threads': stats['active_threads'],
        'total_proxies': stats['total_proxies'],
        'alive_proxies': stats['alive_proxies'],
        'request_count': stats['requests'],
        'is_running': stats.get('is_running', False),
        'channel_name': stats.get('channel_name', None),
        'config': stats.get('config', {})
    })

@bot_api.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://velbots.shop')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
