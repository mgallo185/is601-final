from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
import os
from uuid import UUID
from settings.config import settings
from PIL import Image
import io

# Initialize Minio client
try:
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )
    
    # Don't try to create bucket at import time
    # We'll do this when a function is actually called
except Exception as e:
    print(f"Warning: Could not initialize MinIO client: {e}")
    minio_client = None
# Make sure the bucket exists
try:
    if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
        minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
        print(f"Bucket '{settings.MINIO_BUCKET_NAME}' created successfully")
    else:
        print(f"Bucket '{settings.MINIO_BUCKET_NAME}' already exists")
except S3Error as e:
    print(f"Error checking/creating bucket: {e}")

# Constants
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def upload(file: UploadFile, user_id: UUID) -> str:
    """
    Upload a profile picture for a user
    
    Args:
        file: The uploaded file
        user_id: UUID of the user
        
    Returns:
        str: URL of the uploaded image or None if upload failed
    """
    if minio_client is None:
        print("MinIO client not initialized")
        return None

    try:
        # Validate file type
        if not allowed_file(file):
            print("File type not allowed")
            return None
            
        # Create temporary file
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Resize image
        size = (200, 200)  # Profile picture size: 200x200 pixels
        resized_image_path = resize_image(file_path, size, user_id)
        
        # Generate image name with user ID
        extension = file.filename.split(".")[-1].lower()
        image_name = f"{str(user_id)}.{extension}"
        
        # Upload the resized image to MinIO
        minio_client.fput_object(
            settings.MINIO_BUCKET_NAME, 
            image_name, 
            resized_image_path
        )
        
        # Clean up temporary files
        os.remove(file_path)
        os.remove(resized_image_path)
        
        # Return URL to access the image
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{image_name}"
    except S3Error as exc:
        print(f"S3 error occurred: {exc}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def allowed_file(file: UploadFile) -> bool:
    """
    Check if the file has an allowed extension
    
    Args:
        file: The uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    if not file.filename:
        return False
    extension = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    return extension in ALLOWED_EXTENSIONS

def resize_image(image_path: str, size: tuple, user_id: UUID) -> str:
    """
    Resize an image to the specified size
    
    Args:
        image_path: Path to the original image
        size: Tuple containing width and height
        user_id: UUID of the user
        
    Returns:
        str: Path to the resized image
    """
    try:
        with Image.open(image_path) as img:
            # Handle image orientation (if EXIF data exists)
            if hasattr(img, '_getexif') and img._getexif():
                orientation = 274  # EXIF orientation tag
                exif = dict(img._getexif().items())
                if orientation in exif:
                    if exif[orientation] == 3:
                        img = img.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        img = img.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        img = img.rotate(90, expand=True)
            
            # Resize image while preserving aspect ratio
            img.thumbnail(size)
            
            # Create white background for transparent images
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                background.paste(img, img.split()[-1])
                img = background
            
            # Save resized image
            extension = image_path.split(".")[-1].lower()
            output_path = f"/tmp/{str(user_id)}.{extension}"
            img.save(output_path, quality=85, optimize=True)
            
            return output_path
    except Exception as e:
        print(f"Error resizing image: {e}")
        raise