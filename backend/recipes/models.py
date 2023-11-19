from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


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
        #unique=True,
        null=True,
        blank=False,
    )
    measurement_unit = models.CharField(
        max_length=200,
        null=True,
        blank=False,
    )

    class Meta:
        unique_together = ('name', 'measurement_unit',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
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

class RecipeIngredient(models.Model):
    """Модель Рецепт-Ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField('Quantity',)

    class Meta:
        verbose_name = 'RecipeIngredient'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
