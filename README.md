# User Management System: IS601-Final Project

This project is a comprehensive User Management System designed as the final project for IS601. It includes core user functionalities such as registration, login, profile management, and admin controls. The system is containerized using Docker and includes support for image uploads via Minio.

## Reflection Document
https://github.com/mgallo185/is601-final/blob/main/IS%20601%20Reflection%20Doc.pdf



### Repository and Docker Image Links
https://github.com/mgallo185/is601-final/

https://hub.docker.com/r/mgallo185/is601-final


Screenshots:

Passes all of Pytest: 

<img width="470" alt="image" src="https://github.com/user-attachments/assets/c92c67a0-7d88-406c-843d-8ae7d42bbd07" />

89%/90% Coverage:

<img width="478" alt="image" src="https://github.com/user-attachments/assets/0780d693-3c4d-417c-8103-a8e817752eb1" />


Docker Image:

<img width="959" alt="image" src="https://github.com/user-attachments/assets/69e8f95f-d332-4d0a-b5c0-f85ebba332a5" />


## New Feature: Profile Picture Upload with Minio

Link to Issue: https://github.com/mgallo185/is601-final/issues/8

Users can now upload a profile picture as part of their account setup or update process. Uploaded images are securely stored in an S3-compatible object storage service using Minio.

Validates uploaded image file type and URL

Links to user's profile in the system

Easy configuration through environment variables

Key Aspects: 
- API Endpoint Creation
- Minio Integration: Uses the minio Python SDK to upload images to a specified bucket.
- User Profile Update
- File Type Validation: Only .png, .jpg, and .jpeg extensions are accepted.
- File Size Limit: Maximum upload size is 10MB.
- Image Resizing: Uploaded images are resized to 200x200 pixels using the Pillow (PIL) library. EXIF orientation is respected.
- Temporary File Handling: Uploaded files are temporarily saved and removed after successful upload.



## QA Issues Resolved

The following QA-related improvements and bug fixes were implemented:

 1. First registered user is automatically set as an Admin: https://github.com/mgallo185/is601-final/issues/5
 2. Email verification logic added during user creation: https://github.com/mgallo185/is601-final/issues/6
 3.  Password validation with strength requirements (length, complexity): https://github.com/mgallo185/is601-final/issues/9 
 4.   Unique constraints enforced on email and nickname: https://github.com/mgallo185/is601-final/issues/13
 5.    Profile picture URL validation to ensure valid input: https://github.com/mgallo185/is601-final/issues/17
 6. Fixed issue where is_professional field was not updating: https://github.com/mgallo185/is601-final/issues/15


# Test Cases

Minio File Upload Tests: https://github.com/mgallo185/is601-final/issues/20

# MinIO Client Test Cases

This file contains comprehensive test cases for a MinIO client utility that handles image upload functionality within a FastAPI application. Below is a summary of all test cases organized by the functions they test.

## Tests for `allowed_file` Function

The `allowed_file` function validates whether an uploaded file has an allowed extension (jpg, jpeg, or png).

- **test_allowed_file**: Tests if the function correctly accepts files with valid extensions (jpg, jpeg, png) and rejects invalid ones (gif, txt, no extension).
- **test_allowed_file_case_insensitive**: Verifies that the function accepts valid extensions regardless of case (JPG, PNG, JPEG).
- **test_allowed_file_with_dots**: Ensures the function works correctly with filenames containing multiple dots (e.g., image.backup.jpg).

## Tests for `resize_image` Function

The `resize_image` function resizes uploaded images to specified dimensions while preserving aspect ratio.

- **test_resize_image**: Tests basic image resizing functionality for a JPG image.
- **test_resize_image_png_with_transparency**: Validates that transparent PNG images are properly resized and converted to non-transparent format.
- **test_resize_image_with_exif_rotation**: Tests that images with EXIF rotation data are correctly rotated during resizing.
- **test_resize_image_square**: Verifies that square images are resized correctly to the specified dimensions.
- **test_resize_image_wide**: Ensures landscape (wide) images are resized correctly with width maxed out and height scaled proportionally.
- **test_resize_image_tall**: Confirms portrait (tall) images are resized correctly with height maxed out and width scaled proportionally.
- **test_resize_image_with_other_exif_orientations**: Tests various EXIF orientation values to ensure images are rotated correctly during resizing.

