import csv

# from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

# from django.shortcuts import get_object_or_404

MODELS_FIELDS = {}


class Command(BaseCommand):
    help = 'CSV to SQL'

    # def add_arguments(self, parser):
    #     parser.add_argument('--path', type=str, help="file path")
    #     parser.add_argument('--model_name', type=str, help="model name")
    #     parser.add_argument(
    #         '--app_name',
    #         type=str,
    #         help="django app name that the model is connected to",
    #     )

    def handle(self, *args, **options):
        # file_path = options['path']
        # model = apps.get_model(options['app_name'], options['model_name'])
        # model = apps.get_model('recipes', 'Ingredient')
        with open(
                # file_path,
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
            # reader = csv.DictReader(csv_file, delimiter=',')
            # for row in reader:
            #     for field, value in row.items():
            #         if field in MODELS_FIELDS.keys():
            #             row[field] = get_object_or_404(
            #                 MODELS_FIELDS[field], pk=value
            #             )
            #     model.objects.create(**row)
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
