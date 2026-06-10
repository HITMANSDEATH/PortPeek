import socket
import argparse
import sys
from threading import Thread, Lock
from queue import Queue
from datetime import datetime

# Thread-safe printing lock
print_lock = Lock()
open_ports = []

def scan_worker(target_host, queue, timeout):
    """Worker thread that continuously pulls ports from the queue and scans them."""
    while not queue.empty():
        port = queue.get()
        try:
            # Explicitly force IPv4 and TCP
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Crucial: set the timeout BEFORE trying to connect
            s.settimeout(timeout)
            
            result = s.connect_ex((target_host, port))
            if result == 0:
                with print_lock:
                    print(f"[+] Port {port:<5} is OPEN")
                    open_ports.append(port)
            s.close()
        except Exception:
            pass
        finally:
            queue.task_done()

def main():
    parser = argparse.ArgumentParser(description="Fast, stable TCP Port Scanner.")
    parser.add_argument("target", help="Target IP or domain (e.g., 127.0.0.1)")
    parser.add_argument("-p", "--ports", default="1-1024", help="Port range (default: 1-1024)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads")
    parser.add_argument("--timeout", type=float, default=0.5, help="Timeout in seconds (default: 0.5)")
    
    args = parser.parse_args()

    # Parse port range
    try:
        port_start, port_end = map(int, args.ports.split("-"))
        ports = range(port_start, port_end + 1)
    except ValueError:
        print("[-] Invalid port range format. Use START-END (e.g., 1-1000)")
        return

    # Resolve target
    try:
        target_ip = socket.gethostbyname(args.target)
    except socket.gaierror:
        print(f"[-] Could not resolve hostname: {args.target}")
        return

    print("-" * 50)
    print(f"Scanning Target : {target_ip}")
    print(f"Time Started    : {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 50)

    # Initialize queue and fill it with ports
    queue = Queue()
    for port in ports:
        queue.put(port)

    # Spawn threads
    threads = []
    # Don't spawn more threads than there are ports
    num_threads = min(args.threads, len(ports))
    
    for _ in range(num_threads):
        t = Thread(target=scan_worker, args=(target_ip, queue, args.timeout))
        # Daemon threads will automatically die if the main script exits/crushes
        t.daemon = True 
        t.start()
        threads.append(t)

    # Wait for the queue to completely empty out
    try:
        queue.join()
    except KeyboardInterrupt:
        print("\n[-] Scan aborted by user.")
        sys.exit()

    print("-" * 50)
    print(f"Scan complete. Found {len(open_ports)} open ports.")
    print("-" * 50)

if __name__ == "__main__":
    main()
