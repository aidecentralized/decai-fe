import Peer from 'peerjs';
import { loadOnnxModel } from './model.js';

// Elements
const myPeerIdTextarea = document.getElementById('my-peer-id');
const copyIdButton = document.getElementById('copy-id');
const peerIdInput = document.getElementById('peer-id-input');
const connectButton = document.getElementById('connect-peer');
const chatDiv = document.getElementById('chat');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');
const sendModelButton = document.getElementById('send-model');

let peer = null;
let conn = null;

// Initialize PeerJS
function initializePeer() {
  peer = new Peer();

  peer.on('open', (id) => {
    myPeerIdTextarea.value = id;
  });

  peer.on('connection', (connection) => {
    if (conn && conn.open) {
      connection.close(); // Reject additional connections
      return;
    }

    conn = connection;
    setupConnection();
  });

  peer.on('error', (err) => {
    console.error('PeerJS error:', err);
  });
}

// Setup connection event handlers
function setupConnection() {
  conn.on('open', () => {
    appendMessage('Connection established', 'local');
  });

  conn.on('data', (data) => {
    if (data instanceof ArrayBuffer) {
      handleReceivedModel(data);
    } else {
      appendMessage(`Peer: ${data}`, 'remote');
    }
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
  document.execCommand('copy');
  alert('Peer ID copied to clipboard!');
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
  setupConnection();
};

// Send a message
sendButton.onclick = () => {
  const message = messageInput.value.trim();
  if (!message) return;

  if (conn && conn.open) {
    conn.send(message);
    appendMessage(`You: ${message}`, 'local');
    messageInput.value = '';
  } else {
    alert('No active connection. Please connect to a peer first.');
  }
};

// Handle ONNX Model Sending
sendModelButton.onclick = async () => {
  if (conn && conn.open) {
    const modelBuffer = await loadOnnxModel();  // Load ONNX model as binary
    conn.send(modelBuffer);
    appendMessage('ONNX Model sent', 'local');
  } else {
    alert('No active connection. Please connect to a peer first.');
  }
};

// Handle receiving ONNX model and use ONNX.js for inference
async function handleReceivedModel(data) {
  appendMessage('ONNX Model received', 'remote');

  // Load the ONNX model using ONNX.js
  const session = await ort.InferenceSession.create(data);
  console.log('ONNX Model loaded successfully');

  // Prepare input for the model (example: 2-element vector)
  const inputTensor = new ort.Tensor('float32', [1.0, 2.0], [1, 2]);

  // Run the model
  const results = await session.run({ input: inputTensor });

  // Output the result
  console.log('Inference result:', results);
}

// Initialize PeerJS connection when the page loads
initializePeer();
