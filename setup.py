#!/usr/bin/env python3
"""
Setup Helper Script
Validates environment and helps configure the bot
"""
import os
import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and is configured"""
    env_path = Path(".env")

    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📝 Creating .env from .env.example...")

        example_path = Path(".env.example")
        if example_path.exists():
            import shutil
            shutil.copy(example_path, env_path)
            print("✅ .env file created!")
        else:
            print("❌ .env.example not found!")
            return False

    print("✅ .env file exists")

    # Check critical variables
    required_vars = [
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]

    missing = []

    with open(env_path) as f:
        content = f.read()

        for var in required_vars:
            if f"{var}=your-" in content or f"{var}=sk-proj-xxx" in content:
                missing.append(var)

    if missing:
        print(f"\n⚠️  Missing configuration for: {', '.join(missing)}")
        print("\n📝 Please edit .env and configure these variables:")
        for var in missing:
            print(f"   - {var}")
        return False

    print("✅ All required variables configured")
    return True


def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n📦 Checking dependencies...")

    required_packages = [
        "fastapi",
        "uvicorn",
        "python-telegram-bot",
        "openai",
        "supabase",
        "loguru"
    ]

    missing = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\n📝 Install with:")
        print("   pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies installed")
    return True


def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg...")

    import subprocess

    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"  ✅ FFmpeg installed: {version}")
            return True
        else:
            print("  ❌ FFmpeg not working properly")
            return False

    except FileNotFoundError:
        print("  ❌ FFmpeg not installed")
        print("\n📝 Install FFmpeg:")
        print("   macOS: brew install ffmpeg")
        print("   Linux: apt-get install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org")
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking FFmpeg: {e}")
        return False


def check_assets():
    """Check if assets directory exists"""
    print("\n🖼️  Checking assets...")

    assets_dir = Path("assets")

    if not assets_dir.exists():
        print("  ⚠️  assets/ directory not found, creating...")
        assets_dir.mkdir()
        print("  ✅ assets/ directory created")
    else:
        print("  ✅ assets/ directory exists")

    logo_path = assets_dir / "uniswap_logo.png"

    if not logo_path.exists():
        print("  ⚠️  Uniswap logo not found")
        print("\n📝 Download logo:")
        print("   curl -o assets/uniswap_logo.png https://raw.githubusercontent.com/Uniswap/brand-assets/main/logo/uniswap-unicorn-logo.png")
        print("\n  Note: Bot will work without logo (watermarking will be skipped)")
        return True  # Not critical
    else:
        print("  ✅ Uniswap logo found")
        return True


def check_database():
    """Check Supabase connection"""
    print("\n🗄️  Checking database...")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        from db.client import db

        # Try to access client
        if db.client:
            print("  ✅ Supabase client initialized")

            # Try a simple query
            try:
                result = db.client.table("creators").select("count", count="exact").limit(0).execute()
                print("  ✅ Database connection working")
                return True
            except Exception as e:
                print(f"  ⚠️  Database query failed: {e}")
                print("\n  Make sure you've run the schema.sql:")
                print("     psql -h your-host -d postgres -f db/schema.sql")
                return False
        else:
            print("  ❌ Failed to initialize Supabase client")
            return False

    except Exception as e:
        print(f"  ❌ Database check failed: {e}")
        print("\n  Make sure your Supabase credentials are correct in .env")
        return False


def generate_webhook_secret():
    """Generate a secure webhook secret"""
    import secrets
    secret = secrets.token_urlsafe(32)
    print(f"\n🔐 Generated webhook secret:")
    print(f"   {secret}")
    print("\n   Add to .env:")
    print(f"   TELEGRAM_WEBHOOK_SECRET={secret}")


def print_summary():
    """Print setup summary"""
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)

    print("\n✅ COMPLETED:")
    print("   • watermark.py created")
    print("   • /posted command implemented")
    print("   • .env file ready")
    print("   • Helper scripts created")

    print("\n📝 TODO:")
    print("   1. Configure .env with your API keys")
    print("   2. Setup Supabase database (run db/schema.sql)")
    print("   3. Install FFmpeg (optional for watermarking)")
    print("   4. Download Uniswap logo (optional)")
    print("   5. Run: uvicorn app:app --reload")

    print("\n🚀 NEXT STEPS:")
    print("   • Local testing: python setup.py")
    print("   • Start bot: uvicorn app:app --reload")
    print("   • Test with ngrok: ngrok http 8000")

    print("\n" + "="*60)


def main():
    """Main setup checker"""
    print("🤖 Uniswap Creator Bot - Setup Checker")
    print("="*60)

    checks = [
        ("Environment file", check_env_file),
        ("Dependencies", check_dependencies),
        ("FFmpeg", check_ffmpeg),
        ("Assets", check_assets),
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error checking {name}: {e}")
            results.append((name, False))

    # Database check (optional)
    if results[0][1]:  # If env file is configured
        try:
            db_result = check_database()
            results.append(("Database", db_result))
        except Exception as e:
            print(f"\n⚠️  Database check skipped: {e}")

    # Summary
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    all_passed = all(r[1] for r in results[:2])  # Critical checks

    if all_passed:
        print("\n✅ Setup complete! Ready to run.")
        print("\n🚀 Start the bot:")
        print("   uvicorn app:app --reload")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n📖 See README.md for detailed setup instructions.")

    print("\n💡 Need help?")
    print("   • Webhook secret: python setup.py --generate-secret")
    print("   • Full docs: README.md")


if __name__ == "__main__":
    if "--generate-secret" in sys.argv:
        generate_webhook_secret()
    elif "--summary" in sys.argv:
        print_summary()
    else:
        main()
