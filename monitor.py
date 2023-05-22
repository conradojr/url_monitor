import requests
import hashlib
import os
from datetime import datetime
import time
import logging
from tabulate import tabulate

# Configuração do logger
logging.basicConfig(filename='monitor.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def get_url_content(url, proxies=None, auth=None):
    try:
        response = requests.get(url, proxies=proxies, auth=auth)
        return response.content
    except requests.exceptions.RequestException:
        return None

def get_hash(data):
    hash_object = hashlib.sha256()
    hash_object.update(data)
    return hash_object.hexdigest()

def check_status_and_content(url, previous_status, previous_content_hash, proxies=None, auth=None):
    content = get_url_content(url, proxies=proxies, auth=auth)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if content is not None:
        current_status = 200
        current_content_hash = get_hash(content)
        if current_status != previous_status:
            status_changed = "Yes"
        else:
            status_changed = "No"
            
        logging.info(f"{url}: Status: {current_status}, Hash: {current_content_hash}, Status Changed: {status_changed}")
        return current_time, current_status, current_content_hash, status_changed
    else:
        current_status = -1
        current_content_hash = ""
        logging.warning(f"{url}: Connection error")
        return current_time, current_status, current_content_hash, ""

def check_file_modification(urls_history):
    urls_file = "urls.txt"

    if not os.path.exists(urls_file):
        return False

    with open(urls_file, "r") as file:
        urls_in_file = file.read().splitlines()

    if urls_history == urls_in_file:
        return False

    return True

def monitor(interval, proxy_enabled=False, proxy_host=None, proxy_port=None, proxy_username=None, proxy_password=None):
    urls_file = "urls.txt"
    urls_history = []

    proxies = None
    auth = None

    if proxy_enabled and proxy_host and proxy_port:
        proxies = {
            'http': f'http://{proxy_host}:{proxy_port}',
            'https': f'https://{proxy_host}:{proxy_port}',
        }
        if proxy_username and proxy_password:
            auth = requests.auth.HTTPProxyAuth(proxy_username, proxy_password)

    while True:
        logging.info(f"--- {datetime.now()} ---")

        if check_file_modification(urls_history):
            with open(urls_file, "r") as file:
                urls_history = file.read().splitlines()

        data = []
        for url in urls_history:
            previous_time, previous_status, previous_content_hash, previous_status_changed = get_previous_status_and_content_hash(url)
            current_time, current_status, current_content_hash, current_status_changed = check_status_and_content(url, previous_status, previous_content_hash, proxies, auth)
            update_previous_status_and_content_hash(url, current_time, current_status, current_content_hash, current_status_changed)
            
            data.append([url, current_time, current_status, current_content_hash, current_status_changed])
        
        log_data = [[url, current_time, current_status, current_content_hash, current_status_changed] for url, current_time, current_status, current_content_hash, current_status_changed in data if current_status_changed == 'Yes']
        if log_data:
            logging.info("Changes detected:")
            print(tabulate(log_data, headers=["URL", "Last Checked", "HTTP Code", "Hash", "Status Changed"], tablefmt='psql'))

        time.sleep(interval)

def get_previous_status_and_content_hash(url):
    file_name = f"{url.replace('/', '_')}.txt"
    if os.path.exists(file_name):
        with open(file_name, "r") as file:
            previous_time, previous_status, previous_content_hash, previous_status_changed = file.read().splitlines()
            return previous_time, int(previous_status), previous_content_hash, previous_status_changed
    else:
        return "", -1, "", ""

def update_previous_status_and_content_hash(url, time, status, content_hash, status_changed):
    file_name = f"{url.replace('/', '_')}.txt"
    with open(file_name, "w") as file:
        file.write(f"{time}\n{status}\n{content_hash}\n{status_changed}")

# Configuração do intervalo de verificação (em segundos)
interval = 10

# Configurações do proxy (opcional)
proxy_enabled = False
proxy_host = 'proxy.example.com'
proxy_port = 8080
proxy_username = 'username'
proxy_password = 'password'

# Iniciar o monitoramento
monitor(interval, proxy_enabled, proxy_host, proxy_port, proxy_username, proxy_password)
