import pytest

from api.v2.models.convoModel import EmailInDB
from datetime import datetime
from fastapi.testclient import TestClient
from main import app
from unittest import mock

client = TestClient(app)


class TestResponseTimeUtilities:

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_normal_scenario(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 5, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 10, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 1

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_no_response(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time is None

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_no_client_response(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time is None

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_no_company_response(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 2, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time is None

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_double_client(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 1, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 1, 10, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 1, 12, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 12

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_double_company(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 1, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 1, 10, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 1, 12, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 10

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_repsonse_time_multiple_hours(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 2, 35, 4)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 2, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 3, 0, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 155

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_repsonse_time_multiple_days(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 2, 0, 0, 0)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 1440

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_seconds_rounding(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 2, 40)
            )
        ]
        response_time = utilityService.get_first_response_time(email_list)
        assert response_time == 2

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_response_time_invalid_list_provided(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        with pytest.raises(ValueError):
            utilityService.get_first_response_time(email_list)

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_average_response_time_normal_scenario(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 5, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 10, 0)
            )
        ]
        avg_response_time = utilityService.get_avg_response_time(email_list)
        assert avg_response_time == 3

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_average_response_time_no_response(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        avg_response_time = utilityService.get_avg_response_time(email_list)
        assert avg_response_time is None

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_average_response_time_no_client_response(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        avg_response_time = utilityService.get_avg_response_time(email_list)
        assert avg_response_time is None

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_average_response_time_invalid_list_provided(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 0, 1, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 0, 0, 0)
            )
        ]
        with pytest.raises(ValueError):
            utilityService.get_avg_response_time(email_list)

    @mock.patch("api.v2.services.issuesService.collection_configurations")
    def test_get_average_response_time_double_client(self, mock_collection):
        import api.v2.services.utilityService as utilityService
        email_list = [
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 1, 0, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Client",
                time=datetime(2024, 1, 1, 1, 10, 0)
            ),
            EmailInDB(
                message="lorem ipsum",
                sender_type="Company",
                time=datetime(2024, 1, 1, 1, 12, 0)
            )
        ]
        avg_response_time = utilityService.get_avg_response_time(email_list)
        assert avg_response_time == 12

