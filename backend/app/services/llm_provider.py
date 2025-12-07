"""
AI服务提供商基类和多平台实现
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncGenerator
import openai
import anthropic
import dashscope
import httpx
from app.core.config import settings


class BaseLLMProvider(ABC):
    """AI服务提供商抽象基类"""

    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = None,
        **kwargs
    ) -> str:
        """同步对话补全"""
        pass

    @abstractmethod
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式对话补全"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI服务提供商"""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> str:
        client = openai.AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        client = openai.AsyncOpenAI(api_key=api_key)
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class ClaudeProvider(BaseLLMProvider):
    """Claude服务提供商"""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> str:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        # 提取system消息
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]

        response = await client.messages.create(
            model=model,
            system=system_msg,
            messages=user_messages,
            max_tokens=kwargs.get("max_tokens", 1024),
            **{k: v for k, v in kwargs.items() if k != "max_tokens"}
        )
        return response.content[0].text

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), None)
        user_messages = [m for m in messages if m["role"] != "system"]

        async with client.messages.stream(
            model=model,
            system=system_msg,
            messages=user_messages,
            max_tokens=kwargs.get("max_tokens", 1024),
        ) as stream:
            async for text in stream.text_stream:
                yield text


class QwenProvider(BaseLLMProvider):
    """通义千问服务提供商"""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "qwen-turbo",
        **kwargs
    ) -> str:
        dashscope.api_key = api_key
        response = await dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format="message",
            **kwargs
        )
        return response.output.choices[0].message.content

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "qwen-turbo",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        dashscope.api_key = api_key
        responses = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format="message",
            stream=True,
            **kwargs
        )
        for response in responses:
            if response.status_code == 200:
                yield response.output.choices[0].message.content


class ErnieProvider(BaseLLMProvider):
    """文心一言服务提供商"""

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "ernie-bot-turbo",
        **kwargs
    ) -> str:
        # 文心一言需要先获取access_token
        access_token = await self._get_access_token(api_key)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}",
                params={"access_token": access_token},
                json={"messages": messages, **kwargs}
            )
            data = response.json()
            return data["result"]

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        api_key: str,
        model: str = "ernie-bot-turbo",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        access_token = await self._get_access_token(api_key)

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}",
                params={"access_token": access_token},
                json={"messages": messages, "stream": True, **kwargs}
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        data = json.loads(line[6:])
                        if "result" in data:
                            yield data["result"]

    async def _get_access_token(self, api_key: str) -> str:
        """获取百度access_token（简化实现，实际需要缓存）"""
        # api_key格式: "api_key:secret_key"
        api_key_part, secret_key = api_key.split(":")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://aip.baidubce.com/oauth/2.0/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": api_key_part,
                    "client_secret": secret_key
                }
            )
            return response.json()["access_token"]


# 工厂函数
def get_llm_provider(provider_name: str) -> BaseLLMProvider:
    """获取AI服务提供商实例"""
    providers = {
        "openai": OpenAIProvider(),
        "claude": ClaudeProvider(),
        "qwen": QwenProvider(),
        "ernie": ErnieProvider(),
    }

    if provider_name not in providers:
        raise ValueError(f"不支持的AI平台: {provider_name}")

    return providers[provider_name]
