import pytest
from fastapi.testclient import TestClient
from main import app
import unittest.mock as mock
from bson import ObjectId
from datetime import datetime
from pydantic import ValidationError

client = TestClient(app)


class TestIssuesEndpoint:
    def test_issues_without_any_params(self):
        with pytest.raises(ValidationError):
            response = client.get("/email/v2/issues/")


    def test_issues_with_invalid_params(self):
        with pytest.raises(ValidationError):
            response = client.get("/email/v2/issues/?skip=-1&limit=-1")


    @mock.patch("api.v2.services.issuesService.collection_issues")
    def test_issues_by_thread_id(self, mock_collection):
        mock_collection.find_one.return_value = {
            "thread_id": "123",
            "thread_subject": "Test thread_subject",
            "sender_email": "test@gmail.com",
            "recepient_email": "aethoroes@gmail.com",
            "status": "ongoing",
            "ongoing_status": "new",
            "start_time": "2021-01-01T00:00:00",
            "products": ["product1", "product2"],
            "issue_summary": "Test summary",
            "_id": ObjectId(),
            "issue_convo_summary_arr": [
                    {
                        "message": "Test email message",
                        "sender_type": "Client",
                        "time": "2021-01-01T00:00:00"
                    },
                    {
                        "message": "Test email message",
                        "sender_type": "Company",
                        "time": "2021-01-01T00:00:00"
                    }
                ]
        }
        response = client.get("/email/v2/issues/123")
        assert response.status_code == 200
        json = response.json()
        assert "id" in json
        assert "issue" in json
        assert "status" in json
        assert "client" in json
        assert "company" in json
        assert "tags" in json
        assert "dateOpened" in json

    @mock.patch("api.v2.services.issuesService.collection_issues")
    def test_issue_with_wrong_id_with_mocking(self, mock_collection):
        mock_collection.find_one.return_value = None
        response = client.get("/email/v2/issues/123")
        assert response.status_code == 404
        assert response.json() == {"detail": "Issue with the thread id 123 not found"}

    @mock.patch("api.v2.services.issuesService.collection_issues")
    def test_issues_with_mocking_v2(self, mock_collection):
        mock_data = [
            {
                "thread_id": "123",
                "thread_subject": "Test thread_subject",
                "sender_email": "test@gmail.com",
                "recepient_email": "sender@gmail.com",
                "status": "ongoing",
                "ongoing_status": "new",
                "start_time": "2024-05-06T05:53:01",
                "products": ["product1", "product2"],
                "issue_summary": "Test summary",
                "_id": ObjectId(),
                "emails": [
                    {
                        "message": "Test email message",
                        "sender_type": "Client",
                        "time": "2021-01-01T00:00:00"
                    },
                    {
                        "message": "Test email message",
                        "sender_type": "Company",
                        "time": "2021-01-01T00:00:00"
                    }
                ]
            },
            {
                "thread_id": "124",
                "thread_subject": "Test thread_subject",
                "sender_email": "test2@gmail.com",
                "recepient_email": "rex@gmail.com",
                "status": "ongoing",
                "ongoing_status": "update",
                "start_time": "2024-07-01T15:00:00",
                "products": [],
                "issue_summary": "Test summary",
                "_id": ObjectId()
            },
            {
                "thread_id": "125",
                "thread_subject": "Test subject",
                "sender_email": "test2@gmail.com",
                "recepient_email": "rex@gmail.com",
                "status": "ongoing",
                "ongoing_status": "update",
                "start_time": "2024-07-01T15:00:00",
                "products": [],
                "issue_summary": "Test summary",
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
        response = client.get(f"/email/v2/issues/?skip={skip}&limit={limit}")
        assert response.status_code == 200
        json = response.json()
        assert "issues" in json
        assert "total" in json
        assert "skip" in json
        assert "limit" in json
        assert len(json["issues"]) == 2
        assert json["total"] == len(mock_data)
        assert json["skip"] == skip
        assert json["limit"] == limit
        assert json["issues"][0]["id"] == "123"
        assert json["issues"][1]["id"] == "124"


class TestIssueServices:
    @mock.patch("api.v2.services.issuesService.collection_issues")
    def test_getIssuesByThreadId(self, mock_collection):
        mock_collection.find_one.return_value = {
            "thread_id": "123",
            "thread_subject": "Test subject",
            "sender_email": "test@gmail.com",
            "recepient_email": "aethoroes@gmail.com",
            "status": "ongoing",
            "ongoing_status": "new",
            "start_time": "2021-01-01T00:00:00",
            "products": ["product1", "product2"],
            "issue_summary": "Test summary",
            "_id": ObjectId(),
            "issue_convo_summary_arr": []
        }
        from api.v2.services.issuesService import getIssueByThreadId
        response = getIssueByThreadId("123")
        assert response.id == "123"
