const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const net = require('net');
const config = require('./config.json');
const CLIENT_PORT = config.client_port;
const SERVER_PORT = config.server_port;

const app = express();
app.use(express.static('public'))
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const tcpClient = new net.Socket();
tcpClient.connect(SERVER_PORT, '127.0.0.1', () => {
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

app.get('/config', (req, res) => {
    res.json({ clientPort: CLIENT_PORT });
});

server.listen(CLIENT_PORT, () => {
    console.log(`Server is running on http://localhost:${CLIENT_PORT}`);
});
