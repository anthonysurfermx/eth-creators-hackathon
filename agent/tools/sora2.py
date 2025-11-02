"""
Sora 2 Video Generator
Real integration with OpenAI Sora 2 API
"""
import asyncio
from typing import Dict, Tuple
from config.settings import settings
from loguru import logger
import httpx
import aiohttp
import os
import uuid

# Don't use OpenAI SDK - Sora 2 not supported yet
# Instead, use direct HTTP calls like N8N does


class Sora2Generator:
    """
    Generates videos using OpenAI Sora 2 API
    """
    
    async def generate(
        self,
        prompt: str,
        duration: int,
        category: str,
        tg_user_id: int = None
    ) -> Dict:
        """
        Generate video with Sora 2

        Args:
            prompt: Original user prompt
            duration: Video duration in seconds (10-60)
            category: Content category
            tg_user_id: Telegram user ID (optional, for notifications)

        Returns:
            {
                "success": bool,
                "video_url": str,
                "thumbnail_url": str,
                "duration": int,
                "enhanced_prompt": str,
                "job_id": str,
                "generation_time": float
            }
        """
        try:
            # Store user ID for later notification
            self.tg_user_id = tg_user_id
            # Enhance prompt with Uniswap branding
            enhanced_prompt = self._enhance_prompt(prompt, category)

            # Sora 2 only supports 4, 8, or 12 seconds
            valid_durations = [4, 8, 12]
            if duration not in valid_durations:
                duration = min(valid_durations, key=lambda x: abs(x - duration))

            logger.info(f"Generating Sora 2 video: {duration}s")
            logger.debug(f"Enhanced prompt: {enhanced_prompt}")

            start_time = asyncio.get_event_loop().time()
            
            # ==================== REAL SORA 2 API CALL ====================
            # Note: Adjust based on actual Sora 2 API when available
            # This is the expected format based on OpenAI patterns
            
            try:
                # Official Sora 2 API - Direct HTTP call like N8N
                # POST https://api.openai.com/v1/videos
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    response = await http_client.post(
                        "https://api.openai.com/v1/videos",
                        headers={
                            "Authorization": f"Bearer {settings.openai_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.sora2_model,
                            "prompt": enhanced_prompt,
                            "size": "720x1280",  # Vertical format for TikTok/Reels (Sora 2 supported sizes: 720x1280 or 1280x720)
                            "seconds": str(duration)
                        }
                    )

                    if response.status_code != 200:
                        raise Exception(f"Sora 2 API error: {response.status_code} - {response.text}")

                    result = response.json()
                    job_id = result["id"]
                    logger.info(f"Sora 2 job created: {job_id}, status: {result.get('status')}")

                # Poll for completion (Sora takes 1-3 minutes)
                max_attempts = 60  # 5 minutes max
                attempt = 0

                # Poll for completion
                async with httpx.AsyncClient(timeout=30.0) as http_client:
                    while attempt < max_attempts:
                        await asyncio.sleep(5)  # Check every 5 seconds

                        # Retrieve video status
                        # GET https://api.openai.com/v1/videos/{video_id}
                        status_response = await http_client.get(
                            f"https://api.openai.com/v1/videos/{job_id}",
                            headers={
                                "Authorization": f"Bearer {settings.openai_api_key}"
                            }
                        )

                        if status_response.status_code != 200:
                            raise Exception(f"Status check error: {status_response.status_code} - {status_response.text}")

                        video_status = status_response.json()
                        status = video_status.get("status")
                        progress = video_status.get("progress", 0)

                        logger.info(f"Sora 2 progress: {progress}% - Status: {status}")

                        if status == "completed":
                            # Video is ready from OpenAI
                            openai_video_url = f"https://api.openai.com/v1/videos/{job_id}/content"
                            logger.info(f"Sora 2 video completed: {openai_video_url}")

                            # 🔄 MIGRACIÓN AUTOMÁTICA A SUPABASE
                            logger.info(f"📥 Downloading video from OpenAI...")
                            video_url, thumbnail_url = await self._upload_to_supabase(
                                openai_video_url,
                                job_id,
                                tg_user_id=self.tg_user_id
                            )
                            logger.info(f"✅ Video uploaded to Supabase: {video_url}")
                            break

                        elif status == "failed":
                            error_msg = video_status.get("error", {}).get("message", "Unknown error")
                            raise Exception(f"Sora 2 generation failed: {error_msg}")

                        attempt += 1

                    else:
                        raise Exception("Sora 2 generation timed out after 5 minutes")
                
            except (AttributeError, Exception) as e:
                # PRODUCTION: Do NOT use placeholder - fail immediately
                logger.error(f"❌ Sora 2 API failed ({type(e).__name__}): {str(e)}")
                logger.error("Video generation service unavailable. Check OpenAI credits and API status.")

                # Use a specific error message that we can catch in the bot
                raise Exception("NO_CREDITS_AVAILABLE")
            
            # ==================== END SORA 2 API ====================
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            logger.info(f"Video generated in {generation_time:.2f}s")
            
            return {
                "success": True,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "duration": duration,
                "enhanced_prompt": enhanced_prompt,
                "job_id": job_id,
                "generation_time": generation_time
            }
        
        except Exception as e:
            logger.error(f"Sora 2 generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate video. Please try again."
            }
    
    def _enhance_prompt(self, prompt: str, category: str) -> str:
        """
        Enhance prompt with quality keywords (brand-neutral, very permissive)
        """
        # Quality modifiers only - NO branding
        quality = "High quality, 4K resolution, professional cinematography, engaging composition, cinematic lighting."

        # Category-specific enhancements (very flexible and permissive)
        category_enhancements = {
            "eth_content": "Ethereum blockchain theme, modern tech aesthetic, innovative visualization.",
            "defi_education": "Clear, friendly visuals. Easy to understand. Educational and approachable tone.",
            "protocol_demo": "Sleek user interface, modern design, tech-forward aesthetic, smooth animations.",
            "cultural_content": "Vibrant, colorful, authentic cultural expression, celebratory atmosphere.",
            "creative": "Artistic interpretation, creative vision, unique perspective, imaginative style.",
            "general": "Engaging narrative, compelling visual storytelling, dynamic composition.",
            # Legacy categories for backward compatibility
            "product_features": "Sleek, modern UI elements. Tech-forward aesthetic.",
            "unichain_tech": "Futuristic, cutting-edge technology visualization. Sci-fi elements.",
            "multi_chain": "Connected networks, flowing data. Interoperability theme.",
            "user_success": "Warm, human-centered. Inspirational and authentic.",
            "cultural_fusion": "Vibrant, colorful. Celebrate culture authentically."
        }

        category_enhance = category_enhancements.get(category, "Engaging and dynamic visual storytelling.")

        # Combine without brand restrictions
        enhanced = f"{prompt}. {category_enhance} {quality}".strip()

        return enhanced

    async def _upload_to_supabase(self, openai_url: str, job_id: str, tg_user_id: int = None) -> Tuple[str, str]:
        """
        Download video from OpenAI and upload to Supabase Storage
        Returns: (public_video_url, thumbnail_url)
        """
        try:
            # Download from OpenAI
            logger.info(f"Downloading video from OpenAI: {openai_url}")
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {settings.openai_api_key}'}
                async with session.get(openai_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"Download failed: {response.status} - {await response.text()}")
                    video_data = await response.read()

            logger.info(f"Video downloaded: {len(video_data)} bytes")

            # Generate unique filename
            filename = f"video_{uuid.uuid4().hex[:12]}.mp4"
            temp_path = f"/tmp/{filename}"

            # Save temporarily
            with open(temp_path, 'wb') as f:
                f.write(video_data)

            logger.info(f"Uploading to Supabase Storage: {filename}")

            # Upload to Supabase
            from supabase import create_client
            supabase = create_client(settings.supabase_url, settings.supabase_service_key)

            with open(temp_path, 'rb') as f:
                supabase.storage.from_('videos').upload(
                    filename,
                    f,
                    file_options={"content-type": "video/mp4"}
                )

            # Get public URL
            public_url = supabase.storage.from_('videos').get_public_url(filename)

            # Clean up
            os.remove(temp_path)

            logger.info(f"Video uploaded successfully: {public_url}")

            # 📱 Send Telegram notification to user
            if tg_user_id:
                logger.info(f"Sending Telegram notification to user {tg_user_id}")
                try:
                    from utils.telegram_notifier import notifier
                    await notifier.send_video_ready_notification(tg_user_id, public_url)
                except Exception as notif_error:
                    logger.error(f"Failed to send Telegram notification: {notif_error}")
                    # Don't fail the entire process if notification fails

            return public_url, None

        except Exception as e:
            logger.error(f"❌ Error uploading to Supabase: {e}")
            # Fallback to OpenAI URL if upload fails
            logger.warning(f"Falling back to OpenAI URL: {openai_url}")
            return openai_url, None
    
    async def _placeholder_generate(
        self, 
        prompt: str, 
        duration: int
    ) -> Tuple[str, str, str]:
        """
        Placeholder generator for testing before Sora 2 API is available
        Returns: (video_url, job_id, thumbnail_url)
        """
        # Simulate generation time
        await asyncio.sleep(2.0)
        
        # Generate deterministic hash for URL
        import hashlib
        hash_id = hashlib.md5(prompt.encode()).hexdigest()[:12]
        
        video_url = f"https://storage.uniswap.com/videos/{hash_id}.mp4"
        job_id = f"sora2_{hash_id}"
        thumbnail_url = f"https://storage.uniswap.com/thumbnails/{hash_id}.jpg"
        
        logger.info(f"Placeholder video generated: {video_url}")
        
        return video_url, job_id, thumbnail_url
    
    async def get_generation_status(self, job_id: str) -> Dict:
        """
        Check status of async video generation
        GET https://api.openai.com/v1/videos/{video_id}
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                status_response = await http_client.get(
                    f"https://api.openai.com/v1/videos/{job_id}",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}"
                    }
                )

                if status_response.status_code != 200:
                    raise Exception(f"Status check error: {status_response.status_code} - {status_response.text}")

                video_status = status_response.json()

                result = {
                    "status": video_status.get("status"),
                    "progress": video_status.get("progress", 0),
                    "video_url": None
                }

                if video_status.get("status") == "completed":
                    # Video is ready - get download URL
                    result["video_url"] = f"https://api.openai.com/v1/videos/{job_id}/content"

                return result

        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"status": "unknown", "error": str(e)}

    async def remix_video(
        self,
        video_id: str,
        new_prompt: str,
        category: str = "product_features"
    ) -> Dict:
        """
        Remix an existing video with a new prompt
        POST https://api.openai.com/v1/videos/{video_id}/remix

        Args:
            video_id: ID of the completed video to remix
            new_prompt: Updated text prompt for the remix
            category: Content category for enhancement

        Returns:
            Same structure as generate() but with remixed_from_video_id
        """
        try:
            enhanced_prompt = self._enhance_prompt(new_prompt, category)

            logger.info(f"Remixing video {video_id} with new prompt")

            # Create remix job - Direct HTTP call
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    f"https://api.openai.com/v1/videos/{video_id}/remix",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"prompt": enhanced_prompt}
                )

                if response.status_code != 200:
                    raise Exception(f"Remix API error: {response.status_code} - {response.text}")

                result = response.json()
                remix_job_id = result["id"]
                logger.info(f"Remix job created: {remix_job_id}, remixed from: {result.get('remixed_from_video_id')}")

            # Poll for completion (same as regular generation)
            max_attempts = 60
            attempt = 0

            async with httpx.AsyncClient(timeout=30.0) as http_client:
                while attempt < max_attempts:
                    await asyncio.sleep(5)

                    status_response = await http_client.get(
                        f"https://api.openai.com/v1/videos/{remix_job_id}",
                        headers={"Authorization": f"Bearer {settings.openai_api_key}"}
                    )

                    if status_response.status_code != 200:
                        raise Exception(f"Status check error: {status_response.status_code} - {status_response.text}")

                    video_status = status_response.json()
                    status = video_status.get("status")
                    progress = video_status.get("progress", 0)

                    logger.info(f"Remix progress: {progress}% - Status: {status}")

                    if status == "completed":
                        video_url = f"https://api.openai.com/v1/videos/{remix_job_id}/content"
                        logger.info(f"Remix completed: {video_url}")

                        return {
                            "success": True,
                            "video_url": video_url,
                            "thumbnail_url": None,
                            "duration": int(video_status.get("seconds", 0)),
                            "enhanced_prompt": enhanced_prompt,
                            "job_id": remix_job_id,
                            "remixed_from": video_id
                        }

                    elif status == "failed":
                        error_msg = video_status.get("error", {}).get("message", "Unknown error")
                        raise Exception(f"Remix failed: {error_msg}")

                    attempt += 1

                else:
                    raise Exception("Remix timed out after 5 minutes")

        except Exception as e:
            logger.error(f"Remix error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to remix video. Please try again."
            }
    
    def estimate_generation_time(self, duration: int) -> int:
        """
        Estimate generation time based on duration
        Returns seconds
        """
        # Rough estimate: ~10s per second of video
        # So a 15s video takes ~150s (2.5 min)
        base_time = duration * 10
        
        # Add buffer for processing
        buffer = 30
        
        return base_time + buffer
    
    def validate_duration(self, duration: int) -> Tuple[bool, str]:
        """Validate video duration"""
        if duration < settings.min_video_duration:
            return False, f"Duration too short. Minimum: {settings.min_video_duration}s"
        
        if duration > settings.max_video_duration:
            return False, f"Duration too long. Maximum: {settings.max_video_duration}s"
        
        return True, "OK"
    
    def get_recommended_duration(self, category: str) -> int:
        """Get recommended duration for category"""
        recommendations = {
            "product_features": 15,
            "defi_education": 30,
            "unichain_tech": 20,
            "multi_chain": 15,
            "user_success": 30,
            "cultural_fusion": 20
        }
        
        return recommendations.get(category, settings.default_video_duration)


# Alternative: Batch generation for multiple users
class BatchSora2Generator:
    """
    Batch generator for processing multiple video requests
    Useful for high-volume scenarios
    """
    
    async def generate_batch(self, requests: list) -> list:
        """
        Generate multiple videos concurrently
        
        Args:
            requests: List of {prompt, duration, category} dicts
            
        Returns:
            List of results
        """
        tasks = []
        generator = Sora2Generator()
        
        for req in requests:
            task = generator.generate(
                req["prompt"],
                req["duration"],
                req["category"]
            )
            tasks.append(task)
        
        # Run concurrently with limit
        results = []
        batch_size = 5  # Process 5 at a time to avoid rate limits
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            results.extend(batch_results)
        
        return results
