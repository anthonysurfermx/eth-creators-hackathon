"""
Test Sora 2 API access directly
"""
import asyncio
from openai import AsyncOpenAI
from config.settings import settings

async def test_sora_access():
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    print("=" * 60)
    print("Testing Sora 2 API Access")
    print("=" * 60)
    print(f"API Key: {settings.openai_api_key[:20]}...")
    print(f"Model: {settings.sora2_model}")
    print()

    try:
        print("Attempting to create video with Sora 2...")
        response = await client.videos.create(
            model=settings.sora2_model,
            prompt="A cat playing piano",
            size="1024x1808",
            seconds="5"
        )

        print("✅ SUCCESS! Video job created:")
        print(f"  Job ID: {response.id}")
        print(f"  Status: {response.status}")
        print(f"  Model: {response.model}")
        print()
        print("🎉 You have Sora 2 API access!")

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print()

        # Check specific error types
        if "404" in str(e) or "not found" in str(e).lower():
            print("💡 Diagnosis: Sora 2 API endpoint not available for your account")
            print("   Action needed: Request access at https://platform.openai.com/sora")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("💡 Diagnosis: Account doesn't have Sora 2 access")
            print("   Action needed: Request access at https://platform.openai.com/sora")
        elif "401" in str(e) or "unauthorized" in str(e).lower():
            print("💡 Diagnosis: API key issue")
            print("   Action needed: Check your API key")
        else:
            print("💡 Diagnosis: Unknown error - might need Sora 2 access")

        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sora_access())
