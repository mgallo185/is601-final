# User Management System

## Overview
A comprehensive User Management System developed for IS601. The system provides essential user management functionalities including registration, login, profile management, admin controls, and secure image uploads via Minio.

![Test Coverage](https://github.com/user-attachments/assets/0780d693-3c4d-417c-8103-a8e817752eb1)

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

## 🔒 Security Improvements

1. **First Admin User Protection**
   - Fixed race condition in the user creation process
   - Ensures only one user can be identified as the "first user" with admin rights
   - [Issue #5](https://github.com/mgallo185/is601-final/issues/5)

2. **Email Verification Logic**
   - Improved email verification flow during user creation
   - [Issue #6](https://github.com/mgallo185/is601-final/issues/6)

3. **Enhanced Password Requirements**
   - Minimum length: 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit
   - At least one special character
   - [Issue #9](https://github.com/mgallo185/is601-final/issues/9)

4. **Unique User Identifiers**
   - Enforced uniqueness constraints on email and nickname
   - [Issue #13](https://github.com/mgallo185/is601-final/issues/13)

5. **Profile Picture URL Validation**
   - Enhanced validation for uploaded image URLs
   - [Issue #17](https://github.com/mgallo185/is601-final/issues/17)

## 🧪 Testing

The project includes comprehensive test coverage with ~90% code coverage:

![Pytest Results](https://github.com/user-attachments/assets/c92c67a0-7d88-406c-843d-8ae7d42bbd07)

### Key Test Categories:

1. **MinIO Client Tests**
   - Image file validation
   - Image resizing with EXIF rotation support
   - Upload function reliability
   - Error handling scenarios
   - [Issue #20](https://github.com/mgallo185/is601-final/issues/20)

2. **User Service Tests**
   - Account creation and verification
   - Role assignment validation
   - Admin privileges for first user
   - Performance testing with bulk operations

3. **Password Validation Tests**
   - Comprehensive tests for password requirements
   - Validation of security constraints

## 🛠️ Bug Fixes

- Fixed issue with `is_professional` field updates ([Issue #15](https://github.com/mgallo185/is601-final/issues/15))
- Corrected Dockerfile and Workflows action file ([Issue #3](https://github.com/mgallo185/is601-final/issues/3))
- Resolved library version mismatches

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
