from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

MAX_LENGHT_EMAIL = 254
MAX_LENGHT = 150


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LENGHT_EMAIL,
        unique=True,
    )
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_LENGHT,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимый символ'
        )]
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LENGHT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='subscribing',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=models.Q(_negated=True, author=models.F('user')),
                name='self_follow',
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
