from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestIssuesGeneral:
    def test_issues_without_any_params(self):
        response = client.get("/email/v2/issues/")
        assert response.status_code == 400

    def test_issues_with_valid_params(self):
        response = client.get("/email/v2/issues/?skip=0&limit=10")
        assert response.status_code == 200
        json = response.json()
        assert "issues" in json
        assert "total" in json
        assert "skip" in json
        assert "limit" in json
        assert len(json["issues"]) > 0
        assert json["total"] > 0
        assert json["skip"] == 0
        assert json["limit"] == 10

    def test_issues_with_invalid_params(self):
        response = client.get("/email/v2/issues/?skip=-1&limit=-1")
        assert response.status_code == 400

    def test_issue_with_wrong_id(self):
        response = client.get("/email/v2/issues/123")
        assert response.status_code == 404
        assert response.json() == {"detail": "Issue with the thread id 123 not found"}

    def test_issue_with_correct_id(self):
        id = client.get("/email/v2/issues/?skip=0&limit=1").json()["issues"][0]["id"]
        response = client.get(f"/email/v2/issues/{id}")
        assert response.status_code == 200
