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
        if not self.prompt_dir.exists(): # Ensure directory exists
            return []
        for file_path in self.prompt_dir.glob("*.yaml"):
            try:
                prompt = await self.read_prompt(file_path.stem)
                if prompt:
                    prompts.append(prompt)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        return prompts

    async def read_prompt(self, title_stem: str) -> Optional[Prompt]: # title_stem is filename without .yaml
        """读取单个prompt"""
        file_path = self.prompt_dir / f"{title_stem}.yaml"
        if not file_path.exists():
            return None

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content_yaml = await f.read()

        data = yaml.safe_load(content_yaml)
        if not isinstance(data, dict):
            print(f"Warning: Could not parse YAML as dictionary from {file_path}. Content: '{content_yaml[:100]}'...")
            return None 

        stat = file_path.stat()

        return Prompt(
            title=data.get("title", title_stem), # Fallback to filename stem if title not in YAML
            content=data.get("content", ""),
            tags=[str(t) for t in data.get("tags", []) if isinstance(t, (str, int, float)) and str(t).strip()], # Ensure tags are strings and not empty
            remark=data.get("remark", ""),
            status=data.get("status", "enabled"),
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime),
            file_path=str(file_path),
            creator_username=data.get("creator_username"),
        )

    async def save_prompt(self, prompt_data: Dict[str, Any]) -> Prompt:
        """保存prompt"""
        title_for_filename = str(prompt_data["title"]).strip()
        if not title_for_filename:
            raise ValueError("Prompt title cannot be empty for filename.")
            
        file_path = self.prompt_dir / f"{title_for_filename}.yaml"

        yaml_data = {
            "title": title_for_filename, # Ensure title in content matches filename intent
            "content": prompt_data.get("content", ""),
            "tags": [str(t).strip() for t in prompt_data.get("tags", []) if str(t).strip()], # Clean and ensure string tags
            "remark": prompt_data.get("remark", ""),
            "status": prompt_data.get("status", "enabled"),
            "creator_username": prompt_data.get("creator_username"),
        }

        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(
                yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
            )
        
        saved_prompt_obj = await self.read_prompt(title_for_filename)
        if not saved_prompt_obj:
            raise IOError(f"Failed to read back prompt '{title_for_filename}' after saving to {file_path}.")
        return saved_prompt_obj

    async def delete_prompt(self, title_stem: str) -> bool:
        """删除prompt by filename stem"""
        file_path = self.prompt_dir / f"{title_stem}.yaml"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    async def update_prompt(
        self, original_title_identifier: str, update_data: Dict[str, Any]
    ) -> Optional[Prompt]:
        """更新prompt. original_title_identifier is the current unique ID (likely filename stem or current YAML title)."""
        
        existing_prompt_model = await self.read_prompt(original_title_identifier)
        if not existing_prompt_model:
             # If not found by stem, perhaps original_title_identifier was the YAML title and it differed from stem
             # This part can be complex if filename stems and YAML titles are not kept in sync by convention.
             # For now, we assume original_title_identifier is how we find the file.
            return None 

        current_yaml_title = existing_prompt_model.title 

        data_to_save = existing_prompt_model.model_dump()
        data_to_save.update(update_data)

        new_yaml_title = str(data_to_save.get("title", current_yaml_title)).strip()
        if not new_yaml_title:
            raise ValueError("Prompt title cannot be empty.")
        data_to_save['title'] = new_yaml_title
        data_to_save['tags'] = [str(t).strip() for t in data_to_save.get("tags", []) if str(t).strip()] # Clean tags for saving

        # File handling: Filename is based on the NEW YAML title.
        new_file_path = self.prompt_dir / f"{new_yaml_title}.yaml"
        original_file_path = self.prompt_dir / f"{original_title_identifier}.yaml" # Path based on how it was identified
        
        # If the new YAML title implies a new filename, and this new filename is different from the original file's path
        if new_yaml_title != original_title_identifier and original_file_path != new_file_path:
            if new_file_path.exists():
                raise ValueError(f"New title '{new_yaml_title}' conflicts with an existing prompt file: {new_file_path}")
            if original_file_path.exists():
                original_file_path.rename(new_file_path)
            else:
                # This case means the file identified by original_title_identifier was not found to be renamed.
                # This could happen if original_title_identifier was a YAML title that didn't match its filename stem.
                # For robustness, one might try to find the file by current_yaml_title if different and original_file_path failed.
                # However, this adds complexity. Assuming original_title_identifier IS the key to find the file.
                print(f"Warning: Original file {original_file_path} not found for renaming. Saving as new file {new_file_path}.")
        
        # Save the prompt. save_prompt will use data_to_save['title'] (new_yaml_title) for the filename.
        # If renamed, it writes to new_file_path. If not renamed, it overwrites original_file_path (or the one matching new_yaml_title if original_identifier was different).
        return await self.save_prompt(data_to_save)

    async def search_prompts(self, query: str, search_in: List[str]) -> List[Prompt]:
        """搜索prompts，根据关键词在指定字段中查找，并按匹配优先级排序。"""
        print(f"[SEARCH_PROMPTS] Received query: '{query}', search_in: {search_in}")

        all_prompts = await self.list_prompts()
        if not all_prompts:
            print("[SEARCH_PROMPTS] No prompts found to search.")
            return []
        
        print(f"[SEARCH_PROMPTS] Loaded {len(all_prompts)} prompts for searching. Titles: {[p.title for p in all_prompts]}")

        results = []
        query_cleaned = query.strip().lower()

        if not query_cleaned:
            print("[SEARCH_PROMPTS] Cleaned query is empty, returning no results.")
            return []
        
        print(f"[SEARCH_PROMPTS] Cleaned query: '{query_cleaned}'")

        for prompt in all_prompts:
            if not prompt:
                print("[SEARCH_PROMPTS] Encountered a None prompt object, skipping.")
                continue
            
            print(f"[SEARCH_PROMPTS] Evaluating prompt: '{prompt.title}'")
                
            score = 0
            prompt_title_lower = str(prompt.title).lower() if prompt.title else ""
            prompt_content_lower = str(prompt.content).lower() if prompt.content else ""
            prompt_tags_lower = [str(t).lower() for t in prompt.tags if isinstance(t, str) and t.strip()] if prompt.tags else []

            matched_in_title = "title" in search_in and query_cleaned in prompt_title_lower
            matched_in_tags = False
            if "tags" in search_in and prompt_tags_lower:
                for tag_lower in prompt_tags_lower:
                    if query_cleaned in tag_lower:
                        matched_in_tags = True
                        break
            
            matched_in_content = "content" in search_in and query_cleaned in prompt_content_lower

            if matched_in_title:
                score = 100
            elif matched_in_tags:
                score = 50
            elif matched_in_content:
                score = 10
            
            print(f"  - Calculated score for '{prompt.title}': {score}")

            if score > 0:
                results.append((score, prompt))

        print(f"[SEARCH_PROMPTS] Unsorted results (score, title): {[(s, p.title) for s, p in results]}")
        results.sort(key=lambda x: x[0], reverse=True)
        
        final_result_prompts = [p for _, p in results]
        print(f"[SEARCH_PROMPTS] Sorted results returned (titles): {[p.title for p in final_result_prompts]}")
        return final_result_prompts
