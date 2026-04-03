# Network Port Scanner GUI

A simple desktop app to scan open TCP ports using a graphical interface. It is written in Python with Tkinter and is made for learning and basic authorized testing.

Python 3.7+ | Tkinter (standard library) | Windows | macOS | Linux | MIT License

## Project Overview

This project helps you find open ports on a target host without using command-line tools.
You enter a Target, Start Port, and End Port, then click Start Scan.
The app shows open ports in real time and lets you export results to a text file.

## Features

- Beginner-friendly GUI
- Target, Start Port, and End Port input fields
- Adjustable Timeout (seconds)
- Multi-threaded scanning - up to 500 concurrent threads for fast results
- Real-time open port results in a scrollable text box
- Progress bar and status updates during scanning
- Service labels for common ports (for example SSH, HTTP, HTTPS)
- Stop button to end a scan early
- Export results to `.txt`
- No external Python packages required

## How to Run

1. Open a terminal in the project folder.
2. Make sure Python 3.7 or newer is installed.
3. Run the app:

```bash
python portscanergui.py
```

If `python` does not work on macOS/Linux, try:

```bash
python3 portscanergui.py
```

If Tkinter is missing on Ubuntu/Debian:

```bash
sudo apt install python3-tk
```

## GUI Usage

1. Enter a Target (example: `127.0.0.1`, `localhost`, or `scanme.nmap.org`).
2. Enter Start Port and End Port (valid range: `1` to `65535`).
3. Optional settings:
- Timeout (s): how long to wait per port.
- Threads: number of parallel scan workers (`1` to `500`).
4. Click Start Scan.
5. Watch results in the Open Ports area.
6. Click Stop to cancel early if needed.
7. After scan completion, click Export Results to save a `.txt` report.

## Detected Service Labels

The app labels these common ports automatically. Other open ports are shown as `Unknown`.

| Port | Service |
|------|---------|
| 21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 110 | POP3 |
| 143 | IMAP |
| 443 | HTTPS |
| 3306 | MySQL |
| 3389 | RDP |
| 5900 | VNC |
| 8080 | HTTP-Alt |

## Troubleshooting

- Error: `Please enter a target`
Fix: Enter a valid hostname or IP in the Target field.

- Error: `Invalid input values`
Fix: Make sure Start Port, End Port, Timeout, and Threads are valid numbers.

- Error: `Invalid port range`
Fix: Use ports between `1` and `65535`, and keep Start Port less than or equal to End Port.

- Scan is too slow
Fix: Lower Timeout, reduce the port range, or increase Threads (up to `500`).

- No open ports found
Fix: This can be normal. Try a different target/range, or check firewall/network rules.

- Export says no results
Fix: Export works only when open ports were found in the completed scan.

## Legal and Ethical Use

Use this tool only on systems you own or have permission to test.

Safe examples:
- `localhost`
- `scanme.nmap.org`
- your own home/lab devices

Do not scan public or private systems without authorization.

## License

MIT License
