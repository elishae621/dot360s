import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from user.models import User, Driver
from faker import Factory


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Driver

    image = factory.django.ImageField(
        from_path=r"C:\Users\Elisha\Pictures\Screenshots\Screenshot (23).png", filename=r"\uploadedimage", format="png")
    user = factory.SubFactory(
        'user.tests.factories.UserFactory', Driver=None)


@factory.django.mute_signals(post_save)
class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Faker('email')
    firstname = factory.Faker('first_name')
    lastname = factory.Faker('last_name')
    password = factory.Faker('password')
    Driver = factory.RelatedFactory(
        ProfileFactory, factory_related_name='user')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        email = kwargs.pop("email", None)
        firstname = kwargs.pop("firstname", None)
        lastname = kwargs.pop("lastname", None)
        password = kwargs.pop("password", None)
        obj = User(email=email, firstname=firstname, lastname=lastname)
        obj.set_password(password)
        obj.save()
        return obj
