import json
import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
import requests
from nxtbn.core.utils import normalize_amount_currencywise
from nxtbn.product.models import Category, Collection, Product, ProductType, ProductVariant
from django.contrib.auth import get_user_model
from nxtbn.product import StockStatus, WeightUnits
from faker import Faker
from nxtbn.filemanager.models import Image
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import random
from tqdm import tqdm

User = get_user_model()

class Command(BaseCommand):
    help = 'Create fake products with multiple variants'

    def add_arguments(self, parser):
        parser.add_argument('--num_products', type=int, default=10, help='Number of fake products to create')

    def handle(self, *args, **options):
        fake = Faker()

        static_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'images/tamaade.png')
        media_image_path = os.path.join(settings.MEDIA_ROOT, 'tamaade.png')

        if not os.path.exists(media_image_path):
            shutil.copy(static_image_path, media_image_path)

        
        num_products = options['num_products']
        categories = Category.objects.all()
        collections = Collection.objects.all()


        for _ in tqdm(range(num_products)):
            category = random.choice(categories)
            collection = random.choice(collections)
            product_type, created  = ProductType.objects.get_or_create(name='Automatic Product Type')
            weight_unit = random.choice(WeightUnits.choices)

            superuser = User.objects.filter(username='admin').first()
            if not superuser:
                self.stdout.write(self.style.NOTICE('Creating superuser with username "admin" and password "admin"...'))
                superuser = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

         
            name = fake.word() 
            with open(media_image_path, 'rb') as image_file:
                image = Image.objects.create(
                    created_by=superuser,
                    name=name,
                    image=File(image_file, name='tamaade.png'),
                    image_alt_text=fake.sentence()
                )

            # Dummy Editor.js one-line content for description
            description_json = json.dumps([
                {
                    "type": "paragraph",
                    "children": [
                        {"text": ""}
                    ]
                },
                {
                    "type": "code",
                    "children": [
                        {"text": "This is a code block."}
                    ]
                },
                {
                    "type": "bulleted-list",
                    "children": [
                        {
                            "type": "list-item",
                            "children": [
                                {"text": "This is a bullet item."}
                            ]
                        }
                    ]
                }
            ])

            product = Product.objects.create(
                name=fake.word(),
                summary=fake.sentence(),
                description=description_json,
                brand=fake.company(),
                category=category,
                created_by=superuser,
                last_modified_by=None,
                product_type=product_type,
                
            )

            product.collections.set([collection])
            product.images.set([image])

            default_variant = ProductVariant.objects.create(
                product=product,
                name='Default',
                currency=settings.BASE_CURRENCY,
                price=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                cost_per_unit=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                compare_at_price=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                sku=fake.uuid4(),
                # weight_unit=weight_unit[0],
                weight_value=random.uniform(1, 1000),
            )


            product.default_variant = default_variant

            for _ in range(random.randint(1, 5)):
                # weight_unit = random.choice(WeightUnits.choices)
                variant = ProductVariant.objects.create(
                    product=product,
                    name=fake.word(),
                    currency=settings.BASE_CURRENCY,
                    price=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                    cost_per_unit=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                    compare_at_price=normalize_amount_currencywise(random.uniform(10, 1000), settings.BASE_CURRENCY),
                    sku=fake.uuid4(),
                    # weight_unit=weight_unit[0],
                    weight_value=random.uniform(1, 1000),
                )

            product.save()

        self.stdout.write(self.style.SUCCESS(f'Created {num_products} fake products with multiple variants'))
        