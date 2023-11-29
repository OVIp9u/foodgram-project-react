from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    password = models.CharField(
        'Пароль',
        max_length=150,
        null=True,
        blank=False,
    )
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

class Subscribe(models.Model):
    """Модель подписки"""
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribing',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name="subscriber",
        on_delete=models.CASCADE,
    )
    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
