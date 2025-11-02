# 🎨 Lovable Integration Guide

## ✅ API Endpoints Ready!

Your backend is now serving 3 public APIs for the landing page:

### Base URL
```
http://localhost:8000
```

---

## 📡 Available Endpoints

### 1. `/api/videos` - Video Gallery
Get paginated list of generated videos

**Example Response:**
```json
{
  "success": true,
  "videos": [
    {
      "id": 20,
      "prompt": "A Mexican mercado transforms into a digital DeFi hub",
      "category": "cultural_fusion",
      "caption": null,
      "hashtags": null,
      "video_url": "https://api.openai.com/v1/videos/video_xxx/content",
      "created_at": "2025-10-09T21:33:32.856784+00:00",
      "duration_seconds": 12
    }
  ],
  "total": 3,
  "offset": 0,
  "limit": 3
}
```

### 2. `/api/stats` - Campaign Stats
Get campaign-wide statistics

**Example Response:**
```json
{
  "success": true,
  "stats": {
    "total_creators": 3,
    "total_videos": 7,
    "total_posts": 0,
    "top_creator_views": 0,
    "avg_videos_per_creator": 2.3
  }
}
```

### 3. `/api/leaderboard` - Top Creators
Get top creators by engagement

**Example Response:**
```json
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "username": "anthonysurfermx",
      "total_views": 15000,
      "total_videos": 8,
      "total_engagements": 2500
    }
  ]
}
```

---

## 🚀 Quick Start for Lovable

### Step 1: Copy this API service

Create `src/lib/api.ts`:

```typescript
const API_BASE = 'http://localhost:8000';

export interface Video {
  id: number;
  prompt: string;
  category: string;
  caption: string | null;
  hashtags: string | null;
  video_url: string;
  created_at: string;
  duration_seconds: number;
}

export interface Stats {
  total_creators: number;
  total_videos: number;
  total_posts: number;
  top_creator_views: number;
  avg_videos_per_creator: number;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  total_views: number;
  total_videos: number;
  total_engagements: number;
}

class API {
  async getVideos(limit = 20, offset = 0): Promise<Video[]> {
    const res = await fetch(`${API_BASE}/api/videos?limit=${limit}&offset=${offset}`);
    const data = await res.json();
    return data.success ? data.videos : [];
  }

  async getStats(): Promise<Stats> {
    const res = await fetch(`${API_BASE}/api/stats`);
    const data = await res.json();
    return data.success ? data.stats : {
      total_creators: 0,
      total_videos: 0,
      total_posts: 0,
      top_creator_views: 0,
      avg_videos_per_creator: 0
    };
  }

  async getLeaderboard(limit = 10): Promise<LeaderboardEntry[]> {
    const res = await fetch(`${API_BASE}/api/leaderboard?limit=${limit}`);
    const data = await res.json();
    return data.success ? data.leaderboard : [];
  }
}

export const api = new API();
```

### Step 2: Use in your components

**Hero Stats Component:**
```typescript
import { api } from '@/lib/api';
import { useEffect, useState } from 'react';

export function HeroStats() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.getStats().then(setStats);
  }, []);

  if (!stats) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="text-center">
        <div className="text-4xl font-bold">{stats.total_creators}</div>
        <div className="text-sm text-gray-600">Creators</div>
      </div>
      <div className="text-center">
        <div className="text-4xl font-bold">{stats.total_videos}</div>
        <div className="text-sm text-gray-600">Videos</div>
      </div>
      <div className="text-center">
        <div className="text-4xl font-bold">{stats.top_creator_views.toLocaleString()}</div>
        <div className="text-sm text-gray-600">Top Views</div>
      </div>
    </div>
  );
}
```

**Video Gallery Component:**
```typescript
import { api, type Video } from '@/lib/api';
import { useEffect, useState } from 'react';

export function VideoGallery() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getVideos(12, 0).then(videos => {
      setVideos(videos);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading videos...</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {videos.map(video => (
        <div key={video.id} className="rounded-lg overflow-hidden shadow-lg">
          <video
            src={video.video_url}
            controls
            className="w-full aspect-[9/16]"
          />
          <div className="p-4">
            <p className="text-sm text-gray-700">{video.prompt}</p>
            <span className="text-xs text-gray-500 mt-2">
              {video.category?.replace('_', ' ')}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Leaderboard Component:**
```typescript
import { api, type LeaderboardEntry } from '@/lib/api';
import { useEffect, useState } from 'react';

