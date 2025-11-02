"""
Video Storage Uploader
Uploads videos to public storage (S3, R2, or similar)
"""
import hashlib
import uuid
from typing import Optional, Tuple
from loguru import logger
import httpx


class VideoStorage:
    """
    Upload videos to public storage
    Supports: AWS S3, Cloudflare R2, or custom endpoints
    """

    def __init__(self, storage_type: str = "local"):
        """
        Args:
            storage_type: "s3", "r2", "custom", or "local"
        """
        self.storage_type = storage_type

    async def upload_video(
        self,
        video_bytes: bytes,
        filename: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Upload video to public storage

        Args:
            video_bytes: Video file content
            filename: Optional custom filename

        Returns:
            (video_url, thumbnail_url) - Public URLs
        """
        try:
            # Generate unique filename if not provided
            if not filename:
                video_hash = hashlib.md5(video_bytes[:1024]).hexdigest()[:12]
                filename = f"{video_hash}.mp4"

            logger.info(f"Uploading video: {filename} ({len(video_bytes)} bytes)")

            # Choose upload method based on storage type
            if self.storage_type == "supabase":
                return await self._upload_to_supabase(video_bytes, filename)
            elif self.storage_type == "s3":
                return await self._upload_to_s3(video_bytes, filename)
            elif self.storage_type == "r2":
                return await self._upload_to_r2(video_bytes, filename)
            elif self.storage_type == "custom":
                return await self._upload_to_custom(video_bytes, filename)
            else:
                # Local/placeholder mode
                return await self._placeholder_upload(video_bytes, filename)

        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise

    async def _upload_to_supabase(self, video_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Upload to Supabase Storage"""
        try:
            from config.settings import settings
            from supabase import create_client

            # Use service key if available for better permissions
            api_key = settings.supabase_service_key if hasattr(settings, 'supabase_service_key') and settings.supabase_service_key else settings.supabase_key

            logger.info(f"Uploading to Supabase with {'service' if api_key != settings.supabase_key else 'anon'} key")

            # Initialize Supabase client
            supabase = create_client(settings.supabase_url, api_key)

            # Upload to Supabase Storage bucket
            bucket_name = "videos"  # Create this bucket in Supabase Dashboard
            file_path = f"generated/{filename}"

            logger.info(f"Uploading {len(video_bytes)} bytes to {bucket_name}/{file_path}")

            # Upload the video
            response = supabase.storage.from_(bucket_name).upload(
                file_path,
                video_bytes,
                file_options={"content-type": "video/mp4", "upsert": "true"}
            )

            logger.info(f"Upload response: {response}")

            # Get public URL
            video_url = supabase.storage.from_(bucket_name).get_public_url(file_path)

            # Generate thumbnail path (you can implement actual thumbnail generation later)
            thumbnail_path = f"thumbnails/{filename.replace('.mp4', '.jpg')}"
            thumbnail_url = supabase.storage.from_(bucket_name).get_public_url(thumbnail_path)

            logger.info(f"✅ Uploaded to Supabase Storage: {video_url}")
            return video_url, thumbnail_url

        except Exception as e:
            logger.error(f"❌ Supabase Storage upload error: {e}")
            logger.error(f"   Bucket: videos, File: {filename}, Size: {len(video_bytes)} bytes")
            import traceback
            logger.error(traceback.format_exc())
            raise

    async def _upload_to_s3(self, video_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Upload to AWS S3"""
        try:
            import boto3
            from config.settings import settings

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )

            # Upload video
            bucket = settings.s3_bucket_name
            video_key = f"videos/{filename}"

            s3_client.put_object(
                Bucket=bucket,
                Key=video_key,
                Body=video_bytes,
                ContentType='video/mp4',
                ACL='public-read'  # Make publicly accessible
            )

            # Construct public URL
            video_url = f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/{video_key}"

            # Generate thumbnail (placeholder for now)
            thumbnail_url = f"https://{bucket}.s3.{settings.aws_region}.amazonaws.com/thumbnails/{filename.replace('.mp4', '.jpg')}"

            logger.info(f"Uploaded to S3: {video_url}")
            return video_url, thumbnail_url

        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            raise

    async def _upload_to_r2(self, video_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Upload to Cloudflare R2"""
        try:
            import boto3
            from config.settings import settings

            # R2 is S3-compatible
            s3_client = boto3.client(
                's3',
                endpoint_url=settings.r2_endpoint,
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key
            )

            bucket = settings.r2_bucket_name
            video_key = f"videos/{filename}"

            s3_client.put_object(
                Bucket=bucket,
                Key=video_key,
                Body=video_bytes,
                ContentType='video/mp4'
            )

            # R2 public URL
            video_url = f"https://{settings.r2_public_domain}/{video_key}"
            thumbnail_url = f"https://{settings.r2_public_domain}/thumbnails/{filename.replace('.mp4', '.jpg')}"

            logger.info(f"Uploaded to R2: {video_url}")
            return video_url, thumbnail_url

        except Exception as e:
            logger.error(f"R2 upload error: {e}")
            raise

    async def _upload_to_custom(self, video_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Upload to custom endpoint (e.g., your own server)
        Implement this based on your storage API
        """
        try:
            from config.settings import settings

            # Example: POST to your custom upload endpoint
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {'video': (filename, video_bytes, 'video/mp4')}
                response = await client.post(
                    settings.custom_upload_endpoint,
                    files=files,
                    headers={"Authorization": f"Bearer {settings.custom_upload_token}"}
                )

                if response.status_code == 200:
                    result = response.json()
                    video_url = result.get("video_url")
                    thumbnail_url = result.get("thumbnail_url", "")

                    logger.info(f"Uploaded to custom storage: {video_url}")
                    return video_url, thumbnail_url
                else:
                    raise Exception(f"Upload failed: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Custom upload error: {e}")
            raise

    async def _placeholder_upload(self, video_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Placeholder for local development
        Returns mock URLs
        """
        # Generate deterministic URLs for testing
        video_hash = hashlib.md5(video_bytes[:1024]).hexdigest()[:12]

        video_url = f"https://storage.uniswap.com/videos/{video_hash}.mp4"
        thumbnail_url = f"https://storage.uniswap.com/thumbnails/{video_hash}.jpg"

        logger.warning(f"Using placeholder upload: {video_url}")
        logger.warning("⚠️ Video not actually uploaded! Configure real storage for production.")

        return video_url, thumbnail_url


# Singleton instance
_storage = None

def get_storage() -> VideoStorage:
    """Get video storage instance"""
    global _storage
    if _storage is None:
        from config.settings import settings
        storage_type = getattr(settings, 'storage_type', 'local')
        logger.info(f"🗂️  Initializing VideoStorage with type: {storage_type}")
        _storage = VideoStorage(storage_type)
    return _storage
