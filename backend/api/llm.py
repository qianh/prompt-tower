from typing import List

from fastapi import APIRouter, HTTPException

from backend.config import settings  # 添加这行导入
from backend.models import PromptOptimizeRequest, PromptOptimizeResponse
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/optimize", response_model=PromptOptimizeResponse)
async def optimize_prompt(request: PromptOptimizeRequest):
    """使用LLM优化prompt"""
    try:
        return await llm_service.optimize_prompt(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")


@router.get("/providers")
async def get_providers():
    """获取可用的LLM提供商"""
    providers = llm_service.get_available_providers()
    return {
        "providers": providers,
        "default": (
            settings.DEFAULT_LLM
            if settings.DEFAULT_LLM in providers
            else providers[0] if providers else None
        ),
    }


@router.get("/providers/{provider}/test")
async def test_provider(provider: str):
    """测试指定的LLM提供商是否可用"""
    is_available = await llm_service.test_provider(provider)
    return {
        "provider": provider,
        "available": is_available,
        "message": "连接成功" if is_available else "连接失败",
    }


@router.get("/config")
async def get_llm_config():
    """获取LLM配置信息"""
    return {
        "default_provider": settings.DEFAULT_LLM,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "timeout": settings.LLM_TIMEOUT,
        "models": {
            "gemini": settings.GEMINI_MODEL,
            "qwen": settings.QWEN_MODEL,
            "deepseek": settings.DEEPSEEK_MODEL,
        },
    }
