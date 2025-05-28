import os
import unittest
from fastapi.testclient import TestClient
from main import app, UPLOAD_DIR, IMAGE_DIR

class UploadAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Create dummy files
        self.test_file_path = "test_sample.txt"
        self.test_image_path = "test_image.jpg"

        with open(self.test_file_path, "w") as f:
            f.write("This is a test file.")

        with open(self.test_image_path, "wb") as f:
            f.write(os.urandom(1024))  # 1KB random bytes


    def test_successful_upload(self):
        with open(self.test_file_path, "rb") as file, open(self.test_image_path, "rb") as image:
            response = self.client.post(
                "/upload/",
                files={
                    "file": ("test_sample.txt", file, "text/plain"),
                    "image": ("test_image.jpg", image, "image/jpeg")
                },
                data={
                    "username": "testuser",
                    "message": "Valid message"
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["message"], "Upload successful")
            self.assertIn("id", response.json())

    def test_invalid_username(self):
        with open(self.test_file_path, "rb") as file:
            response = self.client.post(
                "/upload/",
                files={"file": ("test_sample.txt", file, "text/plain")},
                data={"username": "ab", "message": "Valid message"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Username must be at least 3 characters", response.json()["detail"])

    def test_invalid_message(self):
        with open(self.test_file_path, "rb") as file:
            response = self.client.post(
                "/upload/",
                files={"file": ("test_sample.txt", file, "text/plain")},
                data={"username": "validuser", "message": "no"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn("message must be at least 3 characters", response.json()["detail"])

    def test_missing_required_fields(self):
        response = self.client.post("/upload/", data={"message": "Valid message"})
        self.assertEqual(response.status_code, 422)  # Username missing from form

    def test_long_filename(self):
        long_filename = "a" * 240 + ".txt"
        with open(self.test_file_path, "rb") as file:
            response = self.client.post(
                "/upload/",
                files={"file": (long_filename, file, "text/plain")},
                data={"username": "validuser", "message": "Valid message"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Filename too long.")


if __name__ == "__main__":
    unittest.main()
