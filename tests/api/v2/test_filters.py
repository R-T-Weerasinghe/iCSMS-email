from fastapi.testclient import TestClient
from main import app
import unittest.mock as mock
from bson import ObjectId

client = TestClient(app)


class TestBasicFilters:

    @mock.patch("api.v2.services.filtersService.collection_suggestions")
    @mock.patch("api.v2.services.filtersService.collection_inquiries")
    @mock.patch("api.v2.services.filtersService.collection_issues")
    def test_company_addresses(self, mock_collection_issues, mock_collection_inquiries, mock_collection_suggestions):
        mock_collection_issues.distinct.return_value = ["company1", "company2", "company3"]
        response_issue = client.get("/email/v2/filter/company-addresses?type=issue")
        assert response_issue.status_code == 200
        assert response_issue.json() == {"company_addresses": ["company1", "company2", "company3"]}

        mock_collection_inquiries.distinct.return_value = ["company3", "company4", "company5"]
        response_inquiry = client.get("/email/v2/filter/company-addresses?type=inquiry")
        assert response_inquiry.status_code == 200
        assert response_inquiry.json() == {"company_addresses": ["company3", "company4", "company5"]}

        mock_collection_suggestions.distinct.return_value = ["company6", "company7", "company8"]
        response_suggestion = client.get("/email/v2/filter/company-addresses?type=suggestion")
        assert response_suggestion.status_code == 200
        assert response_suggestion.json() == {"company_addresses": ["company6", "company7", "company8"]}

    def test_company_addresses_invalid_param_value(self):
        response_invalid = client.get("/email/v2/filter/company-addresses?type=invalid")
        assert response_invalid.status_code == 422

    def test_company_addresses_missing_param(self):
        response_missing = client.get("/email/v2/filter/company-addresses")
        assert response_missing.status_code == 400

    @mock.patch("api.v2.services.filtersService.collection_suggestions")
    @mock.patch("api.v2.services.filtersService.collection_inquiries")
    @mock.patch("api.v2.services.filtersService.collection_issues")
    def test_client_addresses(self, mock_collection_issues, mock_collection_inquiries, mock_collection_suggestions):
        mock_collection_issues.distinct.return_value = ["client1", "client2", "client3"]
        response = client.get("/email/v2/filter/client-addresses?type=issue")
        assert response.status_code == 200
        assert response.json() == {"client_addresses": ["client1", "client2", "client3"]}

        mock_collection_inquiries.distinct.return_value = ["client3", "client4", "client5"]
        response = client.get("/email/v2/filter/client-addresses?type=inquiry")
        assert response.status_code == 200
        assert response.json() == {"client_addresses": ["client3", "client4", "client5"]}

        mock_collection_suggestions.distinct.return_value = ["client6", "client7", "client8"]
        response = client.get("/email/v2/filter/client-addresses?type=suggestion")
        assert response.status_code == 200
        assert response.json() == {"client_addresses": ["client6", "client7", "client8"]}

    def test_client_addresses_invalid_param_value(self):
        response = client.get("/email/v2/filter/client-addresses?type=invalid")
        assert response.status_code == 422

    def test_client_addresses_missing_param(self):
        response = client.get("/email/v2/filter/client-addresses")
        assert response.status_code == 400

    def test_statuses(self):
        response = client.get("/email/v2/filter/statuses?type=issue")
        assert response.status_code == 200
        assert response.json() == {"status": ["new", "waiting", "update", "closed"]}

        response = client.get("/email/v2/filter/statuses?type=inquiry")
        assert response.status_code == 200
        assert response.json() == {"status": ["new", "waiting", "update", "closed"]}

        response = client.get("/email/v2/filter/statuses?type=suggestion")
        assert response.status_code == 200
        assert response.json() == {"status": ["new", "waiting", "update", "closed"]}

    def test_statuses_invalid_param_value(self):
        response = client.get("/email/v2/filter/statuses?type=invalid")
        assert response.status_code == 422

    def test_statuses_missing_param(self):
        response = client.get("/email/v2/filter/statuses")
        assert response.status_code == 400

    @mock.patch("api.v2.services.filtersService.collection_suggestions")
    @mock.patch("api.v2.services.filtersService.collection_inquiries")
    @mock.patch("api.v2.services.filtersService.collection_issues")
    def test_tags(self, mock_collection_issues, mock_collection_inquiries, mock_collection_suggestions):
        mock_collection_issues.distinct.return_value = ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]
        response = client.get("/email/v2/filter/tags?type=issue")
        assert response.status_code == 200
        assert response.json() == {"tags": ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]}

        mock_collection_inquiries.distinct.return_value = ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]
        response = client.get("/email/v2/filter/tags?type=inquiry")
        assert response.status_code == 200
        assert response.json() == {"tags": ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]}

        mock_collection_suggestions.distinct.return_value = ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]
        response = client.get("/email/v2/filter/tags?type=suggestion")
        assert response.status_code == 200
        assert response.json() == {"tags": ["API development", "API monitoring", "IAM", "Mercury", "Cloud Management"]}

    def test_tags_invalid_param_value(self):
        response = client.get("/email/v2/filter/tags?type=invalid")
        assert response.status_code == 422

    def test_tags_missing_param(self):
        response = client.get("/email/v2/filter/tags")
        assert response.status_code == 400

