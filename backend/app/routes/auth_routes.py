from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.jwt_handler import create_access_token
from app.schemas.user_schema import UserCreate, UserLogin
from app.models.user import User
from app.utils.auth_dependency import get_current_user
from app.db.database import SessionLocal
from app.utils.auth_dependency import get_current_user
from app.schemas.review_schema import CodeReviewRequest
from app.utils.ai_reviewer import (
    review_code,
    get_repo_info,
    collect_code_files
)
from fastapi import Depends
import json
from app.models.review import Review
from app.utils.security import (
    hash_password,
    verify_password
)

router = APIRouter()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Signup Route
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_pw = hash_password(user.password)

    new_user = User(
        email=user.email,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully"
    }

# Login Route


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/profile")
def profile(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }

@router.post("/review")
def review(
    request: CodeReviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = review_code(
        request.code,
        request.language
    )

    new_review = Review(
        code=request.code,
        review=json.dumps(result["review"]),
        user_id=current_user.id
    )

    db.add(new_review)

    db.commit()

    return result

@router.get("/my-reviews")
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id
    ).all()

    formatted_reviews = []

    for review in reviews:
        formatted_reviews.append({
            "id": review.id,
            "code": review.code,

            # convert string back into dict
            "review": json.loads(review.review)
        })

    return formatted_reviews

@router.delete("/review/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted"
    }

@router.post("/github-review")
def github_review(data: dict):

    owner, repo = get_repo_info(
        data["repo_url"]
    )

    files = collect_code_files(
        owner,
        repo
    )

    return {
        "files_found": len(files),
        "files": files
    }