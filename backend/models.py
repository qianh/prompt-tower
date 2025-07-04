from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class PromptBase(BaseModel):
    title: str = Field(..., description="Prompt标题，必须唯一")
    content: str = Field(..., description="Prompt内容")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    remark: Optional[str] = Field(None, description="备注说明")
    status: Optional[str] = Field(None, description="启用/禁用")
    creator_username: Optional[str] = Field(None, description="创建者用户名")
    usage_count: int = Field(default=0, description="使用次数")


class PromptCreate(PromptBase):
    pass


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    remark: Optional[str] = None
    status: Optional[str] = None
    usage_count: Optional[int] = None


class Prompt(PromptBase):
    created_at: datetime
    updated_at: datetime
    file_path: str

    class Config:
        from_attributes = True


class PromptOptimizeRequest(BaseModel):
    content: str = Field(..., description="需要优化的prompt内容")
    context: Optional[str] = Field(None, description="上下文信息")
    llm_provider: Optional[str] = Field("gemini", description="LLM提供商")


class PromptOptimizeResponse(BaseModel):
    original: str
    optimized: str
    suggestions: List[str]


class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    search_in: List[str] = Field(
        default=["title", "tags", "content"], description="搜索范围"
    )
    limit: int = Field(default=20, ge=1, le=100)


class SearchResponse(BaseModel):
    results: List[Prompt]
    total: int

    query: str


class UserBase(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="Username, must be unique"
    )


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="User password")


class UserInDB(UserBase):
    id: Optional[int] = None  # Will be set by the database or storage mechanism
    hashed_password: str

    class Config:
        from_attributes = True


class User(UserBase):
    id: int  # Or str if using UUIDs
    # email: Optional[str] = None # Add other fields as needed

    class Config:
        from_attributes = True


# Token models for JWT
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Tag models
class TagBase(BaseModel):
    name: str = Field(..., description="Tag name")


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    class Config:
        from_attributes = True
