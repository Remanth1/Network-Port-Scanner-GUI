import socket
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Service identification mapping
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 135: 'MSRPC', 143: 'IMAP',
    443: 'HTTPS', 445: 'SMB', 3306: 'MySQL', 3389: 'RDP',
    5037: 'ADB', 5354: 'WSD', 5900: 'VNC', 7070: 'HTTP-Alt',
    8080: 'HTTP-Alt'
}


def resolve_service_name(port):
    """Return a readable service label for a TCP port."""
    if port in COMMON_PORTS:
        return COMMON_PORTS[port]

    try:
        return socket.getservbyport(port, 'tcp').upper()
    except OSError:
        return 'Unknown'

# Simple port scanner with threading
class PortScanner:
    def __init__(self, target, start_port, end_port, timeout=2.0, num_threads=100, on_open_port=None, on_port_scanned=None):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.timeout = timeout
        self.num_threads = num_threads
        self.open_ports = []
        self.stopped = False
        self.on_open_port = on_open_port
        self.on_port_scanned = on_port_scanned
    
    def scan_port(self, port):
        """Scan a single port and return (port, service, is_open)"""
        if self.stopped:
            return None
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                service = resolve_service_name(port)
                self.open_ports.append((port, service))
                return (port, service, True)
            return (port, None, False)
        except:
            return (port, None, False)
    
    def run(self):
        """Run the scan using a fixed worker pool for better performance."""
        port_queue = queue.Queue()
        for port in range(self.start_port, self.end_port + 1):
            port_queue.put(port)

        worker_count = max(1, self.num_threads)
        threads = []

        for _ in range(worker_count):
            thread = threading.Thread(target=self._worker_loop, args=(port_queue,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def _worker_loop(self, port_queue):
        """Scan ports from a shared queue until empty or stopped."""
        while not self.stopped:
            try:
                port = port_queue.get_nowait()
            except queue.Empty:
                return

            self._scan_port_worker(port)

    def _scan_port_worker(self, port):
        """Worker wrapper that reports open ports and progress via callbacks."""
        scan_result = self.scan_port(port)
        if scan_result and scan_result[2] and self.on_open_port:
            self.on_open_port(scan_result[0], scan_result[1])
        if self.on_port_scanned:
            self.on_port_scanned()


# GUI Application
class ScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Port Scanner")
        self.geometry("600x500")
        self.scanner = None
        self.scanning = False
        self.result_queue = queue.Queue()
        self.total_ports = 0
        self.scanned_ports = 0
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create GUI interface"""
        # Input frame
        input_frame = ttk.LabelFrame(self, text="Scan Settings", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Target input
        ttk.Label(input_frame, text="Target:").grid(row=0, column=0, sticky="w", pady=5)
        self.target_entry = ttk.Entry(input_frame, width=30)
        self.target_entry.grid(row=0, column=1, sticky="w", pady=5)
        self.target_entry.insert(0, "127.0.0.1")
        
        # Port range
        ttk.Label(input_frame, text="Start Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.start_port_entry = ttk.Entry(input_frame, width=10)
        self.start_port_entry.grid(row=1, column=1, sticky="w", pady=5)
        self.start_port_entry.insert(0, "1")
        
        ttk.Label(input_frame, text="End Port:").grid(row=2, column=0, sticky="w", pady=5)
        self.end_port_entry = ttk.Entry(input_frame, width=10)
        self.end_port_entry.grid(row=2, column=1, sticky="w", pady=5)
        self.end_port_entry.insert(0, "1024")
        
        # Timeout
        ttk.Label(input_frame, text="Timeout (s):").grid(row=3, column=0, sticky="w", pady=5)
        self.timeout_entry = ttk.Entry(input_frame, width=10)
        self.timeout_entry.grid(row=3, column=1, sticky="w", pady=5)
        self.timeout_entry.insert(0, "1")
        
        # Threads
        ttk.Label(input_frame, text="Threads:").grid(row=4, column=0, sticky="w", pady=5)
        self.threads_entry = ttk.Entry(input_frame, width=10)
        self.threads_entry.grid(row=4, column=1, sticky="w", pady=5)
        self.threads_entry.insert(0, "100")
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Start Scan", command=self.start_scan)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Status label
        self.status_label = ttk.Label(self, text="Ready")
        self.status_label.pack(padx=10, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self, text="Open Ports", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Results text box with scrollbar
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.results_text = tk.Text(results_frame, height=15, width=50, yscrollcommand=scrollbar.set)
        self.results_text.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=self.results_text.yview)
        
        # Export button
        self.export_btn = ttk.Button(self, text="Export Results", command=self.export_results, state="disabled")
        self.export_btn.pack(pady=10)
    
    def start_scan(self):
        """Start scanning ports"""
        target = self.target_entry.get().strip()
        
        if not target:
            messagebox.showerror("Error", "Please enter a target")
            return
        
        try:
            start_port = int(self.start_port_entry.get())
            end_port = int(self.end_port_entry.get())
            timeout = float(self.timeout_entry.get())
            num_threads = int(self.threads_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")
            return
        
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            messagebox.showerror("Error", "Invalid port range")
            return

        if num_threads < 1 or num_threads > 500:
            messagebox.showerror("Error", "Threads must be between 1 and 500")
            return
        
        # Clear previous results
        self.results_text.delete("1.0", tk.END)
        self.scanning = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.export_btn.config(state="disabled")
        self.total_ports = end_port - start_port + 1
        self.scanned_ports = 0
        self.progress.config(maximum=self.total_ports, value=0)
        self.status_label.config(text="Scanning...")
        
        # Create scanner
        self.scanner = PortScanner(
            target,
            start_port,
            end_port,
            timeout,
            num_threads,
            on_open_port=self.on_open_port_found,
            on_port_scanned=self.on_port_scanned,
        )
        
        # Run scan in background thread
        scan_thread = threading.Thread(target=self.run_scan)
        scan_thread.daemon = True
        scan_thread.start()
        self.after(50, self.process_results)
    
    def run_scan(self):
        """Run the scan in background and signal completion."""
        if not self.scanner:
            return
        self.scanner.run()
        self.result_queue.put(("done", None))

    def on_open_port_found(self, port_num, service):
        """Queue open port events from worker threads for UI-safe processing."""
        self.result_queue.put(("open", (port_num, service)))

    def on_port_scanned(self):
        """Queue progress update events from worker threads."""
        self.result_queue.put(("progress", 1))

    def process_results(self):
        """Process queued scan updates on the Tkinter main thread."""
        while True:
            try:
                event, data = self.result_queue.get_nowait()
            except queue.Empty:
                break

            if event == "open" and data:
                port_num, service = data
                self.results_text.insert(tk.END, f"[+] Port {port_num:5d} ({service})\n")
                self.results_text.see(tk.END)
            elif event == "progress":
                self.scanned_ports += 1
                self.progress.config(value=self.scanned_ports)
            elif event == "done":
                self.finish_scan()
                return

        if self.scanning:
            self.after(50, self.process_results)

    def finish_scan(self):
        """Finalize UI state after scan completion."""
        self.scanning = False
        if self.scanner:
            port_count = len(self.scanner.open_ports)
            self.status_label.config(text=f"Scan complete - {port_count} ports open")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.export_btn.config(state="normal")
        self.progress.config(value=0)
    
    def stop_scan(self):
        """Stop the scan"""
        if self.scanner:
            self.scanner.stopped = True
        self.scanning = False
        self.status_label.config(text="Scan stopped")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def export_results(self):
        """Export results to file"""
        if not self.scanner or not self.scanner.open_ports:
            messagebox.showinfo("Export", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write("Open Ports:\n")
                    f.write(f"Target: {self.scanner.target}\n")
                    f.write(f"Port Range: {self.scanner.start_port}-{self.scanner.end_port}\n\n")
                    for port, service in sorted(self.scanner.open_ports):
                        f.write(f"Port {port:5d} ({service})\n")
                messagebox.showinfo("Success", f"Results saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    try:
        app = ScannerApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Error: {e}")
