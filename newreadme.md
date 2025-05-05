# User Management System: IS601-Final Project

This project is a comprehensive User Management System designed as the final project for IS601. It includes core user functionalities such as registration, login, profile management, and admin controls. The system is containerized using Docker and includes support for image uploads via Minio.


### Repository and Docker Image Links
https://github.com/mgallo185/is601-final/
https://hub.docker.com/r/mgallo185/is601-final


Screenshots:

Passes all of Pytest: <img width="470" alt="image" src="https://github.com/user-attachments/assets/c92c67a0-7d88-406c-843d-8ae7d42bbd07" />

89%/90% Coverage: <img width="478" alt="image" src="https://github.com/user-attachments/assets/0780d693-3c4d-417c-8103-a8e817752eb1" />


Docker Image: <img width="959" alt="image" src="https://github.com/user-attachments/assets/69e8f95f-d332-4d0a-b5c0-f85ebba332a5" />


## New Feature: Profile Picture Upload with Minio

Link to Issue: https://github.com/mgallo185/is601-final/issues/8

Users can now upload a profile picture as part of their account setup or update process. Uploaded images are securely stored in an S3-compatible object storage service using Minio.

Validates uploaded image file type and URL

Links to user's profile in the system

Easy configuration through environment variables

Key Aspects: 
- API Endpoint Creation
- Minio Integration
- User Profile Update
- Upload, resize, and store user profile pictures
- File Format Validation (.jpg, .jpeg, .png)




## QA Issues Resolved

The following QA-related improvements and bug fixes were implemented:

 First registered user is automatically set as an Admin

 Email verification logic added during user creation

 Password validation with strength requirements (length, complexity)

 Unique constraints enforced on email and nickname

 Profile picture URL validation to ensure valid input

 Fixed issue where is_professional field was not updating

 Many additional bug fixes and code quality enhancements





## Test Cases


## How to Run Locally

```bash

git clone https://github.com/mgallo185/is601-final.git
cd is601-final
docker-compose up --build
alembic upgrade head
http://localhost/docs

```

