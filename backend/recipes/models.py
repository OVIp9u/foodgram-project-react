from django.db import models
from django.core.validators import RegexValidator
from users.models import User

class Tag(models.Model):
    """Модель тега рецепта."""
    name = models.CharField(
        max_length=200,
        unique=True,
        null=True,
        blank=False,
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=False,
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Содержит недопустимый символ",
            )
        ],
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name =models.CharField(
        max_length=200,
        unique=True,
        null=True,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        unique=True,
        null=True,
        blank=False,
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    
    tags =  models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    '''author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )'''
    ingredients = models.ManyToManyField(
        Ingredient,
        #through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    name = models.CharField(
        'Название',
        max_length=200
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name
