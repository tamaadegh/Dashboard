import factory
from factory.django import DjangoModelFactory
from faker import Faker
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image as PILImage

from nxtbn.filemanager.models import Image
from nxtbn.users.tests import UserFactory

faker = Faker()

class ImageFactory(DjangoModelFactory):
    class Meta:
        model = Image

    created_by = factory.SubFactory(UserFactory) 
    last_modified_by = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=50))
    image_alt_text = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=50))

    @factory.lazy_attribute
    def image(self):
        # Create an in-memory image file
        img = PILImage.new('RGB', (100, 100), color=(155, 0, 0))  # Red square
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f"{faker.file_name(extension='jpg')}")

