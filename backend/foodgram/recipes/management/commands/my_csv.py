import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User

CSV_DIR = {
    Category: 'category.csv',
    Comments: 'comments.csv',
    Genre: 'genre.csv',
    Review: 'review.csv',
    Title: 'titles.csv',
    User: 'users.csv',
}


class Command(BaseCommand):
    help = 'CSV to SQL'

    def handle(self, *args, **kwargs):
        for model, csv_f in CSV_DIR.items():
            with open(
                f'{settings.BASE_DIR}/static/data/{csv_f}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    model(**data) for data in reader)

        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
