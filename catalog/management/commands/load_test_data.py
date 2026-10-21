import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Загружает тестовые данные (категории и продукты) из фикстур"

    def handle(self, *args, **options):
        # Очистка старых данных
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Загрузка фикстур
        fixtures_dir = os.path.join("catalog", "fixtures")
        call_command("loaddata", os.path.join(fixtures_dir, "categories.json"))
        call_command("loaddata", os.path.join(fixtures_dir, "products.json"))

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены"))
