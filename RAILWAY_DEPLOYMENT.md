# Deploying Telegram Bot to Railway

This guide explains how to deploy the Telegram bot to Railway.

## Architecture

- **Vercel (unicreators.app)**: Public APIs for frontend
- **Railway**: Telegram bot with webhook

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- GitHub repository pushed
- All API keys ready

## Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `anthonysurfermx/uniswap_sora_bot_v2`
5. Click "Deploy Now"

## Step 2: Add Environment Variables

In Railway project settings, add these variables:

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
SORA2_MODEL=sora-2
GPT_MODEL=gpt-4-turbo-preview

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/webhook

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
STORAGE_TYPE=supabase

# Campaign
CAMPAIGN_START_DATE=2025-01-15
CAMPAIGN_END_DATE=2025-02-15
TIMEZONE=America/Mexico_City

# Config
MAX_VIDEOS_PER_DAY=5
LOG_LEVEL=INFO
```

## Step 3: Configure Start Command

Railway should auto-detect `Procfile`, but verify:

- **Start Command**: `python bot.py`

## Step 4: Get Railway URL

Once deployed, Railway will give you a URL like:
```
https://uniswap-sora-bot-production.up.railway.app
```

## Step 5: Update Webhook

Update the webhook URL in Railway environment variables:

```bash
TELEGRAM_WEBHOOK_URL=https://your-app.railway.app/webhook
```

Then redeploy.

## Step 6: Set Telegram Webhook

Run this command locally:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.railway.app/webhook",
    "secret_token": "YOUR_WEBHOOK_SECRET"
  }'
```

## Step 7: Verify Deployment

1. Check Railway logs for "✅ Bot started"
2. Send `/start` to your Telegram bot
3. Bot should respond with welcome message

## Monitoring

### View Logs
- Go to Railway project
- Click on deployment
- View real-time logs

### Check Bot Status
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

## Troubleshooting

### Bot Not Responding
1. Check Railway logs for errors
2. Verify webhook is set correctly
3. Check environment variables

### Build Failures
1. Check Railway build logs
2. Verify `requirements.txt` is correct
3. Ensure Python 3.11+ is used

### Database Connection Issues
1. Verify Supabase credentials
2. Check Supabase is accessible from Railway
3. Review database logs

## Costs

- **Free tier**: $5 credit (enough for testing)
- **Hobby plan**: $5/month (recommended for production)

## Production Checklist

- [ ] All environment variables configured
- [ ] Webhook set to Railway URL
- [ ] Bot responding to /start command
- [ ] Video generation working
- [ ] Database connected
- [ ] Logs show no errors
- [ ] Frontend connected to Vercel APIs

---

**Questions?** Check Railway docs: https://docs.railway.app
