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
        # Use await with aiofiles for async file operations if we switch to aiofiles
        # For now, keeping synchronous file read for simplicity within this locked section
        with open(TAGS_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                tags_list = json.load(f)
                return set(tags_list)
            except json.JSONDecodeError:
                return set()


async def _save_tags_to_file(tags_set: Set[str]) -> None:
    """Saves the set of tags to the JSON file as a sorted list."""
    async with _file_lock:
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
    Returns the added tag name (as provided) or the existing one.
    Raises ValueError if the tag name is empty.
    """
    stripped_tag = tag_name.strip()
    if not stripped_tag:
        raise ValueError("Tag name cannot be empty.")

    current_tags_set = await _load_tags_from_file()
    
    # Case-insensitive check for existence
    for existing_tag in current_tags_set:
        if existing_tag.lower() == stripped_tag.lower():
            return existing_tag # Return existing tag (with its original casing)

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
    # Import PromptService here to avoid circular import issues at module level
    from backend.services.prompt_service import PromptService
    
    prompt_service = PromptService()
    try:
        tags_from_yaml = await prompt_service.get_all_tags_from_yaml_files()
    except Exception as e:
        print(f"Error fetching tags from YAML files during sync: {e}")
        return await get_all_tags() # Return current global tags if YAML scan fails

    if not tags_from_yaml:
        print("No tags found in YAML files to sync.")
        return await get_all_tags()

    current_global_tags_set = await _load_tags_from_file()
    updated_set = current_global_tags_set.copy()
    newly_added_count = 0

    for tag_from_prompt in tags_from_yaml:
        # add_tag function already handles case-insensitivity and adds if new
        # We can call it directly, or replicate its logic for slightly more control here
        original_tag_to_add = tag_from_prompt # Keep original casing from YAML
        tag_exists = False
        for existing_global_tag in updated_set:
            if existing_global_tag.lower() == original_tag_to_add.lower():
                tag_exists = True
                break
        if not tag_exists:
            updated_set.add(original_tag_to_add)
            newly_added_count += 1
            
    if newly_added_count > 0:
        await _save_tags_to_file(updated_set)
        print(f"Synced {newly_added_count} new tag(s) to tags.json from prompt YAML files.")
    else:
        print("No new tags from prompt YAML files to sync to tags.json; all existing YAML tags are already present.")

    return sorted(list(updated_set), key=str.lower)
