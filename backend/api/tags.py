from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend import models, services
from backend.api.auth import get_current_user

router = APIRouter()


@router.get("/tags", response_model=List[str], summary="Get all global tags")
async def read_tags(
    _current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve a list of all globally defined unique tags, sorted alphabetically.
    Returns a direct list of tag name strings.
    """
    try:
        tags_list = await services.tag_service.get_all_tags()
        return tags_list # Directly return List[str]
    except Exception as e:
        # Log error if logger is available
        print(f"Error in read_tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tags",
        )


@router.post(
    "/tags",
    response_model=List[str], # Changed to return the full list of tags
    status_code=status.HTTP_201_CREATED,
    summary="Add a new global tag",
)
async def create_tag(
    tag_create: models.TagCreate,
    _current_user: models.User = Depends(get_current_user),
):
    """
    Add a new tag to the global list.

    - **name**: The name of the tag to create.
    If the tag (case-insensitive) already exists, no new tag is added.
    If the tag name is empty or whitespace only, a 422 error will be raised.
    Returns the complete updated list of global tags.
    """
    try:
        await services.tag_service.add_tag(tag_create.name)
        # After adding, fetch and return the complete list of tags
        updated_tags_list = await services.tag_service.get_all_tags()
        return updated_tags_list
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        # Catch any other unexpected errors from the service layer
        print(f"Error in create_tag: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while creating tag: {str(e)}",
        )
