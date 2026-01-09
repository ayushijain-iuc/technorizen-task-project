from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from database import get_db
from models import User, Profile
from schemas import ProfileCreate, ProfileUpdate, ProfileResponse
from auth import get_current_user
from config import settings
from PIL import Image

router = APIRouter(prefix="/api/profile", tags=["Profile"])


def save_profile_photo(file: UploadFile, user_id: int) -> str:
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    allowed_exts = settings.allowed_extensions_list
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_exts)}"
        )
    

    filename = f"profile_{user_id}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        img = Image.open(filepath)
        img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        img.save(filepath)
    except Exception:
        pass  
    return filename


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    phone_no: Optional[str] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use update endpoint instead."
        )
    
    photo_filename = None
    if profile_photo:
        photo_filename = save_profile_photo(profile_photo, current_user.id)
    
    new_profile = Profile(
        user_id=current_user.id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        phone_no=phone_no,
        profile_photo=photo_filename
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile


@router.put("", response_model=ProfileResponse)
async def update_profile(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    phone_no: Optional[str] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    if first_name is not None:
        profile.first_name = first_name
    if last_name is not None:
        profile.last_name = last_name
    if age is not None:
        profile.age = age
    if phone_no is not None:
        profile.phone_no = phone_no
    

    if profile_photo:
        if profile.profile_photo:
            old_photo_path = os.path.join(settings.UPLOAD_DIR, profile.profile_photo)
            if os.path.exists(old_photo_path):
                os.remove(old_photo_path)
        
        profile.profile_photo = save_profile_photo(profile_photo, current_user.id)
    
    db.commit()
    db.refresh(profile)
    return profile


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    

    if profile.profile_photo:
        photo_path = os.path.join(settings.UPLOAD_DIR, profile.profile_photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.delete(profile)
    db.commit()
    
    return None

