from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from backend.models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    SearchRequest,
    SearchResponse,
    User, # Added for type hinting current_user
)
from backend.services.file_service import FileService
from backend.api.auth import get_current_user # Import the dependency

router = APIRouter(prefix="/prompts", tags=["prompts"])
file_service = FileService()


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
        prompts = [p for p in prompts if tag in p.tags]

    return prompts


@router.get("/{title}", response_model=Prompt)
async def get_prompt(title: str):
    """获取单个prompt"""
    prompt = await file_service.read_prompt(title)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt不存在")
    return prompt


@router.post("/", response_model=Prompt)
async def create_prompt(prompt: PromptCreate, current_user: User = Depends(get_current_user)):
    """创建新prompt"""
    # 检查标题是否已存在
    existing = await file_service.read_prompt(prompt.title)
    if existing:
        raise HTTPException(status_code=400, detail="标题已存在")

    return await file_service.save_prompt(prompt.model_dump())


@router.put("/{title}", response_model=Prompt)
async def update_prompt(title: str, update_data: PromptUpdate, current_user: User = Depends(get_current_user)):
    """更新prompt"""
    updated = await file_service.update_prompt(
        title, update_data.model_dump(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Prompt不存在")
    return updated


@router.delete("/{title}")
async def delete_prompt(title: str, current_user: User = Depends(get_current_user)):
    """删除prompt"""
    success = await file_service.delete_prompt(title)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt不存在")
    return {"message": "删除成功"}


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
    prompt = await file_service.read_prompt(title)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt不存在")

    new_status = "disabled" if prompt.status == "enabled" else "enabled"
    updated = await file_service.update_prompt(title, {"status": new_status})
    return updated
