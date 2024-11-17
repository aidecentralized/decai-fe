import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCDataChannel
import websockets


async def run():
    pc = RTCPeerConnection()
    data_channel = pc.createDataChannel("training")  # Ensure data channel exists
    session_code = "mySessionCode"  # Replace with user input
    max_users = 2  # Replace with user input
    rounds = 5
    current_round = 0
    rank = -1

    # Debugging: Log connection state changes
    @pc.on("connectionstatechange")
    def on_connectionstatechange():
        print(f"[DEBUG] Connection state: {pc.connectionState}")

    # Debugging: Log ICE connection state changes
    @pc.on("iceconnectionstatechange")
    def on_iceconnectionstatechange():
        print(f"[DEBUG] ICE connection state: {pc.iceConnectionState}")

    # Debugging: Log ICE candidates as they are generated
    @pc.on("icecandidate")
    async def on_icecandidate(event):
        if event.candidate:
            print(f"[DEBUG] Sending ICE candidate: {event.candidate}")
            await signaling.send(json.dumps({
                "candidate": event.candidate.toJSON(),
                "target": None  # Replace with appropriate peer ID if needed
            }))
        else:
            print("[DEBUG] ICE gathering completed.")

    async with websockets.connect("ws://localhost:8765") as signaling:
        # Join the session
        print("[DEBUG] Joining session...")
        await signaling.send(json.dumps({
            "action": "join_session",
            "session_code": session_code,
            "max_users": max_users
        }))

        # Handle DataChannel events
        @data_channel.on("open")
        def on_open():
            print("[DEBUG] Data channel is open!")

        @data_channel.on("close")
        def on_close():
            print("[DEBUG] Data channel is closed.")

        @data_channel.on("message")
        def on_message(message):
            nonlocal current_round
            print(f"[DEBUG] Received message on DataChannel: {message}")
            data = json.loads(message)
            if "weights" in data and current_round < rounds:
                print(f"[DEBUG] Round {current_round + 1}: Received weights")
                current_round += 1
                asyncio.create_task(simulate_training())
                data_channel.send(json.dumps({"weights": data["weights"], "round": current_round}))

        # Handle messages from the signaling server
        async for message in signaling:
            data = json.loads(message)

            if data.get("action") == "start_session":
                print(f"[DEBUG] Session started. Peers: {data['peers']}")
                # Get client rank by finding the index of the current client in the list of peers
                for ind, [host, port, *_] in enumerate(data["peers"]):
                    if host == signaling.local_address[0] and port == signaling.local_address[1]:
                        rank = ind
                        break
                print(f"[DEBUG] Client rank: {rank}")
                asyncio.create_task(setup_peer_connections(data["peers"], rank, pc, signaling))

            elif "sdp" in data:
                print(f"[DEBUG] Received SDP: {data['sdp']['type']}, data is {data}")
                desc = RTCSessionDescription(sdp=data["sdp"]["sdp"], type=data["sdp"]["type"])

                if desc.type == "offer":
                    # Handle SDP offer
                    if pc.signalingState in ["stable", "have-local-offer"]:
                        print("[DEBUG] Received SDP offer. Setting remote description...")
                        await pc.setRemoteDescription(desc)
                        print("[DEBUG] Creating SDP answer...")
                        answer = await pc.createAnswer()
                        await pc.setLocalDescription(answer)
                        await signaling.send(json.dumps({
                            "sdp": {
                                "type": pc.localDescription.type,
                                "sdp": pc.localDescription.sdp
                            },
                            "target": data["source"],  # Send the answer to the offerer
                            "source": signaling.local_address
                        }))
                    else:
                        print(f"[ERROR] Cannot handle offer in signaling state: {pc.signalingState}")

                elif desc.type == "answer":
                    # Handle SDP answer
                    if pc.signalingState == "have-local-offer":
                        print("[DEBUG] Received SDP answer. Setting remote description...")
                        await pc.setRemoteDescription(desc)
                    else:
                        print(f"[ERROR] Cannot handle answer in signaling state: {pc.signalingState}")


            elif "candidate" in data:
                print("[DEBUG] Received ICE candidate")
                candidate = RTCIceCandidate(
                    component=data["candidate"]["component"],
                    foundation=data["candidate"]["foundation"],
                    protocol=data["candidate"]["protocol"],
                    priority=data["candidate"]["priority"],
                    ip=data["candidate"]["ip"],
                    port=data["candidate"]["port"],
                    type=data["candidate"]["type"],
                    sdpMid=data["candidate"].get("sdpMid"),
                    sdpMLineIndex=data["candidate"].get("sdpMLineIndex"),
                )
                await pc.addIceCandidate(candidate)


