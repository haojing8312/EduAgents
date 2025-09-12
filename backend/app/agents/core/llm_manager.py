"""
LLM Manager - Dual-model strategy with Claude and GPT-4o
Implements intelligent model selection, fallback mechanisms, and token optimization
"""

import os
from typing import Dict, Any, Optional, List, AsyncGenerator
from enum import Enum
import asyncio
import json
from datetime import datetime
import aiohttp
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken
from pydantic import BaseModel, Field


class ModelType(Enum):
    """Available LLM models"""
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU = "claude-3-5-haiku-20241022"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


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
        }
    }
    
    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        default_model: ModelType = ModelType.CLAUDE_35_SONNET,
        enable_fallback: bool = True,
        max_retries: int = 3,
        temperature: float = 0.7
    ):
        """Initialize the LLM Manager with API clients"""
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize clients
        self.anthropic_client = AsyncAnthropic(api_key=self.anthropic_api_key) if self.anthropic_api_key else None
        self.openai_client = AsyncOpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
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
    
    def select_model_for_task(
        self,
        required_capabilities: List[ModelCapability],
        prefer_speed: bool = False
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_claude(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """Call Claude API with retry logic"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        start_time = datetime.utcnow()
        
        if stream:
            async with self.anthropic_client.messages.stream(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        else:
            response = await self.anthropic_client.messages.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track metrics
            self.total_tokens += response.usage.total_tokens
            self.token_usage_by_model[model] = self.token_usage_by_model.get(model, 0) + response.usage.total_tokens
            
            return response.content[0].text
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | str:
        """Call OpenAI API with retry logic"""
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
        
        start_time = datetime.utcnow()
        
        if stream:
            stream_response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Track metrics
            if response.usage:
                self.total_tokens += response.usage.total_tokens
                self.token_usage_by_model[model] = self.token_usage_by_model.get(model, 0) + response.usage.total_tokens
            
            return response.choices[0].message.content
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
        required_capabilities: Optional[List[ModelCapability]] = None,
        stream: bool = False
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
        
        # Track request
        self.request_count += 1
        start_time = datetime.utcnow()
        
        try:
            # Primary model call
            if model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]:
                result = await self._call_claude(
                    messages, model.value, temperature, max_tokens, stream
                )
            else:
                result = await self._call_openai(
                    messages, model.value, temperature, max_tokens, stream
                )
            
            if stream:
                return result  # Return generator for streaming
            
            # Calculate metrics
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return LLMResponse(
                content=result,
                model_used=model.value,
                tokens_used=self._estimate_tokens(prompt + result),
                latency_ms=latency_ms,
                metadata={
                    "temperature": temperature,
                    "capabilities": required_capabilities
                }
            )
            
        except Exception as e:
            self.error_count += 1
            
            # Fallback logic
            if self.enable_fallback:
                self.fallback_count += 1
                
                # Try fallback model
                fallback_model = (
                    ModelType.GPT_4O if model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]
                    else ModelType.CLAUDE_35_SONNET
                )
                
                try:
                    if fallback_model in [ModelType.CLAUDE_35_SONNET, ModelType.CLAUDE_35_HAIKU]:
                        result = await self._call_claude(
                            messages, fallback_model.value, temperature, max_tokens, stream
                        )
                    else:
                        result = await self._call_openai(
                            messages, fallback_model.value, temperature, max_tokens, stream
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
                            "original_error": str(e)
                        }
                    )
                except Exception as fallback_error:
                    raise Exception(f"Both primary and fallback models failed: {e}, {fallback_error}")
            else:
                raise e
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        temperature: float = 0.3  # Lower temperature for structured output
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
            required_capabilities=[ModelCapability.ANALYSIS]
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            # Retry with more explicit instructions
            retry_prompt = f"""
The previous response was not valid JSON. {prompt}

IMPORTANT: Respond ONLY with valid JSON matching this exact structure:
{json.dumps(response_schema, indent=2)}

No markdown, no explanations, just the JSON object.
"""
            
            retry_response = await self.generate(
                prompt=retry_prompt,
                system_prompt=system_prompt,
                model=model,
                temperature=0.1  # Very low temperature for retry
            )
            
            return json.loads(retry_response.content.strip())
    
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
            "estimated_cost": self._estimate_cost()
        }
    
    def _estimate_cost(self) -> float:
        """Estimate cost based on token usage"""
        cost = 0.0
        
        # Pricing per 1M tokens (approximate)
        pricing = {
            ModelType.CLAUDE_35_SONNET.value: 15.0,
            ModelType.CLAUDE_35_HAIKU.value: 1.0,
            ModelType.GPT_4O.value: 10.0,
            ModelType.GPT_4O_MINI.value: 0.6
        }
        
        for model, tokens in self.token_usage_by_model.items():
            if model in pricing:
                cost += (tokens / 1_000_000) * pricing[model]
        
        return round(cost, 4)