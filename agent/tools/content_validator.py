"""
Content Validator - Enhanced with AI
"""
from typing import Dict, Tuple
from openai import AsyncOpenAI
from config.settings import settings
from loguru import logger

client = AsyncOpenAI(api_key=settings.openai_api_key)

# Approved categories
APPROVED_CATEGORIES = {
    "product_features": {
        "keywords": ["swap", "gasless", "wallet", "limit order", "uniswapx", "bridge", "smart wallet"],
        "description": "Showcase Uniswap product features"
    },
    "defi_education": {
        "keywords": ["defi", "stablecoin", "dex", "learn", "explain", "how", "what is"],
        "description": "Educational content about DeFi"
    },
    "unichain_tech": {
        "keywords": ["unichain", "mev", "fair ordering", "tee", "efficient"],
        "description": "Unichain technical innovations"
    },
    "multi_chain": {
        "keywords": ["cross-chain", "layer 2", "l2", "soneium", "arbitrum", "polygon", "base"],
        "description": "Multi-chain and Layer 2"
    },
    "user_success": {
        "keywords": ["first swap", "my story", "journey", "accessibility", "inclusion"],
        "description": "User success stories"
    },
    "cultural_fusion": {
        "keywords": ["mexico", "mexican", "culture", "mercado", "taco", "mariachi", "folk", "tradition"],
        "description": "Mexican culture + DeFi fusion"
    }
}

# Banned keywords and phrases
BANNED_KEYWORDS = [
    # Price predictions
    "moon", "100x", "1000x", "to the moon", "lambo", "when moon",
    # Gambling
    "casino", "roulette", "betting", "gamble", "lottery",
    # Get rich quick
    "get rich", "easy money", "guaranteed profit", "passive income",
    # Competitors
    "pancakeswap", "sushiswap", "1inch", "curve", "balancer",
    # Political
    "election", "vote for", "politics", "politician",
    # Pump schemes
    "pump", "dump", "rug pull", "scam token"
]


class ContentValidator:
    """
    Validates user prompts against Uniswap content guidelines
    Uses both keyword matching and AI-powered semantic analysis
    """
    
    async def validate(self, prompt: str) -> Dict:
        """
        Main validation method
        Returns: {
            "approved": bool,
            "category": str,
            "reason": str,
            "suggestions": list,
            "confidence": float
        }
        """
        prompt_lower = prompt.lower()
        
        # Step 1: Check banned keywords (fast rejection)
        for banned in BANNED_KEYWORDS:
            if banned in prompt_lower:
                return {
                    "approved": False,
                    "category": None,
                    "reason": f"Contains prohibited content: '{banned}'",
                    "suggestions": [
                        "Focus on DeFi education or Uniswap features",
                        "Avoid price predictions and gambling themes",
                        "Highlight user stories or cultural elements"
                    ],
                    "confidence": 1.0
                }
        
        # Step 2: Category detection (keyword-based)
        detected_category = self._detect_category_keywords(prompt_lower)
        
        # Step 3: AI-powered semantic validation
        ai_validation = await self._ai_validate(prompt, detected_category)
        
        # Combine keyword and AI validation
        if ai_validation["approved"]:
            return {
                "approved": True,
                "category": ai_validation.get("category", detected_category),
                "reason": "Content meets guidelines",
                "duration": 15,  # Default duration
                "confidence": ai_validation.get("confidence", 0.8),
                "enhancement_suggestions": ai_validation.get("suggestions", [])
            }
        else:
            return ai_validation
    
    def _detect_category_keywords(self, prompt_lower: str) -> str:
        """Detect category based on keywords"""
        category_scores = {}
        
        for category, data in APPROVED_CATEGORIES.items():
            score = sum(1 for keyword in data["keywords"] if keyword in prompt_lower)
            category_scores[category] = score
        
        # Return category with highest score, default to defi_education
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        
        return "defi_education"
    
    async def _ai_validate(self, prompt: str, suggested_category: str) -> Dict:
        """
        Use GPT-4 to semantically validate content
        Catches nuanced violations that keyword matching misses
        """
        try:
            system_prompt = """You are a content moderator for Uniswap's UGC campaign.

APPROVED CATEGORIES:
1. Product Features: Gasless swaps, UniswapX, limit orders, smart wallets, bridging
2. DeFi Education: Stablecoins, how swaps work, DEX basics, blockchain education
3. Unichain Tech: MEV protection, fair ordering, TEE, efficient markets
4. Multi-chain: Cross-chain swaps, Layer 2s, Soneium integration
5. User Success: First swap stories, financial inclusion, accessibility
6. Cultural Fusion: Mexican culture + DeFi (mercados, arte, tradiciones)

BANNED:
- Price predictions ("moon", "100x", financial advice)
- Competitor mentions
- Gambling/casino themes
- "Get rich quick" promises
- Political or controversial content
- Misleading information about Uniswap

Analyze the prompt and return JSON:
{
  "approved": true/false,
  "category": "category_name" or null,
  "reason": "explanation",
  "confidence": 0.0-1.0,
  "suggestions": ["list of improvements if rejected"]
}

Be strict but constructive."""

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Validate this video prompt:\n\n\"{prompt}\"\n\nSuggested category: {suggested_category}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            import json
            return json.loads(result)
        
        except Exception as e:
            logger.error(f"AI validation error: {e}")
            # Fallback to keyword-based approval
            return {
                "approved": True,
                "category": suggested_category,
                "reason": "Passed keyword validation",
                "confidence": 0.6
            }
    
    def get_example_prompts(self, category: str) -> list:
        """Get example prompts for a category"""
        examples = {
            "product_features": [
                "Futuristic animation of gasless swaps as frictionless portals - tokens flow with zero fees, cyberpunk aesthetic",
                "Smart wallets as digital assistants guiding users through DeFi, Apple commercial style",
                "UniswapX routing visualized as holographic pathways finding best prices, sci-fi"
            ],
            "defi_education": [
                "Stablecoins as digital anchors in stormy crypto seas - friendly, colorful explainer",
                "How a swap works: animated journey of tokens through blockchain, educational style",
                "DEX vs CEX comparison as two different worlds side by side, informative"
            ],
            "unichain_tech": [
                "MEV protection visualized as force field protecting transactions in neon blockchain city",
                "Fair transaction ordering as perfectly organized assembly line, futuristic factory",
                "TEE technology as secure vault in digital space, high-tech security theme"
            ],
            "multi_chain": [
                "Blockchains as connected planets, Uniswap spacecraft traveling between them",
                "Cross-chain bridge as portal between different blockchain worlds, sci-fi",
                "Layer 2 scaling as express lanes on blockchain highway, traffic flow visualization"
            ],
            "user_success": [
                "Young Mexican entrepreneur's first Uniswap swap transforming their business, cinematic",
                "Grandmother learning DeFi for the first time, heartwarming and inspirational",
                "Student accessing global finance through Uniswap, empowering narrative"
            ],
            "cultural_fusion": [
                "Traditional Mexican mercado transforms into holographic DeFi marketplace, papel picado as blockchain connections",
                "Talavera pottery patterns morph into blockchain networks, vibrant colors",
                "Mariachi band plays as tokens dance in crypto celebration, festive and colorful"
            ]
        }
        
        return examples.get(category, [])