async def setup_peer_connections(peers, rank, pc, signaling):
    """Establish peer connections using SDP and ICE."""

    # Only create SDP offer to nodes with lower rank
    for ind, peer in enumerate(peers):
        if ind >= rank:
            break
        print(f"[DEBUG] Creating SDP offer for peer {peer} with rank {ind}")
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        print(f"[DEBUG] SDP offer sent to peer {peer}")
        await signaling.send(json.dumps({
            "sdp": {
                "type": pc.localDescription.type,
                "sdp": pc.localDescription.sdp
            },
            "target": peer,  # Send to the specific peer
            "source": signaling.local_address  # Identify the source peer
        }))


async def simulate_training():
    """Simulate a training round."""
    print("[DEBUG] Simulating training...")
    await asyncio.sleep(1)  # Simulate training time


asyncio.run(run())




# # python_client.py
# import asyncio
# import json
# import time
# from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, RTCDataChannel
# import websockets
# from simple_model import SimpleModel, serialize_weights, deserialize_weights

# async def run():
#     pc = RTCPeerConnection()
#     model = SimpleModel()
#     rounds = 5  # Set the number of rounds here
#     current_round = 0
#     training_complete = False

#     try:
#         # Establish WebSocket connection to the signaling server
#         async with websockets.connect("ws://localhost:8765") as signaling:

#             # Set up the data channel and message handling
#             @pc.on("datachannel")
#             def on_datachannel(channel: RTCDataChannel):
#                 nonlocal current_round, training_complete
#                 print("Data channel established!")

#                 # channel.on("message", lambda message: print(f"Message from JavaScript: {message}"))
#                 # # Send a message to the JavaScript client when the channel opens
#                 # if channel.readyState == "open":
#                 #     channel.send("Hello from Python!")

#                 async def train_and_send():
#                     nonlocal current_round, training_complete

#                     # Define a callback to handle incoming messages
#                     @channel.on("message")
#                     def on_message(message):
#                         nonlocal current_round, training_complete
#                         data = json.loads(message)
#                         if "weights" in data:
#                             # Deserialize received weights
#                             deserialize_weights(model, data["weights"])
#                             print(f"Received updated weights for round {current_round + 1} from JavaScript")
#                             print(f"Current weights: {data['weights']}")
#                             current_round += 1

#                             # If rounds are not complete, send the next weights
#                             if current_round < rounds:
#                                 print(f"Python training round {current_round + 1}")
#                                 time.sleep(1)  # Simulate training time
#                                 weights = serialize_weights(model)
#                                 print(f"Sending weights {weights}")
#                                 channel.send(json.dumps({"weights": weights, "round": current_round}))
#                             else:
#                                 print("Training complete")
#                                 print("Closing data channel and peer connection from Python")
#                                 channel.close()
#                                 asyncio.create_task(pc.close())  # Close peer connection
#                                 training_complete = True

#                     # Start the first round by sending the initial weights
#                     print(f"Python training round {current_round + 1}")
#                     time.sleep(1)  # Simulate training time
#                     weights = serialize_weights(model)
#                     print(f"Sending weights {weights}")
#                     channel.send(json.dumps({"weights": weights, "round": current_round}))

#                 # Start the training and sending process
#                 asyncio.create_task(train_and_send())

#             # Handle incoming WebSocket messages
#             async for message in signaling:
#                 if training_complete:
#                     break
#                 data = json.loads(message)

#                 # Handle SDP (Session Description Protocol) messages
#                 if "sdp" in data:
#                     sdp_data = data["sdp"]
#                     desc = RTCSessionDescription(sdp=sdp_data["sdp"], type=sdp_data["type"])
#                     await pc.setRemoteDescription(desc)
#                     if desc.type == "offer":
#                         answer = await pc.createAnswer()
#                         await pc.setLocalDescription(answer)
#                         sdp = {
#                             "sdp": pc.localDescription.sdp,
#                             "type": pc.localDescription.type
#                         }
#                         await signaling.send(json.dumps({"sdp": sdp}))

                # # Handle ICE (Interactive Connectivity Establishment) candidates
                # elif "candidate" in data:
                #     # Extract the candidate details from the candidate string
                #     candidate_str = data["candidate"]["candidate"]
                #     candidate_parts = candidate_str.split()

                #     # Extract fields based on their positions in the candidate string
                #     candidate = RTCIceCandidate(
                #         component=int(candidate_parts[1]),  # Typically "1" for RTP
                #         foundation=candidate_parts[0].split(":")[1],
                #         protocol=candidate_parts[2].lower(),  # Usually "udp" or "tcp"
                #         priority=int(candidate_parts[3]),
                #         ip=candidate_parts[4],
                #         port=int(candidate_parts[5]),
                #         type=candidate_parts[7],
                #         sdpMid=data["candidate"].get("sdpMid"),
                #         sdpMLineIndex=data["candidate"].get("sdpMLineIndex"),
                #     )

                #     # Add the candidate to the peer connection
                #     await pc.addIceCandidate(candidate)

#     except websockets.exceptions.ConnectionClosedError as e:
#         print(f"Connection closed with error: {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")

#     finally:
#         # Close the peer connection when the WebSocket connection is closed
#         await pc.close()

# # Run the Python client within an asyncio event loop
# asyncio.run(run())
