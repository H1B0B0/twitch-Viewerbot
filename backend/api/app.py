from flask import Blueprint

health_api = Blueprint('health_api', __name__)

@health_api.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok'}, 200

# Dans votre app.py principal, ajoutez:
# app.register_blueprint(health_api, url_prefix='/health')
