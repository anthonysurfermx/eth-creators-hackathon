# 🚨 AUDIT REPORT: Jardian's Video Issue

**Date:** 2025-10-11
**Reporter:** User (anthonysurfermx)
**Investigated by:** Claude Code

---

## 📋 Summary

User Jardian created a video that passed moderation despite having NO connection to Uniswap or DeFi. The video also fails to display properly and metrics are not being counted.

---

## 🔍 Video Details

**Video ID:** 25
**Creator:** Jardian (User ID: TBD)
**Prompt:** `"a guy eating cereal"`
**Category Assigned:** `defi_education` ❌ (INCORRECT)
**Status:** Approved ❌ (SHOULD HAVE BEEN REJECTED)
**Video URL:** `https://storage.uniswap.com/videos/077be0044904.mp4`
**Thumbnail:** `https://storage.uniswap.com/thumbnails/077be0044904.jpg`
**Created:** 2025-10-11 15:50:47

### Metrics (All Zero):
- Views: 0
- Likes: 0
- Comments: 0
- Shares: 0
- Platform Posts: [] (not shared to social)

---

## 🚨 Issues Found

### ❌ ISSUE #1: Content Filter Bypass
**Severity:** CRITICAL
**Location:** `agent/tools/content_validator.py:174-180`

**Root Cause:**
The content validator has an overly permisive fallback that automatically approves content when AI validation fails:

```python
except Exception as e:
    logger.error(f"AI validation error: {e}")
    # Fallback to keyword-based approval
    return {
        "approved": True,  # ❌ DANGEROUS
        "category": suggested_category,
        "reason": "Passed keyword validation",
        "confidence": 0.6
    }
```

**What Happened:**
1. Prompt "a guy eating cereal" has ZERO Uniswap/DeFi keywords
2. Default category assigned: `"defi_education"` (line 121)
3. AI validation likely failed (API error, timeout, rate limit)
4. Fallback automatically approved it ❌
5. Video was generated and stored

**Impact:**
- Irrelevant content pollutes the platform
- Wastes AI generation credits on non-Uniswap content
- Damages brand reputation
- Users can abuse the system

---

### ❌ ISSUE #2: Metrics Not Counting
**Severity:** HIGH
**Location:** Metrics calculation system

**Evidence:**
```json
{
    "username": "Jardian",
    "total_views": 0,
    "total_videos": 0,  // ❌ Should be 1
    "total_engagements": 0
}
```

**Root Cause:**
Video exists in database but creator stats show `total_videos: 0`. This suggests:
- `recalculate_creator_stats()` is not running
- Video is not being counted in aggregation
- Platform posts are empty (not shared to social media)

**Impact:**
- Leaderboard is inaccurate
- Betting pool data is wrong
- Creator rewards won't be calculated
- Stats dashboards show incorrect numbers

---

### ❌ ISSUE #3: Video Not Shared to Social
**Severity:** MEDIUM
**Evidence:** `platform_posts: []`

**Root Cause:**
The video was generated but never shared to TikTok/Instagram/YouTube. Either:
- Social sharing failed silently
- Video was rejected by social platforms
- Integration is broken

**Impact:**
- No views/engagement data
- Video invisible to public
- Can't track performance
- Metrics remain at zero

---

## 🔧 Recommended Fixes

### Fix #1: Strict Content Validation (CRITICAL)

**File:** `agent/tools/content_validator.py`

```python
async def _ai_validate(self, prompt: str, suggested_category: str) -> Dict:
    try:
        # ... existing AI validation code ...

    except Exception as e:
        logger.error(f"AI validation error: {e}")

        # FIXED: Reject when AI validation fails
        return {
            "approved": False,  # ✅ REJECT by default
            "category": None,
            "reason": "Content validation service unavailable. Please try again.",
            "confidence": 0.0,
            "suggestions": [
                "Make sure your prompt relates to Uniswap, DeFi, or blockchain",
                "Include keywords like: swap, DeFi, Uniswap, blockchain, crypto",
                "Try again in a few moments"
            ]
        }
```

