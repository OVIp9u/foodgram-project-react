import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


OBJECTS_LIST = {
    "Ингредиенты": Ingredient,
}

def clear_data(self):
    for key, value in OBJECTS_LIST.items():
        value.objects.all().delete()
        self.stdout.write(
            self.style.WARNING(f'Существующие записи "{key}" были удалены.')
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
            help='Удаляет существующие данные, записанные ранее',
        )

    
    def handle(self, *args, **options):
        """Загрузка Ингредиентов."""

        if options["delete_existing"]:
            clear_data(self)

        records = []
        with open(
            '../data/ingredients.csv', encoding='utf-8', newline=''
        ) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                record = Ingredient(
                    name=row[0], measurement_unit=row[1]
                )
                records.append(record)

        Ingredient.objects.bulk_create(records)
        self.stdout.write(
            self.style.SUCCESS('Записи ингредиентов сохранены')
        )
