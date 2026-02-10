from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('product', '0021_product_product_pro_name_b60cd1_idx_and_more'),
    ]

    operations = [
        TrigramExtension(),
    ]
