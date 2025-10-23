"""
Media upload API endpoints for images, videos, and audio files
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from PIL import Image
from models.opinion import OpinionMedia, MediaType
from utils.security import get_current_user
from models.user import User

router = APIRouter(prefix="/media", tags=["media"])

# Media upload configuration
UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB for images

# Create upload directories
(UPLOAD_DIR / "images").mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / "videos").mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / "audio").mkdir(parents=True, exist_ok=True)
(UPLOAD_DIR / "thumbnails").mkdir(parents=True, exist_ok=True)


def get_media_type(filename: str) -> MediaType:
    """Determine media type from file extension"""
    ext = Path(filename).suffix.lower()

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return MediaType.IMAGE
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        return MediaType.VIDEO
    elif ext in ALLOWED_AUDIO_EXTENSIONS:
        return MediaType.AUDIO
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}"
        )


def validate_file_size(file_size: int, media_type: MediaType):
    """Validate file size based on media type"""
    if media_type == MediaType.IMAGE and file_size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    elif file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )


def compress_image(image_path: Path, max_size: tuple = (1920, 1080), quality: int = 85):
    """Compress and resize image"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Resize if larger than max_size
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save with compression
            img.save(image_path, "JPEG", quality=quality, optimize=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")


def create_thumbnail(image_path: Path, thumbnail_path: Path, size: tuple = (300, 300)):
    """Create thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, "JPEG", quality=80, optimize=True)
    except Exception as e:
        print(f"Thumbnail creation failed: {str(e)}")


@router.post("/upload", status_code=201)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload media file (image, video, or audio)

    - **file**: Media file to upload
    - Returns: File information including URL and media type
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Determine media type
    media_type = get_media_type(file.filename)

    # Validate file size (read first chunk to check)
    file_content = await file.read()
    file_size = len(file_content)
    validate_file_size(file_size, media_type)

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    # Determine save directory based on media type
    if media_type == MediaType.IMAGE:
        save_dir = UPLOAD_DIR / "images"
    elif media_type == MediaType.VIDEO:
        save_dir = UPLOAD_DIR / "videos"
    else:
        save_dir = UPLOAD_DIR / "audio"

    file_path = save_dir / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # Process image (compress and create thumbnail)
        if media_type == MediaType.IMAGE:
            compress_image(file_path)
            thumbnail_path = UPLOAD_DIR / "thumbnails" / unique_filename
            create_thumbnail(file_path, thumbnail_path)

        # Get final file size after compression
        final_size = file_path.stat().st_size

        return {
            "filename": unique_filename,
            "media_type": media_type,
            "file_path": str(file_path.relative_to(UPLOAD_DIR)),
            "file_size": final_size,
            "mime_type": file.content_type,
            "url": f"/media/files/{media_type.value}/{unique_filename}",
            "thumbnail_url": f"/media/thumbnails/{unique_filename}" if media_type == MediaType.IMAGE else None
        }

    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@router.post("/upload-multiple", status_code=201)
async def upload_multiple_media(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple media files at once

    - **files**: List of media files to upload (max 10 files)
    - Returns: List of uploaded file information
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")

    results = []
    for file in files:
        try:
            result = await upload_media(file, current_user)
            results.append(result)
        except HTTPException as e:
            results.append({
                "filename": file.filename,
                "error": e.detail,
                "status": "failed"
            })

    return {
        "uploaded": len([r for r in results if "error" not in r]),
        "failed": len([r for r in results if "error" in r]),
        "files": results
    }


@router.get("/files/{media_type}/{filename}")
async def get_media_file(media_type: str, filename: str):
    """
    Get media file by type and filename

    - **media_type**: Type of media (image, video, audio)
    - **filename**: Name of the file
    """
    file_path = UPLOAD_DIR / media_type / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    """
    Get thumbnail for an image

    - **filename**: Name of the image file
    """
    thumbnail_path = UPLOAD_DIR / "thumbnails" / filename

    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(thumbnail_path)


@router.delete("/files/{media_type}/{filename}", status_code=200)
async def delete_media_file(
    media_type: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete media file (admin/moderator only)

    - **media_type**: Type of media (image, video, audio)
    - **filename**: Name of the file to delete
    """
    # Check if user has permission (admin or moderator)
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete files")

    file_path = UPLOAD_DIR / media_type / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Delete main file
        file_path.unlink()

        # Delete thumbnail if it's an image
        if media_type == "images":
            thumbnail_path = UPLOAD_DIR / "thumbnails" / filename
            if thumbnail_path.exists():
                thumbnail_path.unlink()

        return {"message": "File deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")
