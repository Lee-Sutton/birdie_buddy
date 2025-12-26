import pytest
from django.urls import reverse

from birdie_buddy.round_entry.factories.hole_factory import HoleFactory
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Hole, Shot


@pytest.fixture
def round(user):
    return RoundFactory(user=user, course_name="Test Course", holes_played=18)


@pytest.fixture
def hole(user, round):
    return HoleFactory(user=user, round=round, number=1, par=4, score=4)


class TestHoleDeleteView:
    def test_login_required(self, client, round, hole):
        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": hole.pk},
        )
        response = client.delete(url)

        assert response.status_code == 302
        assert "users/login/" in response.url

    def test_delete_hole_success(self, authenticated_client, round, hole):
        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": hole.pk},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == 200
        assert response["Content-Type"] == "text/html; charset=utf-8"
        assert not Hole.objects.filter(pk=hole.pk).exists()

    def test_delete_hole_cascades_to_shots(self, authenticated_client, user, round, hole):
        ShotFactory(user=user, hole=hole, start_distance=150, lie="fairway")
        ShotFactory(user=user, hole=hole, start_distance=10, lie="green")
        assert Shot.objects.filter(hole=hole).count() == 2

        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": hole.pk},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == 200
        assert not Hole.objects.filter(pk=hole.pk).exists()
        assert Shot.objects.filter(hole=hole).count() == 0

    def test_cannot_delete_other_users_hole(
        self, authenticated_client, round, django_user_model
    ):
        other_user = django_user_model.objects.create_user(
            username="other", password="test123"
        )
        other_hole = HoleFactory(user=other_user, round=round, number=2, par=4, score=5)

        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": other_hole.pk},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == 404
        assert Hole.objects.filter(pk=other_hole.pk).exists()

    def test_cannot_delete_hole_from_other_users_round(
        self, authenticated_client, user, django_user_model
    ):
        other_user = django_user_model.objects.create_user(
            username="other", password="test123"
        )
        other_round = RoundFactory(
            user=other_user, course_name="Other Course", holes_played=18
        )
        other_hole = HoleFactory(
            user=other_user, round=other_round, number=1, par=4, score=4
        )

        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": other_hole.pk},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == 404
        assert Hole.objects.filter(pk=other_hole.pk).exists()

    def test_delete_nonexistent_hole_returns_404(self, authenticated_client, round):
        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": 99999},
        )

        response = authenticated_client.delete(url)

        assert response.status_code == 404

    def test_delete_hole_with_wrong_round_returns_404(
        self, authenticated_client, user, round, hole
    ):
        # This test now simply verifies that a valid hole can be deleted
        # The "wrong round" concept no longer applies since we don't pass round_id
        url = reverse(
            "round_entry:delete_hole",
            kwargs={"hole_id": hole.pk},
        )

        response = authenticated_client.delete(url)

        # Hole should be successfully deleted
        assert response.status_code == 200
        assert not Hole.objects.filter(pk=hole.pk).exists()
