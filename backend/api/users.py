from typing import List

from fastapi import APIRouter, HTTPException, status
from backend.services.user_service import get_all_users
from backend.services.prompt_service import get_prompt_by_username_count

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[dict])
async def list_users():
    """获取所有用户列表及其提示词数量"""
    try:
        users_data = await get_all_users()
        users_list = []
        
        for user in users_data:
            # 获取该用户的提示词数量
            prompt_count = await get_prompt_by_username_count(user.username)
            users_list.append({
                "id": user.id,
                "username": user.username,
                "prompt_count": prompt_count
            })
        
        return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/{username}/", response_model=dict)
async def get_user_details(username: str):
    """获取特定用户详情及其提示词数量"""
    try:
        users = await get_all_users()
        user_found = None
        for u in users:
            if u.username == username:
                user_found = u
                break
        
        if not user_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        prompt_count = await get_prompt_by_username_count(username)
        
        return {
            "id": user_found.id,
            "username": user_found.username,
            "prompt_count": prompt_count
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user details: {str(e)}"
        )


@router.get("/test")
async def test_endpoint():
    """测试端点"""
    return {"message": "Users API is working"}
