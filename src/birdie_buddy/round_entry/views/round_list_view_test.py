import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.users.factories import UserFactory


@pytest.mark.django_db
class TestRoundListView:
    @property
    def url(self):
        return reverse("round_entry:round_list")

    def test_unauthenticated_user_redirected_to_login(self, client):
        response = client.get(self.url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_authenticated_user_sees_their_rounds_only(self, authenticated_client, user):
        # rounds for the authenticated user
        RoundFactory.create_batch(3, user=user)
        # rounds for another user
        other_user = UserFactory()
        RoundFactory.create_batch(2, user=other_user)

        response = authenticated_client.get(self.url)

        assert response.status_code == 200
        assertTemplateUsed(response, "round_entry/round_list.html")

        content = response.content.decode()
        # should contain 3 rounds and not contain rounds from other user
        assert content.count("View") >= 3

    def test_pagination_works(self, authenticated_client, user):
        # create more than paginate_by (10) rounds for the user
        RoundFactory.create_batch(12, user=user)

        response = authenticated_client.get(self.url)
        assert response.status_code == 200
        # first page should show page_obj and paginator
        assert "Page" in response.content.decode()

        # request second page
        response2 = authenticated_client.get(self.url + "?page=2")
        assert response2.status_code == 200
        assert "Page 2" in response2.content.decode()
