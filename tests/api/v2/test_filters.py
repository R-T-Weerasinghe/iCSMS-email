from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestBasicFilters:
    def test_company_addresses(self):
        response = client.get("/email/v2/filter/company-addresses")
        assert response.status_code == 200
        assert response.json() == {"company_addresses": ["company1", "company2", "company3"]}

    def test_client_addresses(self):
        response = client.get("/email/v2/filter/client-addresses")
        assert response.status_code == 200
        assert response.json() == {"client_addresses": ["client1", "client2", "client3"]}

    def test_statuses(self):
        response = client.get("/email/v2/filter/statuses")
        assert response.status_code == 200
        assert response.json() == {"status": ["New", "Waiting", "Update", "Closed"]}

    def test_tags(self):
        response = client.get("/email/v2/filter/tags")
        assert response.status_code == 200
        assert response.json() == {"tags": ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]}

