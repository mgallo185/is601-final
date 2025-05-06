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


## Test Cases

Minio File Upload Tests: https://github.com/mgallo185/is601-final/issues/20

- test_jpg_image
- test_png_image
- test_invalid_file
- test_upload_file
- test_transparent_png
- test_allowed_file
- test_resize_image_png_with_transparency
- test_resize_image
- test_upload_valid_image
- test_upload_invalid_filetype
- test_upload_no_minio_client
- test_upload_large_image
- test_allowed_file_case_insesitive
- test_upload_file_size_limit

Test cases: https://github.com/mgallo185/is601-final/issues/27

- test_bulk_user_creation_performance
- test_current_user_error
- test_user_create_password_valid
- test_user_create_password_invalid
- test_first_user_gets_admin_role
- test_update_non_existent_user
- test_unlock_user_account_incorrect_id
- test_update_non_existent_user




## How to Run Locally

```bash

git clone https://github.com/mgallo185/is601-final.git
cd is601-final
docker-compose up --build
alembic upgrade head
http://localhost/docs

```
