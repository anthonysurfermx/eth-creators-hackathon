#!/bin/bash
# Update Telegram webhook to new domain

BOT_TOKEN="8305969739:AAFBLbmimsbc3AJtuuvcSV89ro8ZQSWMS2g"
WEBHOOK_SECRET="KrCR37QybYAGgZ4sgvMTGJmflrKIjoXuC48DqYyFP7s"
WEBHOOK_URL="https://unicreators.app/webhook"

echo "🔄 Updating Telegram webhook to: $WEBHOOK_URL"

curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"${WEBHOOK_URL}\",
    \"secret_token\": \"${WEBHOOK_SECRET}\"
  }"

echo -e "\n\n✅ Webhook updated!"
echo "🔍 Verifying..."

curl "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