export function Leaderboard() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);

  useEffect(() => {
    api.getLeaderboard(10).then(setEntries);
  }, []);

  const medals = ['🥇', '🥈', '🥉'];

  return (
    <div className="space-y-2">
      {entries.map((entry, i) => (
        <div key={entry.rank} className="flex items-center gap-4 p-4 bg-white rounded-lg">
          <span className="text-2xl">{medals[i] || `#${entry.rank}`}</span>
          <div className="flex-1">
            <div className="font-semibold">@{entry.username}</div>
            <div className="text-sm text-gray-600">
              {entry.total_videos} videos • {entry.total_views.toLocaleString()} views
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## ⚠️ Important Notes

### Video URLs
Videos are served from OpenAI's API with authentication. These URLs may expire.

**Solutions:**
1. **For MVP/Demo:** Use the URLs directly (they work for ~24 hours)
2. **For Production:** Proxy requests through your backend or store videos in CDN

### CORS
Already configured! The API accepts requests from any origin (` allow_origins=["*"]`).

For production, update this to specific domains only.

---

## 🎨 Landing Page Structure Suggestion

```
┌─────────────────────────────┐
│         HERO SECTION        │
│  Logo + Title + CTA Button  │
│       <HeroStats />         │
└─────────────────────────────┘

┌─────────────────────────────┐
│      VIDEO GALLERY          │
│     <VideoGallery />        │
│   (Grid of 12 videos)       │
└─────────────────────────────┘

┌─────────────────────────────┐
│       LEADERBOARD           │
│     <Leaderboard />         │
│   (Top 10 creators)         │
└─────────────────────────────┘

┌─────────────────────────────┐
│       HOW IT WORKS          │
│  1. Join Telegram Bot       │
│  2. Create AI Videos        │
│  3. Post & Earn Rewards     │
└─────────────────────���───────┘

┌─────────────────────────────┐
│         FOOTER              │
│   Links + Social + Contact  │
└─────────────────────────────┘
```

---

## 🔥 Pro Tips for Lovable

1. **Use shadcn/ui components** for consistent design:
   ```bash
   npx shadcn-ui@latest add card button badge
   ```

2. **Add loading skeletons:**
   ```typescript
   {loading ? <Skeleton /> : <VideoGallery videos={videos} />}
   ```

3. **Implement infinite scroll** for videos:
   ```typescript
   const loadMore = () => {
     api.getVideos(12, videos.length).then(newVideos => {
       setVideos([...videos, ...newVideos]);
     });
   };
   ```

4. **Add animations** with Framer Motion:
   ```typescript
   <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
     <VideoGallery />
   </motion.div>
   ```

5. **Make it responsive:**
   - Mobile: 1 column
   - Tablet: 2 columns
   - Desktop: 3 columns

---

## 🚀 Deploy to Production

When ready to deploy:

1. **Update API_BASE** to your production URL (via cloudflare tunnel or render.com)
2. **Restrict CORS** in `app.py` to your Lovable domain only
3. **Add video CDN** for better performance (Cloudinary, Bunny CDN, etc.)
4. **Add caching** with Redis for `/api/stats` endpoint
5. **Monitor usage** with analytics (PostHog, Plausible, etc.)

---

## 📚 Additional Resources

- [Full API Documentation](./API_DOCS.md)
- [FastAPI Docs](http://localhost:8000/docs) - Interactive API tester
- [Lovable Documentation](https://lovable.dev/docs)
- [shadcn/ui Components](https://ui.shadcn.com/)

---

## ✅ Checklist

- [x] API endpoints created
- [x] CORS configured
- [x] Database schema ready
- [x] 7 sample videos available
- [x] Documentation written
- [ ] Landing page built in Lovable
- [ ] Cloudflare tunnel for public access
- [ ] Video CDN integration (optional)

---

## 🎯 Next Steps

1. **Open Lovable** at https://lovable.dev
2. **Create a new project** called "Uniswap Sora Bot Landing"
3. **Copy the API code** from Step 1
4. **Build components** from Step 2
5. **Test locally** connecting to `http://localhost:8000`
6. **Deploy** and share! 🚀

---

**Questions?** The API is running at http://localhost:8000
Test it: http://localhost:8000/docs 🎉
