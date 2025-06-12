import os
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from openai import AsyncOpenAI
import httpx
from backend.config import settings
from backend.models import PromptOptimizeRequest, PromptOptimizeResponse
import logging

# 配置日志
logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务，支持多种大模型提供商"""

    def __init__(self):
        self.providers = {}
        self.clients = {}
        self._init_providers()

    def _init_providers(self):
        """初始化LLM提供商"""
        # Gemini 配置
        if (
            settings.GEMINI_API_KEY
            and settings.GEMINI_API_KEY != "your_gemini_api_key_here"
        ):
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.providers["gemini"] = self._gemini_optimize
                logger.info(
                    f"Gemini provider initialized with model: {settings.GEMINI_MODEL}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

        # Qwen (通义千问) 配置
        if settings.QWEN_API_KEY and settings.QWEN_API_KEY != "your_qwen_api_key_here":
            try:
                # 为 Qwen 创建自定义的 httpx 客户端，设置更长的超时
                self.clients["qwen"] = AsyncOpenAI(
                    api_key=settings.QWEN_API_KEY,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    timeout=httpx.Timeout(
                        timeout=settings.LLM_TIMEOUT,
                        connect=10.0,  # 连接超时10秒
                        read=settings.LLM_TIMEOUT,  # 读取超时
                        write=10.0,  # 写入超时10秒
                        pool=None,  # 连接池超时不设限制
                    ),
                )
                self.providers["qwen"] = self._qwen_optimize
                logger.info(
                    f"Qwen provider initialized with model: {settings.QWEN_MODEL}, timeout: {settings.LLM_TIMEOUT}s"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Qwen: {e}")

        # DeepSeek 配置
        if (
            settings.DEEPSEEK_API_KEY
            and settings.DEEPSEEK_API_KEY != "your_deepseek_api_key_here"
        ):
            try:
                # 为 DeepSeek 创建自定义的 httpx 客户端，设置更长的超时
                self.clients["deepseek"] = AsyncOpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com/v1",
                    timeout=httpx.Timeout(
                        timeout=settings.LLM_TIMEOUT,
                        connect=10.0,
                        read=settings.LLM_TIMEOUT,
                        write=10.0,
                        pool=None,
                    ),
                )
                self.providers["deepseek"] = self._deepseek_optimize
                logger.info(
                    f"DeepSeek provider initialized with model: {settings.DEEPSEEK_MODEL}, timeout: {settings.LLM_TIMEOUT}s"
                )
            except Exception as e:
                logger.error(f"Failed to initialize DeepSeek: {e}")

        if not self.providers:
            logger.warning(
                "No LLM providers configured. Please check your API keys in .env file"
            )

    async def optimize_prompt(
        self, request: PromptOptimizeRequest
    ) -> PromptOptimizeResponse:
        """优化prompt的主方法"""
        provider = request.llm_provider or settings.DEFAULT_LLM

        if provider not in self.providers:
            available = list(self.providers.keys())
            if not available:
                raise ValueError("没有配置任何LLM提供商，请在.env文件中配置API密钥")

            provider = available[0]
            logger.info(
                f"Requested provider '{request.llm_provider}' not available, using '{provider}'"
            )

        try:
            # 使用 asyncio 超时包装，确保不会无限等待
            return await asyncio.wait_for(
                self.providers[provider](request),
                timeout=settings.LLM_TIMEOUT + 10,  # 给额外10秒的缓冲时间
            )
        except asyncio.TimeoutError:
            logger.error(
                f"LLM optimization timed out after {settings.LLM_TIMEOUT}s with {provider}"
            )
            raise ValueError(
                f"LLM请求超时（{settings.LLM_TIMEOUT}秒），请稍后重试或使用其他提供商"
            )
        except Exception as e:
            logger.error(f"LLM optimization failed with {provider}: {e}")
            # 尝试备用提供商
            for backup_provider, handler in self.providers.items():
                if backup_provider != provider:
                    try:
                        logger.info(f"Trying backup provider: {backup_provider}")
                        return await asyncio.wait_for(
                            handler(request), timeout=settings.LLM_TIMEOUT + 10
                        )
                    except Exception as backup_error:
                        logger.error(
                            f"Backup provider {backup_provider} also failed: {backup_error}"
                        )

            raise ValueError(f"所有LLM提供商都失败了: {str(e)}")

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的Prompt工程师。请帮助用户优化他们的prompt，使其更加清晰、具体和有效。

要求：
1. 保持原意的基础上，让prompt更加清晰明确
2. 添加必要的上下文和约束条件
3. 使用结构化的格式
4. 提供3-5个具体的改进建议

请严格按照以下格式输出（使用中文）：

## 优化后的Prompt

[在这里提供优化后的完整prompt内容]

## 改进建议

1. [具体的改进建议1]
2. [具体的改进建议2]
3. [具体的改进建议3]
4. [具体的改进建议4]（可选）
5. [具体的改进建议5]（可选）

## 优化说明

[简要说明主要的优化点和改进理由]
"""

    async def _gemini_optimize(
        self, request: PromptOptimizeRequest
    ) -> PromptOptimizeResponse:
        """使用Gemini优化prompt"""
        try:
            model = genai.GenerativeModel(settings.GEMINI_MODEL)

            user_prompt = f"原始Prompt：\n{request.content}"
            if request.context:
                user_prompt += f"\n\n上下文信息：\n{request.context}"

            # Gemini 的 generate_content 方法不直接支持 timeout
            # 但我们在外层使用了 asyncio.wait_for 来控制超时
            generation_config = genai.types.GenerationConfig(
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_TOKENS,
            )

            response = await asyncio.to_thread(
                model.generate_content,
                f"{self._get_system_prompt()}\n\n{user_prompt}",
                generation_config=generation_config,
            )

            return self._parse_optimization_response(request.content, response.text)

        except Exception as e:
            logger.error(f"Gemini optimization error: {e}")
            raise ValueError(f"Gemini优化失败: {str(e)}")

    async def _qwen_optimize(
        self, request: PromptOptimizeRequest
    ) -> PromptOptimizeResponse:
        """使用Qwen（通义千问）优化prompt"""
        try:
            client = self.clients["qwen"]

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"原始Prompt：\n{request.content}"},
            ]

            if request.context:
                messages[1]["content"] += f"\n\n上下文信息：\n{request.context}"

            # 调用 Qwen API，超时已在客户端初始化时设置
            response = await client.chat.completions.create(
                model=settings.QWEN_MODEL,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                # 不需要单独设置timeout，已在客户端初始化时设置
            )

            return self._parse_optimization_response(
                request.content, response.choices[0].message.content
            )

        except Exception as e:
            logger.error(f"Qwen optimization error: {e}")
            raise ValueError(f"Qwen优化失败: {str(e)}")

    async def _deepseek_optimize(
        self, request: PromptOptimizeRequest
    ) -> PromptOptimizeResponse:
        """使用DeepSeek优化prompt"""
        try:
            client = self.clients["deepseek"]

            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": f"原始Prompt：\n{request.content}"},
            ]

            if request.context:
                messages[1]["content"] += f"\n\n上下文信息：\n{request.context}"

            # 调用 DeepSeek API，超时已在客户端初始化时设置
            response = await client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                # 不需要单独设置timeout，已在客户端初始化时设置
            )

            return self._parse_optimization_response(
                request.content, response.choices[0].message.content
            )

        except Exception as e:
            logger.error(f"DeepSeek optimization error: {e}")
            raise ValueError(f"DeepSeek优化失败: {str(e)}")

    def _parse_optimization_response(
        self, original: str, response_text: str
    ) -> PromptOptimizeResponse:
        """解析LLM响应，提取优化内容和建议"""
        try:
            # 默认值
            optimized = original
            suggestions = []

            # 尝试提取优化后的Prompt
            if "## 优化后的Prompt" in response_text:
                start = response_text.find("## 优化后的Prompt") + len(
                    "## 优化后的Prompt"
                )
                end = response_text.find("## 改进建议", start)
                if end == -1:
                    end = response_text.find("##", start + 1)
                if end != -1:
                    optimized = response_text[start:end].strip()
                else:
                    optimized = response_text[start:].strip()
            elif "优化后的Prompt：" in response_text:
                start = response_text.find("优化后的Prompt：") + len("优化后的Prompt：")
                end = response_text.find("改进建议", start)
                if end != -1:
                    optimized = response_text[start:end].strip()

            # 尝试提取改进建议
            if "## 改进建议" in response_text:
                start = response_text.find("## 改进建议") + len("## 改进建议")
                end = response_text.find("## 优化说明", start)
                if end == -1:
                    suggestion_text = response_text[start:].strip()
                else:
                    suggestion_text = response_text[start:end].strip()

                lines = suggestion_text.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-")):
                        suggestion = line.lstrip("0123456789.- ").strip()
                        if suggestion:
                            suggestions.append(suggestion)

            # 确保至少有一些建议
            if not suggestions:
                suggestions = [
                    "使用更具体的指令和要求",
                    "添加示例以提高理解准确性",
                    "明确输出格式和约束条件",
                ]

            return PromptOptimizeResponse(
                original=original, optimized=optimized, suggestions=suggestions[:5]
            )

        except Exception as e:
            logger.error(f"Failed to parse optimization response: {e}")
            return PromptOptimizeResponse(
                original=original,
                optimized=(
                    response_text[:1000] if len(response_text) > 1000 else response_text
                ),
                suggestions=["请查看上方的优化内容"],
            )

    def get_available_providers(self) -> List[str]:
        """获取所有可用的LLM提供商"""
        return list(self.providers.keys())

    async def test_provider(self, provider: str) -> bool:
        """测试指定的提供商是否可用"""
        if provider not in self.providers:
            return False

        try:
            test_request = PromptOptimizeRequest(
                content="测试连接", llm_provider=provider
            )
            await self.optimize_prompt(test_request)
            return True
        except Exception as e:
            logger.error(f"Provider {provider} test failed: {e}")
            return False


# 创建全局服务实例
llm_service = LLMService()
