import asyncio
import websockets
import json
from collections import defaultdict

sessions = defaultdict(list)

async def signaling(websocket):
    async for message in websocket:
        print(f"Received message:")  # Debugging received data
        try:
            data = json.loads(message)

            # SDP or ICE candidate handling
            if "sdp" in data or "candidate" in data:
                session_code = websocket.session_code
                target_peer = data.get("target")  # Identify the target peer
                print(f"Relaying message to {target_peer} in session {session_code}")

                # Relay message to the target peer
                for peer in sessions[session_code]:
                    print(f"Checking {peer.remote_address} against {target_peer}")
                    if all(a == b for a, b in zip(peer.remote_address, target_peer)):
                        print(f"Relaying message to {peer.remote_address}, {data['sdp']['type']}, target: {data.get('target')}, source: {data.get('source')}")
                        await peer.send(json.dumps(data))
                continue

            if data["action"] == "join_session":
                session_code = data["session_code"]
                max_users = data["max_users"]

                # Attach session code to the websocket object
                websocket.session_code = session_code
                sessions[session_code].append(websocket)

                if len(sessions[session_code]) == max_users:
                    print(f"Session {session_code} is ready, sending {[c.remote_address for c in sessions[session_code]]}")
                    for conn in sessions[session_code]:
                        await conn.send(json.dumps({
                            "action": "start_session",
                            # "peers": [c.remote_address for c in sessions[session_code] if c != conn]
                            "peers": [c.remote_address for c in sessions[session_code]]
                        }))
                    # del sessions[session_code]
                continue

            print("Unrecognized message format:", data)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def main():
    async with websockets.serve(signaling, "localhost", 8765):
        await asyncio.Future()  # run forever

# Run the WebSocket server within an event loop
asyncio.run(main())
