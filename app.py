from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

PROTOCOLS = {
    "browsing": [
        {
            "time": "0.0s", "direction": "Client → DNS Server", "type": "DNS QUERY",
            "title": "DNS query",
            "message": "Transaction ID: 0xA1B2 | Standard query\nQuestion: example.com  Type: A  Class: IN",
            "highlight": ["example.com", "A", "IN"]
        },
        {
            "time": "0.4s", "direction": "DNS Server → Client", "type": "DNS RESPONSE",
            "title": "DNS response",
            "message": "Transaction ID: 0xA1B2 | Response: NOERROR\nAnswer: example.com  A  93.184.216.34  TTL: 300",
            "highlight": ["NOERROR", "93.184.216.34", "TTL: 300"]
        },
        {
            "time": "0.8s", "direction": "Client → Web Server", "type": "HTTP REQUEST",
            "title": "HTTP GET request",
            "message": "GET / HTTP/1.1\nHost: example.com\nAccept: text/html\nConnection: keep-alive",
            "highlight": ["GET /", "Host:", "HTTP/1.1"]
        },
        {
            "time": "1.2s", "direction": "Web Server → Client", "type": "HTTP RESPONSE",
            "title": "HTTP response",
            "message": "HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: 1256\nConnection: keep-alive",
            "highlight": ["200 OK", "Content-Type", "Content-Length"]
        }
    ],
    "mail": [
        {
            "time": "0.0s", "direction": "Client → Mail Server", "type": "SMTP EHLO",
            "title": "SMTP greeting",
            "message": "EHLO student.example\n",
            "highlight": ["EHLO"]
        },
        {
            "time": "0.3s", "direction": "Mail Server → Client", "type": "SMTP RESPONSE",
            "title": "Server capabilities",
            "message": "250-mail.example SMTP Service Ready\n250-SIZE 10485760\n250-8BITMIME\n250-STARTTLS",
            "highlight": ["250", "STARTTLS"]
        },
        {
            "time": "0.6s", "direction": "Client → Mail Server", "type": "SMTP MAIL FROM",
            "title": "Sender",
            "message": "MAIL FROM:<student@example.com>",
            "highlight": ["MAIL FROM"]
        },
        {
            "time": "0.8s", "direction": "Mail Server → Client", "type": "SMTP RESPONSE",
            "title": "Sender accepted",
            "message": "250 2.1.0 OK",
            "highlight": ["250", "2.1.0"]
        },
        {
            "time": "1.0s", "direction": "Client → Mail Server", "type": "SMTP RCPT TO",
            "title": "Recipient",
            "message": "RCPT TO:<receiver@example.net>",
            "highlight": ["RCPT TO"]
        },
        {
            "time": "1.2s", "direction": "Mail Server → Client", "type": "SMTP RESPONSE",
            "title": "Recipient accepted",
            "message": "250 2.1.5 OK",
            "highlight": ["250", "2.1.5"]
        },
        {
            "time": "1.4s", "direction": "Client → Mail Server", "type": "SMTP DATA",
            "title": "Message data",
            "message": "DATA\nSubject: Assignment Demo\n\nHello, this is a simulated email.\n.",
            "highlight": ["DATA", "Subject:", "."]
        },
        {
            "time": "1.8s", "direction": "Mail Server → Client", "type": "SMTP RESPONSE",
            "title": "Message queued",
            "message": "250 2.0.0 Message accepted for delivery",
            "highlight": ["250", "Message accepted"]
        },
        {
            "time": "2.0s", "direction": "Client → Mail Server", "type": "SMTP QUIT",
            "title": "Close session",
            "message": "QUIT",
            "highlight": ["QUIT"]
        },
        {
            "time": "2.2s", "direction": "Mail Server → Client", "type": "SMTP RESPONSE",
            "title": "Session closed",
            "message": "221 2.0.0 Bye",
            "highlight": ["221", "Bye"]
        }
    ],
    "streaming": [
        {
            "time": "0.0s", "direction": "Client → DNS Server", "type": "DNS QUERY",
            "title": "Resolve streaming host",
            "message": "Question: video.example  Type: A  Class: IN",
            "highlight": ["video.example", "A"]
        },
        {
            "time": "0.3s", "direction": "DNS Server → Client", "type": "DNS RESPONSE",
            "title": "Streaming host resolved",
            "message": "Answer: video.example  A  203.0.113.20  TTL: 60",
            "highlight": ["203.0.113.20", "TTL: 60"]
        },
        {
            "time": "0.7s", "direction": "Client → Web Server", "type": "HTTP GET",
            "title": "Request manifest / playlist",
            "message": "GET /media/playlist.m3u8 HTTP/1.1\nHost: video.example\nAccept: application/vnd.apple.mpegurl",
            "highlight": ["playlist.m3u8", "GET", "Accept:"]
        },
        {
            "time": "1.0s", "direction": "Web Server → Client", "type": "HTTP RESPONSE",
            "title": "Manifest response",
            "message": "HTTP/1.1 200 OK\nContent-Type: application/vnd.apple.mpegurl\nCache-Control: max-age=30",
            "highlight": ["200 OK", "playlist", "Cache-Control"]
        },
        {
            "time": "1.4s", "direction": "Client → Web Server", "type": "HTTP GET",
            "title": "Request segment 1",
            "message": "GET /media/720p/segment001.ts HTTP/1.1\nHost: video.example",
            "highlight": ["segment001.ts", "720p"]
        },
        {
            "time": "1.8s", "direction": "Web Server → Client", "type": "HTTP RESPONSE",
            "title": "Segment 1 delivered",
            "message": "HTTP/1.1 200 OK\nContent-Type: video/mp2t\nContent-Length: 1843200",
            "highlight": ["200 OK", "video/mp2t", "1843200"]
        },
        {
            "time": "2.2s", "direction": "Client → Web Server", "type": "HTTP GET",
            "title": "Request segment 2",
            "message": "GET /media/720p/segment002.ts HTTP/1.1\nHost: video.example",
            "highlight": ["segment002.ts", "720p"]
        },
        {
            "time": "2.6s", "direction": "Web Server → Client", "type": "HTTP RESPONSE",
            "title": "Segment 2 delivered",
            "message": "HTTP/1.1 200 OK\nContent-Type: video/mp2t\nContent-Length: 1798400",
            "highlight": ["200 OK", "video/mp2t", "1798400"]
        }
    ]
}

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/simulate")
def simulate():
    data = request.get_json(silent=True) or {}
    activity = data.get("activity", "browsing")
    if activity not in PROTOCOLS:
        return jsonify({"error": "Unknown activity"}), 400

    # User-entered values are used only for the activity log/demo text.
    return jsonify({
        "activity": activity,
        "steps": PROTOCOLS[activity]
    })

if __name__ == "__main__":
    app.run(debug=True)
