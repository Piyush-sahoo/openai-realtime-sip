from flask import Flask, request, Response
from dotenv import load_dotenv
import asyncio
import json
import os
import requests
import threading
import websockets

load_dotenv()

app = Flask(__name__)

# Configuration
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_WEBHOOK_SECRET = os.environ["OPENAI_WEBHOOK_SECRET"]
SKIP_SIGNATURE_VALIDATION = os.getenv("SKIP_SIGNATURE_VALIDATION", "false").lower() == "true"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8000"))

AUTH_HEADER = {
    "Authorization": "Bearer " + OPENAI_API_KEY
}

# Call accept payload — configures the realtime session
call_accept = {
    "type": "realtime",
    "model": "gpt-realtime",
    "instructions": os.getenv(
        "AI_INSTRUCTIONS",
        "You are a helpful customer support agent. Always respond in English."
    ),
}

# Initial response.create — tells the AI what to say first
response_create = {
    "type": "response.create",
    "response": {
        "instructions": os.getenv(
            "AI_GREETING",
            "Say to the user 'Thank you for calling, how can I help you'"
        ),
    },
}


async def websocket_task(call_id):
    """Connect to the realtime WebSocket and log all events."""
    try:
        async with websockets.connect(
            "wss://api.openai.com/v1/realtime?call_id=" + call_id,
            extra_headers=AUTH_HEADER,
        ) as websocket:
            await websocket.send(json.dumps(response_create))
            print(f"[{call_id}] response.create sent")

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                msg_type = data.get("type", "")

                # Skip logging raw audio deltas (too noisy)
                if msg_type == "response.audio.delta":
                    continue

                print(f"[{call_id}] {msg_type}")

                if msg_type == "error":
                    print(f"[{call_id}] ERROR: {data}")
                elif msg_type == "response.output_audio_transcript.done":
                    print(f"[{call_id}] AI said: {data.get('transcript', '')}")

    except websockets.exceptions.ConnectionClosed:
        print(f"[{call_id}] WebSocket closed")
    except Exception as e:
        print(f"[{call_id}] WebSocket error: {e}")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy"}, 200


@app.route("/webhook/incoming", methods=["POST"])
def webhook():
    # Signature validation
    if SKIP_SIGNATURE_VALIDATION:
        print("WARNING: Skipping signature validation (debug mode)")
    else:
        # TODO: Implement HMAC-SHA256 validation or use openai SDK
        pass

    data = request.get_json()
    if not data:
        return Response(status=200)

    event_type = data.get("type")
    print(f"Webhook event: {event_type}")

    if event_type != "realtime.call.incoming":
        # Accept non-call events (e.g. OpenAI webhook verification pings)
        return Response(status=200)

    call_id = data.get("data", {}).get("call_id")
    if not call_id:
        # Test events from OpenAI dashboard don't have a real call_id
        print("No call_id found (likely a test event) — ignoring")
        return Response(status=200)

    print(f"Incoming call: {call_id}")

    # Accept the call via REST API
    accept_resp = requests.post(
        f"https://api.openai.com/v1/realtime/calls/{call_id}/accept",
        headers={**AUTH_HEADER, "Content-Type": "application/json"},
        json=call_accept,
    )
    print(f"Accept response: {accept_resp.status_code} {accept_resp.text}")

    if accept_resp.status_code == 200:
        # Monitor the call via WebSocket in a background thread
        threading.Thread(
            target=lambda: asyncio.run(websocket_task(call_id)),
            daemon=True,
        ).start()
    else:
        print(f"Failed to accept call: {accept_resp.text}")

    return Response(status=200)


if __name__ == "__main__":
    print(f"Starting server on port {SERVICE_PORT}")
    print(f"Webhook URL: POST /webhook/incoming")
    print(f"Health check: GET /health")
    app.run(host="0.0.0.0", port=SERVICE_PORT, debug=False)
