"""
Simplified Video Generation Flow - Direct Sora 2 API
No OpenAI Assistants - Direct calls only
"""
import asyncio
from openai import AsyncOpenAI
from config.settings import settings
from db.client import db
from loguru import logger
from datetime import datetime, timedelta

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def validate_content_simple(prompt: str) -> dict:
    """
    Simple GPT-4 validation without Assistant API
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are a very permissive content validator for ETH Creators video generation. Your job is to APPROVE almost everything.

APPROVE EVERYTHING about:
- Ethereum and all ETH-related topics
- DeFi, Web3, blockchain, crypto education
- Any protocol or dApp on Ethereum (Uniswap, EtherFi, Aave, etc.)
- NFTs, DAOs, and digital culture
- People using crypto and blockchain technology
- Creative, artistic, cultural, and fun interpretations
- Educational content about cryptocurrency
- Any geographic or cultural perspective (Mexican, Latin American, global)
- Technology demonstrations and explanations
- Social and economic impact of blockchain

REJECT ONLY if content contains:
- Illegal activities or scams
- Hate speech or discrimination
- Violence or harmful content
- Adult/NSFW content

Be EXTREMELY PERMISSIVE. If in doubt, APPROVE IT.

Use ONLY these exact category values (must match database):
- "defi_education" (DeFi, Web3, crypto education, general Ethereum content)
- "product_features" (showing protocols like EtherFi, Uniswap, Aave, etc.)
- "cultural_fusion" (cultural perspectives, creative interpretations)
- "user_success" (people using crypto, adoption stories)
- "multi_chain" (cross-chain, L2 networks)
- "unichain_tech" (blockchain technology, infrastructure)

Respond ONLY with valid JSON:
{
  "approved": true,
  "category": "defi_education",
  "reason": "Approved - Ethereum-related content",
  "suggestions": []
}"""
                },
                {
                    "role": "user",
                    "content": f"Validate this video prompt: {prompt}"
                }
            ],
            temperature=0.3
        )

        import json
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Content validation: {result}")
        return result

    except Exception as e:
        logger.error(f"Validation error: {e}")
        # On technical error, auto-approve to not block users
        logger.warning(f"Auto-approving due to validation service error: {prompt}")
        return {
            "approved": True,
            "category": "defi_education",
            "reason": "Auto-approved (validation service temporarily unavailable)",
            "suggestions": []
        }


async def generate_caption_simple(prompt: str, category: str) -> dict:
    """
    Simple GPT-4 caption generation
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Generate an engaging caption and hashtags for a DeFi video.

Keep it:
- Short (2-3 sentences max)
- Engaging and exciting
- Include relevant hashtags

Respond ONLY with valid JSON:
{
  "caption": "engaging caption here",
  "hashtags": "#Uniswap #DeFi #Web3 #Crypto"
}"""
                },
                {
                    "role": "user",
                    "content": f"Create caption for: {prompt} (Category: {category})"
                }
            ],
            temperature=0.7
        )

        import json
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Caption generated")
        return result

    except Exception as e:
        logger.error(f"Caption generation error: {e}")
        return {
            "caption": "Check out this amazing DeFi video!",
            "hashtags": "#Uniswap #DeFi #Web3"
        }


async def check_user_limits_simple(tg_user_id: int, prompt: str = None) -> dict:
    """
    Check if user can create videos
    Also checks for duplicate prompts to prevent spam
    """
    try:
        creator = await db.get_creator(tg_user_id)

        if not creator:
            return {"can_create": True, "remaining": 10}

        # Check daily limit (20 videos per day)
        today = datetime.now().date()
        videos_today = await db.count_videos_today(tg_user_id)

        if videos_today >= 20:
            return {
                "can_create": False,
                "reason": "Daily limit reached (20 videos/day)"
            }

        # Check for duplicate prompt in last 24 hours
        if prompt:
            from datetime import datetime, timedelta
            yesterday = datetime.now() - timedelta(days=1)

            existing = db.client.table("videos") \
                .select("id, prompt, created_at, status") \
                .eq("tg_user_id", tg_user_id) \
                .eq("prompt", prompt) \
                .gte("created_at", yesterday.isoformat()) \
                .in_("status", ["generating", "ready"])  \
                .execute()

            if existing.data and len(existing.data) > 0:
                last_video = existing.data[0]
                status_text = "being generated" if last_video.get('status') == 'generating' else "created"
                logger.warning(f"⚠️ Duplicate prompt detected for user {tg_user_id}: '{prompt[:50]}...'")
                return {
                    "can_create": False,
                    "reason": f"You already {status_text} this video recently (Video ID: {last_video['id']}). Please try a different prompt.",
                    "duplicate": True,
                    "existing_video_id": last_video['id']
                }

        return {
            "can_create": True,
            "remaining": 20 - videos_today
        }

    except Exception as e:
        logger.error(f"Limit check error: {e}")
        return {"can_create": True, "remaining": 10}


