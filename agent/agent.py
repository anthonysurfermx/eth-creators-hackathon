"""
AgentKit-Powered Orchestrator using OpenAI Assistants API
ETH Creators Bot - Ethereum Content Creation
"""
import json
import asyncio
from typing import Dict, Any, List
from openai import AsyncOpenAI
from config.settings import settings
from db.client import db
from loguru import logger


# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


# ==================== TOOL SCHEMAS ====================

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "validate_content",
            "description": "Validates user prompt against Ethereum content guidelines. Returns approval status and category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user's video prompt to validate"
                    }
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_video_sora2",
            "description": "Generates a video using Sora 2 API. Returns video URL and metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Enhanced prompt with Ethereum branding"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Video duration in seconds (10-60)"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["ecosystem_features", "defi_education", "layer2_tech", "multi_chain", "user_success", "cultural_fusion"]
                    }
                },
                "required": ["prompt", "duration", "category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_caption",
            "description": "Generates engaging caption and hashtags using GPT-4",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Original video prompt"
                    },
                    "category": {
                        "type": "string",
                        "description": "Content category"
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Generated video URL for context"
                    }
                },
                "required": ["prompt", "category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_video_to_db",
            "description": "Saves video metadata to database",
            "parameters": {
                "type": "object",
                "properties": {
                    "tg_user_id": {"type": "integer"},
                    "video_data": {"type": "object"}
                },
                "required": ["tg_user_id", "video_data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_limits",
            "description": "Checks if user is within daily video limit and not in cooldown",
            "parameters": {
                "type": "object",
                "properties": {
                    "tg_user_id": {"type": "integer"}
                },
                "required": ["tg_user_id"]
            }
        }
    }
]


