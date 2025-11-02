# Deploying Uniswap Sora Bot to Vercel

This guide explains how to deploy the Uniswap Creator Bot backend to Vercel for production use.

## Prerequisites

- Vercel account (free tier works)
- GitHub repository with your code
- All required API keys and credentials ready

## Step 1: Prepare Your Repository

1. **Update `.gitignore`** - Make sure sensitive files are not committed:
```
.env
__pycache__/
*.pyc
venv/
.DS_Store
```

2. **Verify `.env.example`** - Ensure template is complete

3. **Commit and push** all changes to GitHub

## Step 2: Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository (`uniswap_sora_bot_v2`)
4. Select the repository and click "Import"

## Step 3: Configure Build Settings

Vercel will auto-detect Python. Configure these settings:

- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`

## Step 4: Add Environment Variables

Add all variables from `.env.example` in Vercel project settings:

### Required Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here
SORA2_MODEL=sora-2
GPT_MODEL=gpt-4-turbo-preview

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBHOOK_SECRET=your-webhook-secret
TELEGRAM_WEBHOOK_URL=https://your-vercel-app.vercel.app/webhook

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
STORAGE_TYPE=supabase

# Campaign
CAMPAIGN_START_DATE=2025-01-15
CAMPAIGN_END_DATE=2025-02-15
TIMEZONE=America/Mexico_City
```

### Optional Variables

```bash
REDIS_URL=redis://your-redis-url (if using Redis)
SENTRY_DSN=your-sentry-dsn (for error tracking)
LOG_LEVEL=INFO
```

## Step 5: Create `vercel.json`

Create this file in your project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

## Step 6: Update Telegram Webhook

After deployment, get your Vercel URL (e.g., `https://your-app.vercel.app`) and:

1. Update `TELEGRAM_WEBHOOK_URL` in Vercel environment variables
2. Set the webhook using this curl command:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.vercel.app/webhook",
    "secret_token": "YOUR_WEBHOOK_SECRET"
  }'
```

## Step 7: Verify Deployment

1. **Check health endpoint**: Visit `https://your-app.vercel.app/health`
2. **Test API**: Visit `https://your-app.vercel.app/api/videos`
3. **Test bot**: Send `/start` to your Telegram bot

## Step 8: Update Frontend

Update your Lovable frontend `.env`:

```bash
VITE_API_URL=https://your-app.vercel.app
```

## Troubleshooting

### Function Timeout Issues

Vercel has a 10-second timeout on free tier. For long-running Sora 2 requests:

1. **Option A**: Upgrade to Pro ($20/month) for 60-second timeout
2. **Option B**: Use async processing:
   - Bot acknowledges request immediately
   - Process video in background
   - Send notification when complete

### Build Failures

- Check Vercel build logs
- Verify all dependencies in `requirements.txt`
- Ensure Python version compatibility (3.11+)

### Webhook Not Working

- Verify webhook URL is HTTPS
- Check secret token matches
- Review Vercel function logs
- Test webhook locally with ngrok first

## Production Checklist

- [ ] All environment variables set
- [ ] Webhook configured and tested
- [ ] Supabase storage bucket created and public
- [ ] Database migrations run
- [ ] Frontend updated with production API URL
- [ ] Error monitoring configured (Sentry)
- [ ] Rate limiting configured
- [ ] CORS origins restricted (if needed)
- [ ] Campaign dates set correctly

## Monitoring

### View Logs

```bash
vercel logs your-app-name --follow
```

### Check Function Invocations

- Visit Vercel Dashboard > your-project > Analytics
- Monitor function executions and errors

## Scaling Considerations

- **Database**: Supabase free tier supports up to 500MB
- **Storage**: Supabase storage has 1GB free limit
- **Functions**: Vercel free tier has 100GB-hours/month
- **Bandwidth**: 100GB/month on free tier

Monitor usage and upgrade tiers as needed for your campaign.

## Support

- Vercel Docs: https://vercel.com/docs
- Telegram Bot API: https://core.telegram.org/bots/api
- Supabase Docs: https://supabase.com/docs

## Security Notes

1. **Never commit** `.env` to git
2. **Rotate secrets** after deployment
3. **Enable** webhook secret validation
4. **Monitor** unusual API usage
5. **Set** rate limits on endpoints

---

**Ready to deploy?** Push your code and let Vercel handle the rest! 🚀
