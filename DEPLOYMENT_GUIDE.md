# OpenAI Realtime SIP Call Handler - Deployment Guide

## Overview

This service connects incoming SIP calls (via Vobiz telephony) to OpenAI's Realtime API, enabling AI-powered voice conversations. When someone calls your Vobiz number, the AI answers and has a real-time conversation with the caller.

## Architecture

```
Caller → Vobiz SIP Trunk → OpenAI SIP Endpoint → Webhook → Your Service → OpenAI Realtime API
```

**Flow:**
1. Caller dials your Vobiz number (+918046733659)
2. Vobiz routes call to OpenAI's SIP endpoint
3. OpenAI sends webhook to your service
4. Your service accepts the call via OpenAI API
5. WebSocket connection established for audio streaming
6. AI converses with caller in real-time

---

## Prerequisites

### Required Accounts & Credentials

1. **OpenAI Account**
   - API Key (starts with `sk-`)
   - Project ID (starts with `proj_`)
   - Webhook Secret (starts with `whsec_`)
   - Optional: Prompt ID (starts with `pmpt_`)

2. **Vobiz Account**
   - SIP Trunk configured
   - Phone number assigned (+918046733659)

3. **Development Environment**
   - Python 3.8 or higher
   - ngrok installed (for local testing)
   - Internet connection

---

## Step 1: Vobiz Configuration

### 1.1 Configure SIP Trunk

**Already Completed ✓**

Your Vobiz trunk is configured with:
- **Trunk Name:** openai inbound call
- **Trunk ID:** cd101042-748c-4002-a110-2e5f490f4993
- **Phone Number:** +918046733659
- **Primary URI:** `proj_r9BlSVZT8fTiZqmL5BwIN4z8@sip.api.openai.com`
- **Status:** Enabled

**No action needed** - Vobiz is already routing calls to OpenAI's SIP endpoint.

---

## Step 2: Service Installation

### 2.1 Download the Service

Extract the service files to a directory on your server.

### 2.2 Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` file with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_PROJECT_ID=proj_r9BlSVZT8fTiZqmL5BwIN4z8
OPENAI_WEBHOOK_SECRET=whsec-your-webhook-secret-here
OPENAI_PROMPT_ID=pmpt_69b443cf6f088190a704075d0ce92ae30555b4ac58111073

# Debug (set to false in production)
SKIP_SIGNATURE_VALIDATION=false

# Vobiz Configuration
VOBIZ_PHONE_NUMBER=+918046733659

# Service Configuration
SERVICE_PORT=8000

# AI Configuration
AI_INSTRUCTIONS=You are a helpful customer support agent
AI_VOICE=alloy
```

**Important:** Replace placeholder values with your actual credentials from OpenAI platform.

---

## Step 3: OpenAI Platform Configuration

### 3.1 Get Your Credentials

1. **API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create or copy your API key

2. **Project ID:**
   - Go to https://platform.openai.com/settings/organization/general
   - Copy your Project ID (format: `proj_xxxxx`)

3. **Webhook Secret:**
   - Go to https://platform.openai.com/settings/organization/webhooks
   - Create a new webhook (see Step 3.2)
   - Copy the webhook secret (format: `whsec_xxxxx`)

### 3.2 Configure Webhook

**CRITICAL STEP:** OpenAI needs to know where to send incoming call notifications.

1. Start your service (see Step 4)
2. Copy the ngrok URL displayed (e.g., `https://abc123.ngrok.io`)
3. Go to https://platform.openai.com/settings/organization/webhooks
4. Click "Create Webhook"
5. Configure:
   - **Endpoint URL:** `https://abc123.ngrok.io/webhook/incoming`
   - **Event Type:** Select `realtime.call.incoming`
   - **Description:** Vobiz SIP Call Handler
6. Click "Create"
7. **Copy the webhook secret** and update `.env` file
8. Restart your service

---

## Step 4: Running the Service

### 4.1 Local Testing (with ngrok)

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the service
python app.py
```

The service will:
1. Start ngrok tunnel automatically
2. Display the public webhook URL
3. Start the HTTP server

**Output Example:**
```
============================================================
✓ Ngrok tunnel established!
============================================================
Public URL: https://abc123.ngrok.io
Webhook Endpoint: https://abc123.ngrok.io/webhook/incoming
Health Check: https://abc123.ngrok.io/health
============================================================

