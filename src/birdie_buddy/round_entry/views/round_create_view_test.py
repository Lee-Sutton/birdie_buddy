import pytest
from django.urls import reverse
from birdie_buddy.round_entry.models import Round
from pytest_django.asserts import assertTemplateUsed, assertRedirects


@pytest.mark.django_db
class TestRoundCreateView:
    @property
    def url(self):
        return reverse("round_entry:create_round")

    def test_unauthenticated_user_redirected_to_login(self, client):
        response = client.get(self.url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_authenticated_user_can_access_create_round(self, authenticated_client):
        url = reverse("round_entry:create_round")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "round_entry/round_form.html")

    def test_can_create_round(self, authenticated_client, user):
        data = {"course_name": "Test Golf Course", "holes_played": 18}

        response = authenticated_client.post(self.url, data)

        # Check if round was created
        assert Round.objects.count() == 1
        round = Round.objects.first()
        assert round.course_name == "Test Golf Course"
        assert round.holes_played == 18
        assert round.user == user

        # Check redirect to first hole
        assertRedirects(
            response,
            reverse("round_entry:create_hole", kwargs={"id": round.id, "number": 1}),
        )

    @pytest.mark.parametrize(
        "data",
        [
            {"course_name": "", "holes_played": 18},
            {"course_name": "test", "holes_played": ""},
        ],
    )
    def test_invalid_form_returns_errors(self, data, authenticated_client):
        url = reverse("round_entry:create_round")

        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert Round.objects.count() == 0
        assert "This field is required" in response.content.decode()
