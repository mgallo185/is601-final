# 🧪 Test Documentation

This document provides detailed information about the test suite for the User Management System.

## 📊 Test Coverage

The project has comprehensive test coverage with ~90% code coverage:

![Test Coverage](https://github.com/user-attachments/assets/0780d693-3c4d-417c-8103-a8e817752eb1)

All tests are passing:

![Passing Tests](https://github.com/user-attachments/assets/c92c67a0-7d88-406c-843d-8ae7d42bbd07)

## 📁 MinIO Client Test Cases

> Full issue details: [GitHub Issue #20](https://github.com/mgallo185/is601-final/issues/20)

### Tests for `allowed_file` Function

The `allowed_file` function validates whether an uploaded file has an allowed extension (jpg, jpeg, or png).

| Test Name | Description |
|-----------|-------------|
| **test_allowed_file** | Tests if the function correctly accepts valid extensions (jpg, jpeg, png) and rejects invalid ones (gif, txt, no extension). |
| **test_allowed_file_case_insensitive** | Verifies that the function accepts valid extensions regardless of case (JPG, PNG, JPEG). |
| **test_allowed_file_with_dots** | Ensures the function works correctly with filenames containing multiple dots (e.g., image.backup.jpg). |

### Tests for `resize_image` Function

The `resize_image` function resizes uploaded images to specified dimensions while preserving aspect ratio.

| Test Name | Description |
|-----------|-------------|
| **test_resize_image** | Tests basic image resizing functionality for a JPG image. |
| **test_resize_image_png_with_transparency** | Validates that transparent PNG images are properly resized and converted to non-transparent format. |
| **test_resize_image_with_exif_rotation** | Tests that images with EXIF rotation data are correctly rotated during resizing. |
| **test_resize_image_square** | Verifies that square images are resized correctly to the specified dimensions. |
| **test_resize_image_wide** | Ensures landscape (wide) images are resized correctly with width maxed out and height scaled proportionally. |
| **test_resize_image_tall** | Confirms portrait (tall) images are resized correctly with height maxed out and width scaled proportionally. |
| **test_resize_image_with_other_exif_orientations** | Tests various EXIF orientation values to ensure images are rotated correctly during resizing. |

### Tests for `upload` Function

The `upload` function is an async function that handles the upload of images to MinIO storage.

| Test Name | Description |
|-----------|-------------|
| **test_upload_valid_image** | Tests successful upload of a valid image file. |
| **test_upload_invalid_filetype** | Verifies that invalid file types are rejected. |
| **test_upload_no_minio_client** | Tests error handling when the MinIO client is not initialized. |
| **test_upload_large_image** | Validates that large images are properly resized before upload. |
| **test_upload_file_size_limit** | Tests handling of files that exceed size limits. |
| **test_upload_s3_error** | Verifies proper error handling when an S3Error occurs during upload. |
| **test_upload_file_without_extension** | Tests that files without extensions are rejected. |
| **test_upload_handles_file_open_errors** | Ensures the system properly handles errors that occur when opening files. |
| **test_upload_handles_resize_errors** | Tests error handling when image resizing fails. |

### Test Fixtures

The test suite includes several fixtures to support testing:

- **mock_minio_client**: Mock for the MinIO client.
- **mock_settings**: Mock configuration for MinIO settings.
- **test_user_id**: UUID for test user identification.
- **test_jpg_image**, **test_png_image**, **test_transparent_png**: Different test image files.
- **test_invalid_file**: Non-image file for negative testing.
- **test_upload_file**: FastAPI UploadFile object for upload testing.

## 🧩 Test Fixtures

> Full issue details: [GitHub Issue #27](https://github.com/mgallo185/is601-final/issues/27)

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

## 🔄 User Service Test Cases

### Test updating non-existent user
```python
async def test_update_non_existent_user(db_session):
    non_existent_user_id = "non-existent-id"
    updated_user = await UserService.update(db_session, non_existent_user_id, {"email": "new_email@example.com"})
    assert updated_user is None
```

This test verifies that the `UserService.update()` method handles gracefully the situation when a user with the provided ID does not exist in the database. The expected behavior is that the method returns `None` instead of raising an exception, allowing the application to handle non-existent resources properly.

### Test listing users beyond available range
```python
async def test_list_users_beyond_range(db_session):
    users = await UserService.list_users(db_session, skip=1000, limit=10)
    assert len(users) == 0
```

This test ensures that when attempting to list users with pagination parameters that go beyond the available range (skipping 1000 users), the `UserService.list_users()` method returns an empty list rather than failing. This validates that the pagination mechanism works correctly even when requesting data outside the available range.

### Test for account unlock using incorrect ID
```python
async def test_unlock_user_account_incorrect_id(db_session):
    incorrect_user_id = "incorrect-id"
    unlocked = await UserService.unlock_user_account(db_session, incorrect_user_id)
    assert unlocked is False
```

This test checks that the `UserService.unlock_user_account()` method returns `False` when attempting to unlock a user account with an ID that doesn't exist in the system. This verifies that the method properly handles invalid user IDs without throwing exceptions.

### Test that the first user in the system is automatically assigned the ADMIN role
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

This test verifies a business rule that the first registered user in the entire system should automatically be assigned the ADMIN role and have their email pre-verified.

### Performance Test: Bulk User Creation
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

### User Verification Test
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

## 🔐 Password Validation Tests

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

This test validates that passwords meeting all security requirements are accepted, including:
- At least 8 characters
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
    
    # Check if any error message contains our expected error message (partial match)
    found = False
    for error in error_details:
        if error_msg in error["msg"]:
            found = True
            break
    assert found, f"Expected error message '{error_msg}' not found in {[error['msg'] for error in error_details]}"
```

This test verifies that passwords failing specific requirements are properly rejected with appropriate error messages.
