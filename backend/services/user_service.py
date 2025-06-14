import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from backend.models import UserCreate, UserInDB
from backend.utils.security import get_password_hash

DATA_DIR = Path(__file__).parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# In-memory cache of users to reduce file I/O, and an ID counter
_users_cache: Dict[str, UserInDB] = {}
_current_id_counter: int = 0


def _load_users_from_file() -> None:
    global _users_cache, _current_id_counter
    if not USERS_FILE.exists():
        _users_cache = {}
        _current_id_counter = 0
        _save_users_to_file()  # Create the file with an empty list/dict
        return

    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            loaded_users = data.get("users", [])
            _current_id_counter = data.get("next_id", 0)
            _users_cache = {u["username"]: UserInDB(**u) for u in loaded_users}
    except (json.JSONDecodeError, FileNotFoundError):
        _users_cache = {}
        _current_id_counter = 0
        # If file is corrupted or not found, try to save a new empty one
        _save_users_to_file()


def _save_users_to_file() -> None:
    try:
        # Convert UserInDB objects to dictionaries for JSON serialization
        serializable_users = [user.model_dump() for user in _users_cache.values()]
        with open(USERS_FILE, "w") as f:
            json.dump(
                {"users": serializable_users, "next_id": _current_id_counter},
                f,
                indent=4,
            )
    except IOError as e:
        # Handle file writing errors (e.g., log them)
        print(f"Error saving users file: {e}")


# Load users when the module is imported
_load_users_from_file()


async def get_user_by_username(username: str) -> Optional[UserInDB]:
    return _users_cache.get(username)


async def create_user_in_db(user_data: UserCreate) -> Optional[UserInDB]:
    global _current_id_counter
    if await get_user_by_username(user_data.username):
        return None  # User already exists

    hashed_password = get_password_hash(user_data.password)
    _current_id_counter += 1
    new_user = UserInDB(
        id=_current_id_counter,
        username=user_data.username,
        hashed_password=hashed_password,
    )
    _users_cache[new_user.username] = new_user
    _save_users_to_file()
    return new_user


async def get_all_users() -> List[UserInDB]:  # Mainly for debugging/admin
    return list(_users_cache.values())
