import pytest
import os
import uuid
from unittest import mock
from fastapi import UploadFile
from PIL import Image
from io import BytesIO
from minio.error import S3Error

# Import the module to test
from app.utils.minio_client import upload, allowed_file, resize_image

# Fixtures
@pytest.fixture
def test_user_id():
    """Generate a test user ID"""
    return uuid.uuid4()

@pytest.fixture
def test_jpg_image():
    """Create a test JPG image file"""
    image_path = "/tmp/test_image.jpg"
    img = Image.new("RGB", (400, 300), color="blue")
    img.save(image_path)
    yield image_path
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)

@pytest.fixture
def test_png_image():
    """Create a test PNG image file"""
    image_path = "/tmp/test_image.png"
    img = Image.new("RGB", (400, 300), color="green")
    img.save(image_path)
    yield image_path
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)

@pytest.fixture
def test_invalid_file():
    """Create an invalid 'image' file (txt)"""
    file_path = "/tmp/test_invalid.txt"
    with open(file_path, "w") as f:
        f.write("This is not an image")
    yield file_path
    # Cleanup
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.fixture
def test_upload_file():
    """Create a FastAPI UploadFile for testing"""
    img = Image.new("RGB", (400, 300), color="red")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return UploadFile(filename="test_upload.jpg", file=buffer)

@pytest.fixture
def test_transparent_png():
    """Create a transparent PNG image file"""
    image_path = "/tmp/test_transparent.png"
    img = Image.new("RGBA", (400, 300), (255, 255, 255, 0))
    img.save(image_path)
    yield image_path
    # Cleanup
    if os.path.exists(image_path):
        os.remove(image_path)


# Tests for allowed_file function
def test_allowed_file():
    """Test allowed_file with various file types"""
    file_data = BytesIO(b"dummy data")
    
    # Valid extensions
    assert allowed_file(UploadFile(filename="image.jpg", file=file_data))
    assert allowed_file(UploadFile(filename="image.jpeg", file=file_data))
    assert allowed_file(UploadFile(filename="image.png", file=file_data))
    
    # Invalid extensions
    assert not allowed_file(UploadFile(filename="image.gif", file=file_data))
    assert not allowed_file(UploadFile(filename="image.txt", file=file_data))
    assert not allowed_file(UploadFile(filename="image", file=file_data))  # No extension
    assert not allowed_file(UploadFile(filename="", file=file_data))  # Empty filename


# Tests for resize_image function
def test_resize_image(test_jpg_image, test_user_id):
    """Test image resizing functionality"""
    size = (200, 200)
    resized_path = resize_image(test_jpg_image, size, test_user_id)
    
    # Verify the resized image exists
    assert os.path.exists(resized_path)
    assert resized_path == f"/tmp/{str(test_user_id)}.jpg"
    
    # Verify the resized image has correct dimensions
    with Image.open(resized_path) as img:
        width, height = img.size
        # The image should be at most 200x200, but might be smaller
        # due to aspect ratio preservation
        assert width <= size[0]
        assert height <= size[1]
        
    # Clean up
    os.remove(resized_path)

def test_resize_image_png_with_transparency(test_transparent_png, test_user_id):
    """Test resizing a PNG image with transparency"""
    size = (200, 200)
    resized_path = resize_image(test_transparent_png, size, test_user_id)
    
    # Verify the resized image exists
    assert os.path.exists(resized_path)
    assert resized_path == f"/tmp/{str(test_user_id)}.png"
    
    # Verify the resized image has correct dimensions and mode
    with Image.open(resized_path) as img:
        width, height = img.size
        assert width <= size[0]
        assert height <= size[1]
        assert img.mode in ("RGB", "L")  # Should have converted to non-transparent
        
    # Clean up
    os.remove(resized_path)

def test_resize_image_with_exif_rotation():
    """Test resizing an image with EXIF rotation data"""
    test_user_id = uuid.uuid4()
    filename = f"test_exif.jpg"
    img_path = f"/tmp/{filename}"
    
    # Create a basic image
    img = Image.new("RGB", (400, 300), "red")
    img.save(img_path)
    
    # Mock the Image.open to simulate EXIF data
    with mock.patch("PIL.Image.open") as mock_open:
        mock_img = mock.MagicMock()
        mock_img.mode = "RGB"
        mock_img.size = (400, 300)
        mock_img._getexif.return_value = {274: 6}  # 6 means rotate 270 degrees
        mock_open.return_value.__enter__.return_value = mock_img
        
        resize_image(img_path, (200, 200), test_user_id)
        
        # Verify that rotate was called
        mock_img.rotate.assert_called_once_with(270, expand=True)
    
    # Clean up
    if os.path.exists(img_path):
        os.remove(img_path)


# Tests for upload function
@pytest.mark.asyncio
async def test_upload_valid_image(test_upload_file, test_user_id):
    """Test uploading a valid image"""
    # Reset the file pointer
    test_upload_file.file.seek(0)
    
    # Mock the MinIO client and its methods
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        # Configure the mock
        mock_minio.fput_object.return_value = None
        
        # Call the upload function
        result = await upload(test_upload_file, test_user_id)
        
        # Check that MinIO client was called with correct parameters
        mock_minio.fput_object.assert_called_once()
        
        # Verify result is a valid URL
        assert result is not None
        assert result.startswith("http://")
        assert str(test_user_id) in result

@pytest.mark.asyncio
async def test_upload_invalid_filetype(test_user_id):
    """Test uploading an invalid file type"""
    # Create invalid file
    invalid_file = UploadFile(filename="invalid.txt", file=BytesIO(b"not an image"))
    
    # Mock the MinIO client
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        # Call the upload function
        result = await upload(invalid_file, test_user_id)
        
        # Verify MinIO client was not called
        mock_minio.fput_object.assert_not_called()
        
        # Verify result is None
        assert result is None



@pytest.mark.asyncio
async def test_upload_no_minio_client(test_upload_file, test_user_id):
    """Test upload when MinIO client is not initialized"""
    # Reset the file pointer
    test_upload_file.file.seek(0)
    
    # Mock minio_client to be None
    with mock.patch("app.utils.minio_client.minio_client", None):
        # Call the upload function
        result = await upload(test_upload_file, test_user_id)
        
        # Verify result is None
        assert result is None

@pytest.mark.asyncio
async def test_upload_large_image(test_user_id):
    """Test uploading a large image that will be resized"""
    # Create a large image
    img = Image.new("RGB", (1200, 900), "purple")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    
    large_file = UploadFile(filename="large_image.jpg", file=buffer)
    
    # Mock the MinIO client
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        # Call the upload function
        result = await upload(large_file, test_user_id)
        
        # Verify MinIO client was called
        mock_minio.fput_object.assert_called_once()
        
        # Verify result is a valid URL
        assert result is not None
        assert result.startswith("http://")

# Integration test (requires actual MinIO server)
@pytest.mark.skip(reason="Requires actual MinIO server")
@pytest.mark.asyncio
async def test_integration_upload(test_upload_file, test_user_id):
    """Integration test with actual MinIO server (skipped by default)"""
    # Reset the file pointer
    test_upload_file.file.seek(0)
    
    # Call the upload function without mocking
    result = await upload(test_upload_file, test_user_id)
    
    # Verify result is a valid URL
    assert result is not None
    assert result.startswith("http://")
    assert str(test_user_id) in result
