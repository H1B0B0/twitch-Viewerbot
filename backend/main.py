from flask import Flask, send_file, request, redirect, abort
from flask_cors import CORS
from functools import wraps
import os
import sys
import logging
import jwt
from dotenv import load_dotenv
import webbrowser
from api import api
from gevent.pywsgi import WSGIServer

def get_env_path():
    """Get the correct path for .env file in both dev and PyInstaller environments"""
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        bundle_dir = sys._MEIPASS
        return os.path.join(bundle_dir, '.env')
    else:
        # Running in normal Python environment
        return os.path.join(os.path.dirname(__file__), '.env')

# Modify logging configuration
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle (production)
    logging.getLogger().setLevel(logging.CRITICAL)  # Only show errors
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("werkzeug").setLevel(logging.CRITICAL)  # Disable Flask debug logs
else:
    # Running in development mode
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = get_env_path()
load_dotenv(env_path)

# Check for JWT_SECRET in environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    logger.error(f"JWT_SECRET not found in environment variables. Env path: {env_path}")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            logger.info(f"Env file contents: {f.read()}")
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

        # Make /login and /register public, even with query params
        if path.startswith('/login') or path.startswith('/register'):
            return f(*args, **kwargs)

        # Get token
        token = request.cookies.get('access_token')
        is_authenticated = token and verify_token(token)

        if not is_authenticated:
            logger.info("Redirecting to login - not authenticated")
            return redirect('/login')

        if is_authenticated and (path == '/login' or path == '/login.html'):
            logger.info("Redirecting authenticated user from login to home")
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

@app.route('/register')
def serve_register():
    # If you have a register.html in static/
    register_file = os.path.join(app.static_folder, 'register.html')
    if os.path.exists(register_file):
        return send_file(register_file)
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

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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
    
    from threading import Timer
    Timer(1.5, open_browser).start()

    CERT_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.cert')
    KEY_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.key')


    if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
        https_server = WSGIServer(
            ('0.0.0.0', 443),
            app,
            certfile=CERT_PATH,
            keyfile=KEY_PATH,
            log=None  # Disable WSGIServer logs in production
        )
        logger.info("Starting HTTPS on port 443")
        https_server.serve_forever()
    else:
        logger.warning("SSL certificates not found, running in development mode")
        if getattr(sys, 'frozen', False):
            # Production mode
            app.run(debug=False, host='0.0.0.0', port=3001)
        else:
            # Development mode
            app.run(debug=True, host='0.0.0.0', port=3001)