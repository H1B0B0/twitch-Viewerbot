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
import argparse
import platform
import subprocess
import shutil

if platform.system() != "Windows":
    import resource
else:
    resource = None

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

# Parse command line arguments - Do this first!
parser = argparse.ArgumentParser()
parser.add_argument('--dev', action='store_true', help='Run in development mode without authentication')
parser.add_argument('--domain', type=str, help='Domain name for Let\'s Encrypt certificate')
parser.add_argument('--email', type=str, help='Email address for Let\'s Encrypt registration')
parser.add_argument('--renew', action='store_true', help='Force renewal of Let\'s Encrypt certificate')
parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
args = parser.parse_args()

# Load environment variables from .env file
env_path = get_env_path()
load_dotenv(env_path)

# Only check for JWT_SECRET if not in dev mode
JWT_SECRET = None
if not args.dev:
    JWT_SECRET = os.getenv('JWT_SECRET')
    if not JWT_SECRET:
        logger.error(f"JWT_SECRET not found in environment variables. Env path: {env_path}")
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                logger.info(f"Env file contents: {f.read()}")
        raise ValueError("JWT_SECRET must be set in environment variables")
else:
    # In dev mode, use a dummy secret
    JWT_SECRET = 'dev_secret_key'
    logger.warning("Running in development mode - Using dummy JWT secret")

app = Flask(__name__, static_folder='static')
app.config['JWT_SECRET'] = JWT_SECRET

# Simplified CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000", "http://localhost:3001", "https://velbots.shop"],
             "methods": ["GET", "POST", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }
     })

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

def verify_token(token):
    try:
        # Add leeway parameter to handle time differences
        jwt.decode(
            token, 
            app.config['JWT_SECRET'], 
            algorithms=["HS256"],
            leeway=5
        )
        return True
    except jwt.InvalidTokenError as e:
        logger.error(f"Token verification failed: {e}")
        return False

def auth_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication if in dev mode
        if getattr(parser.parse_args(), 'dev', False):
            return f(*args, **kwargs)

        path = request.path
        logger.info(f"Current path: {path}")

        # Liste des ressources statiques à ignorer
        static_resources = [
            'favicon.ico',
            '.js',
            '.css',
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
            '.svg',
            '.woff',
            '.woff2',
            '.ttf',
            '.eot'
        ]
        
        # Vérifier si c'est une ressource statique
        is_static = any(path.endswith(ext) for ext in static_resources) or \
                   path.startswith(('/api/', '/_next/', '/static/', '/images/'))
                   
        if is_static:
            return f(*args, **kwargs)

        # Get token and check authentication
        token = request.cookies.get('access_token')
        is_authenticated = token and verify_token(token)
        logger.info(f"Is authenticated: {is_authenticated}")

        # Si l'utilisateur est authentifié et essaie d'accéder à login/register
        if is_authenticated and path in ['/login', '/register']:
            logger.info("Redirecting authenticated user from login/register to home")
            return redirect('/')

        # Check if path should bypass auth
        is_public_path = path in ['/login', '/register']
        if is_public_path and not is_authenticated:
            return f(*args, **kwargs)

        # If not authenticated and not a public path, redirect to login
        if not is_authenticated:
            logger.info("Redirecting to login - not authenticated")
            return redirect('/login')

        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
@auth_middleware  # Ajouter le middleware ici
def serve_login():
    # If you have a login.html in static/
    login_file = os.path.join(app.static_folder, 'login.html')
    logger.info(f"Login file path: {login_file}")
    if os.path.exists(login_file):
        return send_file(login_file)
    return abort(404)

