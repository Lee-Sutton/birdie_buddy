import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed
from birdie_buddy.round_entry.factories.full_round_factory import full_round_factory
from birdie_buddy.round_entry.factories.round_factory import RoundFactory


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
        round = full_round_factory(user=user)
        url = reverse("round_entry:round_detail", kwargs={"id": round.id})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assertTemplateUsed("round_detail.html")
        assert response.context["round"] == round
        assert list(response.context["holes"]) == list(round.hole_set.all())

    def test_incomplete_round_shows_continue(self, authenticated_client, user):
        """Incomplete rounds render the continue button with correct href"""
        round = RoundFactory(user=user, holes_played=18)
        url = reverse("round_entry:round_detail", kwargs={"id": round.id})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assert response.context["show_stats"] is False
        # continue_href should be in context and point to create_hole for hole 1
        assert "continue_href" in response.context
        expected = reverse(
            "round_entry:create_hole", kwargs={"id": round.id, "number": 1}
        )
        assert response.context["continue_href"] == expected
        assert expected in response.content.decode()

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
