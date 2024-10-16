// main.js
import Peer from 'peerjs';

// Elements
const myPeerIdTextarea = document.getElementById('my-peer-id');
const copyIdButton = document.getElementById('copy-id');
const peerIdInput = document.getElementById('peer-id-input');
const connectButton = document.getElementById('connect-peer');
const chatDiv = document.getElementById('chat');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');

let peer = null;
let conn = null;

// Initialize PeerJS
function initializePeer() {
  // Create a new Peer. You can pass an ID or let PeerJS generate one.
  peer = new Peer();

  // When the connection to the PeerJS server is open and the ID is assigned
  peer.on('open', (id) => {
    myPeerIdTextarea.value = id;
  });

  // Handle incoming connections
  peer.on('connection', (connection) => {
    if (conn && conn.open) {
      connection.close(); // Reject additional connections
      return;
    }

    conn = connection;
    setupConnection();
  });

  // Handle errors
  peer.on('error', (err) => {
    console.error(err);
    alert('' + err);
  });
}

// Setup connection event handlers
function setupConnection() {
  conn.on('open', () => {
    appendMessage('Connection established', 'local');
  });

  conn.on('data', (data) => {
    appendMessage(`Peer: ${data}`, 'remote');
  });

  conn.on('close', () => {
    appendMessage('Connection closed', 'local');
    conn = null;
  });
}

// Append messages to the chat
function appendMessage(message, type) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${type}`;
  msgDiv.textContent = message;
  chatDiv.appendChild(msgDiv);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

// Copy Peer ID to clipboard
copyIdButton.onclick = () => {
  myPeerIdTextarea.select();
  myPeerIdTextarea.setSelectionRange(0, 99999); // For mobile devices
  navigator.clipboard.writeText(myPeerIdTextarea.value)
    .then(() => {
      alert('Peer ID copied to clipboard!');
    })
    .catch(err => {
      console.error('Failed to copy!', err);
    });
};

// Connect to another peer
connectButton.onclick = () => {
  const peerId = peerIdInput.value.trim();
  if (!peerId) {
    alert('Please enter a valid Peer ID.');
    return;
  }

  if (conn && conn.open) {
    alert('Already connected to a peer.');
    return;
  }

  conn = peer.connect(peerId);

  conn.on('open', () => {
    appendMessage('Connection established', 'local');
  });

  conn.on('data', (data) => {
    appendMessage(`Peer: ${data}`, 'remote');
  });

  conn.on('close', () => {
    appendMessage('Connection closed', 'local');
    conn = null;
  });

  conn.on('error', (err) => {
    console.error(err);
    alert('Connection error: ' + err);
  });
};

// Send a message
sendButton.onclick = () => {
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  if (conn && conn.open) {
    conn.send(message);
    appendMessage(`You: ${message}`, 'local');
    messageInput.value = '';
  } else {
    alert('No active connection. Please connect to a peer first.');
  }
};

// Optional: Handle Enter key for sending messages
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendButton.click();
  }
});

// Initialize the PeerJS connection when the page loads
initializePeer();
