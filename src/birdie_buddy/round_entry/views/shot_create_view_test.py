import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.models import Round, Hole, Shot

User = get_user_model()


@pytest.fixture
def round(user):
    return RoundFactory(user=user, holes_played=18)


@pytest.fixture
def hole(round, user):
    return HoleFactory(user=user, round=round, number=1, score=3)


@pytest.mark.django_db
class TestCreateShotsView:
    def test_unauthenticated_user_redirected_to_login(self, client, round, hole):
        url = reverse(
            "round_entry:create_shots", kwargs={"id": round.id, "number": hole.number}
        )
        response = client.get(url)
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_authenticated_user_can_access_shots_form(
        self, authenticated_client, round, hole
    ):
        url = reverse(
            "round_entry:create_shots", kwargs={"id": round.id, "number": hole.number}
        )
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed("shots_form.html")

    def test_formset_has_correct_number_of_forms(
        self, authenticated_client, round, hole
    ):
        url = reverse(
            "round_entry:create_shots", kwargs={"id": round.id, "number": hole.number}
        )
        response = authenticated_client.get(url)
        assert response.context["formset"].total_form_count() == hole.score

    def test_can_create_shots(self, authenticated_client, round, hole, user):
        url = reverse(
            "round_entry:create_shots", kwargs={"id": round.id, "number": hole.number}
        )

        # Prepare formset data
        data = {
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-start_distance": "400",
            "form-0-lie": "tee",
            "form-1-start_distance": "100",
            "form-1-lie": "rough",
            "form-2-start_distance": "10",
            "form-2-lie": "green",
        }

        response = authenticated_client.post(url, data)

        # Check if shots were created
        assert Shot.objects.count() == 3
        shots = Shot.objects.all()

        # Verify first shot
        assert shots[0].start_distance == 400
        assert shots[0].lie == "tee"
        assert shots[0].hole == hole
        assert shots[0].user == user

        # Verify redirect
        assert response.status_code == 302
        assertRedirects(
            response,
            reverse(
                "round_entry:create_hole",
                kwargs={"id": round.id, "number": hole.number + 1},
            ),
        )

    def test_invalid_formset_returns_errors(self, authenticated_client, round, hole):
        url = reverse(
            "round_entry:create_shots", kwargs={"id": round.id, "number": hole.number}
        )

        # Submit invalid data (missing required fields)
        data = {
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-start_distance": "",  # Missing required field
            "form-0-lie": "fairway",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert Shot.objects.count() == 0
        assert "This field is required" in response.content.decode()

    def test_cannot_access_other_users_hole(self, authenticated_client):
        # Create another user's hole
        other_user = User.objects.create_user(username="other", password="pass123")
        other_round = RoundFactory(
            user=other_user,
        )
        other_hole = HoleFactory(user=other_user, round=other_round, number=1, score=3)

        url = reverse(
            "round_entry:create_shots",
            kwargs={"id": other_round.id, "number": other_hole.number},
        )
        response = authenticated_client.get(url)
        assert response.status_code == 404
