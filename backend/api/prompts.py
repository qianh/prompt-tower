from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.auth import get_current_user  # Import the dependency
from backend.models import User  # Added for type hinting current_user
from backend.models import (Prompt, PromptCreate, PromptUpdate, SearchRequest,
                            SearchResponse)
from backend.services.file_service import FileService
from backend.services.prompt_service import \
    PromptService  # Import PromptService

router = APIRouter(prefix="/prompts", tags=["prompts"])
file_service = (
    FileService()
)  # Keep for read-only operations like list and get_prompt if not moved to service
prompt_service = PromptService()  # Instantiate PromptService


@router.get("/", response_model=List[Prompt])
async def list_prompts(
    status: Optional[str] = Query(None, description="过滤状态"),
    tag: Optional[str] = Query(None, description="过滤标签"),
):
    """获取所有prompts"""
    prompts = await file_service.list_prompts()

    # 应用过滤
    if status:
        prompts = [p for p in prompts if p.status == status]
    if tag:
        prompts = [p for p in prompts if p.tags and tag in p.tags] # Added check for p.tags existence

    return prompts


@router.get("/tags/", response_model=List[str])
async def get_all_tags():
    """获取所有不重复的tags"""
    try:
        tags = await prompt_service.get_all_tags()
        return tags
    except Exception as e:
        # Log the exception e if a logger is available
        raise HTTPException(status_code=500, detail="获取标签失败")


@router.get("/{title}", response_model=Prompt)
async def get_prompt(title: str):
    """获取单个prompt"""
    prompt = await file_service.read_prompt(title)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt不存在")
    return prompt


@router.post("/", response_model=Prompt)
async def create_prompt(
    prompt: PromptCreate, current_user: User = Depends(get_current_user)
):
    """创建新prompt"""
    try:
        return await prompt_service.create_prompt(
            prompt_data=prompt, creator_username=current_user.username
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{title}", response_model=Prompt)
async def update_prompt(
    title: str,
    update_data: PromptUpdate,
    current_user: User = Depends(get_current_user),
):
    """更新prompt"""
    try:
        updated_prompt = await prompt_service.update_prompt(
            title=title, update_data=update_data, current_username=current_user.username
        )
        if (
            not updated_prompt
        ):  # Should be handled by service raising 404, but as a safeguard
            raise HTTPException(status_code=404, detail="Prompt不存在")
        return updated_prompt
    except ValueError as e:  # For validation errors from service
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{title}")
async def delete_prompt(title: str, current_user: User = Depends(get_current_user)):
    """删除prompt"""
    try:
        success = await prompt_service.delete_prompt(
            title=title, current_username=current_user.username
        )
        if not success:  # Should be handled by service raising 404, but as a safeguard
            raise HTTPException(status_code=404, detail="Prompt不存在或删除失败")
        return {"message": "删除成功"}
    except ValueError as e:  # Should not happen if service raises HTTPExceptions
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_prompts(request: SearchRequest):
    """搜索prompts"""
    results = await file_service.search_prompts(request.query, request.search_in)
    return SearchResponse(
        results=results[: request.limit], total=len(results), query=request.query
    )


@router.post("/{title}/toggle-status", response_model=Prompt)
async def toggle_status(title: str, current_user: User = Depends(get_current_user)):
    """切换prompt状态"""
    try:
        updated_prompt = await prompt_service.toggle_prompt_status(
            title=title, current_username=current_user.username
        )
        if not updated_prompt:  # Should be handled by service raising 404
            raise HTTPException(status_code=404, detail="Prompt不存在")
        return updated_prompt
    except ValueError as e:  # Should not happen
        raise HTTPException(status_code=400, detail=str(e))
