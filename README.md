# PortPeek Suite: TCP Scanning Tools

A collection of high-performance network scanning utilities built in Python. This suite includes both a lightweight CLI tool for quick audits and a robust GUI application for interactive service discovery.

## The Suite

### 1. PortPeek Light (CLI)
A high-speed, headless port scanner designed for performance in terminal environments. 
- **Best for:** Automated scripts, quick network audits, and CI/CD pipelines.
- **Performance:** Scans ~1,000 ports in under 2 seconds.

### 2. PortPeek Pro (GUI)
A feature-rich desktop application built with `tkinter`, providing a visual interface for complex network mapping.
- **Best for:** Interactive security research and detailed service fingerprinting.
- **Includes:** Banner grabbing for automated service identification.

---

## Features
- **Concurrent Execution:** Utilizes a thread-safe Producer-Consumer architecture to handle thousands of concurrent socket connections without freezing.
- **Service Fingerprinting:** The Pro version performs "Banner Grabbing" to identify the software version running on open ports.
- **Thread Management:** Graceful handling of thread lifecycle, ensuring resources are released immediately upon scan completion or user cancellation.
- **No Dependencies:** Built entirely with Python standard libraries (`socket`, `threading`, `tkinter`, `queue`).

---

## How to Run

### PortPeek Light (CLI)
```bash
python scanner.py <TARGET_IP> -p 1-1024 -t 100
```

### PortPeek Pro (GUI)
```
python gui_scanner.py
```

---

## Technical Overview

The NetScan Suite is architected to prioritize performance through concurrent processing and thread-safe data handling.

### Core Architecture
- **Producer-Consumer Pattern:** A centralized `Queue` manages the distribution of port ranges. Worker threads act as consumers, pulling tasks from the queue and executing socket operations, which ensures optimal CPU utilization and avoids the overhead of spawning a new process for every port.
- **Asynchronous UI (Pro Version):** To prevent the interface from freezing during intensive network I/O, the Pro version implements a decoupled architecture. The `tkinter` main loop handles user input and rendering, while a dedicated `scan_manager` thread orchestrates worker threads in the background. Result injection into the GUI is handled via thread-safe callbacks (`root.after`), ensuring data consistency between the background worker threads and the main UI thread.

### Networking & Concurrency
- **Socket Programming:** The suite leverages low-level `socket` objects with `AF_INET` and `SOCK_STREAM` protocols to execute TCP 3-way handshakes. Non-blocking `connect_ex` calls are utilized, paired with configurable timeouts, to efficiently categorize ports as open, closed, or filtered.
- **Thread Safety:** A `threading.Lock` is implemented to synchronize console output and result list updates, preventing race conditions when multiple threads attempt to write to the terminal or GUI table simultaneously.
- **Graceful Termination:** The Pro version features a non-blocking "Stop" mechanism. By clearing the task queue and using daemonized threads, the suite ensures that all network connections are closed and threads are released instantly when a scan is aborted by the user.

### Service Fingerprinting (Pro Version)
- **Banner Grabbing:** Upon identifying an open port, the tool initiates a secondary handshake attempt. It sends a generic `HEAD` request and captures the server's response header. The resulting buffer is decoded using `utf-8` with error suppression to ensure the tool remains stable even when encountering binary data or malformed responses.

---

## Disclaimer

This tool is intended for educational and authorized security auditing purposes only. Use only on networks and devices you own or have explicit permission to scan.
