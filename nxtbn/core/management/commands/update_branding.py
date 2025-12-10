from django.core.management.base import BaseCommand
from nxtbn.core.models import SiteSettings, InvoiceSettings
from nxtbn.warehouse.models import Warehouse
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Update branding values for existing DB entries (Tamaade defaults)'

    def handle(self, *args, **options):
        updated = False
        # Update Site settings
        if SiteSettings.objects.exists():
            for ss in SiteSettings.objects.all():
                ss.site_name = 'Tamaade Ecommerce'
                ss.contact_email = 'contact@tamaade.com'
                ss.company_name = ss.company_name or 'Tamaade'
                ss.save()
            self.stdout.write(self.style.SUCCESS('Updated SiteSettings to Tamaade defaults'))
            updated = True

        # Update Invoice settings
        if InvoiceSettings.objects.exists():
            for inv in InvoiceSettings.objects.all():
                inv.store_name = 'Tamaade Ecommerce'
                inv.contact_email = 'billing@tamaade.com'
                inv.save()
            self.stdout.write(self.style.SUCCESS('Updated InvoiceSettings to Tamaade defaults'))
            updated = True

        # Update Django Site name
        if Site.objects.exists():
            for s in Site.objects.all():
                s.name = 'Tamaade Ecommerce'
                s.save()
            self.stdout.write(self.style.SUCCESS('Updated Django Site names to Tamaade Ecommerce'))
            updated = True

        if not updated:
            self.stdout.write(self.style.NOTICE('No branding changes required; no settings found.'))
