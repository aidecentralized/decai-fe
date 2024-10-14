import { createLibp2p } from 'libp2p';
import { webSockets } from '@libp2p/websockets';
import { webRTCStar } from '@libp2p/webrtc-star';
import { mplex } from '@libp2p/mplex';
import { noise } from '@libp2p/noise';
import { multiaddr } from '@multiformats/multiaddr';
import { pipe } from 'it-pipe';
import { collect, take } from 'streaming-iterables';
import { fromString, toString } from 'uint8arrays';

let node;
let connectedStream;

const peerIdInput = document.getElementById('yourPeerId');
const addressesTextarea = document.getElementById('yourAddresses');
const targetPeerAddrInput = document.getElementById('targetPeerAddr');
const connectButton = document.getElementById('connectButton');
const messageListDiv = document.getElementById('messageList');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

async function createNode() {
  const wrtcStar = webRTCStar();

  node = await createLibp2p({
    transports: [
      webSockets(),
      wrtcStar.transport
    ],
    connectionEncryption: [noise()],
    streamMuxers: [mplex()],
    peerDiscovery: [
      wrtcStar.discovery
    ]
  });

  await node.start();

  // Display Peer ID and addresses
  const peerId = node.peerId.toString();
  peerIdInput.value = peerId;

  const addresses = node.getMultiaddrs().map(addr => addr.toString()).join('\n');
  addressesTextarea.value = addresses;

  // Handle incoming connections
  node.handle('/chat/1.0.0', ({ stream }) => {
    connectedStream = stream;
    readFromStream(stream);
  });

  node.addEventListener('peer:discovery', (evt) => {
    const peer = evt.detail;
    console.log(`Discovered peer: ${peer.id.toString()}`);
  });
}

async function connectToPeer() {
  const targetAddr = targetPeerAddrInput.value;
  if (!targetAddr) {
    alert('Please enter a valid multiaddress.');
    return;
  }

  try {
    const stream = await node.dialProtocol(multiaddr(targetAddr), '/chat/1.0.0');
    connectedStream = stream;
    readFromStream(stream);
    appendMessage(`Connected to peer: ${targetAddr}`);
  } catch (err) {
    console.error('Connection error:', err);
    appendMessage(`Failed to connect to peer: ${err.message}`);
  }
}

async function sendMessage() {
  const message = messageInput.value;
  if (!message || !connectedStream) {
    return;
  }

  try {
    await pipe(
      [fromString(message)],
      connectedStream.sink
    );
    appendMessage(`You: ${message}`);
    messageInput.value = '';
  } catch (err) {
    console.error('Send error:', err);
    appendMessage(`Failed to send message: ${err.message}`);
  }
}

async function readFromStream(stream) {
  try {
    await pipe(
      stream.source,
      async function (source) {
        for await (const msg of source) {
          const message = toString(msg.subarray());
          appendMessage(`Peer: ${message}`);
        }
      }
    );
  } catch (err) {
    console.error('Read error:', err);
  }
}

function appendMessage(message) {
  const msgDiv = document.createElement('div');
  msgDiv.textContent = message;
  messageListDiv.appendChild(msgDiv);
}

connectButton.addEventListener('click', connectToPeer);
sendButton.addEventListener('click', sendMessage);

createNode();
