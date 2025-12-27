from django.contrib.auth import get_user_model
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
