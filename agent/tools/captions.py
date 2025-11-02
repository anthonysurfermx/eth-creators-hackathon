"""AI-powered caption generation"""
from openai import AsyncOpenAI
from config.settings import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

class CaptionGenerator:
    async def generate(self, prompt: str, category: str, video_url: str = None) -> dict:
        """Generate engaging caption with GPT-4"""
        system = "Create engaging 2-3 sentence social media captions for Uniswap DeFi videos. Be concise, use emojis, make it shareable."
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Video prompt: {prompt}\nCategory: {category}"}
            ],
            max_tokens=150
        )
        
        caption = response.choices[0].message.content
        hashtags = self._get_hashtags(category)
        
        return {"caption": caption, "hashtags": hashtags}
    
    def _get_hashtags(self, category: str) -> str:
        """Get category-specific hashtags"""
        base = "#Uniswap #UniswapMexico #DeFi #Web3"
        category_tags = {
            "cultural_fusion": " #CryptoMexico #LatinCrypto",
            "unichain_tech": " #Unichain #Web3Tech",
            "product_features": " #GaslessSwaps #UniswapX"
        }
        return base + category_tags.get(category, "")
