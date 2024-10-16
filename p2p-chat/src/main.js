import { createLibp2p } from 'libp2p';
import { webRTCStar } from '@libp2p/webrtc-star';
import { noise } from '@libp2p/noise';
import { mplex } from '@libp2p/mplex';
import { fromString, toString } from 'uint8arrays';

let node; // Store the libp2p node
let connectedStream; // Store the connected stream

// Ensure the code runs after the DOM has loaded
window.onload = async function () {
  const messageList = document.getElementById('messageList');
  const messageInput = document.getElementById('messageInput');
  const sendButton = document.getElementById('sendButton');
  const peerIdTextarea = document.getElementById('yourPeerId');
  const targetPeerIdInput = document.getElementById('targetPeerId');
  const connectButton = document.getElementById('connectButton');

  // Initialize the libp2p node
  async function createNode() {
    try {
      const wrtcStar = webRTCStar(); // WebRTC Star transport

      node = await createLibp2p({
        transports: [wrtcStar.transport],
        connectionEncryption: [noise()],
        streamMuxers: [mplex()],
        peerDiscovery: [wrtcStar.discovery],
      });

      await node.start();

      // Display the Peer ID
      peerIdTextarea.value = node.peerId.toString();

      // Handle incoming connections
      node.handle('/chat/1.0.0', ({ stream }) => {
        connectedStream = stream;
        readFromStream(stream);
        appendMessage('Connected to peer!');
      });

      console.log(`Node started with Peer ID: ${node.peerId}`);
    } catch (error) {
      console.error('Error starting node:', error);
      appendMessage(`Error: ${error.message}`);
    }
  }

  // Connect to a peer using their Peer ID
  async function connectToPeer() {
    const targetPeerId = targetPeerIdInput.value.trim();
    if (!targetPeerId) {
      alert('Please enter a valid peer ID.');
      return;
    }

    try {
      console.log(`Connecting to peer: ${targetPeerId}`);
      const { stream } = await node.dialProtocol(`/p2p/${targetPeerId}`, '/chat/1.0.0');
      connectedStream = stream;
      appendMessage(`Connected to peer: ${targetPeerId}`);
      readFromStream(stream);
    } catch (error) {
      console.error('Connection error:', error);
      appendMessage(`Failed to connect: ${error.message}`);
    }
  }

  // Send a message to the connected peer
  async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !connectedStream) return;

    try {
      await connectedStream.sink([fromString(message)]);
      appendMessage(`You: ${message}`);
      messageInput.value = '';
    } catch (error) {
      console.error('Send error:', error);
      appendMessage(`Failed to send message: ${error.message}`);
    }
  }

  // Read messages from the stream
  async function readFromStream(stream) {
    try {
      for await (const chunk of stream.source) {
        const message = toString(chunk.subarray());
        appendMessage(`Peer: ${message}`);
      }
    } catch (error) {
      console.error('Read error:', error);
      appendMessage(`Read error: ${error.message}`);
    }
  }

  // Append a message to the chat area
  function appendMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = text;
    messageList.appendChild(messageDiv);
  }

  // Add event listeners
  connectButton.addEventListener('click', connectToPeer);
  sendButton.addEventListener('click', sendMessage);

  // Start the node
  await createNode();
};