**Additionally, enforce minimum keyword requirements:**

```python
def _detect_category_keywords(self, prompt_lower: str) -> str:
    """Detect category based on keywords"""
    category_scores = {}

    for category, data in APPROVED_CATEGORIES.items():
        score = sum(1 for keyword in data["keywords"] if keyword in prompt_lower)
        category_scores[category] = score

    # ✅ FIXED: Require at least 1 keyword match
    if max(category_scores.values()) == 0:
        return None  # No category = rejection

    return max(category_scores, key=category_scores.get)
```

---

### Fix #2: Fix Metrics Calculation

**File:** `app.py` (recalculate_creator_stats function)

Add logging and verification:

```python
def recalculate_creator_stats(creator_id: int):
    """Recalculate aggregated stats for a creator"""
    logger.info(f"🔄 Recalculating stats for creator {creator_id}")

    # Get all videos
    videos = db.client.table("videos") \
        .select("id") \
        .eq("tg_user_id", creator_id) \
        .execute()

    video_ids = [v["id"] for v in videos.data]

    if not video_ids:
        logger.warning(f"⚠️  No videos found for creator {creator_id}")
        return

    # ... rest of function ...

    logger.info(f"✅ Updated creator {creator_id}: {total_videos} videos, {total_views} views")
```

**Then run:**
```bash
python3 << 'EOF'
from app import recalculate_creator_stats
# Find Jardian's user_id and recalculate
recalculate_creator_stats(JARDIAN_USER_ID)
EOF
```

---

### Fix #3: Add Content Validation Logging

**File:** `agent/tools/content_validator.py`

Add detailed logging to track rejections:

```python
async def validate(self, prompt: str) -> Dict:
    """Main validation method"""
    prompt_lower = prompt.lower()

    logger.info(f"🔍 Validating prompt: {prompt[:50]}...")

    # Step 1: Banned keywords
    for banned in BANNED_KEYWORDS:
        if banned in prompt_lower:
            logger.warning(f"❌ Rejected: Contains banned keyword '{banned}'")
            return {...}

    # Step 2: Category detection
    detected_category = self._detect_category_keywords(prompt_lower)

    if detected_category is None:
        logger.warning(f"❌ Rejected: No relevant keywords found")
        return {
            "approved": False,
            "reason": "Prompt must relate to Uniswap or DeFi",
            "suggestions": [...]
        }

    logger.info(f"✅ Category detected: {detected_category}")

    # ... rest of validation ...
```

---

## 📊 Prevention Measures

1. **Add Rate Limiting**
   - Max 3 video requests per user per hour
   - Prevents spam/abuse

2. **Add Moderation Dashboard**
   - Review flagged content
   - Manual override capability
   - Track rejection reasons

3. **Add Alerts**
   - Slack/Email when validation fails
   - Monitor fallback activation rate
   - Alert on zero-engagement videos

4. **Add Tests**
   ```python
   def test_irrelevant_content_rejected():
       validator = ContentValidator()
       result = await validator.validate("a guy eating cereal")
       assert result["approved"] == False
   ```

---

## ✅ Action Items

- [ ] Fix content validator fallback (CRITICAL)
- [ ] Add minimum keyword requirement
- [ ] Recalculate Jardian's stats manually
- [ ] Investigate why social sharing failed
- [ ] Add validation logging
- [ ] Write tests for edge cases
- [ ] Add rate limiting
- [ ] Consider deleting/hiding Jardian's video

---

## 📝 Notes

This incident reveals a **critical security flaw** in content moderation. The fallback approval is dangerous and must be fixed immediately to prevent:
- Spam/abuse
- Off-brand content
- Wasted AI credits
- Damage to platform reputation

**Priority:** 🔴 CRITICAL - Fix immediately before more users discover the loophole.
