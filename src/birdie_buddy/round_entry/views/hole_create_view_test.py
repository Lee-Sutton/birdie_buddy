"""Test suite for the hole create view"""

from django.urls import reverse
import pytest
from django.test import Client
from pytest_django.asserts import assertTemplateUsed
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.models import Round, Hole


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
