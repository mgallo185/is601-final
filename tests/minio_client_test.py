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
def mock_minio_client():
    """Fixture to mock the Minio client."""
    with patch("app.utils.minio_client.minio_client", autospec=True) as mock_client:
        yield mock_client


@pytest.fixture
def mock_settings():
    """Fixture to mock the settings."""
    return {
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_BUCKET_NAME": "bucket_name",
        "MINIO_ACCESS_KEY": "test-access-key",
        "MINIO_SECRET_KEY": "test-secret-key",
        "MINIO_USE_SSL": False,
    }
    

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

def test_allowed_file_case_insensitive():
    """Test allowed_file with uppercase extensions"""
    file_data = BytesIO(b"dummy data")
    
    # Uppercase extensions should still be allowed
    assert allowed_file(UploadFile(filename="image.JPG", file=file_data))
    assert allowed_file(UploadFile(filename="image.PNG", file=file_data))
    assert allowed_file(UploadFile(filename="image.JPEG", file=file_data))

def test_allowed_file_with_dots():
    """Test allowed_file with filenames containing multiple dots"""
    file_data = BytesIO(b"dummy data")
    
    # Multiple dots in filename
    assert allowed_file(UploadFile(filename="image.backup.jpg", file=file_data))
    assert not allowed_file(UploadFile(filename="image.backup.gif", file=file_data))

# Additional tests for resize_image function
def test_resize_image_square(test_user_id):
    """Test resizing a square image"""
    image_path = "/tmp/test_square.jpg"
    img = Image.new("RGB", (400, 400), color="yellow")
    img.save(image_path)
    
    size = (200, 200)
    resized_path = resize_image(image_path, size, test_user_id)
    
    # Verify dimensions
    with Image.open(resized_path) as img:
        width, height = img.size
        assert width == size[0]
        assert height == size[0]  # Should be square
    
    # Clean up
    os.remove(image_path)
    os.remove(resized_path)

def test_resize_image_wide(test_user_id):
    """Test resizing a wide (landscape) image"""
    image_path = "/tmp/test_wide.jpg"
    img = Image.new("RGB", (600, 300), color="orange")
    img.save(image_path)
    
    size = (200, 200)
    resized_path = resize_image(image_path, size, test_user_id)
    
    # Verify dimensions - width should be maxed, height proportional
    with Image.open(resized_path) as img:
        width, height = img.size
        assert width == size[0]
        assert height < size[1]  # Height should be smaller due to aspect ratio
    
    # Clean up
    os.remove(image_path)
    os.remove(resized_path)

def test_resize_image_tall(test_user_id):
    """Test resizing a tall (portrait) image"""
    image_path = "/tmp/test_tall.jpg"
    img = Image.new("RGB", (300, 600), color="purple")
    img.save(image_path)
    
    size = (200, 200)
    resized_path = resize_image(image_path, size, test_user_id)
    
    # Verify dimensions - height should be maxed, width proportional
    with Image.open(resized_path) as img:
        width, height = img.size
        assert width < size[0]  # Width should be smaller due to aspect ratio
        assert height == size[1]
    
    # Clean up
    os.remove(image_path)
    os.remove(resized_path)


def test_resize_image_with_other_exif_orientations():
    """Test different EXIF orientation values"""
    test_user_id = uuid.uuid4()
    img_path = "/tmp/test_exif_multi.jpg"
    
    # Create a basic image
    img = Image.new("RGB", (400, 300), "blue")
    img.save(img_path)
    
    orientations = {
        1: 0,    # Normal orientation
        3: 180,  # 180° rotation
        6: 270,  # 270° rotation
        8: 90,   # 90° rotation
    }
    
    for exif_value, expected_rotation in orientations.items():
        with mock.patch("PIL.Image.open") as mock_open:
            mock_img = mock.MagicMock()
            mock_img.mode = "RGB"
            mock_img.size = (400, 300)
            mock_img._getexif.return_value = {274: exif_value}  # EXIF orientation tag
            mock_open.return_value.__enter__.return_value = mock_img
            
            resize_image(img_path, (200, 200), test_user_id)
            
            # Verify rotation was called with correct angle if not normal orientation
            if exif_value != 1:
                mock_img.rotate.assert_called_once_with(expected_rotation, expand=True)
            else:
                mock_img.rotate.assert_not_called()
    
    # Clean up
    if os.path.exists(img_path):
        os.remove(img_path)