## Tests for `upload` Function

The `upload` function is an async function that handles the upload of images to MinIO storage.

- **test_upload_valid_image**: Tests successful upload of a valid image file.
- **test_upload_invalid_filetype**: Verifies that invalid file types are rejected.
- **test_upload_no_minio_client**: Tests error handling when the MinIO client is not initialized.
- **test_upload_large_image**: Validates that large images are properly resized before upload.
- **test_upload_file_size_limit**: Tests handling of files that exceed size limits (placeholder for future implementation).
- **test_upload_s3_error**: Verifies proper error handling when an S3Error occurs during upload.
- **test_upload_file_without_extension**: Tests that files without extensions are rejected.
- **test_upload_handles_file_open_errors**: Ensures the system properly handles errors that occur when opening files.
- **test_upload_handles_resize_errors**: Tests error handling when image resizing fails.

## Test Fixtures

The test suite includes several fixtures to support testing:

- **mock_minio_client**: Mock for the MinIO client.
- **mock_settings**: Mock configuration for MinIO settings.
- **test_user_id**: UUID for test user identification.
- **test_jpg_image**, **test_png_image**, **test_transparent_png**: Different test image files.
- **test_invalid_file**: Non-image file for negative testing.
- **test_upload_file**: FastAPI UploadFile object for upload testing.

These tests ensure comprehensive coverage of the image upload functionality, including validation, resizing, and error handling scenarios.

Test cases: https://github.com/mgallo185/is601-final/issues/27

In the tests/conftest.py directory:

## Test Fixtures

Our testing relies on several key fixtures defined in `conftest.py`:

### Unique User Data

```python
@pytest.fixture
def unique_user_data():
    return {
        "nickname": f"user_{uuid.uuid4().hex[:8]}",
        "email": f"user_{uuid.uuid4().hex[:8]}@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "AUTHENTICATED"
    }
```

This fixture generates random user data with unique identifiers for testing. It creates:
- A random nickname using UUID
- A unique email address using UUID
- Standard name fields
- Default authenticated role

### Test User

```python
@pytest.fixture
async def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        nickname="test_user",
        email="testuser@example.com",
        role=UserRole.AUTHENTICATED,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    hashed_password = hash_password("password123")
    user.hashed_password = hashed_password 
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

## Test Cases located in tests_conftest.py
### Bulk User Creation Performance

```python
async def test_bulk_user_creation_performance(
    db_session, users_with_same_role_50_users
):
    async with db_session.begin():
        for user in users_with_same_role_50_users:
            db_session.add(user)
        await db_session.flush()
    async with db_session.begin():
        result = await db_session.execute(
            select(User).filter_by(role=UserRole.AUTHENTICATED)
        )
        users = result.scalars().all()
        assert len(users) == 50
```

This test verifies that we can efficiently create and store multiple users (50) in the database.

### User Verification

```python
@pytest.mark.asyncio
async def test_current_user_error(db_session, verified_user):
    """Test that a user is correctly created and stored in the database."""
    result = await db_session.execute(select(User).filter_by(email=verified_user.email))
    stored_user = result.scalars().first()
    assert stored_user is not None
    assert stored_user.email == verified_user.email
    assert verify_password("MySuperPassword$1234", stored_user.hashed_password)
```

This test ensures that a verified user is properly stored in the database and that password verification works correctly.


## Password Validation Test case in test_user_schemas.py

The codebase includes comprehensive tests to ensure password validation works correctly during user creation.

### Valid Password Tests

```python
@pytest.mark.parametrize("password", [
    "Secure*1234",
    "Complex!23",
    "Ab1!defg",
    "P@55w0rd",
    "Very$ecure2023"
])
def test_user_create_password_valid(password, user_create_data):
    user_create_data["password"] = password
    user = UserCreate(**user_create_data)
    assert user.password == password
