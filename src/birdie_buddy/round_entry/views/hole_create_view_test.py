"""Test suite for the hole create view"""

from django.urls import reverse
import pytest
from django.test import Client
from pytest_django.asserts import assertRedirects
from birdie_buddy.round_entry.models import Round


@pytest.fixture
def round(user):
    # TODO: create round factory
    return Round.objects.create(user=user, course_name="Pitts", holes_played=18)


def test_login_required(client: Client, round):
    url = reverse("round_entry:create_hole", kwargs={"id": round.pk, "number": 1})
    response = client.get(url)
    assertRedirects(response, "/login")