class ETHCreatorsAgent:
    """
    AgentKit-powered orchestrator for video creation workflow
    Uses OpenAI Assistants API for intelligent multi-step reasoning
    For ETH Creators - Ethereum content campaign
    """
    
    def __init__(self):
        self.assistant_id = None
        self.tools_module = None
    
    async def initialize(self):
        """Create or retrieve assistant"""
        try:
            # Try to get existing assistant by name
            assistants = await client.beta.assistants.list()
            for assistant in assistants.data:
                if assistant.name == "ETH Creators Agent v2":
                    self.assistant_id = assistant.id
                    logger.info(f"Using existing assistant: {self.assistant_id}")
                    return

            # Create new assistant
            assistant = await client.beta.assistants.create(
                name="ETH Creators Agent v2",
                instructions=self._get_system_instructions(),
                tools=TOOL_SCHEMAS,
                model=settings.gpt_model
            )
            self.assistant_id = assistant.id
            logger.info(f"Created new assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"Error initializing assistant: {e}")
            logger.warning("⚠️  Assistant API initialization failed, but bot will continue")
            logger.warning("   Video generation uses simple_flow.py (no Assistant API required)")
            self.assistant_id = None  # Bot can still work without Assistant API
    
    def _get_system_instructions(self) -> str:
        """System instructions for the agent"""
        return """You are the ETH Creators Agent, orchestrating AI video creation for a UGC campaign.

**Your Role:**
Help users create high-quality, on-brand videos about Ethereum using Sora 2. You guide them through content validation, video generation, and delivery.

**Workflow:**
1. Check user limits (cooldown, daily quota)
2. Validate prompt against content guidelines
3. If approved, generate video with Sora 2
4. Add Ethereum watermark
5. Generate engaging caption + hashtags
6. Save to database
7. Deliver complete package to user

**Content Guidelines:**

✅ APPROVED CATEGORIES:
- Ecosystem Features: Swaps, liquidity pools, smart wallets, staking, NFTs
- DeFi Education: Stablecoins, how swaps work, DEX basics, why transactions fail
- Layer 2 Tech: Scroll, Arbitrum, MEV protection, fair ordering, efficient markets
- Multi-chain: Cross-chain swaps, interoperability, bridges
- User Success: First transaction stories, financial inclusion, accessibility
- Cultural Fusion: Mexican culture + DeFi (mercados, arte, tradiciones)

❌ BANNED:
- Price predictions ("moon", "100x", financial advice)
- Competitor mentions (Solana, BSC, etc.)
- Gambling/casino themes
- "Get rich quick" promises
- Political or controversial content

**Tone:**
Be enthusiastic, encouraging, and educational. If content is rejected, be constructive and suggest improvements. Always emphasize quality and creativity.

**Required Elements:**
- Video duration: 10-60 seconds
- Hashtags: #Ethereum #ETHCreators #DeFi #Web3 + category tags
- NO brand watermarks or logos (for legal safety - user-generated content must remain independent)

Use your tools effectively to orchestrate the entire workflow."""
    
    async def create_video_flow(
        self,
        tg_user_id: int,
        username: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Main workflow: orchestrates video creation from prompt to delivery
        Uses AgentKit to intelligently handle multi-step process
        """
        if not self.assistant_id:
            await self.initialize()

        try:
            # 🔒 Cache para evitar llamadas duplicadas (FIX CRÍTICO)
            tool_call_cache = {}

            # Create thread for this conversation
            thread = await client.beta.threads.create()

            # Add user message
            await client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""User @{username} (ID: {tg_user_id}) wants to create a video.

Prompt: "{prompt}"

⚠️ IMPORTANT: Only call generate_video_sora2 ONCE per request. Each call costs $3 USD.

Please:
1. Check if user can create videos (limits/cooldown)
2. Validate the prompt
3. If approved, generate the video (ONCE ONLY - do not retry or duplicate)
4. Generate caption + hashtags
5. Save to database
6. Return the complete package"""
            )

            # Run assistant
            run = await client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )

            # Poll for completion and handle tool calls
            max_iterations = 20  # 🔒 Reducido de 60 a 20 para prevenir loops largos
            iteration = 0

            while run.status in ["queued", "in_progress", "requires_action"] and iteration < max_iterations:
                iteration += 1
                logger.info(f"Agent iteration {iteration}/{max_iterations}, status: {run.status}")
                await asyncio.sleep(2)

                run = await client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                if run.status == "requires_action":
                    # Handle function calls
                    tool_outputs = []

                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)

                        # 🔒 Create cache key para detectar duplicados
                        import hashlib
                        args_str = json.dumps(arguments, sort_keys=True)
                        cache_key = f"{function_name}:{hashlib.md5(args_str.encode()).hexdigest()}"

                        # 🔒 Check cache primero
                        if cache_key in tool_call_cache:
                            logger.warning(f"⚠️ DUPLICATE CALL PREVENTED: {function_name} - using cached result")
                            output = tool_call_cache[cache_key]
                        else:
                            logger.info(f"🔧 Executing tool: {function_name} | Args: {str(arguments)[:100]}")

                            # Execute the function
                            output = await self._execute_tool(function_name, arguments, tg_user_id)

                            # 🔒 Cache expensive operations para prevenir duplicados
                            if function_name in ["generate_video_sora2", "generate_caption"]:
                                tool_call_cache[cache_key] = output
                                logger.info(f"💾 Cached result for: {function_name}")

                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(output)
                        })

                    # Submit tool outputs
                    run = await client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            
            # Check final status
            logger.info(f"Agent loop ended. Final status: {run.status}, iterations: {iteration}/{max_iterations}")

            if run.status == "completed":
                # Get final response
                messages = await client.beta.threads.messages.list(thread_id=thread.id)
                assistant_message = messages.data[0].content[0].text.value

                logger.info(f"Agent completed successfully. Response length: {len(assistant_message)}")

                # Save conversation for context
                await db.save_conversation({
                    "tg_user_id": tg_user_id,
                    "thread_id": thread.id,
                    "run_id": run.id,
                    "user_message": prompt,
                    "assistant_message": assistant_message
                })

                # Parse structured response
                # The assistant should return JSON with video details
                try:
                    result = json.loads(assistant_message)
                    logger.info(f"Parsed JSON result with keys: {list(result.keys())}")
                    return result
                except Exception as parse_error:
                    # Fallback if assistant returns text
                    logger.warning(f"Could not parse assistant response as JSON: {parse_error}")
                    logger.debug(f"Assistant response: {assistant_message[:200]}...")
                    return {
                        "success": True,
                        "message": assistant_message
                    }

            elif iteration >= max_iterations:
                logger.error(f"Agent timeout: reached {max_iterations} iterations without completion")
                return {
                    "success": False,
                    "error": "timeout",
                    "message": "Video generation took too long. Please try again with a simpler prompt."
                }

            else:
                logger.error(f"Run failed with status: {run.status}")

                # Get error details if available
                error_message = "Sorry, something went wrong. Please try again."
                if run.last_error:
                    logger.error(f"Error details: {run.last_error}")
                    error_message = f"Error: {run.last_error.message if hasattr(run.last_error, 'message') else str(run.last_error)}"

                return {
                    "success": False,
                    "error": f"Agent failed: {run.status}",
                    "message": error_message
                }
        
        except Exception as e:
            logger.error(f"Error in create_video_flow: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "An error occurred. Please try again later."
            }
    
    async def _execute_tool(
        self, 
        function_name: str, 
        arguments: Dict, 
        tg_user_id: int
    ) -> Dict:
        """
        Execute tool functions called by the agent
        """
        try:
            if function_name == "check_user_limits":
                return await self._check_user_limits(arguments["tg_user_id"])
            
            elif function_name == "validate_content":
                return await self._validate_content(arguments["prompt"])
            
            elif function_name == "generate_video_sora2":
                return await self._generate_video(
                    arguments["prompt"],
                    arguments["duration"],
                    arguments["category"]
                )
            
            elif function_name == "generate_caption":
                return await self._generate_caption(
                    arguments["prompt"],
                    arguments["category"],
                    arguments.get("video_url")
                )
            
            elif function_name == "save_video_to_db":
                # Handle both formats: video_data as key or all arguments as video_data
                video_data = arguments.get("video_data", arguments)
                return await self._save_video_to_db(
                    arguments.get("tg_user_id", tg_user_id),
                    video_data
                )
            
            else:
                return {"error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            logger.error(f"Error executing {function_name}: {e}")
            return {"error": str(e)}
    
    # ==================== TOOL IMPLEMENTATIONS ====================
    
    async def _check_user_limits(self, tg_user_id: int) -> Dict:
        """Check if user can create videos"""
        from datetime import datetime, timedelta
        
        creator = await db.get_creator(tg_user_id)
        
        if not creator:
            return {"allowed": True, "reason": "New user"}
        
        # Check if banned
        if creator.get("is_banned"):
            return {
                "allowed": False,
                "reason": "User is banned from campaign",
                "strikes": creator.get("strikes", 0)
            }
        
        # Check cooldown
        if creator.get("cooldown_until"):
            cooldown_until = datetime.fromisoformat(creator["cooldown_until"])
            if datetime.now() < cooldown_until:
                return {
                    "allowed": False,
                    "reason": f"User in cooldown until {cooldown_until.strftime('%Y-%m-%d %H:%M')}",
                    "cooldown_until": cooldown_until.isoformat()
                }
        
        # Check daily limit
        videos_today = await db.count_videos_today(tg_user_id)
        if videos_today >= settings.max_videos_per_day:
            return {
                "allowed": False,
                "reason": f"Daily limit reached ({settings.max_videos_per_day} videos/day)",
                "videos_today": videos_today
            }
        
        return {
            "allowed": True,
            "videos_today": videos_today,
            "limit": settings.max_videos_per_day
        }
    
    async def _validate_content(self, prompt: str) -> Dict:
        """Validate prompt against guidelines"""
        from agent.tools.content_validator import ContentValidator
        
        validator = ContentValidator()
        return await validator.validate(prompt)
    
    async def _generate_video(self, prompt: str, duration: int, category: str) -> Dict:
        """Generate video with Sora 2"""
        from agent.tools.sora2 import Sora2Generator
        
        generator = Sora2Generator()
        return await generator.generate(prompt, duration, category)
    
    async def _generate_caption(self, prompt: str, category: str, video_url: str = None) -> Dict:
        """Generate caption with GPT-4"""
        from agent.tools.captions import CaptionGenerator
        
        generator = CaptionGenerator()
        return await generator.generate(prompt, category, video_url)
    
    async def _save_video_to_db(self, tg_user_id: int, video_data: Dict) -> Dict:
        """Save video to database"""
        try:
            video = await db.create_video(video_data)
            return {
                "success": True,
                "video_id": video["id"],
                "video_uuid": video["video_uuid"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global agent instance
agent = ETHCreatorsAgent()
