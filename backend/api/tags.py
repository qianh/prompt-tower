from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from backend import models, services
from backend.api.auth import get_current_user

router = APIRouter()


@router.get("/tags", response_model=List[models.Tag], summary="Get all global tags")
async def read_tags(
    _current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve a list of all globally defined unique tags, sorted alphabetically.
    """
    tags_list = await services.tag_service.get_all_tags()
    return [models.Tag(name=tag_name) for tag_name in tags_list]


@router.post(
    "/tags",
    response_model=models.Tag,
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
    If the tag (case-insensitive) already exists, the existing tag
    (with its original casing) will be returned.
    If the tag name is empty or whitespace only, a 422 error will be raised.
    """
    try:
        added_tag_name = await services.tag_service.add_tag(tag_create.name)
        return models.Tag(name=added_tag_name)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
    except Exception as e:
        # Catch any other unexpected errors from the service layer
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