@app.route('/register')
@auth_middleware  # Ajouter le middleware ici
def serve_register():
    # If you have a register.html in static/
    register_file = os.path.join(app.static_folder, 'register.html')
    logger.info(f"Register file path: {register_file}")
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
    origin = request.headers.get('Origin')
    if origin in ["http://localhost:3000", "http://localhost:3001", "https://velbots.shop"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def setup_lets_encrypt(domain, email, force_renewal=False):
    """
    Set up Let's Encrypt certificates for the domain
    
    Args:
        domain: The domain name to get a certificate for
        email: Email address for registration and recovery
        force_renewal: Whether to force certificate renewal
    
    Returns:
        Tuple of (cert_path, key_path) or None if failed
    """
    if not domain:
        logger.error("Domain name is required for Let's Encrypt")
        return None
        
    if not email:
        logger.error("Email address is required for Let's Encrypt")
        return None
    
    certs_dir = os.path.join(os.path.dirname(__file__), 'certs')
    os.makedirs(certs_dir, exist_ok=True)
    
    cert_path = os.path.join(certs_dir, f'{domain}.cert')
    key_path = os.path.join(certs_dir, f'{domain}.key')
    
    # Check if certificates already exist and not forcing renewal
    if os.path.exists(cert_path) and os.path.exists(key_path) and not force_renewal:
        logger.info(f"Using existing certificates for {domain}")
        return (cert_path, key_path)
    
    logger.info(f"Obtaining Let's Encrypt certificate for {domain}")
    
    # First, check if the domain is resolvable
    try:
        import socket
        socket.gethostbyname(domain)
        logger.info(f"Domain {domain} is resolvable")
    except Exception as e:
        logger.error(f"Domain {domain} is not resolvable: {e}")
        logger.error("Make sure your domain points to this server's IP address")
        return None
    
    # Create temporary directory for certbot with absolute paths
    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'temp_certbot'))
    os.makedirs(temp_dir, exist_ok=True)
    
    # Check if port 80 is available for validation
    try:
        import socket
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('0.0.0.0', 80))
        test_socket.close()
        logger.info("Port 80 is available for Let's Encrypt validation")
        port_available = True
    except Exception as e:
        logger.warning(f"Port 80 is not available: {e}")
        logger.warning("Will try to stop any service using port 80 during certificate issuance")
        port_available = False
    
    # Start a temporary web server to handle ACME challenges if needed
    http_server = None
    original_port_80_state = None
    
    try:
        # Check if certbot is available first
        try:
            version_result = subprocess.run(['certbot', '--version'], 
                                           capture_output=True, text=True, timeout=5)
            if version_result.returncode != 0:
                logger.error(f"Certbot not properly installed: {version_result.stderr}")
                return None
            logger.info(f"Certbot version: {version_result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Certbot command failed or not found: {e}")
            return None
            
        if not port_available:
            # Try to temporarily stop services on port 80
            logger.info("Attempting to free port 80 for Let's Encrypt validation")
            try:
                if platform.system() != "Windows":
                    # On Linux/Unix, try to find and stop the process using port 80
                    find_process = subprocess.run(
                        "lsof -i :80 | awk 'NR>1 {print $2}'", 
                        shell=True, capture_output=True, text=True)
                    process_ids = find_process.stdout.strip().split('\n')
                    
                    if process_ids and process_ids[0]:
                        logger.info(f"Found processes using port 80: {process_ids}")
                        original_port_80_state = process_ids
                        for pid in process_ids:
                            if pid:
                                try:
                                    subprocess.run(['kill', '-9', pid], check=True)
                                    logger.info(f"Temporarily stopped process {pid} using port 80")
                                except subprocess.SubprocessError as e:
                                    logger.error(f"Failed to stop process {pid}: {e}")
                else:
                    # On Windows, this is more complex - we'll just warn the user
                    logger.warning("On Windows, please manually ensure port 80 is free for Let's Encrypt validation")
            except Exception as e:
                logger.error(f"Failed to free port 80: {e}")
            
            # Double-check if port is now available
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(('0.0.0.0', 80))
                test_socket.close()
                logger.info("Successfully freed port 80 for validation")
                port_available = True
            except Exception as e:
                logger.warning(f"Port 80 is still not available: {e}")
                logger.warning("Will attempt to get certificate anyway")
            
        # Use certbot to obtain a certificate
        cmd = [
            'certbot', 'certonly', '--standalone',
            '--preferred-challenges', 'http',
            '--agree-tos',
            '--email', email,
            '-d', domain,
            '--non-interactive',
            '--config-dir', temp_dir,
            '--work-dir', temp_dir,
            '--logs-dir', temp_dir
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Try running certbot with more detailed debugging and timeout
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                logger.error(f"Failed to obtain certificate: {result.stderr}")
                
                # Try to gather more debug information
                logger.info("Running certbot with debug options...")
                debug_cmd = cmd + ['--debug']
                debug_result = subprocess.run(debug_cmd, capture_output=True, text=True, timeout=180)
                logger.info(f"Debug output: {debug_result.stdout}")
                
                # Check the log file if possible
                log_path = os.path.join(temp_dir, 'letsencrypt.log')
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        log_contents = f.read()
                        logger.info(f"Log file contents: {log_contents}")
                
                return None
                
            # Copy the certificates to our certs directory
            live_dir = os.path.join(temp_dir, 'live', domain)
            
            if not os.path.exists(live_dir):
                logger.error(f"Expected certificate directory not found: {live_dir}")
                # Try to find where certificates were actually created
                for root, dirs, files in os.walk(temp_dir):
                    if 'fullchain.pem' in files and 'privkey.pem' in files:
                        logger.info(f"Found certificates in unexpected location: {root}")
                        live_dir = root
                        break
                else:
                    return None
                    
            # Now copy files if we have a valid live_dir
            cert_file = os.path.join(live_dir, 'fullchain.pem')
            key_file = os.path.join(live_dir, 'privkey.pem')
            
            if os.path.exists(cert_file) and os.path.exists(key_file):
                shutil.copy(cert_file, cert_path)
                shutil.copy(key_file, key_path)
                logger.info(f"Successfully obtained certificates for {domain}")
                return (cert_path, key_path)
            else:
                logger.error(f"Certificate files not found in expected location")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Certbot command timed out after 180 seconds")
            return None
    
    except Exception as e:
        logger.error(f"Error setting up Let's Encrypt: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        # Restore original state of port 80 if we stopped any services
        if original_port_80_state:
            logger.info("Restoring original services that were using port 80")
            # This part is complex and depends on your system
            # For simplicity, we'll just log that manual intervention may be needed
            logger.info("You may need to manually restart services that were using port 80")
            
        # Clean up temporary directory but save logs if there was an error
        try:
            log_path = os.path.join(temp_dir, 'letsencrypt.log')
            if os.path.exists(log_path):
                log_backup = os.path.join(os.path.dirname(__file__), 'certbot_error.log')
                shutil.copy(log_path, log_backup)
                logger.info(f"Saved certbot logs to {log_backup}")
        except Exception as e:
            logger.error(f"Error saving certbot logs: {e}")
            
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {e}")

def open_browser():
    if args.no_browser:
        return
    
    print("Opening browser...")
    url = f"https://{args.domain}" if args.domain else "https://velbots.shop"
    webbrowser.open(url)

def set_resource_limits():
    # Vérifier si le module resource est disponible (systèmes Unix/Linux/macOS)
    if resource:
        # Increase the soft limit for number of open files
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(4096, hard), hard))
    else:
        # Sur Windows, cette fonction ne fait rien
        logger.info("Resource limits adjustment not supported on Windows")

