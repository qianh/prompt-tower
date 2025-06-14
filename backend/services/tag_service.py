import asyncio
import json
from pathlib import Path
from typing import List, Set

# Path to the tags.json file
TAGS_FILE_PATH = Path(__file__).parent.parent / "data" / "tags.json"

# Ensure the data directory and tags.json file exist
DATA_DIR = TAGS_FILE_PATH.parent
DATA_DIR.mkdir(exist_ok=True)
if not TAGS_FILE_PATH.exists():
    with open(TAGS_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Lock for file operations
_file_lock = asyncio.Lock()


async def _load_tags_from_file() -> Set[str]:
    """Loads the set of tags from the JSON file."""
    async with _file_lock:
        if not TAGS_FILE_PATH.exists() or TAGS_FILE_PATH.stat().st_size == 0:
            return set()
        with open(TAGS_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                tags_list = json.load(f)
                return set(tags_list)
            except json.JSONDecodeError:
                # Handle cases where the file might be corrupted or empty
                return set()


async def _save_tags_to_file(tags_set: Set[str]) -> None:
    """Saves the set of tags to the JSON file as a sorted list."""
    async with _file_lock:
        # Sort for consistent order in the file
        sorted_tags_list = sorted(list(tags_set), key=str.lower)
        with open(TAGS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted_tags_list, f, ensure_ascii=False, indent=2)


async def get_all_tags() -> List[str]:
    """Returns a sorted list of all unique global tags."""
    tags_set = await _load_tags_from_file()
    return sorted(list(tags_set), key=str.lower)


async def add_tag(tag_name: str) -> str:
    """
    Adds a new tag to the global list if it doesn't already exist
    (case-insensitive check).
    Returns the added tag name (as provided).
    Raises ValueError if the tag name is empty.
    """
    stripped_tag = tag_name.strip()
    if not stripped_tag:
        raise ValueError("Tag name cannot be empty.")

    current_tags_set = await _load_tags_from_file()

    # Case-insensitive check for existence
    if any(
        existing_tag.lower() == stripped_tag.lower()
        for existing_tag in current_tags_set
    ):
        # Return the existing tag that matches (could be different case)
        for existing_tag in current_tags_set:
            if existing_tag.lower() == stripped_tag.lower():
                return existing_tag
        return stripped_tag  # Should not be reached if logic is correct

    current_tags_set.add(stripped_tag)  # Add with original casing
    await _save_tags_to_file(current_tags_set)
    return stripped_tag


async def sync_tags_from_prompts() -> List[str]:
    """
    Scans all prompt files, extracts their tags, and adds any new unique tags
    to the global tags.json file.
    This is useful for initializing tags.json or ensuring it's up-to-date
    with tags already defined in prompt files.
    Returns the updated list of all global tags.
    """
    from backend.services.prompt_service import \
        get_all_prompts_brief  # To avoid circular import

    all_prompts = await get_all_prompts_brief()
    tags_from_prompts: Set[str] = set()
    for prompt_data in all_prompts:
        if prompt_data.get("tags") and isinstance(prompt_data["tags"], list):
            for tag in prompt_data["tags"]:
                if isinstance(tag, str) and tag.strip():
                    tags_from_prompts.add(tag.strip())

    if not tags_from_prompts:
        return await get_all_tags()

    current_global_tags_set = await _load_tags_from_file()
    updated_set = current_global_tags_set.copy()
    newly_added_count = 0

    for tag_from_prompt in tags_from_prompts:
        # Add if not already present (case-insensitive check)
        if not any(
            existing_tag.lower() == tag_from_prompt.lower()
            for existing_tag in updated_set
        ):
            updated_set.add(tag_from_prompt)  # Add with casing from prompt
            newly_added_count += 1

    if newly_added_count > 0:
        await _save_tags_to_file(updated_set)
        print(f"Synced {newly_added_count} tags to tags.json from prompts.")
    else:
        print("No new tags from prompts to sync to tags.json.")

    return sorted(list(updated_set), key=str.lower)
