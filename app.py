from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base Application Layer Flows
APP_PROTOCOLS = {
    "browsing": [
        {
            "time": "0.0s", "direction": "Client -> DNS Server", "type": "DNS QUERY",
            "layer": "Application / Transport (UDP 53)",
            "title": "DNS query",
            "message": "Transaction ID: 0xA1B2 | Standard query\nQuestion: example.com  Type: A  Class: IN",
            "highlight": ["example.com", "A", "IN"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "53412 -> 53"
        },
        {
            "time": "0.4s", "direction": "DNS Server -> Client", "type": "DNS RESPONSE",
            "layer": "Application / Transport (UDP 53)",
            "title": "DNS response",
            "message": "Transaction ID: 0xA1B2 | Response: NOERROR\nAnswer: example.com  A  93.184.216.34  TTL: 300",
            "highlight": ["NOERROR", "93.184.216.34", "TTL: 300"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "53 -> 53412"
        },
        {
            "time": "1.4s", "direction": "Client -> Web Server", "type": "HTTP REQUEST",
            "layer": "Application (L7)",
            "title": "HTTP GET request",
            "message": "GET / HTTP/1.1\nHost: example.com\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64)\nAccept: text/html\nConnection: keep-alive",
            "highlight": ["GET /", "Host:", "HTTP/1.1"],
            "flags": "[PSH, ACK]", "seq": "1001", "ack": "5001", "ports": "49820 -> 80/443"
        },
        {
            "time": "1.8s", "direction": "Web Server -> Client", "type": "HTTP RESPONSE",
            "layer": "Application (L7)",
            "title": "HTTP response",
            "message": "HTTP/1.1 200 OK\nDate: Thu, 28 Sep 2026 12:00:00 GMT\nContent-Type: text/html; charset=UTF-8\nContent-Length: 1256\nConnection: keep-alive",
            "highlight": ["200 OK", "Content-Type", "Content-Length"],
            "flags": "[PSH, ACK]", "seq": "5001", "ack": "1257", "ports": "80/443 -> 49820"
        }
    ],
    "mail": [
        {
            "time": "0.0s", "direction": "Client -> DNS Server", "type": "DNS MX QUERY",
            "layer": "Application / Transport (UDP 53)",
            "title": "DNS MX query",
            "message": "Transaction ID: 0x8F31 | Query: example.net  Type: MX  Class: IN",
            "highlight": ["example.net", "MX"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "51230 -> 53"
        },
        {
            "time": "0.3s", "direction": "DNS Server -> Client", "type": "DNS MX RESPONSE",
            "layer": "Application / Transport (UDP 53)",
            "title": "DNS MX response",
            "message": "Answer: example.net  MX preference: 10 mail.example.net\nAdditional: mail.example.net A 198.51.100.25",
            "highlight": ["mail.example.net", "Pref 10", "198.51.100.25"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "53 -> 51230"
        },
        {
            "time": "1.0s", "direction": "Mail Server -> Client", "type": "SMTP GREETING",
            "layer": "Application (L7)",
            "title": "SMTP server greeting",
            "message": "220 mail.example.net ESMTP Postfix Service Ready",
            "highlight": ["220", "Service Ready"],
            "flags": "[PSH, ACK]", "seq": "8001", "ack": "3001", "ports": "25 -> 50124"
        },
        {
            "time": "1.3s", "direction": "Client -> Mail Server", "type": "SMTP EHLO",
            "layer": "Application (L7)",
            "title": "SMTP client EHLO",
            "message": "EHLO student.example\r\n",
            "highlight": ["EHLO", "student.example"],
            "flags": "[PSH, ACK]", "seq": "3001", "ack": "8048", "ports": "50124 -> 25"
        },
        {
            "time": "1.6s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Server capabilities",
            "message": "250-mail.example.net Hello student.example\n250-SIZE 10485760\n250-8BITMIME\n250-STARTTLS\n250 HELP",
            "highlight": ["250", "SIZE", "STARTTLS"],
            "flags": "[PSH, ACK]", "seq": "8048", "ack": "3024", "ports": "25 -> 50124"
        },
        {
            "time": "1.9s", "direction": "Client -> Mail Server", "type": "SMTP MAIL FROM",
            "layer": "Application (L7)",
            "title": "Sender envelope",
            "message": "MAIL FROM:<student@example.com>",
            "highlight": ["MAIL FROM"],
            "flags": "[PSH, ACK]", "seq": "3024", "ack": "8120", "ports": "50124 -> 25"
        },
        {
            "time": "2.1s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Sender accepted",
            "message": "250 2.1.0 OK",
            "highlight": ["250", "2.1.0"],
            "flags": "[PSH, ACK]", "seq": "8120", "ack": "3055", "ports": "25 -> 50124"
        },
        {
            "time": "2.3s", "direction": "Client -> Mail Server", "type": "SMTP RCPT TO",
            "layer": "Application (L7)",
            "title": "Recipient envelope",
            "message": "RCPT TO:<receiver@example.net>",
            "highlight": ["RCPT TO"],
            "flags": "[PSH, ACK]", "seq": "3055", "ack": "8136", "ports": "50124 -> 25"
        },
        {
            "time": "2.5s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Recipient accepted",
            "message": "250 2.1.5 OK",
            "highlight": ["250", "2.1.5"],
            "flags": "[PSH, ACK]", "seq": "8136", "ack": "3087", "ports": "25 -> 50124"
        },
        {
            "time": "2.7s", "direction": "Client -> Mail Server", "type": "SMTP DATA",
            "layer": "Application (L7)",
            "title": "Message data command",
            "message": "DATA",
            "highlight": ["DATA"],
            "flags": "[PSH, ACK]", "seq": "3087", "ack": "8152", "ports": "50124 -> 25"
        },
        {
            "time": "2.9s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Start mail input",
            "message": "354 Start mail input; end with <CRLF>.<CRLF>",
            "highlight": ["354", "<CRLF>.<CRLF>"],
            "flags": "[PSH, ACK]", "seq": "8152", "ack": "3093", "ports": "25 -> 50124"
        },
        {
            "time": "3.2s", "direction": "Client -> Mail Server", "type": "SMTP DATA PAYLOAD",
            "layer": "Application (L7)",
            "title": "Email headers & body",
            "message": "From: student@example.com\nTo: receiver@example.net\nSubject: Assignment Demo\n\nHello, this is a simulated email.\n.",
            "highlight": ["From:", "To:", "Subject:", "."],
            "flags": "[PSH, ACK]", "seq": "3093", "ack": "8196", "ports": "50124 -> 25"
        },
        {
            "time": "3.5s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Message queued",
            "message": "250 2.0.0 Ok: queued as 4X8910AB",
            "highlight": ["250", "queued as 4X8910AB"],
            "flags": "[PSH, ACK]", "seq": "8196", "ack": "3210", "ports": "25 -> 50124"
        },
        {
            "time": "3.7s", "direction": "Client -> Mail Server", "type": "SMTP QUIT",
            "layer": "Application (L7)",
            "title": "Close session",
            "message": "QUIT",
            "highlight": ["QUIT"],
            "flags": "[PSH, ACK]", "seq": "3210", "ack": "8230", "ports": "50124 -> 25"
        },
        {
            "time": "3.9s", "direction": "Mail Server -> Client", "type": "SMTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Session closed",
            "message": "221 2.0.0 Bye",
            "highlight": ["221", "Bye"],
            "flags": "[PSH, ACK]", "seq": "8230", "ack": "3216", "ports": "25 -> 50124"
        }
    ],
    "streaming": [
        {
            "time": "0.0s", "direction": "Client -> DNS Server", "type": "DNS QUERY",
            "layer": "Application / Transport (UDP 53)",
            "title": "Resolve streaming CDN host",
            "message": "Question: video.cdn.example  Type: A  Class: IN",
            "highlight": ["video.cdn.example", "A"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "58190 -> 53"
        },
        {
            "time": "0.3s", "direction": "DNS Server -> Client", "type": "DNS RESPONSE",
            "layer": "Application / Transport (UDP 53)",
            "title": "Streaming host resolved",
            "message": "Answer: video.cdn.example  A  203.0.113.20  TTL: 60",
            "highlight": ["203.0.113.20", "TTL: 60"],
            "flags": "UDP", "seq": "-", "ack": "-", "ports": "53 -> 58190"
        },
        {
            "time": "1.3s", "direction": "Client -> Web Server", "type": "HTTP GET",
            "layer": "Application (L7)",
            "title": "Request master playlist (.m3u8)",
            "message": "GET /media/playlist.m3u8 HTTP/1.1\nHost: video.cdn.example\nAccept: application/vnd.apple.mpegurl",
            "highlight": ["playlist.m3u8", "GET", "Accept:"],
            "flags": "[PSH, ACK]", "seq": "1001", "ack": "7001", "ports": "54210 -> 443"
        },
        {
            "time": "1.6s", "direction": "Web Server -> Client", "type": "HTTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Manifest response",
            "message": "HTTP/1.1 200 OK\nContent-Type: application/vnd.apple.mpegurl\nCache-Control: max-age=30\n\n#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=2800000,RESOLUTION=1280x720",
            "highlight": ["200 OK", "playlist.m3u8", "720p"],
            "flags": "[PSH, ACK]", "seq": "7001", "ack": "1120", "ports": "443 -> 54210"
        },
        {
            "time": "2.0s", "direction": "Client -> Web Server", "type": "HTTP GET",
            "layer": "Application (L7)",
            "title": "Request video segment 001.ts",
            "message": "GET /media/720p/segment001.ts HTTP/1.1\nHost: video.cdn.example\nRange: bytes=0-",
            "highlight": ["segment001.ts", "720p", "Range"],
            "flags": "[PSH, ACK]", "seq": "1120", "ack": "7210", "ports": "54210 -> 443"
        },
        {
            "time": "2.4s", "direction": "Web Server -> Client", "type": "HTTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Segment 001 delivered",
            "message": "HTTP/1.1 206 Partial Content\nContent-Type: video/mp2t\nContent-Length: 1843200\n\n[Binary MPEG-2 Transport Stream (1.8 MB)]",
            "highlight": ["206 Partial Content", "video/mp2t", "1.8 MB"],
            "flags": "[PSH, ACK]", "seq": "7210", "ack": "1240", "ports": "443 -> 54210"
        },
        {
            "time": "2.8s", "direction": "Client -> Web Server", "type": "HTTP GET",
            "layer": "Application (L7)",
            "title": "Request video segment 002.ts",
            "message": "GET /media/720p/segment002.ts HTTP/1.1\nHost: video.cdn.example",
            "highlight": ["segment002.ts", "720p"],
            "flags": "[PSH, ACK]", "seq": "1240", "ack": "9053", "ports": "54210 -> 443"
        },
        {
            "time": "3.2s", "direction": "Web Server -> Client", "type": "HTTP RESPONSE",
            "layer": "Application (L7)",
            "title": "Segment 002 delivered",
            "message": "HTTP/1.1 206 Partial Content\nContent-Type: video/mp2t\nContent-Length: 1798400\n\n[Binary MPEG-2 Transport Stream (1.7 MB)]",
            "highlight": ["206 Partial Content", "video/mp2t", "1.7 MB"],
            "flags": "[PSH, ACK]", "seq": "9053", "ack": "1360", "ports": "443 -> 54210"
        }
    ],
    "transport": [
        {
            "time": "0.0s", "direction": "Client -> Server", "type": "TCP [SYN]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 3-Way Handshake: Step 1 [SYN]",
            "message": "TCP Header:\nSource Port: 54122 | Dest Port: 443 (HTTPS)\nSequence Number: 1000 | Ack Number: 0\nFlags: [SYN] | Window Size: 65535\nOptions: MSS 1460, SACK Permitted, Window Scale 7",
            "highlight": ["Flags: [SYN]", "Seq=1000", "Ack=0", "Win=65535", "Port 54122 -> 443"],
            "flags": "[SYN]", "seq": "1000", "ack": "0", "ports": "54122 -> 443",
            "state": "SYN-SENT"
        },
        {
            "time": "0.3s", "direction": "Server -> Client", "type": "TCP [SYN, ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 3-Way Handshake: Step 2 [SYN, ACK]",
            "message": "TCP Header:\nSource Port: 443 | Dest Port: 54122\nSequence Number: 5000 | Ack Number: 1001 (Seq+1)\nFlags: [SYN, ACK] | Window Size: 65535\nOptions: MSS 1460, SACK Permitted",
            "highlight": ["Flags: [SYN, ACK]", "Seq=5000", "Ack=1001", "Port 443 -> 54122"],
            "flags": "[SYN, ACK]", "seq": "5000", "ack": "1001", "ports": "443 -> 54122",
            "state": "SYN-RECEIVED"
        },
        {
            "time": "0.6s", "direction": "Client -> Server", "type": "TCP [ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 3-Way Handshake: Step 3 [ACK] (Established)",
            "message": "TCP Header:\nSource Port: 54122 | Dest Port: 443\nSequence Number: 1001 | Ack Number: 5001 (Seq+1)\nFlags: [ACK] | Window Size: 65535\nConnection State: ESTABLISHED",
            "highlight": ["Flags: [ACK]", "Seq=1001", "Ack=5001", "State: ESTABLISHED"],
            "flags": "[ACK]", "seq": "1001", "ack": "5001", "ports": "54122 -> 443",
            "state": "ESTABLISHED"
        },
        {
            "time": "1.0s", "direction": "Client -> Server", "type": "TCP [PSH, ACK] DATA",
            "layer": "Transport / Application Data",
            "title": "TCP Data Push: Client transmits Request",
            "message": "TCP Header: Source Port: 54122, Dest Port: 443, Seq=1001, Ack=5001, Flags=[PSH, ACK]\nPayload Length: 350 bytes (Carrying HTTP Request / Mail command)\nNext Expected Sequence: 1351",
            "highlight": ["Flags: [PSH, ACK]", "Len=350 bytes", "Next Seq=1351"],
            "flags": "[PSH, ACK]", "seq": "1001", "ack": "5001", "ports": "54122 -> 443",
            "state": "ESTABLISHED"
        },
        {
            "time": "1.3s", "direction": "Server -> Client", "type": "TCP [ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP Acknowledgment: Server confirms data received",
            "message": "TCP Header:\nSource Port: 443 | Dest Port: 54122\nSequence Number: 5001 | Ack Number: 1351 (1001 + 350)\nFlags: [ACK] | Window Size: 65185",
            "highlight": ["Flags: [ACK]", "Ack=1351 (Cumulative)", "Win=65185"],
            "flags": "[ACK]", "seq": "5001", "ack": "1351", "ports": "443 -> 54122",
            "state": "ESTABLISHED"
        },
        {
            "time": "1.7s", "direction": "Server -> Client", "type": "TCP [PSH, ACK] DATA",
            "layer": "Transport / Application Data",
            "title": "TCP Data Push: Server transmits Response Payload",
            "message": "TCP Header: Source Port: 443, Dest Port: 54122, Seq=5001, Ack=1351, Flags=[PSH, ACK]\nPayload Length: 1256 bytes (Carrying HTTP 200 / SMTP response)\nNext Expected Sequence: 6257",
            "highlight": ["Flags: [PSH, ACK]", "Len=1256 bytes", "Next Seq=6257"],
            "flags": "[PSH, ACK]", "seq": "5001", "ack": "1351", "ports": "443 -> 54122",
            "state": "ESTABLISHED"
        },
        {
            "time": "2.0s", "direction": "Client -> Server", "type": "TCP [ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP Acknowledgment: Client confirms response received",
            "message": "TCP Header:\nSource Port: 54122 | Dest Port: 443\nSequence Number: 1351 | Ack Number: 6257 (5001 + 1256)\nFlags: [ACK] | Window Size: 64240",
            "highlight": ["Flags: [ACK]", "Ack=6257", "Payload Verified"],
            "flags": "[ACK]", "seq": "1351", "ack": "6257", "ports": "54122 -> 443",
            "state": "ESTABLISHED"
        },
        {
            "time": "2.4s", "direction": "Client -> Server", "type": "TCP [FIN, ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 4-Way Teardown: Step 1 Client [FIN, ACK]",
            "message": "TCP Header:\nSource Port: 54122 | Dest Port: 443\nSequence Number: 1351 | Ack Number: 6257\nFlags: [FIN, ACK] | State: FIN-WAIT-1\nClient signals it has no more data to transmit.",
            "highlight": ["Flags: [FIN, ACK]", "State: FIN-WAIT-1", "Close Channel"],
            "flags": "[FIN, ACK]", "seq": "1351", "ack": "6257", "ports": "54122 -> 443",
            "state": "FIN-WAIT-1"
        },
        {
            "time": "2.7s", "direction": "Server -> Client", "type": "TCP [ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 4-Way Teardown: Step 2 Server [ACK]",
            "message": "TCP Header:\nSource Port: 443 | Dest Port: 54122\nSequence Number: 6257 | Ack Number: 1352 (Seq+1)\nFlags: [ACK] | Server State: CLOSE-WAIT | Client State: FIN-WAIT-2",
            "highlight": ["Flags: [ACK]", "Ack=1352", "State: CLOSE-WAIT / FIN-WAIT-2"],
            "flags": "[ACK]", "seq": "6257", "ack": "1352", "ports": "443 -> 54122",
            "state": "CLOSE-WAIT"
        },
        {
            "time": "3.0s", "direction": "Server -> Client", "type": "TCP [FIN, ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 4-Way Teardown: Step 3 Server [FIN, ACK]",
            "message": "TCP Header:\nSource Port: 443 | Dest Port: 54122\nSequence Number: 6257 | Ack Number: 1352\nFlags: [FIN, ACK] | Server State: LAST-ACK\nServer closes its half of the connection.",
            "highlight": ["Flags: [FIN, ACK]", "State: LAST-ACK", "Server Closes"],
            "flags": "[FIN, ACK]", "seq": "6257", "ack": "1352", "ports": "443 -> 54122",
            "state": "LAST-ACK"
        },
        {
            "time": "3.3s", "direction": "Client -> Server", "type": "TCP [ACK]",
            "layer": "Transport Layer (L4 - TCP)",
            "title": "TCP 4-Way Teardown: Step 4 Client [ACK] (Closed)",
            "message": "TCP Header:\nSource Port: 54122 | Dest Port: 443\nSequence Number: 1352 | Ack Number: 6258 (Seq+1)\nFlags: [ACK] | Client State: TIME-WAIT (2*MSL) -> CLOSED",
            "highlight": ["Flags: [ACK]", "State: TIME-WAIT -> CLOSED", "Session Terminated"],
            "flags": "[ACK]", "seq": "1352", "ack": "6258", "ports": "54122 -> 443",
            "state": "CLOSED"
        }
    ]
}

def get_integrated_flow(activity: str, include_transport: bool):
    if not include_transport:
        return APP_PROTOCOLS.get(activity, [])

    if activity == "transport":
        return APP_PROTOCOLS["transport"]

    base = APP_PROTOCOLS.get(activity, [])
    if activity == "browsing":
        dns_steps = base[:2]
        http_steps = base[2:]
        tcp_handshake = [
            {
                "time": "0.6s", "direction": "Client -> Web Server", "type": "TCP [SYN]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN] Client -> Port 80/443",
                "message": "TCP Header: Source Port: 49820, Dest Port: 80\nSeq=1000, Ack=0, Flags=[SYN], Win=65535, MSS=1460",
                "highlight": ["SYN", "Seq=1000", "Port 49820 -> 80"],
                "flags": "[SYN]", "seq": "1000", "ack": "0", "ports": "49820 -> 80", "state": "SYN-SENT"
            },
            {
                "time": "0.9s", "direction": "Web Server -> Client", "type": "TCP [SYN, ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN, ACK] Server -> Client",
                "message": "TCP Header: Source Port: 80, Dest Port: 49820\nSeq=5000, Ack=1001, Flags=[SYN, ACK], Win=65535",
                "highlight": ["SYN, ACK", "Seq=5000", "Ack=1001"],
                "flags": "[SYN, ACK]", "seq": "5000", "ack": "1001", "ports": "80 -> 49820", "state": "SYN-RECEIVED"
            },
            {
                "time": "1.1s", "direction": "Client -> Web Server", "type": "TCP [ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [ACK] (Connection Established)",
                "message": "TCP Header: Source Port: 49820, Dest Port: 80\nSeq=1001, Ack=5001, Flags=[ACK], State: ESTABLISHED",
                "highlight": ["ACK", "ESTABLISHED"],
                "flags": "[ACK]", "seq": "1001", "ack": "5001", "ports": "49820 -> 80", "state": "ESTABLISHED"
            }
        ]
        tcp_teardown = [
            {
                "time": "2.1s", "direction": "Client -> Web Server", "type": "TCP [FIN, ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Teardown [FIN, ACK] Client Closes",
                "message": "TCP Header: Flags=[FIN, ACK], Seq=1257, Ack=6257, State: FIN-WAIT-1",
                "highlight": ["FIN, ACK", "Close Connection"],
                "flags": "[FIN, ACK]", "seq": "1257", "ack": "6257", "ports": "49820 -> 80", "state": "FIN-WAIT-1"
            },
            {
                "time": "2.3s", "direction": "Web Server -> Client", "type": "TCP [ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Teardown [ACK] Server Confirms",
                "message": "TCP Header: Flags=[ACK], Seq=6257, Ack=1258, State: CLOSE-WAIT -> CLOSED",
                "highlight": ["ACK", "Connection Closed"],
                "flags": "[ACK]", "seq": "6257", "ack": "1258", "ports": "80 -> 49820", "state": "CLOSED"
            }
        ]
        return dns_steps + tcp_handshake + http_steps + tcp_teardown

    elif activity == "mail":
        dns_steps = base[:2]
        smtp_steps = base[2:]
        tcp_handshake = [
            {
                "time": "0.5s", "direction": "Client -> Mail Server", "type": "TCP [SYN]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN] Client -> Port 25 (SMTP)",
                "message": "TCP Header: Source Port: 50124, Dest Port: 25\nSeq=3000, Ack=0, Flags=[SYN], Win=65535, MSS=1460",
                "highlight": ["SYN", "Port 50124 -> 25 (SMTP)"],
                "flags": "[SYN]", "seq": "3000", "ack": "0", "ports": "50124 -> 25", "state": "SYN-SENT"
            },
            {
                "time": "0.7s", "direction": "Mail Server -> Client", "type": "TCP [SYN, ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN, ACK] Server Ready",
                "message": "TCP Header: Source Port: 25, Dest Port: 50124\nSeq=8000, Ack=3001, Flags=[SYN, ACK]",
                "highlight": ["SYN, ACK", "Seq=8000", "Ack=3001"],
                "flags": "[SYN, ACK]", "seq": "8000", "ack": "3001", "ports": "25 -> 50124", "state": "SYN-RECEIVED"
            },
            {
                "time": "0.9s", "direction": "Client -> Mail Server", "type": "TCP [ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [ACK] (SMTP Channel Established)",
                "message": "TCP Header: Flags=[ACK], Seq=3001, Ack=8001, State: ESTABLISHED",
                "highlight": ["ACK", "ESTABLISHED"],
                "flags": "[ACK]", "seq": "3001", "ack": "8001", "ports": "50124 -> 25", "state": "ESTABLISHED"
            }
        ]
        return dns_steps + tcp_handshake + smtp_steps

    elif activity == "streaming":
        dns_steps = base[:2]
        stream_steps = base[2:]
        tcp_handshake = [
            {
                "time": "0.6s", "direction": "Client -> Web Server", "type": "TCP [SYN]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN] to Media CDN Port 443",
                "message": "TCP Header: Source Port: 54210, Dest Port: 443 (HTTPS)\nSeq=1000, Ack=0, Flags=[SYN], Win=65535",
                "highlight": ["SYN", "Port 443 (HTTPS)"],
                "flags": "[SYN]", "seq": "1000", "ack": "0", "ports": "54210 -> 443", "state": "SYN-SENT"
            },
            {
                "time": "0.9s", "direction": "Web Server -> Client", "type": "TCP [SYN, ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [SYN, ACK] CDN Ready",
                "message": "TCP Header: Source Port: 443, Dest Port: 54210\nSeq=7000, Ack=1001, Flags=[SYN, ACK]",
                "highlight": ["SYN, ACK", "Seq=7000", "Ack=1001"],
                "flags": "[SYN, ACK]", "seq": "7000", "ack": "1001", "ports": "443 -> 54210", "state": "SYN-RECEIVED"
            },
            {
                "time": "1.1s", "direction": "Client -> Web Server", "type": "TCP [ACK]",
                "layer": "Transport Layer (L4 - TCP)",
                "title": "TCP Handshake [ACK] (HLS Channel Established)",
                "message": "TCP Header: Flags=[ACK], Seq=1001, Ack=7001, State: ESTABLISHED",
                "highlight": ["ACK", "ESTABLISHED"],
                "flags": "[ACK]", "seq": "1001", "ack": "7001", "ports": "54210 -> 443", "state": "ESTABLISHED"
            }
        ]
        return dns_steps + tcp_handshake + stream_steps

    return base

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/api/simulate")
def simulate():
    data = request.get_json(silent=True) or {}
    activity = data.get("activity", "browsing")
    include_transport = data.get("include_transport", True)

    if activity not in APP_PROTOCOLS:
        return jsonify({"error": "Unknown activity"}), 400

    steps = get_integrated_flow(activity, include_transport)
    return jsonify({
        "activity": activity,
        "include_transport": include_transport,
        "steps": steps
    })

if __name__ == "__main__":
    app.run(debug=True)