if __name__ == '__main__':
    set_resource_limits()
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(app.instance_path), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    logger.info(f"Static folder path: {os.path.abspath(app.static_folder)}")
    if not os.path.exists(app.static_folder):
        logger.error(f"Static folder not found: {app.static_folder}")
        exit(1)

    if args.dev:
        logger.warning("Running in development mode - Authentication disabled")
    
    from threading import Timer
    Timer(1.5, open_browser).start()

    # Try Let's Encrypt if domain is provided
    lets_encrypt_certs = None
    if args.domain:
        logger.info(f"Attempting to set up Let's Encrypt for domain: {args.domain}")
        lets_encrypt_certs = setup_lets_encrypt(args.domain, args.email, args.renew)
        if lets_encrypt_certs:
            logger.info(f"Using Let's Encrypt certificates for {args.domain}")
            CERT_PATH, KEY_PATH = lets_encrypt_certs
        else:
            logger.warning("Let's Encrypt setup failed, falling back to local certificates")

    if not lets_encrypt_certs:
        # Use local certificates as fallback
        CERT_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.cert')
        KEY_PATH = os.path.join(os.path.dirname(__file__), 'certs', 'velbots.shop.key')
        
        if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
            logger.warning("Local certificates not found, will fall back to HTTP mode")

    try:
        if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
            # Try to start HTTPS server
            logger.info("Starting HTTPS on port 443")
            try:
                https_server = WSGIServer(
                    ('0.0.0.0', 443),
                    app,
                    certfile=CERT_PATH,
                    keyfile=KEY_PATH,
                    log=None  # Disable WSGIServer logs in production
                )
                logger.info("HTTPS server created successfully, starting server...")
                https_server.serve_forever()
            except Exception as e:
                logger.error(f"Failed to start HTTPS server: {e}")
                logger.warning("Falling back to unsecure HTTP mode")
                raise  # Re-raise to fall back to HTTP mode
        else:
            logger.warning("SSL certificates not found, falling back to HTTP mode")
            raise FileNotFoundError("SSL certificates not available")
            
    except Exception as e:
        # Fallback to HTTP mode if HTTPS fails
        logger.warning(f"⚠️ RUNNING IN UNSECURE MODE (HTTP) ⚠️ - Reason: {str(e)}")
        logger.warning("Your connection is not encrypted and may not be secure.")
        
        # Decide which port to use
        http_port = 80 if not getattr(sys, 'frozen', False) and not args.dev else 3001
        
        if http_port == 80:
            logger.info(f"Starting HTTP server on port {http_port}")
            http_server = WSGIServer(('0.0.0.0', http_port), app, log=None)
            http_server.serve_forever()
        else:
            # Use Flask's built-in server for development
            logger.info(f"Starting development HTTP server on port {http_port}")
            app.run(debug=not getattr(sys, 'frozen', False), host='0.0.0.0', port=http_port)