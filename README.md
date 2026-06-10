# PortPeek: Multi-Threaded TCP Port Scanner

A fast and reliable port scanning utility written in Python. This tool maps open ports on a target host to identify active services and potential network attack surfaces.

## Performance
- **Speed:** Capable of scanning 1,000+ ports in approximately 2 seconds using concurrent thread execution.
- **Efficiency:** Utilizes a thread-safe worker queue to manage connections, preventing network deadlocks and OS-level bottlenecks.

## Features
- **Multi-Threading:** Distributes scanning tasks across a configurable pool of threads for high-speed performance.
- **Concurrency:** Uses a Producer-Consumer architecture to ensure the scan remains stable even under high thread counts.
- **Robustness:** Implements non-blocking socket connections with configurable timeouts to handle unresponsive hosts gracefully.

## Prerequisites
- Python 3.x
- No external libraries required (uses built-in `socket`, `threading`, and `queue` modules).

## How to Run

### Command Line
Run the scanner by providing a target IP or domain:
```
python scanner.py 127.0.0.1 -p 1-1024 -t 100
```
## Options

### target: The IP address or hostname to scan.

### -p, --ports: Port range to scan (format: START-END, default: 1-1024).

### -t, --threads: Number of concurrent threads to use (default: 100).

### --timeout: Connection timeout in seconds (default: 0.5).


## Technical Details
 
### Architecture: Employs a thread-safe queue where a main controller manages the distribution of port scanning tasks to a pool of worker threads.

### Networking: Utilizes the socket library to initiate TCP connections (the 3-way handshake) to verify if a port is listening.
 
### Optimization: By using daemonized threads and a Queue.join() mechanism, the tool ensures clean execution and instant resource cleanup upon completion.
  
Disclaimer: This tool is intended for educational and authorized security auditing purposes only. Use only on networks and devices you own or have explicit permission to scan.
