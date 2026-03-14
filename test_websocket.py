"""
Quick test script to verify WebSocket connectivity to OpenAI Realtime API
"""
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_websocket():
    api_key = os.getenv("OPENAI_API_KEY")
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    print(f"Testing WebSocket connection...")
    print(f"URL: {url}")
    print(f"API Key: {api_key[:20]}...")
    
    try:
        print("Connecting...")
        ws = await asyncio.wait_for(
            websockets.connect(url, extra_headers=headers),
            timeout=10.0
        )
        print("✓ Connected successfully!")
        
        print("Waiting for first message...")
        message = await asyncio.wait_for(ws.recv(), timeout=5.0)
        event = json.loads(message)
        print(f"✓ Received: {event.get('type')}")
        print(f"Full message: {json.dumps(event, indent=2)}")
        
        await ws.close()
        print("✓ Test completed successfully")
        
    except asyncio.TimeoutError:
        print("✗ Connection timeout - check network/firewall")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"✗ Invalid status code: {e.status_code}")
        print(f"  This usually means authentication failed")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
