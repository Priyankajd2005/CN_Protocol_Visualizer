# Application Layer Protocol Visualizer

## Assignment coverage
This project implements the required two-panel dashboard:
- Left: Browsing, Mail, Streaming activities
- Right: sequential protocol visualization
- Browsing: DNS query/response + HTTP GET/response
- Mail: SMTP EHLO, MAIL FROM, RCPT TO, DATA, QUIT
- Streaming: DNS + HTTP playlist/manifest + segment requests
- Controls: Previous, Play/Pause, Next, Replay
- Activity log and timing indicators
- Responsive layout for smaller screens

The protocol behavior is simulated, as allowed by the assignment.

## Requirements
- Python 3.10+ recommended
- Flask

## Windows / VS Code setup

Open PowerShell in this project folder.

### 1. Check Python
Try:
python --version

If that does not work, try:
py --version

### 2. Create virtual environment
python -m venv venv

If `python` does not work but `py` does:
py -m venv venv

### 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

If PowerShell blocks activation, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

### 4. Install Flask
python -m pip install flask

### 5. Run
python app.py

### 6. Open browser
Go to:
http://127.0.0.1:5000

## Stop server
In PowerShell press:
Ctrl + C

## Suggested demo
1. Open Browsing and click Visit Page.
2. Show DNS query, DNS response, HTTP GET, HTTP response.
3. Use Previous/Next and Replay.
4. Click Mail, fill To/Subject/Body, click Send Email.
5. Show EHLO → MAIL FROM → RCPT TO → DATA → QUIT.
6. Click Streaming, select quality, click Play.
7. Show DNS → playlist/manifest → segment requests.
8. Mention that this is a protocol simulation, not a real SMTP/HTTP socket connection.

## AI usage requirement
The assignment requires evidence of AI assistance. Keep screenshots of your AI prompts/responses. In your submission state the platform/model used. If you used ChatGPT, write the exact model name shown in your ChatGPT interface.

## Important accuracy note
The assignment allows simulated protocols. The dashboard therefore uses representative protocol messages rather than making real network connections.
