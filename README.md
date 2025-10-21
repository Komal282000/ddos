

# HTTP Range Header DoS Tool (Educational)

**WARNING**: This tool is provided for educational purposes only. Unauthorized denial-of-service (DoS) attacks are illegal and unethical. Use this tool responsibly and only against systems you have explicit permission to test.

## Overview

This Python script implements a denial-of-service (DoS) tool that leverages the "HTTP Range header" vulnerability, often associated with the "Apache Killer" attack. The attack attempts to exhaust server resources by sending requests with a large number of overlapping `Range` headers, forcing the server to perform excessive processing.

The tool uses multiple threads and can route traffic through SOCKS4, SOCKS5, or HTTP CONNECT proxies to obscure the origin of the requests. It rotates User-Agent strings to mimic various browsers and bots.

`

## Features

*   **HTTP Range Header Attack**: Generates a malicious `Range` header with many overlapping byte ranges.
*   **Multi-threading**: Launches multiple attacker threads to parallelize requests.
*   **Proxy Support**: Supports SOCKS4, SOCKS5, and HTTP CONNECT proxies.
*   **User-Agent Rotation**: Randomly selects User-Agent strings to appear as different clients.
*   **Configurable Duration**: Specifies how long the attack should run.

## Requirements

*   Python 3.x
*   `PySocks` library: `pip install PySocks`

## How it Works (Technical Details)

The core of this attack lies in the `generate_range_header()` function. It constructs an HTTP `Range` header similar to this:

```
Range: bytes=0-,5-0,5-1,5-2,...,5-1299
```

When a web server receives such a header, especially if it's not optimized to handle malformed or excessive ranges, it might attempt to process each specified byte range. With a large number of overlapping ranges, this can consume significant CPU and memory resources on the server, leading to a denial of service for legitimate users.

Each attacker thread:
1.  Chooses a random proxy from the loaded list.
2.  Establishes a connection to the proxy (or directly to the target if no proxy type is specified).
3.  For HTTP CONNECT proxies, it performs a manual `CONNECT` handshake.
4.  Connects to the target web server (via the proxy).
5.  Sends a `HEAD` request with a randomly chosen `User-Agent` and the specially crafted `Range` header.
6.  Closes the connection and pauses briefly before repeating.

## Usage

```bash
python your_script_name.py <target_url> <threads> <proxy_file> <duration>
```

### Arguments:

*   `<target_url>`: The URL of the target web server (e.g., `http://example.com` or `https://example.com`).
*   `<threads>`: The number of concurrent attacker threads to launch.
*   `<proxy_file>`: A path to a text file containing a list of proxies.
*   `<duration>`: The duration of the attack in seconds.

### Proxy File Format:

The `proxy_file` should contain one proxy per line, in the format `ip:port:type`.

*   **`ip`**: The IP address of the proxy server.
*   **`port`**: The port number of the proxy server.
*   **`type`**: The type of proxy. Supported types include:
    *   `socks4`
    *   `socks5`
    *   `connect` (for HTTP CONNECT tunneling)
    *   `tunnel` (alias for `connect`)
    *   Any other value or omission of type will result in a direct connection (no proxy).

**Example `proxies.txt`:**

```
192.168.1.100:1080:socks5
socks.example.com:9050:socks4
http-proxy.org:8080:connect
vpn.provider.com:3128:tunnel
1.2.3.4:8888:socks5
```

## Example Command

To run an attack against `http://testserver.com` with 50 threads, using proxies from `proxies.txt` for 60 seconds:

```bash
python your_script_name.py http://testserver.com 50 proxies.txt 60
```

## Disclaimer

This tool is for educational purposes only. Misuse of this tool can lead to severe legal consequences. The author is not responsible for any misuse or damage caused by this program.
