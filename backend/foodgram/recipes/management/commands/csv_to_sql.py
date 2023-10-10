import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

MODELS_FIELDS = {}


class Command(BaseCommand):
    help = 'CSV to SQL'

    def handle(self, *args, **options):
        with open(
                f'{settings.BASE_DIR}/data/ingredients.csv',
                'rt',
                encoding='utf-8',
        ) as csv_file:
            file_reader = csv.reader(csv_file)
            for row in file_reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
