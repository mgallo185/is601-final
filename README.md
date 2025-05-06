# User Management System: IS601-Final Project

This project is a comprehensive User Management System designed as the final project for IS601. It includes core user functionalities such as registration, login, profile management, and admin controls. The system is containerized using Docker and includes support for image uploads via Minio.

## 🔗 Quick Links
- [GitHub Repository](https://github.com/mgallo185/is601-final/)
- [Docker Image](https://hub.docker.com/r/mgallo185/is601-final)
- [Reflection Document](https://github.com/mgallo185/is601-final/blob/main/IS%20601%20Reflection%20Doc.pdf)

## ✨ Features

### Core Functionality
- User registration with email verification
- Secure authentication system
- Profile management
- Admin user controls
- Role-based access control

### Profile Picture Upload with Minio
Users can now upload profile pictures with the following features:
- S3-compatible object storage via Minio
- File type validation (.png, .jpg, .jpeg)
- 10MB file size limit
- Automatic image resizing to 200x200px
- EXIF orientation preservation

## 🚀 Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- Git

### Running Locally
```bash
# Clone the repository
git clone https://github.com/mgallo185/is601-final.git
cd is601-final

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the application with Docker
docker-compose up --build

# Run database migrations
alembic upgrade head

# Access the application
# Open http://localhost/docs in your browser
```
### Docker Image:

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



##  🛠️ QA Issues Resolved and Bug Fixes

The following QA-related improvements and bug fixes were implemented:

 1. First registered user is automatically set as an Admin: https://github.com/mgallo185/is601-final/issues/5

    Fixed a race condition in the user creation process. The is_first_user method was vulnerable to concurrent requests, potentially allowing multiple "first users" to be created simultaneously. This could lead to privilege escalation issues since the first user is typically granted admin rights.
    
The fixed implementation properly checks the user count atomically before any new user creation, ensuring that only one user can ever be identified as the "first user" in the system, maintaining proper access control security.

 2. Email verification logic added during user creation: https://github.com/mgallo185/is601-final/issues/6

Moved sending verification email when the email is being sent to the user, so that the user can be created first and then sent the proper verification email that will have their id attached.


 3.  Password validation with strength requirements (length, complexity): https://github.com/mgallo185/is601-final/issues/9


Implemented comprehensive password strength requirements across all authentication flows to improve system security. The new password validation enforces the following criteria:

- Minimum length of 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

These requirements are now consistently applied in both the password creation flow for new accounts and the password reset functionality for existing users. This enhancement significantly reduces vulnerability to brute force attacks and ensures compliance with modern security standards.


 4.   Unique constraints enforced on email and nickname: https://github.com/mgallo185/is601-final/issues/13

Resolved an issue where users could register with nicknames/usernames that were already taken in the database. This created confusion in user identification and potential security vulnerabilities with account impersonation.

Implemented a proper uniqueness constraint on the nickname field in the database schema and added validation in the registration process to check for existing nicknames before account creation. When a user attempts to register with an already taken nickname, the system now returns a clear error message prompting them to choose a different one.




 5. Profile picture URL validation to ensure valid input: https://github.com/mgallo185/is601-final/issues/17


Ensured the provided URL is well-formed and points to an image file by validating that it ends with standard image extensions
such as .jpg, .jpeg or .png.

Implemented robust URL validation mechanisms to ensure secure and valid profile picture uploads. This includes verifying that the URL is properly structured, ends with acceptable image file extensions, and optionally confirming the URL's accessibility and that it references a valid image resource.


 6. Fixed issue where is_professional field was not updating: https://github.com/mgallo185/is601-final/issues/15

Added the is_professional field in the user schema. The is_professional field was added to both user_update and user_response schemas, ensuring proper data handling and seamless functionality for update

7. Fixed Dockerfile and Workflows action file: https://github.com/mgallo185/is601-final/issues/3

- Updated the Docker File to allow build.
- Fixed the workflow action yml file to pass the build if the vulnerabilities are found. Adjusted workflow file for my own settings such as my docker repo and adding Minio Settings
- Fixed the Application throwing error due to library version mismatch



## 🧪 Testing

The project includes comprehensive test coverage with ~90% code coverage:

![Test Coverage](https://github.com/user-attachments/assets/0780d693-3c4d-417c-8103-a8e817752eb1)

All tests are passing:

![Passing Tests](https://github.com/user-attachments/assets/c92c67a0-7d88-406c-843d-8ae7d42bbd07)

### Key Test Categories:

1. **MinIO Client Tests** - Ensuring robust image upload functionality:
   - File validation
   - Image resizing with EXIF orientation support
   - Error handling

2. **User Service Tests** - Validating core user management functionality:
   - Account creation and verification
   - Role assignment validation
   - Admin privileges for first user
   - Error handling for edge cases

3. **Password Validation Tests** - Verifying security requirements:
   - Length and complexity validation
   - Proper error handling for invalid passwords

For detailed test documentation, see [testing.md](testing.md).

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
