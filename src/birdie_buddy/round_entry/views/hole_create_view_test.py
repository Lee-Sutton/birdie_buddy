"""Test suite for the hole create view"""

from django.urls import reverse
import pytest
from django.test import Client
from pytest_django.asserts import assertTemplateUsed
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.models import Round, Hole
from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Shot


@pytest.fixture
def round(user):
    return RoundFactory(user=user, course_name="Pitts", holes_played=18)


class TestHoleCreateView:
    def test_login_required(self, client: Client, round):
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        response = client.get(url)
        assert response.status_code == 302
        assert "users/login/" in response.url

    def test_get_create_hole_form(self, authenticated_client, round):
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        response = authenticated_client.get(url)

        assert response.status_code == 200
        assertTemplateUsed("hole_form.html")

    def test_create_new_hole(self, authenticated_client, round, user):
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        data = {
            "score": 4,
            "mental_scorecard": 4,
            "par": 4,
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 302
        assert (
            reverse("round_entry:create_shots", kwargs={"id": round.pk, "number": 1})
            in response.url
        )

        hole = Hole.objects.get(round=round, number=1)
        assert hole.score == 4
        assert hole.mental_scorecard == 4
        assert hole.user == user

    def test_cannot_create_hole_for_other_users_round(
        self, authenticated_client, round, django_user_model
    ):
        # Create another user and their round
        other_user = django_user_model.objects.create_user(
            username="other", password="test123"
        )
        other_round = Round.objects.create(
            user=other_user, course_name="Other Course", holes_played=18
        )

        url = reverse(
            "round_entry:create_hole", kwargs={"id": other_round.pk, "number": 1}
        )
        response = authenticated_client.get(url)

        assert response.status_code == 404

    def test_invalid_form_data(self, authenticated_client, round):
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        data = {"score": 0, "mental_scorecard": ""}  # Invalid score

        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert "form" in response.context
        assert len(response.context["form"].errors) > 0
        assert Hole.objects.count() == 0

    def test_update_existing_hole_and_shots(self, authenticated_client, round, user):
        # Create a hole and some shots
        hole = HoleFactory(user=user, round=round, number=1, score=3, par=4, mental_scorecard=3)
        ShotFactory(hole=hole, user=user, start_distance=100, lie="fairway")
        ShotFactory(hole=hole, user=user, start_distance=50, lie="green")
        assert Shot.objects.filter(hole=hole).count() == 2

        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        data = {"score": 4, "mental_scorecard": 4, "par": 4}
        response = authenticated_client.post(url, data)
        assert response.status_code == 302
        # Should redirect to shots entry for this hole
        assert reverse("round_entry:create_shots", kwargs={"id": round.pk, "number": 1}) in response.url
        # Should update the hole
        hole.refresh_from_db()
        assert hole.score == 4
        assert hole.mental_scorecard == 4
        # Should not create a new hole
        assert round.hole_set.filter(number=1).count() == 1

    def test_finish_button_shown_if_round_complete(self, authenticated_client, round, user):
        # Fill all holes for the round
        for n in range(1, round.holes_played + 1):
            h = HoleFactory(user=user, round=round, number=n, score=3, par=4, mental_scorecard=3)
            ShotFactory(hole=h, user=user, start_distance=100, lie="fairway")
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert b"Finish" in response.content

    def test_hole_form_prefilled_when_editing(self, authenticated_client, round, user):
        hole = HoleFactory(user=user, round=round, number=1, score=5, par=4, mental_scorecard=2)
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        # The form should be prefilled with the hole's values
        form = response.context["form"]
        assert form.initial["score"] == 5
        assert form.initial["par"] == 4
        assert form.initial["mental_scorecard"] == 2

    def test_back_and_next_links_present(self, authenticated_client, round, user):
        # Test for first hole
        url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert reverse("round_entry:create_round") in response.content.decode()
        # Test for a later hole
        url2 = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 2})
        response2 = authenticated_client.get(url2)
        assert response2.status_code == 200
        prev_url = reverse("round_entry:create_shots", kwargs={"id": round.pk, "number": 1})
        assert prev_url in response2.content.decode()
