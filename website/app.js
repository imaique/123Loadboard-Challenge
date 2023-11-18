const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const net = require('net');

const app = express();
app.use(express.static('public'))
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const tcpClient = new net.Socket();
tcpClient.connect(8080, '127.0.0.1', () => {
    console.log('Connected to Python TCP server');
});

tcpClient.on('data', (data) => {
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(data.toString());
        }
    });
});

wss.on('connection', (ws) => {
    ws.on('message', (message) => {
        tcpClient.write(message);
    });
});

// Serve index.html
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

const PORT = 8081;
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
