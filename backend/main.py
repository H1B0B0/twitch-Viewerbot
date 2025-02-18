from flask import Flask, send_from_directory, current_app, send_file, request, redirect, abort
from flask_cors import CORS
from functools import wraps
import os
import logging
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import webbrowser
from api import api  # Import the API blueprint
from gevent.pywsgi import WSGIServer

# Set urllib3's logger level to WARNING
logging.getLogger("urllib3").setLevel(logging.WARNING)
# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Check for JWT_SECRET in environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    logger.error("JWT_SECRET not found in environment variables")
    raise ValueError("JWT_SECRET must be set in environment variables")

app = Flask(__name__, static_folder='static')
app.config['JWT_SECRET'] = JWT_SECRET

# Simplified CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000", "http://localhost:3001"],
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Set-Cookie"]
         }
     })

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

def verify_token(token):
    try:
        jwt.decode(token, app.config['JWT_SECRET'], algorithms=["HS256"])
        return True
    except jwt.InvalidTokenError as e:
        logger.error(f"Token verification failed: {e}")
        return False

def auth_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        path = request.path
        logger.info(f"Current path: {path}")
        
        # Skip middleware for API routes and static files
        if path.startswith(('/api/', '/_next/', '/static/', '/images/')) or \
           path.endswith(('.js', '.css', '.ico', '.png', '.jpg', '.jpeg', '.gif')):
            return f(*args, **kwargs)
        
        # Define public paths (including their HTML versions)
        public_paths = ['/login', '/register', '/login.html', '/register.html']
        is_public = path in public_paths
        
        # Get token from cookies
        token = request.cookies.get('access_token')
        is_authenticated = token and verify_token(token)
        
        logger.info(f"Auth status: {is_authenticated}")
        
        # Redirect logic
        if not is_public and not is_authenticated:
            logger.info("Redirecting to login")
            return redirect('/login')
            
        if is_public and is_authenticated and path not in ['/api/register', '/api/login']:
            logger.info("Redirecting")
            return redirect('/')
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def serve_login():
    # If you have a login.html in static/
    login_file = os.path.join(app.static_folder, 'login.html')
    if os.path.exists(login_file):
        return send_file(login_file)
    return abort(404)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@auth_middleware  # Optional if you still want to protect routes
def serve_frontend(path):
    # Return the static files from the "static" folder
    if not path:
        path = 'index.html'
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_file(full_path)
    # Fallback to serving index.html
    return send_file(os.path.join(app.static_folder, 'index.html'))

# Ajoutez ces headers à toutes les réponses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Ajoutez cette fonction avant le if __name__ == '__main__':
def open_browser():
    print("Opening browser...")
    webbrowser.open('https://velbots.shop')

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(app.instance_path), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    logger.info(f"Static folder path: {os.path.abspath(app.static_folder)}")
    if not os.path.exists(app.static_folder):
        logger.error(f"Static folder not found: {app.static_folder}")
        exit(1)
    
    # Lancer le navigateur après un court délai
    from threading import Timer
    Timer(1.5, open_browser).start()

    CERT_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.cert')
    KEY_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.key')


    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        https_server = WSGIServer(
            ('0.0.0.0', 443),
            app,
            certfile=CERT_PATH,
            keyfile=KEY_PATH
        )
        logger.info("Starting HTTPS on port 443")
        https_server.serve_forever()
    else:
        logger.warning("SSL certificates not found, running in development mode")
        app.run(debug=True, host='0.0.0.0', port=3001)