"""
Vercel serverless function - Ultra simplified for API only
No complex imports, just FastAPI + Supabase
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

# Create app
app = FastAPI(title="Uniswap Creator Bot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Uniswap Creator Bot v2",
        "description": "AgentKit-powered UGC video campaign bot",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": "production"
    }


@app.get("/api/videos")
async def get_videos(limit: int = 20, offset: int = 0):
    """Get public videos - import Supabase only when needed"""
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return {"success": False, "error": "Database not configured", "videos": []}

        supabase = create_client(supabase_url, supabase_key)

        result = supabase.table("videos") \
            .select("id, prompt, category, caption, hashtags, video_url, watermarked_url, thumbnail_url, created_at, duration_seconds, creators(username)") \
            .eq("status", "ready") \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()

        videos = []
        for video in result.data:
            video_url = video.get("watermarked_url") or video.get("video_url", "")
            creator_username = None
            if video.get("creators") and isinstance(video["creators"], dict):
                creator_username = video["creators"].get("username")

            videos.append({
                "id": video["id"],
                "prompt": video.get("prompt", ""),
                "category": video.get("category", "unknown"),
                "caption": video.get("caption", ""),
                "hashtags": video.get("hashtags", ""),
                "video_url": video_url,
                "thumbnail_url": video.get("thumbnail_url", ""),
                "created_at": video.get("created_at", ""),
                "duration_seconds": video.get("duration_seconds", 12),
                "creator_username": creator_username
            })

        return {
            "success": True,
            "videos": videos,
            "total": len(videos)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "videos": []
        }


@app.get("/api/stats")
async def get_stats():
    """Get public statistics"""
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return {"success": False, "error": "Database not configured"}

        supabase = create_client(supabase_url, supabase_key)

        videos_result = supabase.table("videos").select("id", count="exact").eq("status", "ready").execute()
        creators_result = supabase.table("creators").select("id", count="exact").execute()
        posts_result = supabase.table("posts").select("id").execute()

        total_videos = videos_result.count or 0
        total_creators = creators_result.count or 0
        total_posts = len(posts_result.data) if posts_result.data else 0

        return {
            "success": True,
            "stats": {
                "total_creators": total_creators,
                "total_videos": total_videos,
                "total_posts": total_posts,
                "avg_videos_per_creator": round(total_videos / total_creators, 1) if total_creators > 0 else 0
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get public leaderboard"""
    try:
        from supabase import create_client

        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            return {"success": False, "error": "Database not configured"}

        supabase = create_client(supabase_url, supabase_key)

        creators_result = supabase.table("creators") \
            .select("username, total_views, total_videos, total_engagements") \
            .order("total_views", desc=True) \
            .limit(limit) \
            .execute()

        top_creators = []
        for i, creator in enumerate(creators_result.data):
            top_creators.append({
                "rank": i + 1,
                "username": creator.get("username", "Anonymous"),
                "total_views": creator.get("total_views", 0),
                "total_videos": creator.get("total_videos", 0),
                "total_engagements": creator.get("total_engagements", 0)
            })

        return {
            "success": True,
            "leaderboard": top_creators
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "leaderboard": []
        }


# Vercel handler with Mangum (ASGI adapter for serverless)
from mangum import Mangum
handler = Mangum(app)