Configure this webhook URL in OpenAI platform:
https://abc123.ngrok.io/webhook/incoming
============================================================
```

**Copy the webhook URL** and configure it in OpenAI platform (Step 3.2).

### 4.2 Production Deployment

For production, deploy to a server with a static public URL:

**Recommended Platforms:**
- **Railway:** Easy Python deployment with automatic HTTPS
- **Render:** Free tier available with HTTPS
- **AWS EC2/Lightsail:** Full control with nginx + Let's Encrypt
- **Google Cloud Run:** Serverless with automatic HTTPS
- **DigitalOcean App Platform:** Simple deployment

**Production Requirements:**
- HTTPS enabled (required by OpenAI)
- Static public URL (not ngrok)
- Python 3.8+ runtime
- Port 8000 accessible (or configure `SERVICE_PORT`)

**Production Configuration:**
1. Set `SKIP_SIGNATURE_VALIDATION=false` in `.env`
2. Use a production WSGI server (e.g., gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
3. Configure webhook with your production URL

---

## Step 5: Testing

### 5.1 Test Webhook Endpoint

In OpenAI platform webhook settings:
1. Click "Send test event"
2. Select event type: `realtime.call.incoming`
3. Click "Send"

**Expected Result:**
- Service logs show "Received webhook"
- OpenAI shows "Received HTTP 200"

### 5.2 Test Real Call

1. Call your Vobiz number: **+918046733659**
2. The AI should answer within 2-3 seconds
3. Have a conversation with the AI

**Expected Logs:**
```
Received webhook at...
Incoming call: [call_id]
Call accepted via API
WebSocket connected for call...
Session created for call...
```

---

## Troubleshooting

### Issue: Webhook Returns 401 (Invalid Signature)

**Cause:** Webhook secret mismatch

**Solution:**
1. Verify `OPENAI_WEBHOOK_SECRET` in `.env` matches OpenAI platform
2. Ensure no extra spaces or quotes in `.env`
3. Restart service after updating `.env`

**Temporary Workaround:**
- Set `SKIP_SIGNATURE_VALIDATION=true` in `.env` (testing only)
- **Never use in production!**

### Issue: Call Gets 500 Error from OpenAI

**Cause:** Webhook not configured or unreachable

**Solution:**
1. Verify webhook is configured in OpenAI platform
2. Ensure ngrok URL is correct and accessible
3. Check service is running and logs show no errors
4. Test webhook with "Send test event" button

### Issue: "No session found for call_id"

**Cause:** Test event with fake call ID

**Solution:**
- This is expected for test events
- Make a real call to test actual functionality

### Issue: ngrok Not Found

**Cause:** ngrok not installed

**Solution:**
- Download from https://ngrok.com/download
- Windows: `choco install ngrok`
- Mac: `brew install ngrok`

### Issue: Port 8000 Already in Use

**Solution:**
1. Change `SERVICE_PORT` in `.env` to another port (e.g., 8001)
2. Restart service

---

## Configuration Reference

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key | `sk-proj-...` |
| `OPENAI_PROJECT_ID` | Yes | OpenAI project ID | `proj_r9BlSVZT8fTiZqmL5BwIN4z8` |
| `OPENAI_WEBHOOK_SECRET` | Yes | Webhook signature secret | `whsec_...` |
| `OPENAI_PROMPT_ID` | No | Custom prompt template | `pmpt_...` |
| `SKIP_SIGNATURE_VALIDATION` | No | Skip webhook validation (testing only) | `false` |
| `VOBIZ_PHONE_NUMBER` | No | Your Vobiz phone number | `+918046733659` |
| `SERVICE_PORT` | No | HTTP server port | `8000` |
| `AI_INSTRUCTIONS` | No | System instructions for AI | `You are a helpful agent` |
| `AI_VOICE` | No | Voice selection | `alloy` |

### Available Voices

- `alloy` (default) - Neutral, balanced
- `echo` - Male, clear
- `shimmer` - Female, warm
- `fable` - British accent
- `onyx` - Deep, authoritative
- `nova` - Energetic
- `sage` - Calm, wise

---

## Monitoring

### Service Logs

The service logs all significant events to stdout:

```
2026-03-13 23:15:48 - server - INFO - Received webhook
2026-03-13 23:15:48 - server - INFO - Incoming call: rtc_xxx
2026-03-13 23:15:48 - call_manager - INFO - Call accepted
2026-03-13 23:15:48 - openai_client - INFO - Accepting call
2026-03-13 23:15:49 - websocket_handler - INFO - WebSocket connected
2026-03-13 23:15:49 - websocket_handler - INFO - Session created
```

### Health Check

Check service status:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-13T17:45:48.012523"
}
```

---

## Security Considerations

### Production Checklist

- [ ] Set `SKIP_SIGNATURE_VALIDATION=false`
- [ ] Use HTTPS (required by OpenAI)
- [ ] Keep `.env` file secure (never commit to git)
- [ ] Use production WSGI server (not Flask dev server)
- [ ] Enable firewall rules (allow only necessary ports)
- [ ] Monitor logs for suspicious activity
- [ ] Rotate API keys periodically

### Webhook Security

The service validates webhook signatures using HMAC-SHA256 to ensure requests are from OpenAI. Never disable signature validation in production.

---

## Support

### Getting Help

1. Check service logs for error messages
2. Verify all configuration in `.env`
3. Test webhook with "Send test event" in OpenAI platform
4. Check Vobiz trunk status is "Enabled"

### Common Issues

- **401 Unauthorized:** Webhook secret mismatch
- **404 Not Found:** Incorrect webhook URL
- **500 Server Error:** Service not running or crashed
- **Connection Timeout:** Network/firewall issues

---

## Appendix

### Project Structure

```
sip-realtime-handler/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (DO NOT COMMIT)
├── .env.example          # Configuration template
├── README.md             # Quick start guide
├── DEPLOYMENT_GUIDE.md   # This file
├── start.bat             # Windows startup script
└── src/
    ├── __init__.py
    ├── config.py         # Configuration management
    ├── logger.py         # Logging setup
    ├── server.py         # HTTP server & webhook handler
    ├── webhook_validator.py  # Webhook signature validation
    ├── call_manager.py   # Call lifecycle management
    ├── openai_client.py  # OpenAI API client
    └── websocket_handler.py  # WebSocket connection handler
```

### Version Information

- **Service Version:** 1.0.0
- **Python Version:** 3.8+
- **OpenAI API:** Realtime API v1
- **Last Updated:** March 2026
