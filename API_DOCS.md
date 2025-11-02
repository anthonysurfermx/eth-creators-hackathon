# Uniswap Sora Bot - Public API Documentation

## Base URL
```
http://localhost:8000
```

For production, replace with your deployed URL (e.g., via cloudflare tunnel or ngrok).

---

## Endpoints

### 1. Get Videos (Gallery)

**GET** `/api/videos`

Retrieve a paginated list of completed videos with metadata.

#### Query Parameters
- `limit` (optional, default: 20): Number of videos to return
- `offset` (optional, default: 0): Pagination offset

#### Response
```json
{
  "success": true,
  "videos": [
    {
      "id": 14,
      "prompt": "A Mexican mercado transforms into a digital DeFi hub",
      "category": "cultural_fusion",
      "caption": "When tradition meets innovation 🌮✨",
      "hashtags": "#Uniswap #UniswapMexico #DeFi #Web3",
      "video_url": "https://api.openai.com/v1/videos/video_xxx/content",
      "created_at": "2025-10-09T23:24:58.065Z",
      "duration": 12
    }
  ],
  "total": 20,
  "offset": 0,
  "limit": 20
}
```

#### Example Usage (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/api/videos?limit=10&offset=0');
const data = await response.json();
console.log(data.videos);
```

---

### 2. Get Statistics

**GET** `/api/stats`

Get campaign-wide statistics for the landing page.

#### Response
```json
{
  "success": true,
  "stats": {
    "total_creators": 3,
    "total_videos": 7,
    "total_posts": 2,
    "top_creator_views": 15000,
    "avg_videos_per_creator": 2.3
  }
}
```

#### Example Usage (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/api/stats');
const data = await response.json();
console.log(data.stats);
```

---

### 3. Get Leaderboard

**GET** `/api/leaderboard`

Get top creators ranked by views and engagement.

#### Query Parameters
- `limit` (optional, default: 10): Number of creators to return

#### Response
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
    },
    {
      "rank": 2,
      "username": "Jardian",
      "total_views": 8500,
      "total_videos": 1,
      "total_engagements": 1200
    }
  ]
}
```

#### Example Usage (JavaScript)
```javascript
const response = await fetch('http://localhost:8000/api/leaderboard?limit=5');
const data = await response.json();
console.log(data.leaderboard);
```

---

## CORS Configuration

All API endpoints support CORS and can be accessed from any origin (configured for MVP).

**Headers included:**
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

---

## Error Handling

All endpoints return a consistent error format:

```json
{
  "success": false,
  "error": "Error message here",
  "videos": []  // or appropriate empty data structure
}
```

---

## Integration with Lovable

### Step 1: Create API Service

Create a new file `src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';

export const api = {
  async getVideos(limit = 20, offset = 0) {
    const response = await fetch(`${API_BASE_URL}/api/videos?limit=${limit}&offset=${offset}`);
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    return response.json();
  },

  async getLeaderboard(limit = 10) {
    const response = await fetch(`${API_BASE_URL}/api/leaderboard?limit=${limit}`);
    return response.json();
  }
};
```

### Step 2: Use in Components

```typescript
import { api } from '@/services/api';
import { useEffect, useState } from 'react';

function VideoGallery() {
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    async function fetchVideos() {
      const data = await api.getVideos(20, 0);
      if (data.success) {
        setVideos(data.videos);
      }
    }
    fetchVideos();
  }, []);

  return (
    <div className="grid grid-cols-3 gap-4">
      {videos.map(video => (
        <div key={video.id}>
          <video src={video.video_url} controls />
          <p>{video.caption}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Video URLs

**Important:** Video URLs from Sora 2 API require authentication.

The bot handles this by:
1. Downloading the video with Bearer token authentication
2. Sending video bytes directly to Telegram

For the landing page, you may need to:
- Proxy video requests through your backend
- Or store videos in public cloud storage (S3, Cloudinary, etc.)

**Current Implementation:**
Videos are served directly from OpenAI's API with authenticated URLs. These URLs expire after a certain time.

---

## Next Steps for Production

1. **Authentication:** Add API keys for production endpoints
2. **Rate Limiting:** Implement rate limiting to prevent abuse
3. **Caching:** Cache responses for better performance
4. **Video Storage:** Move videos to public CDN for faster loading
5. **Analytics:** Track API usage and video views
6. **CORS:** Restrict origins to specific domains

---

## Testing Endpoints

Use the FastAPI auto-generated docs at:
```
http://localhost:8000/docs
```

This provides an interactive Swagger UI for testing all endpoints.

---

## Support

For issues or questions:
- Check `/health` endpoint to verify API is running
- Check Supabase connection in logs
- Ensure `.env` variables are configured correctly
