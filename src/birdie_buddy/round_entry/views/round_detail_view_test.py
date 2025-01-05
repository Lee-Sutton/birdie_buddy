import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.factories.hole_factory import HoleFactory


@pytest.mark.django_db
class TestRoundDetailView:
    def test_login_required(self, client):
        """Test that view requires authentication"""
        round = RoundFactory()
        url = reverse("round_entry:round_detail", kwargs={"id": round.id})
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_get_round_detail(self, authenticated_client, user):
        """Test successful round detail retrieval"""
        round = RoundFactory(user=user)
        HoleFactory.create_batch(18, round=round)

        url = reverse("round_entry:round_detail", kwargs={"id": round.id})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assertTemplateUsed("round_detail.html")
        assert response.context["round"] == round
        assert list(response.context["holes"]) == list(round.hole_set.all())

    def test_get_round_detail_wrong_user(self, authenticated_client):
        """Test that users can't access other users' rounds"""
        round = RoundFactory()  # Created for a different user
        url = reverse("round_entry:round_detail", kwargs={"id": round.id})
        response = authenticated_client.get(url)
        assert response.status_code == 404

    def test_get_round_detail_not_found(self, authenticated_client):
        """Test 404 response for non-existent round"""
        url = reverse("round_entry:round_detail", kwargs={"id": 99999})
        response = authenticated_client.get(url)
        assert response.status_code == 404
