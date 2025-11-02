"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    sora2_model: str = Field(default="sora-2", env="SORA2_MODEL")
    gpt_model: str = Field(default="gpt-4-turbo-preview", env="GPT_MODEL")
    
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(..., env="TELEGRAM_WEBHOOK_SECRET")
    telegram_webhook_url: str = Field(..., env="TELEGRAM_WEBHOOK_URL")
    
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")

    # Video Storage (S3, R2, or custom)
    storage_type: str = Field(default="local", env="STORAGE_TYPE")  # "s3", "r2", "custom", or "local"

    # AWS S3 (if using S3)
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    s3_bucket_name: Optional[str] = Field(None, env="S3_BUCKET_NAME")

    # Cloudflare R2 (if using R2)
    r2_endpoint: Optional[str] = Field(None, env="R2_ENDPOINT")
    r2_access_key_id: Optional[str] = Field(None, env="R2_ACCESS_KEY_ID")
    r2_secret_access_key: Optional[str] = Field(None, env="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: Optional[str] = Field(None, env="R2_BUCKET_NAME")
    r2_public_domain: Optional[str] = Field(None, env="R2_PUBLIC_DOMAIN")

    # Custom storage endpoint (if using custom)
    custom_upload_endpoint: Optional[str] = Field(None, env="CUSTOM_UPLOAD_ENDPOINT")
    custom_upload_token: Optional[str] = Field(None, env="CUSTOM_UPLOAD_TOKEN")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Social Media
    twitter_api_key: Optional[str] = Field(None, env="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(None, env="TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = Field(None, env="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = Field(None, env="TWITTER_ACCESS_SECRET")
    twitter_bearer_token: Optional[str] = Field(None, env="TWITTER_BEARER_TOKEN")
    
    instagram_username: Optional[str] = Field(None, env="INSTAGRAM_USERNAME")
    instagram_password: Optional[str] = Field(None, env="INSTAGRAM_PASSWORD")
    
    tiktok_session_id: Optional[str] = Field(None, env="TIKTOK_SESSION_ID")
    
    # Content Moderation
    max_strikes: int = Field(default=3, env="MAX_STRIKES")
    cooldown_hours: int = Field(default=24, env="COOLDOWN_HOURS")
    max_videos_per_day: int = Field(default=20, env="MAX_VIDEOS_PER_DAY")
    
    # Video Settings
    min_video_duration: int = Field(default=10, env="MIN_VIDEO_DURATION")
    max_video_duration: int = Field(default=60, env="MAX_VIDEO_DURATION")
    default_video_duration: int = Field(default=15, env="DEFAULT_VIDEO_DURATION")
    video_resolution: str = Field(default="1080x1920", env="VIDEO_RESOLUTION")
    
    # Campaign
    campaign_start_date: str = Field(..., env="CAMPAIGN_START_DATE")
    campaign_end_date: str = Field(..., env="CAMPAIGN_END_DATE")
    metrics_update_interval_hours: int = Field(default=6, env="METRICS_UPDATE_INTERVAL_HOURS")
    
    # Watermark
    watermark_image_path: str = Field(default="./assets/uniswap_logo.png", env="WATERMARK_IMAGE_PATH")
    watermark_position: str = Field(default="bottom-right", env="WATERMARK_POSITION")
    watermark_opacity: float = Field(default=0.7, env="WATERMARK_OPACITY")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # Timezone
    timezone: str = Field(default="America/Mexico_City", env="TIMEZONE")
    
    # Feature Flags
    enable_auto_notifications: bool = Field(default=True, env="ENABLE_AUTO_NOTIFICATIONS")
    enable_community_voting: bool = Field(default=True, env="ENABLE_COMMUNITY_VOTING")
    enable_remix_feature: bool = Field(default=True, env="ENABLE_REMIX_FEATURE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
