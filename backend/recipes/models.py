from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель тега."""
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
                message="Недопустимый символ",
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
        #verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
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
    """Модель связи Рецепт-Ингредиент."""
    recipe = models.ForeignKey(
        Recipe,
        #verbose_name='Рецепт',
        related_name='ingredient_list',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        #verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField('Quantity',)

    class Meta:
        #verbose_name = 'RecipeIngredient'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class UsersRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favourite(UsersRecipe):
    class Meta(UsersRecipe.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UsersRecipe):
    class Meta(UsersRecipe.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'