```

This test validates that passwords meeting all security requirements are accepted. Each test password contains:
- At least 8 characters (except "Complex!23" and "P@55w0rd" which are exactly 8)
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Invalid Password Tests

```python
@pytest.mark.parametrize("password,error_msg", [
    ("short1!", "String should have at least 8 characters"),
    ("lowercase1!", "Password must contain at least one uppercase letter."),
    ("UPPERCASE1!", "Password must contain at least one lowercase letter."),
    ("NoDigits!", "Password must contain at least one digit."),
    ("NoSpecial123", "Password must contain at least one special character.")
])
def test_user_create_password_invalid(password, error_msg, user_create_data):
    user_create_data["password"] = password
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(**user_create_data)
    
    # Check that the validation error contains the expected error message
    error_details = exc_info.value.errors()
    
    # Print the actual error messages for debugging
    print(f"Actual errors: {[error['msg'] for error in error_details]}")
    
    # Check if any error message contains our expected error message (partial match)
    found = False
    for error in error_details:
        if error_msg in error["msg"]:
            found = True
            break
    assert found, f"Expected error message '{error_msg}' not found in {[error['msg'] for error in error_details]}"
```

This test verifies that passwords failing specific requirements are properly rejected with appropriate error messages:

1. **Too Short**: "short1!" - Fails because it has fewer than 8 characters
2. **No Uppercase**: "lowercase1!" - Fails because it doesn't contain any uppercase letters
3. **No Lowercase**: "UPPERCASE1!" - Fails because it doesn't contain any lowercase letters
4. **No Digits**: "NoDigits!" - Fails because it doesn't contain any numbers
5. **No Special Characters**: "NoSpecial123" - Fails because it doesn't contain any special characters

The test captures ValidationError exceptions and verifies that the appropriate error message is included in the validation response.

# User Service Test Cases Explanation

## Test updating non-existent user
```python
async def test_update_non_existent_user(db_session):
    non_existent_user_id = "non-existent-id"
    updated_user = await UserService.update(db_session, non_existent_user_id, {"email": "new_email@example.com"})
    assert updated_user is None
```

This test verifies that the `UserService.update()` method handles gracefully the situation when a user with the provided ID does not exist in the database. The expected behavior is that the method returns `None` instead of raising an exception, allowing the application to handle non-existent resources properly.

## Test listing users beyond available range
```python
async def test_list_users_beyond_range(db_session):
    users = await UserService.list_users(db_session, skip=1000, limit=10)
    assert len(users) == 0
```

This test ensures that when attempting to list users with pagination parameters that go beyond the available range (skipping 1000 users), the `UserService.list_users()` method returns an empty list rather than failing. This validates that the pagination mechanism works correctly even when requesting data outside the available range.

## Test for account unlock using incorrect ID
```python
async def test_unlock_user_account_incorrect_id(db_session):
    incorrect_user_id = "incorrect-id"
    unlocked = await UserService.unlock_user_account(db_session, incorrect_user_id)
    assert unlocked is False
```

This test checks that the `UserService.unlock_user_account()` method returns `False` when attempting to unlock a user account with an ID that doesn't exist in the system. This verifies that the method properly handles invalid user IDs without throwing exceptions.

## Test that the first user in the system is automatically assigned the ADMIN role
```python
async def test_first_user_gets_admin_role(db_session, email_service, monkeypatch):
    # Mock the is_first_user method to return True
    original_is_first_user = UserService.is_first_user
    async def mock_is_first_user(*args, **kwargs):
        return True
    monkeypatch.setattr(UserService, "is_first_user", mock_is_first_user)
    
    # Create a user without specifying role
    user_data = {
        "nickname": generate_nickname(),
        "email": "first_user@example.com",
        "password": "FirstUser123!"
    }
    
    # Create the user
    user = await UserService.create(db_session, user_data, email_service)
    
    # Restore the original method
    monkeypatch.setattr(UserService, "is_first_user", original_is_first_user)
    
    # Assertions
    assert user is not None
    assert user.role == UserRole.ADMIN
    assert user.email_verified is True  # First admin user should be auto-verified
```

This test verifies a business rule that the first registered user in the entire system should automatically be assigned the ADMIN role and have their email pre-verified. The test:

1. Mocks the `UserService.is_first_user()` method to always return `True`, simulating that this is the first user being created
2. Creates a new user without explicitly specifying a role
3. Verifies that:
   - The user was created successfully
   - The user automatically received the ADMIN role
   - The user's email was automatically marked as verified

This ensures the system correctly implements the security policy where the first user becomes the system administrator.



## How to Run Locally

```bash

git clone https://github.com/mgallo185/is601-final.git
cd is601-final
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up --build
alembic upgrade head
http://localhost/docs

```
