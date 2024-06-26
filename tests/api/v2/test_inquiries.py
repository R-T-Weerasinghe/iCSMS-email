import pytest
from fastapi.testclient import TestClient
from main import app
import unittest.mock as mock
from bson import ObjectId
from pydantic import ValidationError

client = TestClient(app)


class TestInquiries:
    def test_inquiries_without_any_params(self):
        with pytest.raises(ValidationError):
            response = client.get("/email/v2/inquiries/")


    def test_inquiries_with_invalid_params(self):
        with pytest.raises(ValidationError):
            response = client.get("/email/v2/inquiries/?skip=-1&limit=-1")


    @mock.patch("api.v2.services.inquiriesService.collection_inquiries")
    def test_inquiries_with_mocking(self, mock_collection):
        mock_collection.find_one.return_value = {
            "thread_id": "123",
            "subject": "Test subject",
            "sender_email": "test@gmail.com",
            "recepient_email": "aethoroes@gmail.com",
            "status": "ongoing",
            "ongoing_status": "new",
            "start_time": "2021-01-01T00:00:00",
            "products": ["product1", "product2"],
            "inquiry_summary": "Test summary",
            "_id": ObjectId()
        }
        response = client.get("/email/v2/inquiries/123")
        assert response.status_code == 200
        json = response.json()
        assert "id" in json
        assert "inquiry" in json
        assert "status" in json
        assert "client" in json
        assert "company" in json
        assert "tags" in json
        assert "dateOpened" in json

    @mock.patch("api.v2.services.inquiriesService.collection_inquiries")
    def test_inquiry_with_wrong_id_with_mocking(self, mock_collection):
        mock_collection.find_one.return_value = None
        response = client.get("/email/v2/inquiries/123")
        assert response.status_code == 404
        assert response.json() == {"detail": "Inquiry with the thread id 123 not found"}

    @mock.patch("api.v2.services.inquiriesService.collection_inquiries")
    def test_inquiries_with_mocking_v2(self, mock_collection):
        mock_data = [
            {
                "thread_id": "123",
                "subject": "Test subject",
                "sender_email": "test@gmail.com",
                "recepient_email": "sender@gmail.com",
                "status": "ongoing",
                "ongoing_status": "new",
                "start_time": "2021-01-01T00:00:00",
                "products": ["product1", "product2"],
                "inquiry_summary": "Test summary",
                "_id": ObjectId(),
                "emails": [
                    {
                        "body": "Test email body",
                        "isClient": True,
                        "dateTime": "2021-01-01T00:00:00"
                    },
                    {
                        "body": "Test email body",
                        "isClient": False,
                        "dateTime": "2021-01-01T00:00:00"
                    }
                ]
            },
            {
                "thread_id": "124",
                "subject": "Test subject",
                "sender_email": "test2@gmail.com",
                "recepient_email": "rex@gmail.com",
                "status": "ongoing",
                "ongoing_status": "update",
                "start_time": "2024-07-01T15:00:00",
                "products": [],
                "inquiry_summary": "Test summary",
                "_id": ObjectId()
            },
            {
                "thread_id": "125",
                "subject": "Test subject",
                "sender_email": "test2@gmail.com",
                "recepient_email": "rex@gmail.com",
                "status": "ongoing",
                "ongoing_status": "update",
                "start_time": "2024-07-01T15:00:00",
                "products": [],
                "inquiry_summary": "Test summary",
                "_id": ObjectId()
            }
        ]

        class MockCursor:
            def __init__(self, data):
                self.data = data
                self._skip = None
                self._limit = None

            def skip(self, n):
                self._skip = n
                return self

            def limit(self, n):
                self._limit = n
                return self

            def __iter__(self):
                if self._skip is not None and self._limit is not None:
                    return iter(self.data[self._skip:self._skip + self._limit])
                raise ValueError("Skip and limit must be set")

        mock_collection.find.return_value = MockCursor(mock_data)
        mock_collection.count_documents.return_value = len(mock_data)

        skip = 0
        limit = 2
        response = client.get(f"/email/v2/inquiries/?skip={skip}&limit={limit}")
        assert response.status_code == 200
        json = response.json()
        assert "inquiries" in json
        assert "total" in json
        assert "skip" in json
        assert "limit" in json
        assert len(json["inquiries"]) == 2
        assert json["total"] == len(mock_data)
        assert json["skip"] == skip
        assert json["limit"] == limit
        assert json["inquiries"][0]["id"] == "123"
        assert json["inquiries"][1]["id"] == "124"
