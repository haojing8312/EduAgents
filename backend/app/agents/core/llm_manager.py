"""
LLM Manager - Dual-model strategy with Claude and GPT-4o
Implements intelligent model selection, fallback mechanisms, token optimization, and LLM response caching
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp
import tiktoken
import httpx
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logger for this module
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available LLM models"""

    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU = "claude-3-5-haiku-20241022"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    DEEPSEEK_CHAT = "deepseek-chat"


class ModelCapability(Enum):
    """Model capabilities for intelligent selection"""

    REASONING = "reasoning"
    CREATIVITY = "creativity"
    ANALYSIS = "analysis"
    CODING = "coding"
    LANGUAGE = "language"
    VISION = "vision"


class LLMResponse(BaseModel):
    """Structured LLM response"""

    content: str
    model_used: str
    tokens_used: int
    latency_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMManager:
    """
    Advanced LLM Manager with dual-model strategy
    Implements intelligent routing, fallback, and optimization
    """

    # Model capability matrix for intelligent selection
    MODEL_CAPABILITIES = {
        ModelType.CLAUDE_35_SONNET: {
            ModelCapability.REASONING: 0.95,
            ModelCapability.CREATIVITY: 0.98,
            ModelCapability.ANALYSIS: 0.93,
            ModelCapability.CODING: 0.96,
            ModelCapability.LANGUAGE: 0.97,
        },
        ModelType.GPT_4O: {
            ModelCapability.REASONING: 0.94,
            ModelCapability.CREATIVITY: 0.92,
            ModelCapability.ANALYSIS: 0.96,
            ModelCapability.CODING: 0.95,
            ModelCapability.LANGUAGE: 0.94,
        },
        ModelType.CLAUDE_35_HAIKU: {
            ModelCapability.REASONING: 0.88,
            ModelCapability.CREATIVITY: 0.90,
            ModelCapability.ANALYSIS: 0.87,
            ModelCapability.CODING: 0.89,
            ModelCapability.LANGUAGE: 0.91,
        },
        ModelType.GPT_4O_MINI: {
            ModelCapability.REASONING: 0.85,
            ModelCapability.CREATIVITY: 0.86,
            ModelCapability.ANALYSIS: 0.88,
            ModelCapability.CODING: 0.87,
            ModelCapability.LANGUAGE: 0.89,
        },
    }

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_base_url: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        anthropic_model_name: Optional[str] = None,
        openai_model_name: Optional[str] = None,
        default_model: ModelType = ModelType.DEEPSEEK_CHAT,
        enable_fallback: bool = True,
        max_retries: int = 3,
        temperature: float = 0.7,
        test_mode: bool = False,
    ):
        """Initialize the LLM Manager with API clients"""
        self.test_mode = test_mode
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_base_url = anthropic_base_url or os.getenv("ANTHROPIC_API_BASE", "https://api.anthropic.com")
        self.openai_base_url = openai_base_url or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.anthropic_model_name = anthropic_model_name or os.getenv("ANTHROPIC_MODEL_NAME")
        self.openai_model_name = openai_model_name or os.getenv("OPENAI_MODEL_NAME")

        # Initialize clients (skip if in test mode)
        if self.test_mode:
            self.anthropic_client = None
            self.openai_client = None
        else:
            # 配置代理设置
            proxy_config = self._get_proxy_config()

            self.anthropic_client = (
                AsyncAnthropic(
                    api_key=self.anthropic_api_key,
                    base_url=self.anthropic_base_url,
                    http_client=httpx.AsyncClient(proxy=proxy_config) if proxy_config else None
                )
                if self.anthropic_api_key
                else None
            )
            self.openai_client = (
                AsyncOpenAI(
                    api_key=self.openai_api_key,
                    base_url=self.openai_base_url,
                    http_client=httpx.AsyncClient(proxy=proxy_config) if proxy_config else None
                ) if self.openai_api_key else None
            )

        self.default_model = default_model
        self.enable_fallback = enable_fallback
        self.max_retries = max_retries
        self.temperature = temperature

        # Token tracking
        self.total_tokens = 0
        self.token_usage_by_model = {}

        # Performance metrics
        self.request_count = 0
        self.error_count = 0
        self.fallback_count = 0

        # Initialize tokenizers
        self.gpt_tokenizer = tiktoken.encoding_for_model("gpt-4o")

        # Cache integration
        self.enable_caching = True
        self._llm_cache = None

    def _get_proxy_config(self) -> Optional[str]:
        """获取代理配置"""
        # 优先使用HTTPS代理，然后HTTP代理
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy") or \
                os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        return proxy

    def select_model_for_task(
        self, required_capabilities: List[ModelCapability], prefer_speed: bool = False
    ) -> ModelType:
        """Intelligently select the best model for a given task"""
        if prefer_speed:
            # Prefer faster models for speed-critical tasks
            candidates = [ModelType.CLAUDE_35_HAIKU, ModelType.GPT_4O_MINI]
        else:
            # Use premium models for quality-critical tasks
            candidates = [ModelType.CLAUDE_35_SONNET, ModelType.GPT_4O]

        # Score models based on required capabilities
        model_scores = {}
        for model in candidates:
            score = sum(
                self.MODEL_CAPABILITIES[model].get(cap, 0)
                for cap in required_capabilities
            ) / len(required_capabilities)
            model_scores[model] = score

        # Return the best scoring model
        return max(model_scores, key=model_scores.get)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
    ) -> str:
        """Call Claude API with retry logic"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # 使用自定义模型名称（如果配置了）
        actual_model = self.anthropic_model_name or model

        response = await self.anthropic_client.messages.create(
            model=actual_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Track metrics
        self.total_tokens += response.usage.total_tokens
        self.token_usage_by_model[model] = (
            self.token_usage_by_model.get(model, 0) + response.usage.total_tokens
        )

        return response.content[0].text

    async def _call_claude_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Call Claude API with streaming"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")

        # 使用自定义模型名称（如果配置了）
        actual_model = self.anthropic_model_name or model

        async with self.anthropic_client.messages.stream(
            model=actual_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:
                yield text

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
    ) -> str:
        """Call OpenAI API with retry logic"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # 使用自定义模型名称（如果配置了）
        actual_model = self.openai_model_name or model

        response = await self.openai_client.chat.completions.create(
            model=actual_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Track metrics
        if response.usage:
            self.total_tokens += response.usage.total_tokens
            self.token_usage_by_model[model] = (
                self.token_usage_by_model.get(model, 0)
                + response.usage.total_tokens
            )

        return response.choices[0].message.content

    async def _call_openai_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Call OpenAI API with streaming"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # 使用自定义模型名称（如果配置了）
        actual_model = self.openai_model_name or model

        stream_response = await self.openai_client.chat.completions.create(
            model=actual_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream_response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
        required_capabilities: Optional[List[ModelCapability]] = None,
        stream: bool = False,
    ) -> AsyncGenerator[str, None] | LLMResponse:
        """
        Generate response from LLM with intelligent model selection and fallback
        """
        # Select model based on task requirements
        if model is None:
            if required_capabilities:
                model = self.select_model_for_task(required_capabilities)
            else:
                model = self.default_model

        temperature = temperature or self.temperature

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Handle test mode
        if self.test_mode:
            if stream:
                return self._generate_mock_stream(prompt, system_prompt, model.value)
            else:
                response_content = await self._generate_mock_response(prompt, system_prompt, model.value)
                return LLMResponse(
                    content=response_content,
                    model_used=f"mock-{model.value}",
                    tokens_used=100,  # Mock token count
                    latency_ms=500.0,  # Mock latency
                    metadata={"test_mode": True}
                )

        # Check cache first (only for non-streaming requests)
        if not stream and self.enable_caching:
            # Initialize cache if needed
            if self._llm_cache is None:
                try:
                    from app.core.cache import llm_cache
                    self._llm_cache = llm_cache
                except ImportError:
                    pass  # Cache not available

            # Check for cached response
            if self._llm_cache:
                # Create cache key from combined prompt
                full_prompt = f"{system_prompt or ''}\n\n{prompt}"
                cached_response = await self._llm_cache.get_llm_response(
                    full_prompt, model.value
                )
                if cached_response:
                    # Return cached response wrapped in LLMResponse
                    return LLMResponse(
                        content=cached_response,
                        model_used=model.value,
                        tokens_used=0,  # No new tokens used
                        latency_ms=0.1,  # Minimal cache lookup time
                        metadata={"cached": True, "cache_hit": True}
                    )

        # Track request
        self.request_count += 1
        start_time = datetime.utcnow()

        try:
            # Primary model call
            if stream:
                # Return streaming generator
                if model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]:
                    return self._call_claude_stream(
                        messages, model.value, temperature, max_tokens
                    )
                else:
                    return self._call_openai_stream(
                        messages, model.value, temperature, max_tokens
                    )
            else:
                # Non-streaming call
                if model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]:
                    result = await self._call_claude(
                        messages, model.value, temperature, max_tokens
                    )
                else:
                    result = await self._call_openai(
                        messages, model.value, temperature, max_tokens
                    )

                # Calculate metrics
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                # Cache the response
                if self.enable_caching and self._llm_cache:
                    full_prompt = f"{system_prompt or ''}\n\n{prompt}"
                    await self._llm_cache.cache_llm_response(
                        full_prompt, model.value, result
                    )

                return LLMResponse(
                    content=result,
                    model_used=model.value,
                    tokens_used=self._estimate_tokens(prompt + result),
                    latency_ms=latency_ms,
                    metadata={
                        "temperature": temperature,
                        "capabilities": required_capabilities,
                        "cached": False,
                        "cache_hit": False
                    },
                )

        except Exception as e:
            self.error_count += 1

            # Fallback logic
            if self.enable_fallback:
                self.fallback_count += 1

                # Try fallback model
                fallback_model = (
                    ModelType.GPT_4O
                    if model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]
                    else ModelType.CLAUDE_35_SONNET
                )

                try:
                    if fallback_model in [
                        ModelType.CLAUDE_35_SONNET,
                        ModelType.CLAUDE_35_HAIKU,
                    ]:
                        result = await self._call_claude(
                            messages,
                            fallback_model.value,
                            temperature,
                            max_tokens,
                        )
                    else:
                        result = await self._call_openai(
                            messages,
                            fallback_model.value,
                            temperature,
                            max_tokens,
                        )

                    if stream:
                        return result

                    latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

                    return LLMResponse(
                        content=result,
                        model_used=fallback_model.value,
                        tokens_used=self._estimate_tokens(prompt + result),
                        latency_ms=latency_ms,
                        metadata={
                            "temperature": temperature,
                            "capabilities": required_capabilities,
                            "fallback": True,
                            "original_error": str(e),
                        },
                    )
                except Exception as fallback_error:
                    raise Exception(
                        f"Both primary and fallback models failed: {e}, {fallback_error}"
                    )
            else:
                raise e

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        temperature: float = 0.3,  # Lower temperature for structured output
    ) -> Dict[str, Any]:
        """Generate structured JSON output from LLM"""

        # Enhance prompt with schema instructions
        enhanced_prompt = f"""
{prompt}

Please provide your response in the following JSON format:
```json
{json.dumps(response_schema, indent=2)}
```

Ensure your response is valid JSON that matches the schema exactly.
"""

        response = await self.generate(
            prompt=enhanced_prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            required_capabilities=[ModelCapability.ANALYSIS],
        )

        # Debug: check if we're in test mode and what we got
        print(f"🔍 generate_structured got response: {type(response)} - content type: {type(response.content)}")
        if self.test_mode:
            print(f"🔍 test mode response content: {response.content[:200]}...")

        # Parse JSON response with enhanced error handling
        def clean_json_content(content: str) -> str:
            """Clean and prepare JSON content for parsing"""
            # Remove markdown code blocks
            if "```json" in content:
                parts = content.split("```json")
                if len(parts) > 1:
                    content = parts[1].split("```")[0]
            elif "```" in content:
                # Handle generic code blocks
                parts = content.split("```")
                if len(parts) >= 3:
                    content = parts[1]

            # Strip whitespace
            content = content.strip()

            # Find the JSON content between first { and last }
            start_idx = content.find("{")
            end_idx = content.rfind("}")

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                content = content[start_idx:end_idx + 1]

            # Fix common JSON issues
            # Replace smart quotes with regular quotes
            content = content.replace(""", '"').replace(""", '"')
            content = content.replace("'", '"')

            # Handle incomplete strings by truncating at the last complete key-value pair
            # This is a safety mechanism for extremely large responses
            if len(content) > 50000:  # If response is very large
                last_complete = content.rfind('",')
                if last_complete > 0:
                    # Find the closing brace for this section
                    remaining = content[last_complete + 2:].strip()
                    if not remaining.endswith('}'):
                        content = content[:last_complete + 2] + '\n}'

            return content

        def advanced_json_repair(content: str, error: json.JSONDecodeError) -> str:
            """Advanced JSON repair mechanisms for common formatting issues"""
            try:
                # Handle specific error types
                error_msg = str(error).lower()

                if "expecting ',' delimiter" in error_msg:
                    # Look for missing commas between key-value pairs
                    lines = content.split('\n')
                    repaired_lines = []

                    for i, line in enumerate(lines):
                        stripped = line.strip()
                        # If line ends with " and next line starts with ", add comma
                        if (stripped.endswith('"') and not stripped.endswith('",') and
                            i < len(lines) - 1 and lines[i + 1].strip().startswith('"')):
                            line = line.rstrip() + ','
                        repaired_lines.append(line)

                    content = '\n'.join(repaired_lines)

                elif "expecting property name" in error_msg:
                    # Handle trailing comma issues
                    content = re.sub(r',\s*}', '}', content)
                    content = re.sub(r',\s*]', ']', content)

                elif "unterminated string" in error_msg:
                    # Find and fix unterminated strings
                    if hasattr(error, 'pos'):
                        # Truncate at error position and try to close properly
                        error_pos = error.pos
                        before_error = content[:error_pos]

                        # Find last complete key-value pair
                        last_quote = before_error.rfind('"')
                        if last_quote > 0:
                            # Look backwards to find proper truncation point
                            truncate_pos = before_error.rfind('",', 0, last_quote)
                            if truncate_pos > 0:
                                content = before_error[:truncate_pos + 2] + '\n}'

                return content
            except Exception as repair_error:
                logger.debug(f"JSON高级修复失败: {repair_error}")
                return content

        try:
            # Clean and extract JSON from response
            content = clean_json_content(response.content)
            return json.loads(content)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败: {e}, 尝试修复...")

            # Try to fix the JSON using advanced repair mechanisms
            try:
                # Apply advanced JSON repair
                repaired_content = advanced_json_repair(content, e)
                result = json.loads(repaired_content)
                logger.info(f"✅ JSON高级修复成功")
                return result
            except json.JSONDecodeError:
                logger.warning(f"JSON高级修复失败，尝试传统修复...")

            # Try legacy repair approach if advanced repair fails
            try:
                # Attempt to fix incomplete JSON
                content = clean_json_content(response.content)

                # Handle unterminated strings - find last complete pair
                if "Unterminated string" in str(e):
                    # Find the position of the error
                    error_pos = getattr(e, 'pos', len(content))

                    # Truncate at the last complete JSON element before the error
                    truncated = content[:error_pos]

                    # Find last complete key-value pair
                    last_comma = truncated.rfind('",')
                    if last_comma > 0:
                        truncated = truncated[:last_comma + 2]

                        # Close any open objects/arrays
                        open_braces = truncated.count('{') - truncated.count('}')
                        open_brackets = truncated.count('[') - truncated.count(']')

                        for _ in range(open_brackets):
                            truncated += ']'
                        for _ in range(open_braces):
                            truncated += '}'

                        return json.loads(truncated)

            except Exception as repair_error:
                logger.warning(f"JSON修复失败: {repair_error}")

            # Retry with more explicit instructions and simplified request
            retry_prompt = f"""
The previous response contained invalid JSON. Please provide a response in valid JSON format only.

Original request: {prompt}

CRITICAL INSTRUCTIONS:
1. Respond ONLY with valid JSON - no markdown, no explanations
2. Ensure all strings are properly escaped with double quotes
3. Do not include any text outside the JSON object
4. If the content is large, prioritize completeness of structure over detail

Required JSON structure:
{json.dumps(response_schema, indent=2)}
"""

            # 实现3次重试机制，绝不降低质量
            max_retries = 3
            for retry_count in range(max_retries):
                try:
                    logger.info(f"🔄 JSON解析重试 {retry_count + 1}/{max_retries}")

                    retry_response = await self.generate(
                        prompt=retry_prompt,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=0.1 - (retry_count * 0.02),  # 逐渐降低温度
                    )

                    cleaned_retry = clean_json_content(retry_response.content)
                    result = json.loads(cleaned_retry)

                    logger.info(f"✅ JSON解析重试第{retry_count + 1}次成功")
                    return result

                except json.JSONDecodeError as retry_error:
                    logger.warning(f"⚠️ JSON解析重试第{retry_count + 1}次失败: {retry_error}")
                    if retry_count == max_retries - 1:
                        # 3次重试都失败，明确抛出错误，不提供低质量兜底
                        logger.error(f"❌ JSON解析经过{max_retries}次重试全部失败")
                        logger.error(f"最终错误内容预览: {retry_response.content[:500]}...")
                        raise json.JSONDecodeError(
                            f"JSON解析失败，经过{max_retries}次重试仍无法解析。"
                            f"最后一次错误: {retry_error}",
                            retry_response.content,
                            retry_error.pos if hasattr(retry_error, 'pos') else 0
                        )

                    # 继续下一次重试
                    continue


    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for a given text"""
        try:
            return len(self.gpt_tokenizer.encode(text))
        except:
            # Rough estimate: 1 token per 4 characters
            return len(text) // 4

    def get_metrics(self) -> Dict[str, Any]:
        """Get usage metrics and statistics"""
        return {
            "total_tokens": self.total_tokens,
            "token_usage_by_model": self.token_usage_by_model,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "fallback_count": self.fallback_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "fallback_rate": self.fallback_count / max(self.request_count, 1),
            "estimated_cost": self._estimate_cost(),
        }

    def _estimate_cost(self) -> float:
        """Estimate cost based on token usage"""
        cost = 0.0

        # Pricing per 1M tokens (approximate)
        pricing = {
            ModelType.CLAUDE_35_SONNET.value: 15.0,
            ModelType.CLAUDE_35_HAIKU.value: 1.0,
            ModelType.GPT_4O.value: 10.0,
            ModelType.GPT_4O_MINI.value: 0.6,
        }

        for model, tokens in self.token_usage_by_model.items():
            if model in pricing:
                cost += (tokens / 1_000_000) * pricing[model]

        return round(cost, 4)

    # Mock methods for testing
    async def _generate_mock_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "mock-model"
    ) -> str:
        """Generate a realistic mock response based on the prompt content"""

        # Simulate processing time
        await asyncio.sleep(0.5)

        # Generate contextual responses based on prompt keywords
        prompt_lower = prompt.lower()
        system_lower = (system_prompt or "").lower()

        # Debug: show what we're matching against
        print(f"🔍 Mock matching - prompt keywords: {prompt_lower[:100]}...")
        print(f"🔍 Mock matching - system keywords: {system_lower[:100]}...")

        # Check for Course Architect first (higher priority)
        if "course structure" in prompt_lower or "course architect" in system_lower or "course architecture" in system_lower:
            print("🔍 Matched: Course Architect")
            return json.dumps({
                "modules": [
                    {
                        "id": "1",
                        "title": "Introduction to AI Ethics",
                        "duration": "1 week",
                        "objectives": [
                            "Understand fundamental AI ethics principles",
                            "Identify key ethical challenges in AI development"
                        ],
                        "key_concepts": ["AI ethics", "moral reasoning", "technological impact"],
                        "activities": ["Ethics case study analysis", "Group discussions", "Reflection essays"],
                        "deliverables": ["Ethics framework document", "Case study presentation"],
                        "prerequisites": ["Basic understanding of AI technology"],
                        "resources": ["Ethics readings", "Case study materials", "Discussion forums"]
                    },
                    {
                        "id": "2",
                        "title": "Bias and Fairness in AI",
                        "duration": "1 week",
                        "objectives": [
                            "Analyze bias in AI systems",
                            "Evaluate fairness metrics and approaches"
                        ],
                        "key_concepts": ["Algorithmic bias", "fairness metrics", "data representation"],
                        "activities": ["Bias detection workshop", "Fairness algorithm design", "Real-world case analysis"],
                        "deliverables": ["Bias audit report", "Fairness improvement proposal"],
                        "prerequisites": ["Understanding of AI ethics basics"],
                        "resources": ["Bias detection tools", "Fairness research papers", "Algorithm examples"]
                    }
                ],
                "project_phases": [
                    {
                        "phase": "Research and Analysis",
                        "description": "Students research AI ethics challenges and analyze real-world cases",
                        "duration": "2 weeks",
                        "milestones": ["Research complete", "Case analysis finished"],
                        "success_criteria": ["Comprehensive research documentation", "Clear case analysis"]
                    },
                    {
                        "phase": "Solution Development",
                        "description": "Students develop ethical frameworks and solutions",
                        "duration": "2 weeks",
                        "milestones": ["Framework draft", "Solution prototype"],
                        "success_criteria": ["Well-structured ethical framework", "Practical solution proposal"]
                    }
                ],
                "assessment_points": [
                    {
                        "type": "Formative",
                        "timing": "Weekly",
                        "focus": "Understanding and progress",
                        "weight": 40
                    },
                    {
                        "type": "Summative",
                        "timing": "End of course",
                        "focus": "Final project and framework",
                        "weight": 60
                    }
                ],
                "learning_pathways": {
                    "standard": {"description": "Regular pace with guided support", "pace": "4 weeks"},
                    "accelerated": {"description": "Fast-track for advanced students", "pace": "3 weeks"},
                    "supported": {"description": "Additional scaffolding for struggling students", "pace": "5 weeks"}
                },
                "resource_plan": {
                    "materials": ["Ethics textbook", "Case study collection", "Research articles"],
                    "tools": ["Discussion platform", "Collaboration tools", "Presentation software"],
                    "spaces": ["Classroom", "Computer lab", "Online forum"],
                    "external_resources": ["Ethics experts", "Industry case studies", "Online databases"]
                }
            })
        elif "theoretical framework" in prompt_lower or "educational theorist" in system_lower:
            print("🔍 Matched: Education Theorist")
            return json.dumps({
                "learning_theories": [
                    {
                        "id": "1",
                        "title": "Introduction to AI Ethics",
                        "duration": "1 week",
                        "objectives": [
                            "Understand fundamental AI ethics principles",
                            "Identify key ethical challenges in AI development"
                        ],
                        "key_concepts": ["AI ethics", "moral reasoning", "technological impact"],
                        "activities": ["Ethics case study analysis", "Group discussions", "Reflection essays"],
                        "deliverables": ["Ethics framework document", "Case study presentation"],
                        "prerequisites": ["Basic understanding of AI technology"],
                        "resources": ["Ethics readings", "Case study materials", "Discussion forums"]
                    },
                    {
                        "id": "2",
                        "title": "Bias and Fairness in AI",
                        "duration": "1 week",
                        "objectives": [
                            "Analyze bias in AI systems",
                            "Evaluate fairness metrics and approaches"
                        ],
                        "key_concepts": ["Algorithmic bias", "fairness metrics", "data representation"],
                        "activities": ["Bias detection workshop", "Fairness algorithm design", "Real-world case analysis"],
                        "deliverables": ["Bias audit report", "Fairness improvement proposal"],
                        "prerequisites": ["Understanding of AI ethics basics"],
                        "resources": ["Bias detection tools", "Fairness research papers", "Algorithm examples"]
                    }
                ],
                "project_phases": [
                    {
                        "phase": "Research and Analysis",
                        "description": "Students research AI ethics challenges and analyze real-world cases",
                        "duration": "2 weeks",
                        "milestones": ["Research complete", "Case analysis finished"],
                        "success_criteria": ["Comprehensive research documentation", "Clear case analysis"]
                    },
                    {
                        "phase": "Solution Development",
                        "description": "Students develop ethical frameworks and solutions",
                        "duration": "2 weeks",
                        "milestones": ["Framework draft", "Solution prototype"],
                        "success_criteria": ["Well-structured ethical framework", "Practical solution proposal"]
                    }
                ],
                "assessment_points": [
                    {
                        "type": "Formative",
                        "timing": "Weekly",
                        "focus": "Understanding and progress",
                        "weight": 40
                    },
                    {
                        "type": "Summative",
                        "timing": "End of course",
                        "focus": "Final project and framework",
                        "weight": 60
                    }
                ],
                "learning_pathways": {
                    "standard": {"description": "Regular pace with guided support", "pace": "4 weeks"},
                    "accelerated": {"description": "Fast-track for advanced students", "pace": "3 weeks"},
                    "supported": {"description": "Additional scaffolding for struggling students", "pace": "5 weeks"}
                },
                "resource_plan": {
                    "materials": ["Ethics textbook", "Case study collection", "Research articles"],
                    "tools": ["Discussion platform", "Collaboration tools", "Presentation software"],
                    "spaces": ["Classroom", "Computer lab", "Online forum"],
                    "external_resources": ["Ethics experts", "Industry case studies", "Online databases"]
                }
            })
        elif "content design" in prompt_lower or "material" in prompt_lower or "worksheets" in prompt_lower or "templates" in prompt_lower or "digital" in prompt_lower:
            print("🔍 Matched: Material Creator")
            return json.dumps({
                "worksheets": [
                    {
                        "title": "AI Ethics Case Study Analysis Worksheet",
                        "type": "worksheet",
                        "format": "PDF",
                        "description": "Structured worksheet for analyzing AI ethics case studies",
                        "sections": [
                            {"title": "Case Overview", "type": "text_input"},
                            {"title": "Stakeholder Analysis", "type": "table"},
                            {"title": "Ethical Issues Identification", "type": "checklist"},
                            {"title": "Solution Proposal", "type": "long_text"}
                        ],
                        "instructions": "Students will use this worksheet to systematically analyze AI ethics cases"
                    },
                    {
                        "title": "Bias Detection Lab Guide",
                        "type": "lab_guide",
                        "format": "PDF",
                        "description": "Step-by-step guide for conducting bias detection experiments",
                        "sections": [
                            {"title": "Pre-lab Setup", "type": "checklist"},
                            {"title": "Experiment Steps", "type": "numbered_list"},
                            {"title": "Data Collection", "type": "table"},
                            {"title": "Analysis Questions", "type": "questions"}
                        ],
                        "instructions": "Follow these steps to conduct bias detection analysis"
                    }
                ],
                "templates": [
                    {
                        "name": "Project Proposal Template",
                        "type": "document_template",
                        "format": "DOCX",
                        "sections": ["Executive Summary", "Problem Statement", "Methodology", "Timeline"]
                    },
                    {
                        "name": "Presentation Template",
                        "type": "presentation_template",
                        "format": "PPTX",
                        "slides": ["Title", "Problem", "Research", "Solution", "Conclusion"]
                    }
                ],
                "teacher_guide": {
                    "title": "AI Ethics PBL Course - Teacher Implementation Guide",
                    "format": "PDF",
                    "sections": [
                        {
                            "title": "Course Overview",
                            "content": "Comprehensive overview of AI ethics education goals and objectives"
                        },
                        {
                            "title": "Implementation Strategy",
                            "content": "Step-by-step guide for implementing PBL methodology"
                        },
                        {
                            "title": "Lesson Plans",
                            "content": "Detailed lesson plans for each module with timing and activities"
                        },
                        {
                            "title": "Assessment Guidelines",
                            "content": "How to evaluate student progress and project outcomes"
                        },
                        {
                            "title": "Troubleshooting",
                            "content": "Common challenges and solutions for teachers"
                        }
                    ],
                    "duration": "Complete course implementation guide"
                },
                "digital_resources": [
                    {
                        "title": "Interactive AI Ethics Simulator",
                        "type": "web_application",
                        "description": "Students can simulate ethical decisions in AI scenarios",
                        "url": "https://ai-ethics-simulator.example.com",
                        "requirements": "Web browser, internet connection"
                    },
                    {
                        "title": "Bias Detection Toolkit",
                        "type": "software_tool",
                        "description": "Tool for detecting bias in datasets and algorithms",
                        "platform": "Python/Jupyter",
                        "installation": "pip install bias-detector"
                    },
                    {
                        "title": "Virtual Reality Ethics Lab",
                        "type": "vr_experience",
                        "description": "Immersive experiences for exploring AI ethics scenarios",
                        "platform": "VR headsets",
                        "duration": "30-45 minutes per scenario"
                    }
                ],
                "resources": [
                    {"type": "Reading", "title": "AI Ethics Principles", "source": "IEEE Standards"},
                    {"type": "Video", "title": "The Age of AI Documentary", "duration": "45 minutes"},
                    {"type": "Interactive", "title": "AI Bias Detection Tool", "platform": "Web-based"}
                ]
            })
        elif "assessment" in prompt_lower:
            return json.dumps({
                "assessment_framework": {
                    "philosophy": "Authentic assessment aligned with real-world application",
                    "formative_methods": ["Peer feedback", "Self-reflection", "Progress check-ins"],
                    "summative_methods": ["Project portfolio", "Presentation", "Written analysis"],
                    "rubric_criteria": ["Understanding", "Application", "Critical thinking", "Communication"]
                }
            })
        else:
            # General response - ensure it's valid JSON
            print("🔍 Matched: General/Fallback")
            return json.dumps({
                "general_response": {
                    "approach": "comprehensive",
                    "recommendations": [
                        "Clear Learning Objectives: Well-defined, measurable outcomes that align with student needs",
                        "Engaging Activities: Interactive, hands-on experiences that promote active learning",
                        "Authentic Assessment: Real-world applications that demonstrate student understanding",
                        "Collaborative Elements: Opportunities for peer interaction and shared learning",
                        "Technology Integration: Appropriate use of digital tools to enhance learning"
                    ],
                    "outcome": "Students develop both content knowledge and essential 21st-century skills while maintaining engagement and motivation throughout the learning process"
                },
                "status": "success",
                "type": "general_educational_recommendation"
            })

    async def _generate_mock_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "mock-model"
    ) -> AsyncGenerator[str, None]:
        """Generate a mock streaming response"""
        response_text = await self._generate_mock_response(prompt, system_prompt, model)

        # Split response into chunks and yield with delays
        words = response_text.split()
        chunk_size = 10

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            await asyncio.sleep(0.1)  # Simulate streaming delay
            yield chunk + " "
