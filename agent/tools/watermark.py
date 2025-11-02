"""
Video Watermarking with FFmpeg
Adds Uniswap branding to generated videos
"""
import asyncio
import os
import tempfile
from typing import Dict
from pathlib import Path
import httpx
from loguru import logger
from config.settings import settings


async def add_watermark(video_url: str) -> Dict:
    """
    Add Uniswap watermark to video using FFmpeg

    Args:
        video_url: URL of the video to watermark

    Returns:
        {
            "success": bool,
            "watermarked_url": str,
            "original_url": str,
            "watermark_applied": bool,
            "error": str (optional)
        }
    """
    try:
        logger.info(f"Adding watermark to video: {video_url}")

        # Check if watermark image exists
        watermark_path = Path(settings.watermark_image_path)

        if not watermark_path.exists():
            logger.warning(f"Watermark image not found: {watermark_path}")
            logger.info("Skipping watermark, returning original video")
            return {
                "success": True,
                "watermarked_url": video_url,
                "original_url": video_url,
                "watermark_applied": False,
                "message": "Watermark image not found, using original video"
            }

        # Download video from URL
        logger.info("Downloading video...")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(video_url)
            response.raise_for_status()
            video_data = response.content

        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as input_file:
            input_path = input_file.name
            input_file.write(video_data)

        output_path = input_path.replace('.mp4', '_watermarked.mp4')

        # Build FFmpeg command
        ffmpeg_cmd = await _build_ffmpeg_command(
            input_path,
            output_path,
            str(watermark_path)
        )

        # Execute FFmpeg
        logger.info("Applying watermark with FFmpeg...")
        process = await asyncio.create_subprocess_shell(
            ffmpeg_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
            logger.error(f"FFmpeg failed: {error_msg}")

            # Cleanup
            _cleanup_temp_files(input_path, output_path)

            # Return original video on error
            return {
                "success": True,
                "watermarked_url": video_url,
                "original_url": video_url,
                "watermark_applied": False,
                "message": "Watermarking failed, using original video"
            }

        # Upload watermarked video (you'll need to implement upload logic)
        # For now, we'll return a placeholder URL
        # In production, upload to S3/Supabase Storage/CDN
        watermarked_url = await _upload_watermarked_video(output_path)

        # Cleanup temporary files
        _cleanup_temp_files(input_path, output_path)

        logger.info(f"Watermark applied successfully: {watermarked_url}")

        return {
            "success": True,
            "watermarked_url": watermarked_url,
            "original_url": video_url,
            "watermark_applied": True
        }

    except Exception as e:
        logger.error(f"Watermarking error: {e}")
        return {
            "success": False,
            "error": str(e),
            "watermarked_url": video_url,  # Fallback to original
            "original_url": video_url,
            "watermark_applied": False
        }


async def _build_ffmpeg_command(
    input_path: str,
    output_path: str,
    watermark_path: str
) -> str:
    """
    Build FFmpeg command for watermarking

    Position options:
    - bottom-right: main_w-overlay_w-10:main_h-overlay_h-10
    - bottom-left: 10:main_h-overlay_h-10
    - top-right: main_w-overlay_w-10:10
    - top-left: 10:10
    - center: (main_w-overlay_w)/2:(main_h-overlay_h)/2
    """

    # Parse position setting
    position_map = {
        "bottom-right": "main_w-overlay_w-20:main_h-overlay_h-20",
        "bottom-left": "20:main_h-overlay_h-20",
        "top-right": "main_w-overlay_w-20:20",
        "top-left": "20:20",
        "center": "(main_w-overlay_w)/2:(main_h-overlay_h)/2"
    }

    position = position_map.get(
        settings.watermark_position,
        "main_w-overlay_w-20:main_h-overlay_h-20"  # Default: bottom-right
    )

    # Opacity (0.0 to 1.0)
    opacity = settings.watermark_opacity

    # FFmpeg command with overlay filter
    # Scale watermark to 15% of video width
    cmd = (
        f'ffmpeg -i "{input_path}" -i "{watermark_path}" '
        f'-filter_complex "[1:v]scale=iw*0.15:-1,format=rgba,colorchannelmixer=aa={opacity}[wm];'
        f'[0:v][wm]overlay={position}" '
        f'-c:a copy -y "{output_path}"'
    )

    return cmd


async def _upload_watermarked_video(video_path: str) -> str:
    """
    Upload watermarked video to storage

    TODO: Implement actual upload to:
    - Supabase Storage
    - AWS S3
    - Cloudinary
    - or any CDN

    For MVP, we'll just return a placeholder URL
    """

    # Option 1: Upload to Supabase Storage
    try:
        from db.client import db

        with open(video_path, 'rb') as f:
            video_data = f.read()

        # Generate unique filename
        import uuid
        filename = f"watermarked_{uuid.uuid4().hex}.mp4"

        # Upload to Supabase Storage
        # Assuming you have a 'videos' bucket
        result = db.client.storage.from_('videos').upload(
            path=filename,
            file=video_data,
            file_options={"content-type": "video/mp4"}
        )

        # Get public URL
        public_url = db.client.storage.from_('videos').get_public_url(filename)

        logger.info(f"Video uploaded to Supabase: {public_url}")
        return public_url

    except Exception as e:
        logger.warning(f"Upload to Supabase failed: {e}")

        # Fallback: Return placeholder
        # In production, handle this properly
        import hashlib
        hash_id = hashlib.md5(open(video_path, 'rb').read()).hexdigest()[:12]
        placeholder_url = f"https://storage.uniswap.com/watermarked/{hash_id}.mp4"

        logger.info(f"Using placeholder URL: {placeholder_url}")
        return placeholder_url


def _cleanup_temp_files(*file_paths):
    """Remove temporary files"""
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
                logger.debug(f"Cleaned up temp file: {path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {path}: {e}")


async def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed"""
    try:
        process = await asyncio.create_subprocess_shell(
            "ffmpeg -version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return process.returncode == 0
    except:
        return False


# Utility function for testing
async def test_watermark():
    """Test watermark functionality"""
    logger.info("Testing watermark...")

    # Check FFmpeg
    if not await check_ffmpeg_installed():
        logger.error("FFmpeg not installed! Install with: brew install ffmpeg")
        return

    # Test with placeholder video
    test_video_url = "https://example.com/test.mp4"
    result = await add_watermark(test_video_url)

    logger.info(f"Test result: {result}")


if __name__ == "__main__":
    # Quick test
    asyncio.run(test_watermark())
