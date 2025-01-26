import factory
from birdie_buddy.round_entry.models import Round
from birdie_buddy.users.factories import UserFactory


class RoundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Round

    user = factory.SubFactory(UserFactory)
    holes_played = factory.Faker("random_int", min=1, max=18)
