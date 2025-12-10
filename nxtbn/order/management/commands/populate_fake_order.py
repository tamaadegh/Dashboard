import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from django.contrib.auth import get_user_model
from nxtbn.order import OrderStatus
from nxtbn.payment import PaymentStatus
from nxtbn.product.models import Product, ProductVariant
from nxtbn.order.models import Order, OrderLineItem, Address
from nxtbn.payment.models import Payment, PaymentMethod

fake = Faker()


class Command(BaseCommand):
    help = 'Generate fake orders for selected products'
    
    def handle(self, *args, **options):
        selected_products = Product.objects.filter(variants__isnull=False).distinct().order_by('?')[:5]
        User = get_user_model()

        for product in selected_products:
            default_variant = product.variants.first()  
            if not default_variant:
                self.stdout.write(self.style.WARNING(f"Skipping product '{product.name}' because it doesn't have any variants defined"))
                continue

            shipping_address = Address.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                street_address=fake.street_address(),
                city=fake.city(),
                country=fake.country(),
                phone_number=fake.phone_number(),
                email=fake.email()
            )
            billing_address = Address.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                street_address=fake.street_address(),
                city=fake.city(),
                country=fake.country(),
                phone_number=fake.phone_number(),
                email=fake.email()
            )

            random_user = User.objects.order_by('?').first()

            payment_status = random.choice(PaymentStatus.values) 
            paid_at = timezone.now() if payment_status == PaymentStatus.CAPTURED else None

            # Convert price to sub-units (e.g., cents)
            variant_price_subunit = int(default_variant.price * 100)

            order = Order.objects.create(
                user=random_user, 
                supplier=product.supplier,
                # payment_method=random.choice(PaymentMethod.values),  
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_price=variant_price_subunit,  # Save price in sub-units
                status=random.choice(OrderStatus.values) 
            )

            OrderLineItem.objects.create(
                order=order,
                variant=default_variant,
                quantity=random.randint(1, 5),  
                price_per_unit=variant_price_subunit,  # Price per unit in sub-units
                total_price=variant_price_subunit  # Total price in sub-units
            )

            payment_status = random.choice(PaymentStatus.values) 
            paid_at = timezone.now() if payment_status == PaymentStatus.CAPTURED else None

            payment = Payment.objects.create(
                order=order,
                payment_method=random.choice([PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL]),  
                payment_amount=order.total_price,  # Payment amount in sub-units
                payment_status=payment_status,
                paid_at=paid_at,
            )

            self.stdout.write(self.style.SUCCESS(f"Fake order created for product '{product.name}'. Payment {'successful' if payment_status == PaymentStatus.CAPTURED else 'failed'}"))

        self.stdout.write(self.style.SUCCESS('Fake orders generation completed'))
