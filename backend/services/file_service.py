from datetime import datetime
from typing import Any, Dict, List, Optional

import aiofiles
import yaml

from backend.config import settings
from backend.models import Prompt


class FileService:
    def __init__(self):
        self.prompt_dir = settings.PROMPT_TEMPLATE_DIR

    async def list_prompts(self) -> List[Prompt]:
        """列出所有prompt"""
        prompts = []
        for file_path in self.prompt_dir.glob("*.yaml"):
            try:
                prompt = await self.read_prompt(file_path.stem)
                if prompt:
                    prompts.append(prompt)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        return prompts

    async def read_prompt(self, title: str) -> Optional[Prompt]:
        """读取单个prompt"""
        file_path = self.prompt_dir / f"{title}.yaml"
        if not file_path.exists():
            return None

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()

        data = yaml.safe_load(content)

        # 获取文件修改时间
        stat = file_path.stat()

        return Prompt(
            title=data.get("title", title),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            remark=data.get("remark", ""),
            status=data.get("status", "enabled"),
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
            file_path=str(file_path),
            creator_username=data.get("creator_username"),
        )

    async def save_prompt(self, prompt_data: Dict[str, Any]) -> Prompt:
        """保存prompt"""
        title = prompt_data["title"]
        file_path = self.prompt_dir / f"{title}.yaml"

        # 准备YAML数据
        yaml_data = {
            "title": title,
            "content": prompt_data["content"],
            "tags": prompt_data.get("tags", []),
            "remark": prompt_data.get("remark", ""),
            "status": prompt_data.get("status", "enabled"),
            "creator_username": prompt_data.get(
                "creator_username"
            ),  # Add creator_username
        }

        # 保存到文件
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(
                yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
            )

        # 返回保存的prompt
        return await self.read_prompt(title)

    async def delete_prompt(self, title: str) -> bool:
        """删除prompt"""
        file_path = self.prompt_dir / f"{title}.yaml"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def update_prompt(
        self, title: str, update_data: Dict[str, Any]
    ) -> Optional[Prompt]:
        """更新prompt"""
        # 读取现有数据
        existing = await self.read_prompt(title)
        if not existing:
            return None

        # 更新数据
        prompt_dict = existing.model_dump()

        # 如果标题改变，需要重命名文件
        new_title = update_data.get("title", title)
        if new_title != title:
            old_path = self.prompt_dir / f"{title}.yaml"
            new_path = self.prompt_dir / f"{new_title}.yaml"
            if new_path.exists():
                raise ValueError(f"标题 '{new_title}' 已存在")
            old_path.rename(new_path)

        # 更新字段
        for key, value in update_data.items():
            if value is not None and key in prompt_dict:
                prompt_dict[key] = value

        # 保存更新
        return await self.save_prompt(prompt_dict)

    async def search_prompts(self, query: str, search_in: List[str]) -> List[Prompt]:
        """搜索prompts"""
        all_prompts = await self.list_prompts()
        results = []
        query_lower = query.lower()

        for prompt in all_prompts:
            score = 0

            # 按优先级搜索
            if "title" in search_in and query_lower in prompt.title.lower():
                score = 100
            elif "tags" in search_in:
                for tag in prompt.tags:
                    if query_lower in tag.lower():
                        score = max(score, 50)
                        break
            elif "content" in search_in and query_lower in prompt.content.lower():
                score = max(score, 10)

            if score > 0:
                results.append((score, prompt))

        # 按分数排序
        results.sort(key=lambda x: x[0], reverse=True)
        return [prompt for _, prompt in results]
