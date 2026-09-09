# Project: P04_fastapi_login
# Layer: Controller (HTTP / Routes)
# Source: examples/full-example/app/routes/posts.py

from typing import List

from app.db import get_session
from app.db.actions import create_post, get_user_by_name
from app.exceptions import InvalidUserName
from app.models.posts import PostCreate, PostResponse
from app.security import manager
from fastapi import APIRouter
from fastapi.param_functions import Depends

router = APIRouter(prefix="/posts")


@router.post("/create", response_model=PostResponse)
def create(
    post: PostCreate, user=Depends(manager), db=Depends(get_session)
) -> PostResponse:
    post = create_post(post.text, user, db)
    return PostResponse.from_orm(post)