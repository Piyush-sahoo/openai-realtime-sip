# OpenAI Realtime SIP Call Handler

AI-powered voice conversations for incoming phone calls using OpenAI's Realtime API and Vobiz telephony.

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your credentials:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_PROJECT_ID=proj_r9BlSVZT8fTiZqmL5BwIN4z8
OPENAI_WEBHOOK_SECRET=your_webhook_secret_here
```

### 3. Run the Service

```bash
python app.py
```

The service will start ngrok automatically and display your webhook URL.

### 4. Configure OpenAI Webhook

1. Copy the webhook URL from the console output
2. Go to https://platform.openai.com/settings/organization/webhooks
3. Create webhook with the URL and select `realtime.call.incoming` event
4. Copy the webhook secret to your `.env` file
5. Restart the service

### 5. Test

Call your Vobiz number: **+918046733659**

The AI will answer and have a conversation with you!

---

## Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions for your team
- **[.env.example](.env.example)** - Configuration template

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_PROJECT_ID` | Your OpenAI project ID |
| `OPENAI_WEBHOOK_SECRET` | Webhook signature secret |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVICE_PORT` | 8000 | HTTP server port |
| `AI_INSTRUCTIONS` | "You are a helpful customer support agent" | AI system prompt |
| `AI_VOICE` | alloy | Voice selection (alloy, echo, shimmer, fable, onyx, nova, sage) |
| `OPENAI_PROMPT_ID` | - | Optional prompt template ID |
| `SKIP_SIGNATURE_VALIDATION` | false | Skip webhook validation (testing only) |

## Architecture

```
Caller → Vobiz → OpenAI SIP → Webhook → Your Service → OpenAI Realtime API
```

1. Caller dials +918046733659
2. Vobiz routes to OpenAI's SIP endpoint
3. OpenAI sends webhook to your service
4. Service accepts call and establishes WebSocket
5. AI converses with caller in real-time

## Troubleshooting

### Webhook Returns 401

**Issue:** Invalid webhook signature

**Solution:** Verify `OPENAI_WEBHOOK_SECRET` matches OpenAI platform

### Call Gets 500 Error

**Issue:** Webhook not configured or unreachable

**Solution:** 
1. Verify webhook is configured in OpenAI platform
2. Ensure service is running and accessible
3. Test with "Send test event" button

### ngrok Not Found

**Solution:** Install ngrok from https://ngrok.com/download

## Production Deployment

For production, deploy to a server with HTTPS and a static URL:

- Railway
- Render
- AWS EC2/Lightsail
- Google Cloud Run
- DigitalOcean App Platform

**Important:** Set `SKIP_SIGNATURE_VALIDATION=false` in production.

## Support

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting and configuration.

## License

Proprietary - Internal Use Only
