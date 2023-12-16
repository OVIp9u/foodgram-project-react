import csv

from api.constants import PATH
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


def clear_data(self):
    Ingredient.objects.all().delete()
    self.stdout.write(
        self.style.WARNING('Существующие записи ингредиентов были удалены.')
    )


class Command(BaseCommand):
    help = "Загружает CSV данные из файла data."

    def add_arguments(self, parser):
        # Аргумент для удаления всех имеющихся в БД данных
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            dest='delete_existing',
            default=False,
            help='Удаляет предыдущие данные',
        )

    def handle(self, *args, **options):
        """Загрузка Ингредиентов."""

        if options["delete_existing"]:
            clear_data(self)
            return None
        with open(
            PATH, encoding='utf-8', newline=''
        ) as csvfile:
            reader = csv.reader(csvfile)
            for name, measurement_unit in reader:
                Ingredient.objects.get_or_create(
                    name=name, measurement_unit=measurement_unit
                )

        self.stdout.write(
            self.style.SUCCESS('Записи ингредиентов сохранены')
        )