async def create_video_simple(tg_user_id: int, username: str, prompt: str) -> dict:
    """
    Simplified video generation flow - NO ASSISTANT API
    """
    try:
        logger.info(f"=== Starting simple video flow for @{username} ===")

        # Step 1: Check limits (including duplicate detection)
        logger.info("Step 1: Checking user limits and duplicates")
        limits = await check_user_limits_simple(tg_user_id, prompt)

        if not limits.get("can_create"):
            return {
                "success": False,
                "error": "duplicate_prompt" if limits.get("duplicate") else "limit_exceeded",
                "reason": limits.get("reason"),
                "duplicate": limits.get("duplicate", False),
                "existing_video_id": limits.get("existing_video_id")
            }

        # Step 2: Validate content
        logger.info("Step 2: Validating content")
        validation = await validate_content_simple(prompt)

        if not validation.get("approved"):
            return {
                "success": False,
                "approved": False,
                "reason": validation.get("reason")
            }

        category = validation.get("category", "defi_education")

        # Step 2.5: Create PENDING video record immediately to prevent race conditions
        # This ensures duplicate detection works even if multiple requests come simultaneously
        logger.info("Step 2.5: Creating pending video record to prevent duplicates")
        pending_video_data = {
            "tg_user_id": tg_user_id,
            "prompt": prompt,
            "enhanced_prompt": prompt,  # Will update later
            "duration_seconds": 15,
            "category": category,
            "status": "generating",  # Mark as generating
            "video_url": None,  # Will update after generation
            "thumbnail_url": None
        }

        pending_video = await db.create_video(pending_video_data)
        pending_video_id = pending_video.get("id")
        logger.info(f"✅ Created pending video record ID: {pending_video_id} (prevents duplicates)")

        # Step 3: Generate video with Sora 2
        logger.info("Step 3: Generating video with Sora 2")
        from agent.tools.sora2 import Sora2Generator

        generator = Sora2Generator()
        video_result = await generator.generate(
            prompt=prompt,
            duration=15,  # Default 15 seconds
            category=category,
            tg_user_id=tg_user_id  # Pass user ID for Telegram notification
        )

        if not video_result.get("success"):
            # Mark pending video as failed
            logger.warning(f"Video generation failed, marking pending video {pending_video_id} as failed")
            await db.update_video_by_id(pending_video_id, {"status": "failed"})
            return video_result

        # Step 4: Generate caption
        logger.info("Step 4: Generating caption")
        caption_result = await generate_caption_simple(prompt, category)

        # Step 5: Update pending video record with final data
        logger.info(f"Step 5: Updating pending video {pending_video_id} with final data")
        update_data = {
            "video_url": video_result.get("video_url"),
            "thumbnail_url": video_result.get("thumbnail_url"),
            "enhanced_prompt": video_result.get("enhanced_prompt"),
            "duration_seconds": video_result.get("duration"),
            "sora_job_id": video_result.get("job_id"),
            "generation_time_seconds": video_result.get("generation_time"),
            "status": "ready"
        }

        await db.update_video_by_id(pending_video_id, update_data)
        video_id = pending_video_id

        logger.info(f"=== Video flow completed successfully! Video ID: {video_id} ===")

        return {
            "success": True,
            "approved": True,
            "video_url": video_result.get("video_url"),
            "video_id": video_id,
            "caption": caption_result.get("caption"),
            "hashtags": caption_result.get("hashtags"),
            "category": category,
            "job_id": video_result.get("job_id"),
            "duration": video_result.get("duration")
        }

    except Exception as e:
        logger.error(f"Simple flow error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "message": "An error occurred during video generation"
        }
