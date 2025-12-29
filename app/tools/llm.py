"""LLM wrapper with retry and structured output support."""

import json
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.errors import LLMError
from app.core.logging import get_logger
from app.core.retry import retry_on_llm_error

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """OpenAI LLM client with retry and structured output."""

    def __init__(self) -> None:
        """Initialize LLM client."""
        settings = get_settings()
        # Support custom API base URL for proxies
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,  # Will be None if not set, defaults to OpenAI
        )
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens

    @retry_on_llm_error
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate text completion.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            
        Returns:
            Generated text
            
        Raises:
            LLMError: If generation fails
        """
        try:
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens,
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise LLMError("Empty response from LLM")
            
            logger.info(
                "llm_generation_success",
                model=self.model,
                prompt_length=len(prompt),
                response_length=len(content),
            )
            return content
            
        except Exception as e:
            logger.error("llm_generation_failed", error=str(e))
            raise LLMError(f"LLM generation failed: {e}") from e

    @retry_on_llm_error
    async def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
        system_prompt: str | None = None,
    ) -> T:
        """Generate structured output using Pydantic model.
        
        Args:
            prompt: User prompt
            response_model: Pydantic model for response
            system_prompt: Optional system prompt
            
        Returns:
            Parsed Pydantic model instance
            
        Raises:
            LLMError: If generation or parsing fails
        """
        try:
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add JSON schema instruction with clear examples
            schema = response_model.model_json_schema()
            # Remove 'description' and 'title' to reduce confusion
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Build a cleaner schema representation
            fields_desc = []
            for field_name, field_info in properties.items():
                field_type = field_info.get("type", "string")
                if field_type == "array":
                    item_type = field_info.get("items", {}).get("type", "string")
                    fields_desc.append(f'  "{field_name}": [{item_type}, {item_type}, ...]')
                else:
                    fields_desc.append(f'  "{field_name}": <{field_type}>')
            
            fields_str = ",\n".join(fields_desc)
            
            enhanced_prompt = f"""{prompt}

You MUST respond with a JSON object containing actual data values. The JSON structure should be:
{{
{fields_str}
}}

IMPORTANT:
- Fill in ACTUAL VALUES based on the research query, not schema descriptions
- Each array should contain real strings/values, not type definitions
- Do NOT return the schema itself, return data that matches the schema

Return ONLY the JSON object with real data, no additional text."""
            
            messages.append({"role": "user", "content": enhanced_prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise LLMError("Empty response from LLM")
            
            # Parse JSON and validate with Pydantic
            parsed = response_model.model_validate_json(content)
            
            logger.info(
                "llm_structured_generation_success",
                model=self.model,
                response_model=response_model.__name__,
            )
            return parsed
            
        except Exception as e:
            logger.error("llm_structured_generation_failed", error=str(e))
            raise LLMError(f"Structured generation failed: {e}") from e


# Global LLM client instance
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance.
    
    Returns:
        LLMClient: Global LLM client
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
