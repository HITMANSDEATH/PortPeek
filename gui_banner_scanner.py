import socket
import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread, Lock
from queue import Queue
from datetime import datetime

class PortScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Threaded Port Scanner")
        self.root.geometry("650x500")
        self.root.minsize(550, 400)

        # State variables
        self.is_scanning = False
        self.print_lock = Lock()
        self.queue = Queue()
        self.threads = []

        self.setup_ui()

    def setup_ui(self):
        # Configuration Frame (Inputs)
        config_frame = ttk.LabelFrame(self.root, text=" Configuration ", padding=10)
        config_frame.pack(fill="x", padx=15, pady=10)

        # Target IP/Domain
        ttk.Label(config_frame, text="Target:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(config_frame, width=20)
        self.target_entry.insert(0, "127.0.0.1")
        self.target_entry.grid(row=0, column=1, padx=5, pady=5)

        # Ports
        ttk.Label(config_frame, text="Ports:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.ports_entry = ttk.Entry(config_frame, width=12)
        self.ports_entry.insert(0, "1-1024")
        self.ports_entry.grid(row=0, column=3, padx=5, pady=5)

        # Threads & Timeout
        ttk.Label(config_frame, text="Threads:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.threads_entry = ttk.Entry(config_frame, width=10)
        self.threads_entry.insert(0, "100")
        self.threads_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Timeout (s):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.timeout_entry = ttk.Entry(config_frame, width=10)
        self.timeout_entry.insert(0, "0.5")
        self.timeout_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons Control Frame
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill="x", padx=15)

        self.start_btn = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan_thread)
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop Scan", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        # Progress Status
        self.status_label = ttk.Label(btn_frame, text="Status: Ready", font=("Helvetica", 10, "italic"))
        self.status_label.pack(side="right", padx=10)

        # Results Display (Treeview Table)
        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("port", "status", "banner")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("port", text="Port")
        self.tree.heading("status", text="Status")
        self.tree.heading("banner", text="Banner / Banner Grab Response")
        
        self.tree.column("port", width=80, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("banner", width=400, anchor="w")

        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def log_result(self, port, banner):
        """Thread-safe injection of results into the UI table."""
        self.root.after(0, lambda: self.tree.insert("", "end", values=(port, "OPEN", banner)))

    def update_status(self, text):
        """Thread-safe update of the status text label."""
        self.root.after(0, lambda: self.status_label.config(text=f"Status: {text}"))

    def scan_worker(self, target_host, timeout):
        """Worker thread executing socket connection loops."""
        while self.is_scanning and not self.queue.empty():
            port = self.queue.get()
            banner = "Unknown"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(timeout)
                result = s.connect_ex((target_host, port))
                
                if result == 0:
                    try:
                        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                        banner = s.recv(1024).decode('utf-8', errors='ignore').strip().split('\n')[0]
                    except Exception:
                        banner = "Detected (No Banner response)"
                    
                    self.log_result(port, banner)
                s.close()
            except Exception:
                pass
            finally:
                self.queue.task_done()

    def start_scan_thread(self):
        """Validates inputs and triggers the scanning process on a background thread."""
        target = self.target_entry.get().strip()
        ports_raw = self.ports_entry.get().strip()
        
        try:
            threads_count = int(self.threads_entry.get())
            timeout = float(self.timeout_entry.get())
            port_start, port_end = map(int, ports_raw.split("-"))
            ports = range(port_start, port_end + 1)
        except ValueError:
            messagebox.showerror("Input Error", "Please verify your formatting.\nPorts: START-END (e.g. 1-1024)\nThreads: Integer\nTimeout: Float")
            return

        try:
            target_ip = socket.gethostbyname(target)
        except socket.gaierror:
            messagebox.showerror("DNS Error", f"Could not resolve host target: {target}")
            return

        # Clear previous rows from table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Adjust UI buttons state
        self.is_scanning = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.update_status("Scanning...")

        # Clear queue and fill with new ports
        while not self.queue.empty():
            self.queue.get()
        for port in ports:
            self.queue.put(port)

        # Wrapper thread to manage workers so GUI thread doesn't hang
        def scan_manager():
            self.threads = []
            num_workers = min(threads_count, len(ports))
            for _ in range(num_workers):
                t = Thread(target=self.scan_worker, args=(target_ip, timeout))
                t.daemon = True
                t.start()
                self.threads.append(t)
            
            self.queue.join()
            self.is_scanning = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.update_status("Scan Complete")

        Thread(target=scan_manager, daemon=True).start()

    def stop_scan(self):
        """Gracefully alerts background loops to halt execution instantly."""
        if self.is_scanning:
            self.is_scanning = False
            # Empty out the remaining queue to force workers to shut down cleanly
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                    self.queue.task_done()
                except Exception:
                    break
            self.update_status("Aborted by User")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerGUI(root)
    root.mainloop()
