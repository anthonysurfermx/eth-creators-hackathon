#!/usr/bin/env python3
"""
Quick test to check OpenAI Assistant
"""
import asyncio
from openai import AsyncOpenAI
from config.settings import settings

async def test_assistant():
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        # Check if assistant exists
        assistant = await client.beta.assistants.retrieve(
            assistant_id="asst_QURwCr38KyATBhezf8URzSOT"
        )
        print(f"✅ Assistant found: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Tools: {len(assistant.tools)} tools configured")

        # Try a simple thread
        thread = await client.beta.threads.create()
        print(f"✅ Thread created: {thread.id}")

        # Send a message
        message = await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Test message"
        )
        print(f"✅ Message sent: {message.id}")

        # Try to run (will likely fail without tools, but will show error)
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )
        print(f"✅ Run created: {run.id}")
        print(f"   Status: {run.status}")

        # Wait a bit and check status
        await asyncio.sleep(3)
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"   Final status: {run.status}")

        if run.status == "failed":
            print(f"   ❌ Error: {run.last_error}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_assistant())
