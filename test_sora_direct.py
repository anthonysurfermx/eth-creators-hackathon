"""
Test Sora 2 API with direct HTTP calls
"""
import asyncio
import httpx
from config.settings import settings

async def test_sora_direct():
    print("=" * 60)
    print("Testing Sora 2 API - Direct HTTP Call")
    print("=" * 60)
    print(f"API Key: {settings.openai_api_key[:20]}...")
    print(f"Model: {settings.sora2_model}")
    print()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Attempting to create video with Sora 2...")

            response = await client.post(
                "https://api.openai.com/v1/videos",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.sora2_model,
                    "prompt": "A cat playing piano",
                    "size": "720x1280",
                    "seconds": "4"
                }
            )

            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            print()

            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! Video job created:")
                print(f"  Job ID: {result.get('id')}")
                print(f"  Status: {result.get('status')}")
                print(f"  Model: {result.get('model')}")
                print()
                print("🎉 You have Sora 2 API access!")
            elif response.status_code == 404:
                print("❌ 404 Not Found")
                print("💡 Diagnosis: Sora 2 endpoint not available for your account")
                print("   Action: Request access at https://platform.openai.com/sora")
            elif response.status_code == 403:
                print("❌ 403 Forbidden")
                print("💡 Diagnosis: Your account doesn't have Sora 2 access")
                print("   Action: Request access at https://platform.openai.com/sora")
            elif response.status_code == 401:
                print("❌ 401 Unauthorized")
                print("💡 Diagnosis: API key issue")
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"Message: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sora_direct())
