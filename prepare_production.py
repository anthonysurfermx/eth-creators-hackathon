#!/usr/bin/env python3
"""
Production Readiness Checker
Validates all requirements before deployment
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking environment variables...")

    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("💡 Copy .env.example to .env and fill in your values")
        return False

    required_vars = [
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_WEBHOOK_SECRET",
        "TELEGRAM_WEBHOOK_URL",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "STORAGE_TYPE",
        "CAMPAIGN_START_DATE",
        "CAMPAIGN_END_DATE",
        "TIMEZONE"
    ]

    env_content = env_path.read_text()
    missing = []

    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=\n" in env_content:
            missing.append(var)

    if missing:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        return False

    print("✅ All required environment variables present")
    return True


def check_database_videos():
    """Check database has valid videos"""
    print("\n🔍 Checking database videos...")

    try:
        from db.client import Database
        db = Database()

        result = db.client.table("videos").select("id, video_url, status").eq("status", "ready").execute()
        videos = result.data

        if not videos:
            print("⚠️  No ready videos in database")
            print("💡 Users will be able to create videos once deployed")
            return True

        # Check if videos have valid URLs (not placeholders)
        valid_videos = [v for v in videos if v.get("video_url") and "supabase" in v["video_url"]]

        print(f"✅ {len(valid_videos)} videos ready for display")
        if len(valid_videos) < len(videos):
            print(f"⚠️  {len(videos) - len(valid_videos)} videos have invalid URLs (will be hidden)")

        return True

    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


def check_timezone():
    """Check timezone configuration"""
    print("\n🔍 Checking timezone...")

    try:
        from config.settings import settings
        tz = ZoneInfo(settings.timezone)
        now = datetime.now(tz)

        print(f"✅ Timezone: {settings.timezone}")
        print(f"   Current time: {now.strftime('%Y-%m-%d %I:%M %p')}")
        return True

    except Exception as e:
        print(f"❌ Timezone check failed: {e}")
        return False


def check_campaign_dates():
    """Check campaign dates are valid"""
    print("\n🔍 Checking campaign dates...")

    try:
        from config.settings import settings
        from datetime import datetime

        start = datetime.strptime(settings.campaign_start_date, "%Y-%m-%d")
        end = datetime.strptime(settings.campaign_end_date, "%Y-%m-%d")

        if end <= start:
            print("❌ Campaign end date must be after start date")
            return False

        days = (end - start).days
        print(f"✅ Campaign duration: {days} days")
        print(f"   Start: {settings.campaign_start_date}")
        print(f"   End: {settings.campaign_end_date}")

        return True

    except Exception as e:
        print(f"❌ Campaign dates check failed: {e}")
        return False


def check_files():
    """Check required files exist"""
    print("\n🔍 Checking project files...")

    required_files = [
        "app.py",
        "requirements.txt",
        "vercel.json",
        ".env.example",
        "VERCEL_DEPLOYMENT.md"
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False

    print("✅ All required files present")
    return True


def check_gitignore():
    """Check .gitignore protects sensitive files"""
    print("\n🔍 Checking .gitignore...")

    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("⚠️  .gitignore not found")
        return True

    content = gitignore_path.read_text()

    if ".env" not in content:
        print("❌ .env not in .gitignore - your secrets could be exposed!")
        return False

    print("✅ .gitignore properly configured")
    return True


def check_storage():
    """Check storage configuration"""
    print("\n🔍 Checking storage configuration...")

    try:
        from config.settings import settings

        if settings.storage_type != "supabase":
            print(f"⚠️  Storage type is '{settings.storage_type}', expected 'supabase'")
            print("💡 For production, Supabase Storage is recommended")
        else:
            print("✅ Storage configured for Supabase")

        return True

    except Exception as e:
        print(f"❌ Storage check failed: {e}")
        return False


def main():
    print("=" * 80)
    print("🚀 PRODUCTION READINESS CHECK")
    print("=" * 80)

    checks = [
        check_files(),
        check_gitignore(),
        check_env_file(),
        check_timezone(),
        check_campaign_dates(),
        check_storage(),
        check_database_videos()
    ]

    print("\n" + "=" * 80)

    if all(checks):
        print("✅ ALL CHECKS PASSED - Ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Commit and push to GitHub")
        print("2. Follow VERCEL_DEPLOYMENT.md instructions")
        print("3. Configure environment variables in Vercel")
        print("4. Set Telegram webhook to your Vercel URL")
        print("5. Test the bot in production")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Fix issues before deployment")
        print("\n💡 Review the errors above and:")
        print("1. Fill in missing environment variables")
        print("2. Ensure all required files are present")
        print("3. Verify database connection")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