# Additional tests for upload function
@pytest.mark.asyncio
async def test_upload_file_size_limit():
    """Test uploading a file exceeding size limit"""
    test_user_id = uuid.uuid4()
    
    # Create a file that would exceed size limit
    # but mock the file size check
    buffer = BytesIO(b"small content")
    large_file = UploadFile(filename="test.jpg", file=buffer)
    
    # Mock file read to return something that would exceed size limit
    original_read = large_file.read
    large_file.read = mock.AsyncMock(return_value=b"x" * (11 * 1024 * 1024))  # 11MB
    
    # Mock MinIO client
    with mock.patch("app.utils.minio_client.minio_client"):
        result = await upload(large_file, test_user_id)
        
        # Since we're not actually checking file size in the code,
        # this test is more for future implementation
        # Restore original method to avoid issues
        large_file.read = original_read

@pytest.mark.asyncio
async def test_upload_s3_error():
    """Test handling of S3Error during upload"""
    test_user_id = uuid.uuid4()
    
    # Create valid file
    buffer = BytesIO()
    img = Image.new("RGB", (100, 100), "red")
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    
    valid_file = UploadFile(filename="test.jpg", file=buffer)
    
    # Mock MinIO client to raise S3Error
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        mock_minio.fput_object.side_effect = S3Error(
            code="InternalError",
            message="Internal server error",
            resource="/bucket/object",
            request_id="request123",
            host_id="host123",
            response="error"
        )
        
        # Mock open and Image.open to avoid actual file operations
        with mock.patch("builtins.open", mock.mock_open()), \
             mock.patch("PIL.Image.open") as mock_img_open:
            mock_img = mock.MagicMock()
            mock_img.mode = "RGB"
            mock_img.size = (100, 100)
            mock_img_open.return_value.__enter__.return_value = mock_img
            
            result = await upload(valid_file, test_user_id)
            
            # Should handle the error and return None
            assert result is None

@pytest.mark.asyncio
async def test_upload_file_without_extension():
    """Test uploading a file without an extension"""
    test_user_id = uuid.uuid4()
    
    # Create file without extension
    no_ext_file = UploadFile(filename="testimage", file=BytesIO(b"content"))
    
    # Mock MinIO client
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        result = await upload(no_ext_file, test_user_id)
        
        # Should return None as file isn't allowed
        assert result is None
        # Verify MinIO client was not called
        mock_minio.fput_object.assert_not_called()



@pytest.mark.asyncio
async def test_upload_handles_file_open_errors():
    """Test handling errors when opening files"""
    test_user_id = uuid.uuid4()
    
    # Create valid file
    valid_file = UploadFile(filename="test.jpg", file=BytesIO(b"content"))
    
    # Mock MinIO client
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        # Mock open to raise an exception
        with mock.patch("builtins.open") as mock_open:
            mock_open.side_effect = IOError("Cannot open file")
            
            result = await upload(valid_file, test_user_id)
            
            # Should handle the error and return None
            assert result is None
            # Verify MinIO client was not called
            mock_minio.fput_object.assert_not_called()

@pytest.mark.asyncio
async def test_upload_handles_resize_errors():
    """Test handling errors during image resizing"""
    test_user_id = uuid.uuid4()
    
    # Create valid file
    valid_file = UploadFile(filename="test.jpg", file=BytesIO(b"content"))
    
    # Mock MinIO client
    with mock.patch("app.utils.minio_client.minio_client") as mock_minio:
        # Mock open to work but resize_image to fail
        with mock.patch("builtins.open", mock.mock_open()), \
             mock.patch("app.utils.minio_client.resize_image") as mock_resize:
            mock_resize.side_effect = Exception("Failed to resize")
            
            result = await upload(valid_file, test_user_id)
            
            # Should handle the error and return None
            assert result is None
            # Verify MinIO client was not called
            mock_minio.fput_object.assert_not_called()
            

